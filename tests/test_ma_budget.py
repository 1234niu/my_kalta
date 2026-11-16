import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ma_evidence import PHASE_QUERY_LIMITS, Run


class BudgetTests(unittest.TestCase):
    def test_tools_stop_even_if_model_never_finalizes(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Mock()
            repo.query.side_effect = ValueError('invalid query')
            runner = Run(repo, 'mock', '', '', Path(directory))
            runner.complete = Mock(return_value=json.dumps({'queries': [{'tool': 'invalid'}] * 3}))
            limit = PHASE_QUERY_LIMITS['analyze']

            with self.assertRaisesRegex(ValueError, 'did not return'):
                runner.phase('analyze', 'Find candidates', {}, 'candidates')

            self.assertEqual(repo.query.call_count, limit)
            self.assertEqual(runner.complete.call_count, limit + 3)
            self.assertEqual(runner.usage['analyze'], dict(model_turns=limit + 3, tool_rounds=3, queries=limit))

    def test_planner_has_no_tool_budget(self):
        repo = Mock()
        runner = Run(repo, 'mock', '', '', Path('.'))
        runner.complete = Mock(side_effect=['{"queries":[{"tool":"invalid"}]}', '{"checks":[]}'])

        self.assertEqual(runner.phase('planner', 'Plan', {}, 'checks'), {'checks': []})
        repo.query.assert_not_called()

    def test_review_budget_exhaustion_preserves_candidates_as_pending(self):
        repo = Mock()
        runner = Run(repo, 'mock', '', '', Path('.'))
        runner.complete = Mock(return_value='{"decisions":[]}')

        review = runner.phase('review', 'Review', {}, 'decisions')
        self.assertTrue(runner.usage['review']['exhausted'])
        self.assertEqual(runner.complete.call_count, PHASE_QUERY_LIMITS['review'] + 3)
        decisions = runner.decide(['p.C.m()'], set(), [], review)
        self.assertEqual(decisions['p.C.m()']['status'], 'pending')
