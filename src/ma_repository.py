"""Read-only retrieval against one verified parent snapshot."""
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import katia


class Repository:
    def __init__(self, task):
        self.task = task
        self.root = katia.source(task).resolve()
        exporter = katia.ROOT / 'src/StaticRelations.java'
        identity = [
            task['repo'], task['parent_commit'], katia.digest(self.root / '.katia-source.json'),
            katia.digest(katia.JAR), katia.digest(exporter),
        ]
        key = hashlib.sha256(json.dumps(identity).encode()).hexdigest()
        self.fingerprint = key
        cache = katia.ROOT / 'dataset/indexes' / (key + '.json')
        if not cache.exists():
            cache.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.TemporaryDirectory(dir=cache.parent) as temp:
                output = Path(temp) / 'graph.json'
                subprocess.run([katia.java_path(), '--class-path', str(katia.JAR), str(exporter),
                                str(self.root), str(output)], check=True, timeout=300)
                output.replace(cache)
        graph = json.loads(cache.read_text())
        self.source_graph = graph
        self._fine = None
        self.locations = graph['locations']
        self.entities = sorted(graph['entities'])
        self.neighbors = defaultdict(list)
        for edge in graph['edges']:
            self.neighbors[edge['from']].append(edge)
            if edge['to'] != edge['from']:
                self.neighbors[edge['to']].append(edge)
        methods = set(graph['instanceMethods'])
        for child, parent in graph['parents'].items():
            edge = dict(kind='EXTENDS', **{'from': child, 'to': parent})
            self.neighbors[child].append(edge)
            self.neighbors[parent].append(edge)
        for name in sorted(methods):
            member_path, signature = name.split('(', 1)
            owner, member = member_path.rsplit('.', 1)
            target = graph['parents'].get(owner)
            visited = {owner}
            while target and target not in visited:
                visited.add(target)
                related = f'{target}.{member}({signature}'
                if related in methods:
                    edge = dict(kind='POSSIBLE_OVERRIDE', **{'from': name, 'to': related})
                    self.neighbors[name].append(edge)
                    self.neighbors[related].append(edge)
                target = graph['parents'].get(target)

    def file(self, name):
        if not isinstance(name, str) or Path(name).is_absolute():
            raise ValueError('Expected a repository-relative Java file')
        path = (self.root / name).resolve()
        if not path.is_relative_to(self.root) or path.suffix != '.java' or not path.is_file():
            raise ValueError('Java source file unavailable in the parent snapshot')
        return path

    def fine_neighbors(self, query):
        """Expose evidence paths without changing the existing method-level query contract."""
        if self._fine is None:
            from fine_relations import build_fine
            self._fine, _ = build_fine(self.task, self.source_graph, self.root)
        node_id, fqn = query.get('node'), query.get('fqn')
        direction, offset = query.get('direction','out'), query.get('offset',0)
        if direction not in ('in','out') or type(offset) is not int or offset<0:
            raise ValueError('Expected direction in/out and nonnegative offset')
        nodes = {node['id']:node for node in self._fine['nodes']}
        if node_id is not None:
            if not isinstance(node_id,str) or node_id not in nodes:
                raise ValueError('Unknown fine graph node')
            selected = {node_id}
        elif isinstance(fqn,str) and fqn in self.source_graph['entities']:
            selected = {name for name,node in nodes.items() if node.get('fqn')==fqn or node.get('method')==fqn}
        else:
            raise ValueError('Expected a node ID or indexed FQN')
        side = 'source' if direction=='out' else 'target'
        edges = [edge for edge in self._fine['edges'] if edge[side] in selected
                 and (query.get('kind') is None or edge['kind']==query['kind'])]
        page = edges[offset:offset+20]
        involved = {edge[key] for edge in page for key in ('source','target')}
        return dict(edges=page,nodes=[nodes[key] for key in sorted(involved)],total=len(edges),
                    next_offset=offset+20 if offset+20<len(edges) else None,
                    fingerprint=self._fine['fingerprint'],truncated=self._fine['truncated'])

    def query(self, request):
        action = request.get('tool')
        if action == 'fine_neighbors':
            return self.fine_neighbors(request)
        if action == 'find_symbol':
            term = request['query']
            if not isinstance(term, str) or not term.strip() or len(term) > 300:
                raise ValueError('Expected a nonempty symbol name')
            matches = [name for name in self.entities if term.casefold() in name.casefold()]
            matches.sort(key=lambda name: (name != term, not name.split('(', 1)[0].endswith('.' + term),
                                           len(name), name))
            return {'matches': [{'fqn': name, 'location': self.locations.get(name)}
                                for name in matches[:15]], 'total': len(matches)}
        if action == 'neighbors':
            entity = request['fqn']
            if entity not in self.entities:
                return {'indexed': False, 'edges': []}
            edges = self.neighbors[entity]
            kind = request.get('kind')
            direction = request.get('direction', 'both')
            if direction not in {'in', 'out', 'both'}:
                raise ValueError('Unknown edge direction')
            matches = [e for e in edges if (kind is None or e['kind'] == kind)
                       and (direction == 'both' or e['from' if direction == 'out' else 'to'] == entity)]
            offset = request.get('offset', 0)
            if type(offset) is not int or offset < 0:
                raise ValueError('Expected a nonnegative offset')
            return {'indexed': True, 'edges': matches[offset:offset+20], 'total': len(matches)}
        if action == 'read_source':
            entity = request.get('fqn')
            location = self.locations[entity] if entity else {}
            file = request.get('file', location.get('file'))
            start = request.get('start', location.get('start', 1))
            end = request.get('end', min(start + 79, location.get('end', start + 79)))
            if type(start) is not int or type(end) is not int or not 1 <= start <= end <= start + 79:
                raise ValueError('Expected a positive span of at most 80 lines')
            path = self.file(file)
            lines = path.read_text(errors='replace').splitlines()[start-1:end]
            excerpt = [{'line': start + i, 'text': line[:400]} for i, line in enumerate(lines)]
            return {'file': path.relative_to(self.root).as_posix(), 'declaration': location,
                    'lines': excerpt, 'truncated_lines': any(len(line) > 400 for line in lines)}
        if action == 'search_source':
            term = request['query']
            if not isinstance(term, str) or not 1 <= len(term.strip()) <= 160:
                raise ValueError('Expected a literal query of 1–160 characters')
            prefix = request.get('path_prefix', '')
            if not isinstance(prefix, str) or Path(prefix).is_absolute() or '..' in Path(prefix).parts:
                raise ValueError('Expected a repository-relative prefix')
            matches = []
            for file in sorted(self.root.rglob('*.java')):
                relative = file.relative_to(self.root).as_posix()
                if not relative.startswith(prefix) or not file.resolve().is_relative_to(self.root):
                    continue
                with file.open(errors='replace') as reader:
                    for num, line in enumerate(reader, 1):
                        index = line.casefold().find(term.casefold())
                        if index >= 0:
                            matches.append({'file': relative, 'line': num,
                                            'text': line[max(0, index-80):index+240].strip()})
                            if len(matches) == 16:
                                return {'matches': matches[:15], 'more': True}
            return {'matches': matches, 'more': False}
        raise ValueError('Unknown retrieval tool')
