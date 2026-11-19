"""Bounded source-level value, configuration and syntactic guard relations for CIA.

Local definitions are ordered and branch results are conservatively merged. Call
arguments are bound to per-call frames, with bounded inlining and opaque summaries
for unavailable bodies. Field storage and dynamic container keys are may-alias
approximations. GUARDS records syntactic nesting, not full CFG control dependence.
Configuration engine conventions are explicit API models, not proven semantics.
"""
from collections import defaultdict, deque
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import re

from tree_sitter import Language, Parser
import tree_sitter_java

from static_compare import owner

PARSER_LANGUAGE = Language(tree_sitter_java.language())
MAX_CALL_DEPTH = 3
MAX_PATH = 40
MAX_NODES = 100000
PLACEHOLDER = re.compile(r'\$\{([^{}]+)\}')


@dataclass
class Value:
    node: str
    type: str = ''
    object_id: str = ''
    literal: str = None


class FineGraphLimit(RuntimeError):
    pass


class FineGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []
        self.edge_keys = set()

    def node(self, node_id, **data):
        if node_id not in self.nodes and len(self.nodes)>=MAX_NODES:
            raise FineGraphLimit('Fine graph node budget exhausted')
        self.nodes.setdefault(node_id, dict(id=node_id, **data))
        return node_id

    def edge(self, source, target, kind, *, certainty='syntactic', **data):
        if not source or not target:
            return
        edge = dict(source=source, target=target, kind=kind, certainty=certainty, **data)
        key = json.dumps(edge, sort_keys=True)
        if key not in self.edge_keys:
            self.edge_keys.add(key)
            self.edges.append(edge)


def literal(node, data):
    if node is None:
        return None
    text = data[node.start_byte:node.end_byte].decode()
    if node.type == 'string_literal':
        try:
            return json.loads(text)
        except ValueError:
            return None
    return None


