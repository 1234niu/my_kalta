"""Compare static candidate retrieval on parent snapshots."""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess
import tempfile

import katia


def owner(entity):
    return entity.split('(', 1)[0].rsplit('.', 1)[0]


def expand(graph, seeds, multihop):
    outgoing = defaultdict(list)
    incoming = defaultdict(list)
    for edge in graph['edges']:
        outgoing[edge['from']].append(edge)
        incoming[edge['to']].append(edge)

    paths = {}
    for seed in seeds:
        root = seed['fqn']
        lineage = {owner(root)}
        current = owner(root)
        while (parent := graph['parents'].get(current)) and parent not in lineage:
            lineage.add(parent)
            current = parent

        def remember(entity, path):
            # Keep one shortest path per first field so different dependencies
            # (such as timestamp configuration and regex state) stay inspectable.
            first_field = next(edge['to'] for edge in path if edge['kind'] != 'CALLS')
            alternatives = paths.setdefault(entity, {})
            if first_field not in alternatives or len(path) < len(alternatives[first_field]):
                alternatives[first_field] = path

        def fields(method, path):
            for access in outgoing[method]:
                if access['kind'] not in {'READ', 'WRITE'}:
                    continue
                field = access['to']
                remember(field, path + [access])
                for writer in incoming[field]:
                    if writer['kind'] != 'WRITE' or owner(writer['from']) not in lineage:
                        continue
                    evidence = path + [access, writer]
                    remember(writer['from'], evidence)
                    if multihop:
                        trace_writers(writer['from'], evidence, {writer['from']}, 3)

        def trace_writers(method, path, visited, remaining):
            for access in outgoing[method]:
                if access['kind'] == 'READ' and owner(access['to']) in lineage:
                    remember(access['to'], path + [access])
            if not remaining:
                return
            for call in incoming[method]:
                caller = call['from']
                if call['kind'] != 'CALLS' or owner(caller) not in lineage or caller in visited:
                    continue
                remember(caller, path + [call])
                trace_writers(caller, path + [call], visited | {caller}, remaining - 1)

        fields(root, [])
        if multihop:
            for call in outgoing[root]:
                if call['kind'] == 'CALLS' and owner(call['to']) in lineage:
                    fields(call['to'], [call])
    return {entity: path for entity, path in paths.items() if entity not in {s['fqn'] for s in seeds}}


def two_hop_calls(graph, seeds):
    """Walk outgoing CALLS only, retaining a source path for each destination."""
    calls = defaultdict(list)
    entities = set(graph['entities'])
    for edge in graph['edges']:
        if edge['kind'] == 'CALLS' and edge['to'] in entities:
            calls[edge['from']].append(edge)
    roots = {seed['fqn'] for seed in seeds if seed['type'] == 'executable'}
    paths = {}
    for root in sorted(roots):
        for first in calls[root]:
            for second in calls[first['to']]:
                paths.setdefault(second['to'], [first, second])
    return {entity: path for entity, path in paths.items()
            if entity not in {seed['fqn'] for seed in seeds}}


def field_paths(graph, seeds, overlays=(), *, mixed=False):
    """Trace fixed CALLS→READ and WRITE→READ←CALLS patterns."""
    outgoing, incoming = defaultdict(list), defaultdict(list)
    for edge in graph['edges']:
        outgoing[edge['from']].append(edge)
        incoming[edge['to']].append(edge)
    roots = {seed['fqn'] for seed in seeds if seed['type'] == 'executable'}
    paths = {}

    def follow_readers(write):
        field = write['to']
        for reader in incoming[field]:
            if reader['kind'] != 'READ' or reader['from'] == write['from']:
                continue
            paths.setdefault(reader['from'], [write, reader])
            for caller in incoming[reader['from']]:
                if caller['kind'] == 'CALLS' and caller['from'] != write['from']:
                    paths.setdefault(caller['from'], [write, reader, caller])

    if mixed:
        for root in sorted(roots):
            for edge in outgoing[root]:
                if edge['kind'] == 'CALLS':
                    for read in outgoing[edge['to']]:
                        if read['kind'] == 'READ':
                            paths.setdefault(read['to'], [edge, read])
                if edge['kind'] == 'WRITE':
                    follow_readers(edge)
    for access in overlays:
        edge = dict(access, **{'from': access['seed'], 'to': access['proposed_fqn']})
        paths.setdefault(edge['to'], [edge])
        if edge['edge'] == 'ADDED_WRITE':
            follow_readers(edge)
    return {name: evidence for name, evidence in paths.items()
            if name not in {seed['fqn'] for seed in seeds}}


