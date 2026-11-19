from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from diff_overlay import seed_field_accesses
from static_compare import field_paths


class StaticFieldTests(unittest.TestCase):
    def test_diff_records_existing_writes_and_reads_but_ignores_locals(self):
        seed = dict(type='executable', fqn='p.C.seed(int)', file='C.java', git_diff_hunk='''@@ -20,0 +20,4 @@
+if (!enabled && limit < THRESHOLD) {
+    this.path = resolve();
+    limit = 0;
+}''')
        graph = dict(entities=['p.Parent.path'], fieldTypes={'p.Parent.path': 'java.lang.String'},
                     parents={'p.C': 'p.Parent'}, variables={'p.C.seed(int)': {'limit': 'int'}})
        self.assertEqual(
            {(access['edge'], access['proposed_fqn'], access['after_line'])
             for access in seed_field_accesses(graph, [seed])},
            {('ADDED_WRITE', 'p.Parent.path', 21), ('ADDED_READ', 'p.C.enabled', 20),
             ('ADDED_READ', 'p.C.THRESHOLD', 20)})

    def test_separate_arms_trace_only_their_expected_paths(self):
        seed = dict(type='executable', fqn='p.C.seed()')
        graph = dict(edges=[
            {'from': 'p.C.seed()', 'to': 'p.D.check()', 'kind': 'CALLS'},
            {'from': 'p.D.check()', 'to': 'p.D.flag', 'kind': 'READ'},
            {'from': 'p.C.get()', 'to': 'p.C.path', 'kind': 'READ'},
            {'from': 'p.C.clean()', 'to': 'p.C.get()', 'kind': 'CALLS'},
        ])
        write = dict(seed=seed['fqn'], proposed_fqn='p.C.path', edge='ADDED_WRITE', after_line=5)
        mixed = field_paths(graph, [seed], mixed=True)
        diff = field_paths(graph, [seed], [write])
        self.assertEqual(set(mixed), {'p.D.flag'})
        self.assertEqual(set(diff), {'p.C.path', 'p.C.get()', 'p.C.clean()'})
        self.assertEqual([edge.get('kind', edge.get('edge')) for edge in diff['p.C.clean()']],
                         ['ADDED_WRITE', 'READ', 'CALLS'])
