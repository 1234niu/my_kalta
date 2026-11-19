"""Extract added Java method call sites from the supplied seed hunks."""
from collections import Counter
import re

HUNK = re.compile(r'^@@ -([0-9]+)(?:,\d+)? \+([0-9]+)(?:,\d+)? @@')


def hunks(diff):
    before, after = [], []
    active = False
    for line in diff.splitlines():
        match = HUNK.match(line)
        if match:
            if active:
                yield before, after
            before, after = [], []
            old, new = map(int, match.groups())
            active = True
        elif active and line.startswith((' ', '+', '-')):
            marker, content = line[0], line[1:]
            if marker != '+':
                before.append((content, old, marker == '-'))
                old += 1
            if marker != '-':
                after.append((content, new, marker == '+'))
                new += 1
    if active:
        yield before, after


def calls(parser, lines):
    if not lines:
        return
    source = ('class Snippet { void snippet() {\n'
              + '\n'.join(line[0] for line in lines) + '\n} }').encode()
    stack = [parser.parse(source).root_node]
    while stack:
        node = stack.pop()
        stack.extend(reversed(node.named_children))
        if node.type != 'method_invocation':
            continue
        name = node.child_by_field_name('name')
        args = node.child_by_field_name('arguments')
        receiver = node.child_by_field_name('object')
        if name is None or args is None or args.has_error:
            continue
        start = name.start_point.row - 1
        end = min(args.end_point.row, len(lines))
        if start < 0 or not any(row[2] for row in lines[start:end]):
            continue
        yield dict(name=name.text.decode(), arity=sum(
            child.type not in {'block_comment', 'line_comment'} for child in args.named_children),
            arguments=[child.text.decode() for child in args.named_children
                       if child.type not in {'block_comment', 'line_comment'}],
            receiver=receiver.text.decode() if receiver else None,
            after_line=lines[start][1], expression=name.text.decode() + args.text.decode())


def candidate_links(call, seed, entities):
    """Find possible existing signatures. Arity and receiver are not type resolution."""
    receiver = call['receiver']
    seed_owner = seed.split('(', 1)[0].rsplit('.', 1)[0]
    if receiver in (None, 'this'):
        owners = {seed_owner}
    elif re.fullmatch(r'[\w$.]+', receiver):
        owners = {receiver, seed_owner.rsplit('.', 1)[0] + '.' + receiver}
    else:
        return []
    prefix = {owner + '.' + call['name'] for owner in owners}
    matches = []
    for entity in entities:
        name, opening, tail = entity.partition('(')
        if not opening or name not in prefix:
            continue
        parameters = tail.removesuffix(')')
        arity = len(parameters.split(',')) if parameters else 0
        if arity == call['arity']:
            matches.append(entity)
    return sorted(matches)


def lineage(owner, parents):
    result = []
    while owner and owner not in result:
        result.append(owner)
        owner = parents.get(owner)
    return result