def overlay_method(lines, start, end, diff):
    """Apply only supplied seed hunks, never fetching the target commit."""
    edits = []
    current = None
    for line in diff.splitlines():
        match = re.match(r'^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
        if match:
            if current:
                edits.append(current)
            old, count, new, _ = match.groups()
            current = dict(old=int(old), count=int(count) if count is not None else 1,
                           new=int(new), before=[], after=[])
        elif current is not None and line.startswith((' ', '+', '-')):
            mark, text = line[0], line[1:]
            if mark != '+':
                current['before'].append(text)
            if mark != '-':
                current['after'].append(text)
    if current:
        edits.append(current)
    fragment = list(lines[start-1:end])
    touched = []
    for edit in sorted(edits, key=lambda e:e['old'], reverse=True):
        index = edit['old'] - start + (1 if edit['count'] == 0 else 0)
        if not 0 <= index <= len(fragment) or index + len(edit['before']) > len(fragment):
            raise ValueError('Seed hunk extends beyond its indexed declaration')
        old = fragment[index:index+len(edit['before'])]
        if [s.strip() for s in old] != [s.strip() for s in edit['before']]:
            raise ValueError('Seed hunk does not match the parent declaration')
        fragment[index:index+len(edit['before'])] = edit['after']
        touched.append((edit['new'], edit['new']+max(0,len(edit['after'])-1)))
    first = min(edits, key=lambda e:e['old']) if edits else None
    shift = first['new'] - first['old'] - (1 if first['count'] == 0 else 0) if first else 0
    return '\n'.join(fragment), touched, shift


class Builder:
    def __init__(self, root, graph, seeds):
        self.root = Path(root)
        self.graph = graph
        self.seeds = seeds
        self.parser = Parser(PARSER_LANGUAGE)
        self.fine = FineGraph()
        self.files = {}
        self.methods = {}
        self.method_index = defaultdict(list)
        self.field_constants = {}
        self.models = {}
        from diff_overlay import seed_field_accesses
        self.inferred_fields = {a['proposed_fqn'] for a in seed_field_accesses(graph,seeds)
                                if a['proposed_fqn'] not in graph['fieldTypes']}
        self.field_types = dict(graph['fieldTypes'])
        self.field_types.update({name:'' for name in self.inferred_fields})
        self.unresolved = []
        self.slots = {}
        self.substitutions = []
        self.seed_starts = []
        self.active_calls = set()
        self.truncated = False
        self._index()

    def _index(self):
        for file in sorted({loc['file'] for loc in self.graph['locations'].values()}):
            data = (self.root/file).read_bytes()
            tree = self.parser.parse(data)
            self.files[file] = (data, tree)
            stack = [tree.root_node]
            declarations = []
            while stack:
                node = stack.pop()
                if node.type in ('method_declaration','constructor_declaration'):
                    declarations.append(node)
                if node.type == 'field_declaration':
                    for child in node.named_children:
                        if child.type == 'variable_declarator':
                            value = child.child_by_field_name('value')
                            name = child.child_by_field_name('name')
                            if value and name:
                                text = literal(value, data)
                                if text is not None:
                                    self.field_constants[(file,name.text.decode(),node.start_point.row+1)] = text
                stack.extend(reversed(node.named_children))
            for fqn,loc in self.graph['locations'].items():
                if loc['file'] != file or '(' not in fqn:
                    continue
                matches = [n for n in declarations if n.end_point.row+1 == loc['end']
                           and n.start_point.row+1 <= loc['start'] <= n.end_point.row+1]
                if len(matches) != 1:
                    continue
                node = matches[0]
                parameters = node.child_by_field_name('parameters')
                names = [p.child_by_field_name('name').text.decode() for p in parameters.named_children
                         if p.child_by_field_name('name')]
                item = dict(fqn=fqn, owner=owner(fqn), file=file, data=data, node=node, names=names,
                            line_offset=0, version='parent', touched=[])
                self.methods[fqn] = item
                member = fqn.split('(',1)[0].rsplit('.',1)[1]
                self.method_index[(item['owner'],member,len(names))].append(fqn)
        owners = defaultdict(set)
        for cls,name,arity in self.method_index:
            owners[cls].add(name)
        for cls,names in owners.items():
            if {'setVariable','getVariable'} <= names:
                self.models[cls] = dict(write='setVariable', read='getVariable', substitute='substitute',
                                        basis='accessor_pair_convention', certainty='modelled')
            elif {'setProperty','getProperty'} <= names:
                self.models[cls] = dict(write='setProperty', read='getProperty', substitute=None,
                                        basis='accessor_pair_convention', certainty='modelled')
        self.models['java.util.Properties'] = dict(write='setProperty',read='getProperty',substitute=None,
                                                   basis='jdk_api', certainty='modelled')
        self.models['java.lang.System'] = dict(write='setProperty',read='getProperty',substitute=None,
                                               basis='jdk_system_properties', certainty='modelled')
        for seed in self.seeds:
            if seed['fqn'] not in self.methods or not seed.get('git_diff_hunk'):
                continue
            item = self.methods[seed['fqn']]
            loc = self.graph['locations'][seed['fqn']]
            try:
                text, touched, shift = overlay_method(item['data'].decode().splitlines(), loc['start'], loc['end'],
                                               seed['git_diff_hunk'])
                data = ('class SeedFragment {\n'+text+'\n}').encode()
                tree = self.parser.parse(data)
                nodes = [n for n in tree.root_node.named_children[0].child_by_field_name('body').named_children
                         if n.type in ('method_declaration','constructor_declaration')]
                if len(nodes) != 1 or nodes[0].has_error:
                    raise ValueError('Patched seed declaration could not be parsed')
                self.methods[seed['fqn']] = dict(item, data=data,node=nodes[0],
                                                line_offset=loc['start']+shift-2,version='seed_after',touched=touched)
            except (ValueError, AttributeError, IndexError) as exc:
                self.unresolved.append(dict(fqn=seed['fqn'],reason=str(exc),kind='seed_overlay'))

    def slot(self, namespace, key, kind):
        token = json.dumps([namespace,key,kind],ensure_ascii=False)
        node_id = f'{kind}:{token}'
        self.fine.node(node_id,kind=kind,namespace=namespace,key=key)
        self.slots[node_id] = (namespace,key,kind)
        return node_id

    def build(self):
        classes = {owner(s['fqn']) if s['type'] != 'type' else s['fqn'] for s in self.seeds}
        # Method-level graph selects related classes; fine data flow remains source-derived.
        frontier = {s['fqn'] for s in self.seeds}
        for _ in range(2):
            peers = {e['to'] for e in self.graph['edges'] if e['from'] in frontier and e['kind']=='CALLS'}
            classes.update(owner(p) for p in peers)
            frontier = peers
        for fqn,item in sorted(self.methods.items()):
            if item['owner'] not in classes:
                continue
            try:
                self.invoke(fqn, [], None, 'root:'+fqn, 0)
            except FineGraphLimit:
                self.truncated=True
            if self.truncated:
                break
        # Relate only explicitly known configuration containers and key identities.
        for namespace, template, destination in self.substitutions:
            keys = set(PLACEHOLDER.findall(template)) if template is not None else None
            for slot,(scope,key,kind) in list(self.slots.items()):
                if kind=='configuration' and scope==namespace and (keys is None or key in keys):
                    self.fine.edge(slot,destination,'SUBSTITUTES',certainty='may' if keys is None else 'modelled',
                                   template=template, dynamic_template=keys is None)
        for read_slot,(scope,key,kind) in list(self.slots.items()):
            if kind!='container_entry' or key=='*':
                continue
            wildcard = next((s for s,identity in self.slots.items()
                             if identity==(scope,'*','container_entry')), None)
            if wildcard is None:
                continue
            self.fine.edge(wildcard,read_slot,'DYNAMIC_KEY_MAY_MATCH',certainty='may')
        return dict(schema_version=1,nodes=list(self.fine.nodes.values()),edges=self.fine.edges,
                    config_models=self.models,unresolved=list({json.dumps(item,sort_keys=True):item for item in self.unresolved}.values()),
                    seed_starts=sorted(set(self.seed_starts)),
                    limits=dict(call_depth=MAX_CALL_DEPTH,nodes=MAX_NODES),truncated=self.truncated)

    def invoke(self, fqn, arguments, receiver, context, depth):
        item = self.methods[fqn]
        if (fqn,context) in self.active_calls or depth>MAX_CALL_DEPTH or len(self.fine.nodes)>=MAX_NODES:
            if len(self.fine.nodes)>=MAX_NODES:
                self.truncated=True
            return None
        self.active_calls.add((fqn,context))
        frame = Frame(self,item,arguments,receiver,context,depth)
        result = frame.run()
        self.active_calls.remove((fqn,context))
        return result


class Frame:
    def __init__(self, builder, item, arguments, receiver, context, depth):
        self.b = builder
        self.g = builder.fine
        self.item = item
        self.fqn = item['fqn']
        self.data = item['data']
        self.context = context
        self.depth = depth
        self.env = {}
        self.returned = []
        self.guards = []
        self.receiver = receiver or Value('',item['owner'],'instance:'+item['owner'])
        self.types = builder.graph['variables'].get(self.fqn,{})
        for i,name in enumerate(item['names']):
            key = f'parameter:{context}:{i}'
            self.g.node(key,kind='parameter',method=self.fqn,index=i,name=name,version=item['version'],
                        file=item['file'],line=item['node'].start_point.row+1+item['line_offset'])
            actual = arguments[i] if i<len(arguments) else None
            if actual:
                self.g.edge(actual.node,key,'ARGUMENT',certainty='modelled',context=context)
            self.env[name] = Value(key,self.types.get(name,''),actual.object_id if actual else key,
                                   actual.literal if actual else None)

    def text(self,node):
        return self.data[node.start_byte:node.end_byte].decode()

    def site(self,node,kind='expression'):
        key = f'{self.item["version"]}:{self.context}:{node.start_byte}:{node.end_byte}:{kind}'
        line = node.start_point.row+1+self.item['line_offset']
        self.g.node(key,kind=kind,method=self.fqn,file=self.item['file'],line=line,
                    end_line=node.end_point.row+1+self.item['line_offset'],
                    version=self.item['version'],code=self.text(node)[:500],context=self.context)
        for guard,branch in self.guards:
            self.g.edge(guard,key,'GUARDS',branch=branch,certainty='syntactic_guard')
        if self.item['version']=='seed_after' and self.depth==0 and any(
                start<=line<=end for start,end in self.item['touched']):
            self.b.seed_starts.append(key)
        return key

    def value(self,node,parts=(),kind='expression',edge='VALUE_FLOW',type_name='',object_id='',constant=None):
        key = self.site(node,kind)
        for part in parts:
            if part:
                self.g.edge(part.node,key,edge,certainty='may' if kind=='opaque_call' else 'syntactic')
        return Value(key,type_name,object_id or key,constant)

    def field(self,name,receiver_type=None):
        cls = receiver_type or self.item['owner']
        visited = set()
        while cls and cls not in visited:
            visited.add(cls)
            fqn=cls+'.'+name
            if fqn in self.b.field_types:
                return fqn
            cls=self.b.graph['parents'].get(cls)
        return None

    def read_field(self,node,fqn,receiver=None):
        loc=self.b.graph['locations'].get(fqn,{})
        self.g.node('field:'+fqn,kind='field',fqn=fqn,
                    provenance='seed_diff_inference' if fqn in self.b.inferred_fields else 'source_declaration',**loc)
        instance=receiver or self.receiver
        identity='field:'+fqn
        if instance.object_id and not instance.object_id.startswith('instance:'):
            identity=instance.object_id+'/'+identity
        value=self.value(node,kind='field_read',type_name=self.b.field_types.get(fqn,''),
                         object_id=identity)
        self.g.edge('field:'+fqn,value.node,'READ_VALUE')
        for (file,name,line),text in self.b.field_constants.items():
            if file==loc.get('file') and name==fqn.rsplit('.',1)[-1] and loc.get('start',line)<=line<=loc.get('end',line):
                value.literal=text
        return value

    def eval(self,node):
        if node is None:
            return None
        kind=node.type
        if kind=='identifier':
            name=self.text(node)
            if name in self.env:
                return self.value(node,[self.env[name]],kind='local_read',type_name=self.env[name].type,
                                  object_id=self.env[name].object_id,constant=self.env[name].literal)
            fqn=self.field(name)
            if fqn:
                return self.read_field(node,fqn)
            return self.value(node,kind='unresolved_name',type_name=name)
        if kind=='this':
            return self.receiver
        if kind=='string_literal':
            return self.value(node,kind='literal',type_name='java.lang.String',constant=literal(node,self.data))
        if kind=='field_access':
            target=node.child_by_field_name('object')
            name=self.text(node.child_by_field_name('field'))
            obj=self.eval(target)
            fqn=self.field(name,obj.type if obj else None)
            if fqn:
                return self.read_field(node,fqn,obj)
            # Class constants often use a short class name.
            candidates=[f for f in self.b.field_types if f.endswith('.'+name)
                        and owner(f).rsplit('.',1)[-1]==self.text(target)]
            if len(candidates)==1:
                return self.read_field(node,candidates[0],obj)
            return self.value(node,[obj],kind='unresolved_field')
        if kind=='update_expression':
            operand=node.named_children[0] if node.named_children else None
            value=self.eval(operand)
            return self.assign(operand,value,node) if operand is not None else value
        if kind=='method_invocation':
            return self.call(node)
        if kind=='object_creation_expression':
            args=node.child_by_field_name('arguments')
            values=[self.eval(n) for n in args.named_children] if args else []
            type_node=node.child_by_field_name('type')
            return self.value(node,values,kind='construction',type_name=self.text(type_node),
                              object_id=f'allocation:{self.context}:{node.start_byte}')
        if kind=='assignment_expression':
            left=node.child_by_field_name('left')
            right=self.eval(node.child_by_field_name('right'))
            return self.assign(left,right,node)
        if kind=='ternary_expression':
            condition=self.eval(node.child_by_field_name('condition'))
            key=self.site(node.child_by_field_name('condition'),'condition')
            self.g.edge(condition.node,key,'CONDITION_INPUT')
            values=[]
            for branch,label in [('consequence','true'),('alternative','false')]:
                self.guards.append((key,label))
                values.append(self.eval(node.child_by_field_name(branch)))
                self.guards.pop()
            return self.value(node,values,kind='merge')
        if kind in ('parenthesized_expression','cast_expression'):
            children=[n for n in node.named_children if n.type not in ('type_identifier','scoped_type_identifier',
                                                                     'integral_type','generic_type','array_type')]
            value=self.eval(children[-1]) if children else None
            type_node=node.child_by_field_name('type')
            return self.value(node,[value],type_name=self.text(type_node) if type_node else (value.type if value else ''),
                              object_id=value.object_id if value else '',constant=value.literal if value else None)
        values=[self.eval(n) for n in node.named_children
                if n.type not in ('line_comment','block_comment','type_arguments')]
        constant=None
        if kind=='binary_expression' and len(values)==2 and all(v and v.literal is not None for v in values):
            if '+' in self.text(node):
                constant=values[0].literal+values[1].literal
        return self.value(node,values,constant=constant)

    def assign(self,left,right,site):
        if right is None:
            return None
        name=self.text(left)
        fqn=None
        if left.type=='identifier' and name not in self.env:
            fqn=self.field(name)
        elif left.type=='field_access':
            target=self.eval(left.child_by_field_name('object'))
            fqn=self.field(self.text(left.child_by_field_name('field')),target.type if target else None)
        result=self.value(site,[right],kind='assignment',type_name=right.type,
                          object_id=right.object_id,constant=right.literal)
        if fqn:
            self.g.node('field:'+fqn,kind='field',fqn=fqn,**self.b.graph['locations'].get(fqn,{}))
            self.g.edge(result.node,'field:'+fqn,'WRITE_VALUE',certainty='may',state_model='field_flow_insensitive')
        elif left.type=='identifier':
            self.env[name]=result
        return result

    def resolve(self,node,name,receiver,args):
        candidates=[]
        # Prefer Spoon's resolved call at this source line and method.
        line=node.start_point.row+1+self.item['line_offset']
        if self.item['version']=='parent':
            candidates=[e['to'] for e in self.b.graph['edges'] if e['from']==self.fqn and e['kind']=='CALLS'
                        and e.get('line')==line and e['to'].split('(',1)[0].endswith('.'+name)
                        and e['to'] in self.b.methods and len(self.b.methods[e['to']]['names'])==len(args)]
        if not candidates:
            cls=receiver.type if receiver else self.item['owner']
            classes=[cls]
            if cls:
                classes.extend(c for c in self.b.models if c.rsplit('.',1)[-1]==cls)
                classes.extend(c for c,_,_ in self.b.method_index if c.rsplit('.',1)[-1]==cls)
            for cls in dict.fromkeys(classes):
                seen=set()
                while cls and cls not in seen:
                    seen.add(cls)
                    candidates.extend(self.b.method_index.get((cls,name,len(args)),[]))
                    cls=self.b.graph['parents'].get(cls)
        candidates=list(dict.fromkeys(candidates))
        if len(candidates)>1:
            def fits(fqn):
                types=fqn.split('(',1)[1][:-1].split(',') if args else []
                return all(not arg.type or arg.type.rsplit('.',1)[-1]==expected.rsplit('.',1)[-1]
                           for arg,expected in zip(args,types))
            matched=[c for c in candidates if fits(c)]
            if matched:
                candidates=matched
        return candidates[0] if len(candidates)==1 else None

    def model(self,receiver,name):
        type_name=re.sub(r'<.*>','',receiver.type).strip()
        models=[(cls,m) for cls,m in self.b.models.items()
                if cls==type_name or cls.rsplit('.',1)[-1]==type_name]
        if len(models)==1:
            return models[0][1]
        return None

    def call(self,node):
        name=self.text(node.child_by_field_name('name'))
        target=node.child_by_field_name('object')
        receiver=self.eval(target) if target else self.receiver
        arguments=node.child_by_field_name('arguments')
        args=[self.eval(n) for n in arguments.named_children if n.type not in ('line_comment','block_comment')]
        result=self.value(node,kind='call')
        namespace=receiver.object_id or receiver.node
        model=self.model(receiver,name)
        if model and model['basis']=='jdk_system_properties':
            namespace='system_properties'
        if model and name in (model['read'],model['write'],model['substitute']):
            self.g.nodes[result.node]['api_model']=model['basis']
            if name==model['substitute'] and args:
                self.g.edge(args[0].node,result.node,'TEMPLATE_INPUT',certainty='modelled')
                self.b.substitutions.append((namespace,args[0].literal,result.node))
            elif args:
                self.g.edge(args[0].node,result.node,'CONFIG_KEY',certainty='modelled')
                key=args[0].literal
                if key is None:
                    self.b.unresolved.append(dict(method=self.fqn,line=self.g.nodes[result.node]['line'],
                                                  kind='dynamic_configuration_key',call=self.text(node)))
                else:
                    slot=self.b.slot(namespace,key,'configuration')
                    if name==model['write'] and len(args)>1:
                        self.g.edge(args[1].node,result.node,'CONFIG_VALUE',certainty='modelled')
                        self.g.edge(result.node,slot,'CONFIG_WRITE',certainty='modelled')
                    elif name==model['read']:
                        self.g.edge(slot,result.node,'CONFIG_READ',certainty='modelled')
                        for default in args[1:]:
                            self.g.edge(default.node,result.node,'CONFIG_DEFAULT',certainty='modelled')
                        result.type=self.b.graph['returnTypes'].get(self.resolve(node,name,receiver,args),'')
            return result
        # Containers carry values but are not automatically treated as configuration engines.
        if name in ('put','get') and args and re.sub(r'<.*>','',receiver.type).rsplit('.',1)[-1] in ('Map','HashMap','Properties'):
            key=args[0].literal if args[0].literal is not None else '*'
            slot=self.b.slot(namespace,key,'container_entry')
            if name=='put' and len(args)>1:
                self.g.edge(args[1].node,result.node,'CONTAINER_VALUE',certainty='modelled')
                self.g.edge(result.node,slot,'CONTAINER_WRITE',certainty='modelled')
            elif name=='get':
                self.g.edge(slot,result.node,'CONTAINER_READ',certainty='modelled')
            return result
        fqn=self.resolve(node,name,receiver,args)
        if fqn:
            self.g.nodes[result.node]['callee']=fqn
        if fqn and self.depth<MAX_CALL_DEPTH and fqn!=self.fqn:
            value=self.b.invoke(fqn,args,receiver,f'{self.context}/call@{node.start_byte}',self.depth+1)
            if value:
                self.g.edge(value.node,result.node,'RETURN_VALUE',certainty='modelled')
                result.type=value.type
                result.object_id=value.object_id
                result.literal=value.literal
            result.type=result.type or self.b.graph['returnTypes'].get(fqn,'')
        else:
            for value in [receiver]+args:
                if value:
                    self.g.edge(value.node,result.node,'OPAQUE_TRANSFORM',certainty='may')
            result.type=self.b.graph['returnTypes'].get(fqn,'') if fqn else ''
            if not fqn and (args or receiver.node):
                self.g.nodes[result.node]['opaque']=True
        return result

    def run(self):
        self.statement(self.item['node'].child_by_field_name('body'))
        if not self.returned:
            return None
        node_id=f'return:{self.context}'
        self.g.node(node_id,kind='return_summary',method=self.fqn,version=self.item['version'],context=self.context,
                    file=self.item['file'],line=self.item['node'].start_point.row+1+self.item['line_offset'])
        for value in self.returned:
            self.g.edge(value.node,node_id,'RETURN_VALUE',certainty='may' if len(self.returned)>1 else 'syntactic')
        first=self.returned[0]
        return Value(node_id,self.b.graph['returnTypes'].get(self.fqn,first.type),
                     first.object_id if all(v.object_id==first.object_id for v in self.returned) else node_id,
                     first.literal if all(v.literal==first.literal for v in self.returned) else None)

    def statement(self,node):
        if node is None or self.b.truncated:
            return
        if len(self.g.nodes)>=MAX_NODES:
            self.b.truncated=True
            return
        kind=node.type
        if kind in ('block','constructor_body'):
            names = [self.text(declaration.child_by_field_name('name'))
                     for child in node.named_children if child.type=='local_variable_declaration'
                     for declaration in child.named_children if declaration.type=='variable_declarator']
            prior = {name:self.env[name] for name in names if name in self.env}
            for child in node.named_children:
                self.statement(child)
            for name in names:
                self.env.pop(name,None)
            self.env.update(prior)
        elif kind=='local_variable_declaration':
            type_node=node.child_by_field_name('type')
            for declaration in node.named_children:
                if declaration.type!='variable_declarator':
                    continue
                name=self.text(declaration.child_by_field_name('name'))
                value=self.eval(declaration.child_by_field_name('value'))
                if value:
                    assigned=self.value(declaration,[value],kind='local_definition',
                                        type_name=self.text(type_node),object_id=value.object_id,constant=value.literal)
                else:
                    assigned=self.value(declaration,kind='local_definition',type_name=self.text(type_node))
                self.env[name]=assigned
        elif kind=='if_statement':
            condition=node.child_by_field_name('condition')
            value=self.eval(condition)
            guard=self.site(condition,'condition')
            self.g.edge(value.node,guard,'CONDITION_INPUT')
            before=dict(self.env)
            branches=[]
            for child,branch in [('consequence','true'),('alternative','false')]:
                self.env=dict(before)
                self.guards.append((guard,branch))
                self.statement(node.child_by_field_name(child))
                self.guards.pop()
                branches.append(dict(self.env))
            self.env=dict(before)
            for name in branches[0].keys() | branches[1].keys():
                values=[b[name] for b in branches if name in b]
                if len(values)==2 and values[0].node!=values[1].node:
                    merged=self.value(node,values,kind='merge',type_name=values[0].type,
                                      object_id=values[0].object_id if values[0].object_id==values[1].object_id else '')
                    self.env[name]=merged
                elif name in before:
                    self.env[name]=values[0]
        elif kind in ('while_statement','do_statement','for_statement','enhanced_for_statement'):
            initial=node.child_by_field_name('init')
            self.statement(initial)
            condition=node.child_by_field_name('condition') or node.child_by_field_name('value')
            value=self.eval(condition)
            guard=self.site(condition or node,'loop_condition')
            if value:
                self.g.edge(value.node,guard,'CONDITION_INPUT')
            self.guards.append((guard,'loop_body'))
            before=dict(self.env)
            self.statement(node.child_by_field_name('body'))
            update=node.child_by_field_name('update')
            self.eval(update)
            self.guards.pop()
            for name in before.keys() & self.env.keys():
                if before[name].node!=self.env[name].node:
                    self.env[name]=self.value(node,[before[name],self.env[name]],kind='loop_merge',
                                             type_name=before[name].type)
        elif kind=='return_statement':
            value=self.eval(node.named_children[0]) if node.named_children else None
            if value:
                self.returned.append(self.value(node,[value],kind='return',type_name=value.type,
                                                object_id=value.object_id,constant=value.literal))
        elif kind=='throw_statement':
            self.value(node,[self.eval(n) for n in node.named_children],kind='throw')
        elif kind=='expression_statement':
            for child in node.named_children:
                self.eval(child)
        elif kind in ('try_statement','try_with_resources_statement','catch_clause','finally_clause',
                      'synchronized_statement','switch_expression','switch_block','switch_block_statement_group'):
            for child in node.named_children:
                if child.type not in ('formal_parameter','catch_formal_parameter'):
                    self.statement(child)
        elif kind not in ('line_comment','block_comment','break_statement','continue_statement'):
            self.eval(node)


def impact_paths(fine, seeds, *, max_depth=MAX_PATH):
    nodes={n['id']:n for n in fine['nodes']}
    edges=defaultdict(list)
    for edge in fine['edges']:
        edges[edge['source']].append(edge)
    starts=set(fine['seed_starts'])
    # Field/type seeds and unresolved overlays retain parent evidence as an explicit fallback.
    overlay_seeds={n['method'] for n in nodes.values() if n.get('version')=='seed_after'}
    for seed in seeds:
        if seed['type']=='field':
            starts.add('field:'+seed['fqn'])
        elif seed['type']=='type':
            starts.update(n['id'] for n in nodes.values()
                          if n.get('method') and owner(n['method'])==seed['fqn'])
        elif seed['fqn'] not in overlay_seeds:
            starts.update(n['id'] for n in nodes.values() if n.get('method')==seed['fqn'])
    visited={start:None for start in sorted(starts) if start in nodes}
    queue=deque(visited)
    paths={}
    while queue:
        current=queue.popleft()
        prior=visited[current] or []
        if len(prior)>=max_depth:
            continue
        for edge in edges[current]:
            target=edge['target']
            if target in visited:
                continue
            path=prior+[edge]
            visited[target]=path
            queue.append(target)
            node=nodes[target]
            fqn=node.get('fqn') or node.get('method')
            if fqn and fqn not in {s['fqn'] for s in seeds}:
                paths.setdefault(fqn,path)
    return paths


def build_fine(task, graph, root):
    """Keep fine caches separate from the unchanged method-level graph export."""
    import katia

    fingerprint = hashlib.sha256(json.dumps(dict(
        task=task, graph=graph, code=katia.digest(Path(__file__)),
        diff_extractor=katia.digest(Path(__file__).with_name('diff_overlay.py')),
        source=katia.digest(Path(root)/'.katia-source.json')), sort_keys=True).encode()).hexdigest()
    cache=katia.ROOT/'dataset/indexes'/f'fine-{fingerprint}.json'
    if cache.exists():
        fine=json.loads(cache.read_text())
    else:
        fine=Builder(root,graph,task['seed_changes']).build()
        fine['fingerprint']=fingerprint
        katia.dump(cache,fine)
    return fine,cache
