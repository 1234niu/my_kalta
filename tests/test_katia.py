import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
import katia

class PipelineTests(unittest.TestCase):
    def test_data_integrity(self):
        report=katia.prepare()
        self.assertEqual(report['tasks'],263)
        self.assertEqual(sum(report['entity_counts'].values()),1931)
        task=katia.load_task(0)
        self.assertNotIn('impacted',task)
        self.assertNotIn('commit',task)

    def test_no_gold_in_prompts_and_added_predictions_allowed(self):
        task=katia.load_task(0)
        task.update(impacted=['SECRET_GOLD'],non_related=['SECRET_UNRELATED'])
        for variant, stage in [('sp',0),('ma',0),('ma',1),('ma',2)]:
            prompt=json.dumps(katia.messages(variant,task,['p.C.x()'],stage,'evidence'))
            self.assertNotIn('SECRET_',prompt)
        self.assertEqual(katia.parse_prediction('["p.New.newMethod()"]'),['p.New.newMethod()'])

    def test_strict_output(self):
        for text in ['```json\n[]\n```','{"predictions":[]}','[1]','[null]','[""]']:
            with self.assertRaises((ValueError,TypeError)):
                katia.parse_prediction(text)
        self.assertEqual(katia.parse_prediction('["a.B.c()","a.B.c()"]'),['a.B.c()'])

    def test_overloads_fields_classes_and_empty(self):
        self.assertEqual(katia.ce('a.Outer.Inner.m(java.lang.String)'), 'Inner.m')
        self.assertEqual(katia.ce('a.Outer.Inner.field'),'Inner.field')
        self.assertEqual(katia.score(['a.C.m(int)'],['a.C.m(String)'],'FQN')['f1'],0)
        self.assertEqual(katia.score(['a.C.m(int)'],['a.C.m(String)'],'CE')['f1'],1)
        self.assertEqual(katia.score([],['a.C.f'],'FQN')['precision'],0)

    def test_median_then_macro_and_missing_run(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/'dataset/processed').mkdir(parents=True)
            (root/'dataset/processed/evaluation-only.jsonl').write_text(json.dumps({'id':'x','impacted':[{'fqn':'p.C.a()'}]})+'\n')
            for rep,pred in enumerate([['p.C.a()'],[],['p.C.a()','p.C.b()']]):
                katia.dump(root/f'results/runs/t/sp/x/{rep}/prediction.json',{'predictions':pred})
            with patch.object(katia,'ROOT',root),patch.object(katia,'load_task',return_value={'id':'x'}):
                result=katia.evaluate('t','sp',[0],3)
                self.assertAlmostEqual(result['metrics']['FQN']['f1'],2/3)
                self.assertFalse(result['complete_benchmark'])
                with self.assertRaises(FileNotFoundError): katia.evaluate('t','sp',[0],4)

class AuthorJarTests(unittest.TestCase):
    def test_direct_dependencies_field_type_constructor_and_absent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); src=root/'src/main/java/p'; src.mkdir(parents=True)
            (src/'A.java').write_text('''package p;
class B { void leaf() {} }
class A extends B {
 int value;
 A() { value=1; }
 void seed() { helper(); }
 void helper() { leaf(); }
 void caller() { seed(); }
 void indirect() { caller(); }
 int reader() { return value; }
 void writer() { value=2; }
 A factory() { return new A(); }
}
class Child extends A {}
''')
            out=root/'outputs';out.mkdir()
            def check(kind,fqn,name):
                return katia.jar_seed(root,{'type':kind,'fqn':fqn},out/name)
            methods=check('executable','p.A.seed()','method.json')
            self.assertIn('p.A.helper()',methods)
            self.assertIn('p.A.caller()',methods)
            self.assertNotIn('p.A.indirect()',methods)
            self.assertNotIn('p.B.leaf()',methods)
            fields=check('field','p.A.value','field.json')
            self.assertIn('p.A.reader()',fields)
            self.assertIn('p.A.writer()',fields)
            types=check('type','p.A','type.json')
            self.assertIn('p.B',types)
            self.assertIn('p.Child',types)
            constructor=check('executable','p.A.A()','ctor.json')
            self.assertIn('p.A.factory()',constructor)
            self.assertEqual(check('executable','p.A.added()','missing.json'),{})
            katia.dump(katia.ROOT/'results/author-jar-fixture.json',dict(methods=methods,fields=fields,types=types,constructor=constructor,absent={}))

if __name__=='__main__': unittest.main()