def inferred_signatures(call, seed, graph):
    """Propose signatures from observed argument types and plausible owners."""
    owner = seed.split('(', 1)[0].rsplit('.', 1)[0]
    bindings = graph['variables'].get(seed, {})
    returns = graph['returnTypes']
    parents = graph['parents']
    owner_chain = lineage(owner, parents)

    def variable_type(name):
        if name in bindings:
            return bindings[name]
        for candidate in owner_chain:
            field = graph['fieldTypes'].get(f'{candidate}.{name}')
            if field:
                return field
        return None

    def expression_type(expr):
        expr = expr.strip()
        declared = variable_type(expr)
        if declared:
            return declared
        indexed = re.fullmatch(r'(\w+)\s*\[.*\]', expr)
        if indexed:
            array = variable_type(indexed[1]) or ''
            return array[:-2] if array.endswith('[]') else None
        if re.fullmatch(r'[0-9]+', expr):
            return 'int'
        if expr.startswith('"') and expr.endswith('"'):
            return 'java.lang.String'
        getter = re.fullmatch(r'(?:(\w+)\.)?(\w+)\(\s*\)', expr)
        if getter:
            receiver, name = getter.groups()
            base = variable_type(receiver) if receiver and receiver != 'this' else owner
            for candidate in lineage(base, parents):
                signature = f'{candidate}.{name}()'
                if signature in returns:
                    return returns[signature]
        return None

    args = [expression_type(arg) for arg in call['arguments']]
    if not all(args):
        return []
    receiver = call['receiver']
    if receiver and receiver != 'this':
        receiver_type = expression_type(receiver)
        owners = [receiver_type] if receiver_type in graph['entities'] else []
    elif not args:
        owners = [candidate for candidate in owner_chain if candidate in graph['entities']]
    else:
        owners = []
        for edge in graph['edges']:
            if edge['from'] != seed or edge['kind'] != 'CALLS':
                continue
            target = edge['to'].split('(', 1)[0]
            target_owner, old_name = target.rsplit('.', 1)
            if target_owner in owner_chain and call['name'].startswith(old_name) and call['name'] != old_name:
                owners.append(target_owner)
        if not owners and receiver is None:
            # A new static import can refer to a repository utility already
            # used by the seed class or an enclosing class.
            enclosing = {owner}
            candidate = owner.rsplit('.', 1)[0]
            while candidate in graph['entities']:
                enclosing.add(candidate)
                candidate = candidate.rsplit('.', 1)[0]
            static_methods = set(graph['staticMethods'])
            for edge in graph['edges']:
                if edge['kind'] != 'CALLS' or edge['to'] not in static_methods:
                    continue
                caller = edge['from'].split('(', 1)[0].rsplit('.', 1)[0]
                if caller in enclosing:
                    owners.append(edge['to'].split('(', 1)[0].rsplit('.', 1)[0])
    return sorted({f"{candidate}.{call['name']}({','.join(args)})" for candidate in owners})


def field_writes(parser, lines, seed, graph, *, include_existing=False):
    if not lines:
        return []
    owner = seed.split('(', 1)[0].rsplit('.', 1)[0]
    source = ('class Snippet { void snippet() {\n'
              + '\n'.join(line[0] for line in lines) + '\n} }').encode()
    stack = [parser.parse(source).root_node]
    locals_seen = set(graph['variables'].get(seed, {}))
    writes = []
    while stack:
        node = stack.pop()
        stack.extend(node.named_children)
        if node.type == 'variable_declarator':
            name = node.child_by_field_name('name')
            if name:
                locals_seen.add(name.text.decode())
        if node.type == 'assignment_expression':
            lhs = node.child_by_field_name('left')
            if lhs is not None:
                writes.append(lhs)
    entities = set(graph['entities'])
    results = []
    for lhs in writes:
        idx = lhs.start_point.row - 1
        if not 0 <= idx < len(lines) or not lines[idx][2]:
            continue
        text = lhs.text.decode()
        if not re.fullmatch(r'(?:this\.)?[A-Za-z_$][\w$]*', text):
            continue
        name = text.removeprefix('this.')
        if text == name and name in locals_seen:
            continue
        known = next((f'{ancestor}.{name}' for ancestor in lineage(owner, graph['parents'])
                      if f'{ancestor}.{name}' in entities), None)
        if known and not include_existing:
            continue
        results.append(dict(seed=seed, edge='ADDED_WRITE', after_line=lines[idx][1],
                            proposed_fqn=known or f'{owner}.{name}'))
    return results


