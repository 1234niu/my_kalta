from collections import defaultdict
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from ma_evidence import Run
from ma_guided import BUDGET, TURNS, Guided, phase


class Fixture:
    def __init__(self, path):
        self.root = path
        self.locations = {'p.C.seed()': dict(file='p/C.java', start=2, end=2)}
        self.neighbors = defaultdict(list)

    def file(self, name):
        return self.root / name


class GuidedTests(unittest.TestCase):
    def test_edges_preserve_seed_path_and_stop_at_three(self):
        repo = Fixture(Path('.'))
        for i in range(4):
            before = 'p.C.seed()' if i == 0 else f'p.C.m{i}()'
            after = f'p.C.m{i+1}()'
            repo.neighbors[before].append({'kind': 'CALLS', 'from': before, 'to': after})
        guided = Guided(repo, [{'fqn': 'p.C.seed()', 'file': 'p/C.java'}])
        guided.starts()
        node = 'N1'
        for depth in range(1, 4):
            result = guided.query('analyze', dict(tool='expand_edges', node=node, direction='out', kind='CALLS'))
            peer = result['edges'][0]['node']
            self.assertEqual(peer['depth'], depth)
            self.assertEqual(len(peer['path']), depth)
            self.assertEqual(peer['seed'], 'p.C.seed()')
            node = peer['id']
        with self.assertRaisesRegex(ValueError, 'depth limit'):
            guided.query('analyze', dict(tool='expand_edges', node=node, direction='out', kind='CALLS'))
        with self.assertRaisesRegex(ValueError, 'unavailable'):
            guided.query('score', dict(tool='expand_edges', node=node))

    def test_search_pagination_and_registered_scope(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'p').mkdir()
            (root / 'p/C.java').write_text('class C {\n' + 'needle\n' * 11 + '}\n')
            repo = Fixture(root)
            guided = Guided(repo, [{'fqn': 'p.C.seed()', 'file': 'p/C.java'}])
            guided.starts()
            guided.hypotheses['H1'] = {'seed': 'p.C.seed()'}
            query = dict(tool='search_code', hypothesis='H1', scope='p', query='needle')
            page = guided.query('analyze', query)
            self.assertEqual(page['next_offset'], 10)
            self.assertEqual(page['matches'][0]['node']['path'][0]['kind'], 'SOURCE_PATTERN')
            self.assertEqual(guided.query('analyze', dict(query, offset=10))['matches'][0]['line'], 12)
            with self.assertRaisesRegex(ValueError, 'registered'):
                guided.query('analyze', dict(query, scope='..'))

    def test_failed_queries_still_consume_budget(self):
        with tempfile.TemporaryDirectory() as temp:
            run = Run(None, 'mock', '', '', Path(temp))
            run.complete = Mock(return_value=json.dumps({'queries': [{'tool': 'invalid'}] * 3}))
            guided = Mock()
            guided.query.side_effect = ValueError('invalid')
            result = phase(run, guided, 'analyze', 'Analyze', {}, 'candidates')
            self.assertEqual(result, {'candidates': []})
            self.assertEqual(guided.query.call_count, BUDGET['analyze'])
            self.assertEqual(run.complete.call_count, TURNS['analyze'])
            self.assertEqual(run.usage['analyze']['errors'], BUDGET['analyze'])