def retrieve(row, cross_class_calls=False, seed_diff=False, field_ablation=False):
    task = katia.load_task(row)
    baseline = katia.static(task)['candidates']
    with tempfile.TemporaryDirectory() as tmp:
        output = Path(tmp) / 'relations.json'
        subprocess.run([katia.java_path(), '--class-path', str(katia.JAR),
                        str(katia.ROOT / 'src/StaticRelations.java'), str(katia.source(task)), str(output)],
                       check=True, timeout=300)
        graph = json.loads(output.read_text())
    seeds = task['seed_changes']
    direct = expand(graph, seeds, False)
    deeper = expand(graph, seeds, True)
    result = dict(id=task['id'], entities=graph['entities'], graph_edges=len(graph['edges']),
                seeds={s['fqn']: s['fqn'] in graph['entities'] for s in seeds},
                candidates={'baseline': baseline, 'fields': sorted(set(baseline) | direct.keys()),
                            'multihop': sorted(set(baseline) | deeper.keys())},
                evidence={'fields': direct, 'multihop': deeper})
    if cross_class_calls:
        paths = two_hop_calls(graph, seeds)
        existing = result['candidates']['multihop']
        expanded = sorted(set(existing) | paths.keys())
        result['candidates']['two_hop_calls'] = expanded
        result['evidence']['two_hop_calls'] = paths
        result['prompt_chars'] = {}
        for arm, candidates in [('multihop', existing), ('two_hop_calls', expanded)]:
            result['prompt_chars'][arm] = {
                name: sum(len(m['content']) for m in katia.messages(variant, task, candidates, stage))
                for name, variant, stage in [('sp', 'sp', 0), ('ma_analysis', 'ma', 0),
                                             ('ma_refinement_fixed', 'ma', 1)]
            }
    if seed_diff:
        from diff_overlay import inferred_fields, lineage, overlay
        calls = overlay(graph, seeds, infer=True)
        fields = inferred_fields(graph, seeds)
        overrides = []
        methods = set(graph['instanceMethods'])
        for seed in seeds:
            name = seed['fqn']
            if name not in methods:
                continue
            member = name[len(owner(name)) + 1:]
            for ancestor in lineage(owner(name), graph['parents'])[1:]:
                target = f'{ancestor}.{member}'
                if target in methods:
                    overrides.append(dict(seed=name, target=target, edge='POSSIBLE_OVERRIDE'))
        additional = {fqn for call in calls
                      for fqn in call['possible_parent_targets'] + call['inferred_targets']}
        additional.update(field['proposed_fqn'] for field in fields)
        additional.update(edge['target'] for edge in overrides)
        previous = result['candidates'].get('two_hop_calls', result['candidates']['multihop'])
        result['candidates']['diff_and_override'] = sorted(
            (set(previous) | additional) - {seed['fqn'] for seed in seeds})
        result['seed_diff_overlay'] = {'added_calls': calls, 'proposed_field_writes': fields,
                                       'possible_overrides': overrides}
    if field_ablation:
        from diff_overlay import seed_field_accesses
        accesses = seed_field_accesses(graph, seeds)
        mixed = field_paths(graph, seeds, mixed=True)
        diff = field_paths(graph, seeds, accesses)
        baseline = set(result['candidates']['diff_and_override'])
        for name, additions in [('mixed_field_paths', mixed), ('seed_field_accesses', diff),
                                ('combined_field_paths', mixed | diff)]:
            result['evidence'][name] = additions
            result['candidates'][name] = sorted(baseline | additions.keys())
        result['seed_field_accesses'] = accesses
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rows', default='0,1,2', help='Comma-separated CSV row positions')
    parser.add_argument('--cross-class-calls', action='store_true', help='Compare outgoing two-hop calls')
    parser.add_argument('--seed-diff-overlay', action='store_true', help='Record call sites added by the seed diff')
    parser.add_argument('--field-ablation', action='store_true',
                        help='Compare graph field paths and new diff accesses against the latest static arm')
    args = parser.parse_args()
    rows = list(dict.fromkeys(int(value) for value in args.rows.split(',')))
    if any(row < 0 for row in rows):
        parser.error('Row positions must be nonnegative')
    results = [retrieve(row, args.cross_class_calls or args.field_ablation,
                        args.seed_diff_overlay or args.field_ablation, args.field_ablation) for row in rows]
    gold_path = katia.ROOT / 'dataset/processed/evaluation-only.jsonl'
    labels = {r['id']: r for r in map(json.loads, gold_path.read_text().splitlines())}
    folder = 'static-two-hop' if args.cross_class_calls else 'static-compare'
    if args.seed_diff_overlay:
        folder = 'static-seed-diff'
    if args.field_ablation:
        folder = 'static-field-ablation'
    output = katia.ROOT / 'results' / folder
    for result in results:
        target = {e['fqn'] for e in labels[result['id']]['impacted']}
        indexed = target & set(result.pop('entities'))
        result['indexed_targets'] = sorted(indexed)
        result['unindexed_targets'] = sorted(target - indexed)
        result['metrics'] = {}
        for name, values in result['candidates'].items():
            hits = set(values) & target
            result['metrics'][name] = dict(candidate_count=len(values), hits=sorted(hits),
                misses=sorted(target - hits), indexed_misses=sorted(indexed - hits),
                indexed_recall=len(hits & indexed) / len(indexed) if indexed else None)
        katia.dump(output / (result['id'] + '.json'), result)
        print(result['id'], len(indexed), [(name, m['candidate_count'], len(m['hits']))
                                          for name, m in result['metrics'].items()], flush=True)


if __name__ == '__main__':
    main()