def overlay(graph, seeds, *, infer=False):
    from tree_sitter import Language, Parser
    import tree_sitter_java

    parser = Parser(Language(tree_sitter_java.language()))
    result = []
    for seed in seeds:
        removed, added = [], []
        for before, after in hunks(seed['git_diff_hunk']):
            removed.extend(calls(parser, before))
            added.extend(calls(parser, after))
        # Compare call shapes across the seed's hunks, including separate move hunks.
        def key(call):
            receiver = call['receiver']
            # Chained receiver expressions often change when an earlier call is added.
            if receiver and '(' in receiver:
                receiver = '<chain>'
            return (receiver, call['name'], call['arity'])

        counts = Counter(map(key, removed))
        for call in added:
            shape = key(call)
            if counts[shape]:
                counts[shape] -= 1
                continue
            possible = candidate_links(call, seed['fqn'], graph['entities'])
            inferred = inferred_signatures(call, seed['fqn'], graph) if infer and not possible else []
            status = 'possible_parent_targets' if possible else 'inferred_targets' if inferred else 'unresolved'
            result.append(dict(call, edge='ADDED_CALL', seed=seed['fqn'], file=seed['file'],
                               status=status, possible_parent_targets=possible, inferred_targets=inferred))
    return result


def inferred_fields(graph, seeds):
    from tree_sitter import Language, Parser
    import tree_sitter_java

    parser = Parser(Language(tree_sitter_java.language()))
    results = []
    for seed in seeds:
        for _, after in hunks(seed['git_diff_hunk']):
            results.extend(dict(write, file=seed['file'])
                           for write in field_writes(parser, after, seed['fqn'], graph))
    return results


def condition_field_reads(parser, lines, seed, graph):
    """Find field reads in added Java conditions without treating method names as fields."""
    if not lines:
        return []
    owner = seed.split('(', 1)[0].rsplit('.', 1)[0]
    source = ('class Snippet { void snippet() {\n'
              + '\n'.join(line[0] for line in lines) + '\n} }').encode()
    locals_seen = set(graph['variables'].get(seed, {}))
    tree = parser.parse(source)
    stack = [tree.root_node]
    conditions = []
    while stack:
        node = stack.pop()
        stack.extend(reversed(node.named_children))
        if node.type in ('variable_declarator', 'formal_parameter', 'catch_formal_parameter'):
            name = node.child_by_field_name('name')
            if name:
                locals_seen.add(name.text.decode())
        if node.type in ('if_statement', 'while_statement', 'do_statement', 'for_statement',
                         'ternary_expression'):
            condition = node.child_by_field_name('condition')
            if condition:
                conditions.append(condition)
    results = []
    for condition in conditions:
        stack = [condition]
        while stack:
            node = stack.pop()
            if node.type in ('parenthesized_expression', 'binary_expression', 'unary_expression'):
                stack.extend(reversed(node.named_children))
                continue
            raw = node.text.decode()
            if node.type not in ('identifier', 'field_access') or not re.fullmatch(r'(?:this\.)?[A-Za-z_$][\w$]*', raw):
                continue
            name = raw.removeprefix('this.')
            if raw == name and name in locals_seen:
                continue
            idx = node.start_point.row - 1
            if not 0 <= idx < len(lines) or not lines[idx][2]:
                continue
            known = next((f'{ancestor}.{name}' for ancestor in lineage(owner, graph['parents'])
                          if f'{ancestor}.{name}' in graph['fieldTypes']), None)
            results.append(dict(seed=seed, edge='ADDED_READ', after_line=lines[idx][1],
                                proposed_fqn=known or f'{owner}.{name}'))
    return results


def seed_field_accesses(graph, seeds):
    from tree_sitter import Language, Parser
    import tree_sitter_java

    parser = Parser(Language(tree_sitter_java.language()))
    accesses = []
    for seed in seeds:
        if seed['type'] != 'executable':
            continue
        for _, after in hunks(seed['git_diff_hunk']):
            writes = field_writes(parser, after, seed['fqn'], graph, include_existing=True)
            reads = condition_field_reads(parser, after, seed['fqn'], graph)
            accesses.extend(dict(access, file=seed['file']) for access in writes + reads)
    return accesses
