from pathlib import Path
import sys
import unittest
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ma_planned import diff_nodes, select_packets


class PlannedTests(unittest.TestCase):
    def test_review_reserves_two_slots_for_distinct_plans(self):
        overlap = {f'common{i}' for i in range(7)}
        candidates = {name: {'plans': {}} for name in sorted(overlap)}
        candidates.update({name: {'plans': {'P1': {}}} for name in ('novel1', 'novel2')})
        self.assertEqual(select_packets(candidates, overlap),
                         ['common0', 'common1', 'common2', 'common3', 'novel1', 'novel2'])

    def test_unqualified_diff_call_is_a_seed_class_hypothesis(self):
        seed = 'p.Source.seed()'
        call = dict(seed=seed, receiver=None, file='p/Source.java', after_line=5,
                    expression='helper(value)', inferred_targets=['p.Util.helper(java.lang.String)'])
        graph = SimpleNamespace(seeds={seed}, repo=SimpleNamespace(locations={}))
        result = diff_nodes({'seed_diff_overlay': {'added_calls': [call]}}, graph)
        self.assertEqual(list(result), ['p.Source.helper(java.lang.String)'])
        self.assertEqual(result['p.Source.helper(java.lang.String)'][0]['kind'], 'DIFF_INFERRED_CALL')
        self.assertEqual(result['p.Source.helper(java.lang.String)'][0]['after_line'], 5)
