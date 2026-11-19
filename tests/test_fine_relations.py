from collections import defaultdict, deque
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import katia
from fine_relations import Builder, impact_paths, overlay_method


SOURCE = '''package p;
import java.util.Properties;
import java.util.Map;
import java.util.HashMap;

class Example {
    Properties a = new Properties();
    Properties b = new Properties();
    boolean enabled;
    static final String KEY = "cache.dir";
    void writeA(String value) { a.setProperty(KEY, value); }
    void writeB(String value) { b.setProperty(KEY, value); }
    String read(Properties config) { return config.getProperty(KEY); }
    void consumeA() {
        String dir = read(a);
        if (dir != null) {
            use(dir);
        } else {
            fail();
        }
    }
    void consumeB() { use(read(b)); }
    void otherKey() { use(a.getProperty("log.dir")); }
    void systemWrite(String value) { System.setProperty("cache.dir", value); }
    void systemRead() { use(System.getProperty("cache.dir")); }
    void overwrite() {
        String dir = a.getProperty(KEY);
        dir = "safe";
        use(dir);
    }
    void guarded(String text) {
        if (enabled) { use(text); } else { fail(); }
        while (enabled) { use(text); break; }
    }
    void use(String value) {}
    void fail() {}
}

class Settings {
    Map values = new HashMap();
    void setVariable(String key, String value) { values.put(key, value); }
    String getVariable(String key) { return (String) values.get(key); }
    String substitute(String text) { return text; }
    void setPaths(String value) { setVariable("cache.dir", value); }
}
class Parser {
    Settings settings = new Settings();
    Settings other = new Settings();
    void seed(String path) { settings.setPaths(path); }
    void dispatch() {
        Map attributes = new HashMap();
        attributes.put("file", settings.substitute("${cache.dir}/foo.jar"));
        consume(attributes);
    }
    void unrelated() { use(other.substitute("${cache.dir}/foo.jar")); }
    void consume(Map attributes) {
        String file = (String) attributes.get("file");
        if (file != null) { use(file); }
    }
    void use(String file) {}
}
'''


def reach(fine, starts, kind=None):
    outgoing=defaultdict(list)
    for edge in fine['edges']:
        outgoing[edge['source']].append(edge)
    seen=set(starts)
    queue=deque(starts)
    while queue:
        for edge in outgoing[queue.popleft()]:
            if edge['target'] not in seen:
                seen.add(edge['target'])
                queue.append(edge['target'])
    return seen


class FineRelationsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory()
        cls.root=Path(cls.temp.name).resolve()
        source=cls.root/'src/main/java/p/Example.java'
        source.parent.mkdir(parents=True)
        source.write_text(SOURCE)
        output=cls.root/'relations.json'
        subprocess.run([katia.java_path(),'--class-path',str(katia.JAR),
                        str(katia.ROOT/'src/StaticRelations.java'),str(cls.root),str(output)],
                       check=True,capture_output=True,timeout=60)
        cls.graph=json.loads(output.read_text())
        cls.fine=Builder(cls.root,cls.graph,[
            dict(type='type',fqn='p.Example'),dict(type='type',fqn='p.Parser')]).build()
        cls.nodes={n['id']:n for n in cls.fine['nodes']}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_config_namespaces_do_not_merge_equal_keys(self):
        keys=[n for n in self.fine['nodes'] if n['kind']=='configuration' and n['key']=='cache.dir']
        a=next(n for n in keys if n['namespace']=='field:p.Example.a')
        b=next(n for n in keys if n['namespace']=='field:p.Example.b')
        reached=reach(self.fine,[a['id']])
        self.assertNotIn(b['id'],reached)
        self.assertTrue(any(self.nodes[n].get('method')=='p.Example.consumeA()' for n in reached))
        self.assertFalse(any(self.nodes[n].get('method')=='p.Example.consumeB()' for n in reached))
        self.assertFalse(any(self.nodes[n].get('method')=='p.Example.otherKey()' for n in reached))

    def test_parameter_return_and_overwrite(self):
        a=next(n for n in self.fine['nodes'] if n['kind']=='configuration' and n['namespace']=='field:p.Example.a')
        reached=reach(self.fine,[a['id']])
        self.assertTrue(any(self.nodes[n].get('method')=='p.Example.read(java.util.Properties)'
                            and '/call@' in self.nodes[n].get('context','') for n in reached))
        use_calls=[n for n in self.fine['nodes'] if n.get('method')=='p.Example.overwrite()'
                   and n.get('code')=='use(dir)' and n['kind']=='call']
        self.assertTrue(use_calls)
        self.assertTrue(all(n['id'] not in reached for n in use_calls))

    def test_guard_labels_record_both_branches_and_loop(self):
        branches={e.get('branch') for e in self.fine['edges'] if e['kind']=='GUARDS'
                  and self.nodes[e['target']].get('method')=='p.Example.guarded(java.lang.String)'}
        self.assertTrue({'true','false','loop_body'} <= branches)
        field='field:p.Example.enabled'
        reached=reach(self.fine,[field])
        self.assertTrue(any(self.nodes[n]['kind']=='condition' for n in reached))

    def test_config_wrapper_substitution_container_and_parameter_chain(self):
        keys=[n for n in self.fine['nodes'] if n['kind']=='configuration'
              and n['namespace']=='field:p.Parser.settings' and n['key']=='cache.dir']
        self.assertEqual(len(keys),1)
        reached=reach(self.fine,[keys[0]['id']])
        self.assertTrue(any(self.nodes[n].get('method')=='p.Parser.consume(java.util.Map)' for n in reached))
        self.assertFalse(any(self.nodes[n].get('method')=='p.Parser.unrelated()' for n in reached))
        self.assertTrue(any(e['kind']=='CONFIG_WRITE' and e['target']==keys[0]['id'] for e in self.fine['edges']))

    def test_overlay_checks_parent_and_builds_missing_field_condition(self):
        fqn='p.Example.guarded(java.lang.String)'
        lines=SOURCE.splitlines()
        row=next(i+1 for i,line in enumerate(lines) if 'if (enabled)' in line)
        old=lines[row-1]
        new=old.replace('enabled','newSwitch')
        diff=f'@@ -{row} +{row} @@\n-{old}\n+{new}'
        seed=dict(type='executable',fqn=fqn,file='src/main/java/p/Example.java',git_diff_hunk=diff)
        fine=Builder(self.root,self.graph,[seed]).build()
        fields=[n for n in fine['nodes'] if n.get('fqn')=='p.Example.newSwitch']
        self.assertTrue(fields)
        self.assertTrue(any(n['kind']=='condition' and n.get('version')=='seed_after' for n in fine['nodes']))
        self.assertFalse(fine['unresolved'])
        with self.assertRaisesRegex(ValueError,'does not match'):
            overlay_method(lines,row,row,f'@@ -{row} +{row} @@\n-bad\n+good')

    def test_system_property_namespace_and_node_limit(self):
        slots=[n for n in self.fine['nodes'] if n['kind']=='configuration'
               and n['namespace']=='system_properties' and n['key']=='cache.dir']
        self.assertEqual(len(slots),1)
        reached=reach(self.fine,[slots[0]['id']])
        self.assertTrue(any(self.nodes[n].get('method')=='p.Example.systemRead()' for n in reached))
        from unittest.mock import patch
        with patch('fine_relations.MAX_NODES',10):
            fine=Builder(self.root,self.graph,[dict(type='type',fqn='p.Example')]).build()
        self.assertTrue(fine['truncated'])
        self.assertLessEqual(len(fine['nodes']),10)

    def test_overlay_line_shift_accounts_for_unseen_edits_before_the_method(self):
        lines=['class C {','void method() {','work();','}','}']
        fragment,touched,shift=overlay_method(lines,2,4,'@@ -3,0 +14,1 @@\n+next();')
        self.assertIn('work();\nnext();',fragment)
        self.assertEqual(touched,[(14,14)])
        self.assertEqual(shift,10)
