import com.google.gson.Gson;
import java.nio.file.*;
import java.util.*;
import java.util.stream.Collectors;
import spoon.Launcher;
import spoon.reflect.code.*;
import spoon.reflect.declaration.*;
import spoon.reflect.visitor.filter.TypeFilter;

class StaticRelations {
    record Edge(String from, String to, String kind, String file, int line) {}
    record Location(String file, int start, int end) {}
    record Graph(Set<String> entities, Set<Edge> edges, Map<String, String> parents,
                 Map<String, String> returnTypes, Map<String, Map<String, String>> variables,
                 Set<String> instanceMethods, Set<String> staticMethods,
                 Map<String, String> fieldTypes, Map<String, Location> locations) {}

    static void locate(Map<String, Location> locations, Path root, String id, CtElement element) {
        var position = element.getPosition();
        if (position.isValidPosition()) {
            locations.putIfAbsent(id, new Location(root.relativize(position.getFile().toPath().toAbsolutePath())
                .toString(), position.getLine(), position.getEndLine()));
        }
    }

    static String name(CtElement declaration) {
        if (declaration == null) return null;
        CtType<?> owner = declaration.getParent(CtType.class);
        if (owner == null) return null;
        String prefix = owner.getQualifiedName().replace('$', '.') + ".";
        if (declaration instanceof CtField<?> field) return prefix + field.getSimpleName();
        if (declaration instanceof CtExecutable<?> executable) {
            String member = executable instanceof CtConstructor<?> ? owner.getSimpleName() : executable.getSimpleName();
            String parameters = executable.getParameters().stream()
                .map(p -> p.getType().getQualifiedName().replace('$', '.'))
                .collect(Collectors.joining(","));
            return prefix + member + "(" + parameters + ")";
        }
        return null;
    }

    static void edge(Set<Edge> edges, Path root, String from, CtElement target, String kind, CtElement site) {
        String to = name(target);
        var pos = site.getPosition();
        if (from != null && to != null && pos.isValidPosition()) {
            edges.add(new Edge(from, to, kind, root.relativize(pos.getFile().toPath().toAbsolutePath()).toString(), pos.getLine()));
        }
    }

    public static void main(String[] args) throws Exception {
        Path root = Path.of(args[0]).toAbsolutePath();
        Launcher spoon = new Launcher();
        spoon.getEnvironment().setNoClasspath(true);
        spoon.getEnvironment().setIgnoreDuplicateDeclarations(true);
        spoon.getEnvironment().setIgnoreSyntaxErrors(true);
        try (var paths = Files.walk(root)) {
            for (Path p : paths.filter(Files::isDirectory).sorted().toList()) {
                if (p.endsWith("src/main/java") || p.endsWith("src/java")) spoon.addInputResource(p.toString());
            }
        }
        var model = spoon.buildModel();
        Set<String> entities = new TreeSet<>();
        Set<Edge> edges = new LinkedHashSet<>();
        Map<String, String> parents = new TreeMap<>();
        Map<String, String> returnTypes = new TreeMap<>();
        Map<String, Map<String, String>> variables = new TreeMap<>();
        Set<String> instanceMethods = new TreeSet<>();
        Set<String> staticMethods = new TreeSet<>();
        Map<String, String> fieldTypes = new TreeMap<>();
        Map<String, Location> locations = new TreeMap<>();
        for (CtType<?> type : model.getElements(new TypeFilter<>(CtType.class))) {
            String id = type.getQualifiedName().replace('$', '.');
            entities.add(id);
            locate(locations, root, id, type);
            if (type.getSuperclass() != null) parents.put(id, type.getSuperclass().getQualifiedName().replace('$', '.'));
        }
        for (CtField<?> field : model.getElements(new TypeFilter<>(CtField.class))) {
            String id = name(field);
            if (id == null) continue;
            entities.add(id);
            locate(locations, root, id, field);
            if (field.getType() != null) {
                fieldTypes.put(id, field.getType().getQualifiedName().replace('$', '.'));
            }
        }
        for (CtExecutable<?> method : model.getElements(new TypeFilter<>(CtExecutable.class))) {
            if (!(method instanceof CtMethod<?> || method instanceof CtConstructor<?>)) continue;
            String from = name(method);
            if (from == null) continue;
            entities.add(from);
            locate(locations, root, from, method);
            if (method instanceof CtMethod<?> m) {
                returnTypes.put(from, m.getType().getQualifiedName().replace('$', '.'));
                if (!m.isStatic() && !m.isPrivate()) instanceMethods.add(from);
                if (m.isStatic()) staticMethods.add(from);
            }
            Map<String, String> bindings = new TreeMap<>();
            for (CtVariable<?> variable : method.getElements(new TypeFilter<>(CtVariable.class))) {
                if (variable.getParent(CtExecutable.class) == method && variable.getType() != null) {
                    String type = variable.getType().getQualifiedName().replace('$', '.');
                    bindings.merge(variable.getSimpleName(), type, (a, b) -> a.equals(b) ? a : "");
                }
            }
            variables.put(from, bindings);
            for (CtFieldAccess<?> access : method.getElements(new TypeFilter<>(CtFieldAccess.class))) {
                if (access.getParent(CtExecutable.class) != method) continue;
                var field = access.getVariable().getDeclaration();
                boolean write = access instanceof CtFieldWrite<?>;
                edge(edges, root, from, field, write ? "WRITE" : "READ", access);
                CtElement parent = access.getParent();
                if (write && (parent instanceof CtOperatorAssignment<?, ?> ||
                    (parent instanceof CtUnaryOperator<?> unary &&
                     Set.of(UnaryOperatorKind.PREINC, UnaryOperatorKind.PREDEC,
                            UnaryOperatorKind.POSTINC, UnaryOperatorKind.POSTDEC).contains(unary.getKind())))) {
                    edge(edges, root, from, field, "READ", access);
                }
            }
            for (CtAbstractInvocation<?> call : method.getElements(new TypeFilter<>(CtAbstractInvocation.class))) {
                if (call.getParent(CtExecutable.class) != method) continue;
                edge(edges, root, from, call.getExecutable().getDeclaration(), "CALLS", call);
            }
        }
        Files.writeString(Path.of(args[1]), new Gson().toJson(
            new Graph(entities, edges, parents, returnTypes, variables, instanceMethods, staticMethods, fieldTypes, locations)));
    }
}
