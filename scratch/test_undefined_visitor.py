import ast
import builtins

class _UndefinedNameDetector(ast.NodeVisitor):
    def __init__(self):
        self.issues = []
        # Prepopulate with standard Python builtins
        self.defined_names = set(dir(builtins))
        self.defined_names.add("self")
        self.defined_names.add("cls")
        self.used_names = []

    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name.split('.')[0]
            self.defined_names.add(name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.defined_names.add(name)
        self.generic_visit(node)

    def visit_ClassDef(self, node):
        self.defined_names.add(node.name)
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        self.defined_names.add(node.name)
        for arg in node.args.args:
            self.defined_names.add(arg.arg)
        for arg in getattr(node.args, "posonlyargs", []):
            self.defined_names.add(arg.arg)
        for arg in node.args.kwonlyargs:
            self.defined_names.add(arg.arg)
        if node.args.vararg:
            self.defined_names.add(node.args.vararg.arg)
        if node.args.kwarg:
            self.defined_names.add(node.args.kwarg.arg)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node):
        self.visit_FunctionDef(node)

    def visit_Assign(self, node):
        for target in node.targets:
            self._collect_target_names(target)
        self.generic_visit(node)

    def visit_AnnAssign(self, node):
        self._collect_target_names(node.target)
        self.generic_visit(node)

    def _collect_target_names(self, target):
        if isinstance(target, ast.Name):
            self.defined_names.add(target.id)
        elif isinstance(target, (ast.Tuple, ast.List)):
            for elt in target.elts:
                self._collect_target_names(elt)
        elif isinstance(target, ast.Attribute):
            if isinstance(target.value, ast.Name):
                self.defined_names.add(target.value.id)

    def visit_For(self, node):
        self._collect_target_names(node.target)
        self.generic_visit(node)

    def visit_AsyncFor(self, node):
        self.visit_For(node)

    def visit_comprehension(self, node):
        self._collect_target_names(node.target)
        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.name:
            self.defined_names.add(node.name)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_names.append((node.id, node.lineno))
        self.generic_visit(node)

    def audit(self):
        # Pass 2: find used names that are never defined anywhere
        for name, lineno in self.used_names:
            if name not in self.defined_names:
                # Add to issues
                self.issues.append({
                    "type": "critical",
                    "title": "Undefined variable or function reference",
                    "line": lineno,
                    "desc": f"Name '{name}' is referenced but is not defined in this file.",
                    "fix": f"Define '{name}', import it, or correct the spelling."
                })

code = """print("Hello from mee.py")
prit(code)
"""

tree = ast.parse(code)
detector = _UndefinedNameDetector()
detector.visit(tree)
detector.audit()

print("Audited Issues:")
for issue in detector.issues:
    print(issue)
