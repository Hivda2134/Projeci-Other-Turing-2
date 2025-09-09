
"""
Symbolic parser for extracting code-meaning features via AST traversal.
"""

import ast
import re
from typing import Dict, List, Optional, Set, Tuple

NameList = List[str]

def split_ident(name: str) -> List[str]:
    parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?![a-z])|\d+", name)
    return [p.lower() for p in re.split(r"[\W]+", name) if p] + [p.lower() for p in parts if p]

def _doc_clean(text: str) -> str:
    if not text:
        return ""
    first_para = text.strip().split("\n\n", 1)
    return re.sub(r"\s+", " ", first_para[0]).strip()

def parse_symbolic_summary(source_code: str) -> Dict[str, List[str] | Dict[str, int] | str]:
    """
    Extract a symbolic summary of a Python source file.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        return {
            "error": f"SyntaxError: {e}", "function_names": [], "method_names": [],
            "class_names": [], "variable_names": [], "param_names": [], "imports": [],
            "import_aliases": [], "from_imports": [], "docstrings": [], "module_doc": "",
            "type_hints": [], "calls": [], "side_effect_calls": [], "metrics": {},
        }

    function_names: NameList = []
    method_names: NameList = []
    class_names: NameList = []
    variable_names: NameList = []
    param_names: NameList = []
    type_hints: NameList = []
    imports: NameList = []
    import_aliases: NameList = []
    from_imports: NameList = []
    docstrings: List[str] = []
    calls: NameList = []
    side_effect_calls: NameList = []

    SIDE_EFFECT_FUNCS = {
        "print", "open", "write", "remove", "rename", "mkdtemp", "requests.get",
        "requests.post", "subprocess.run", "os.system", "shutil.rmtree",
        "random.seed", "setattr", "delattr",
    }

    def _name_of_call(node: ast.Call) -> Optional[str]:
        if isinstance(node.func, ast.Name):
            return node.func.id
        elif isinstance(node.func, ast.Attribute):
            parts = []
            cur = node.func
            while isinstance(cur, ast.Attribute):
                parts.append(cur.attr)
                cur = cur.value
            if isinstance(cur, ast.Name):
                parts.append(cur.id)
            return ".".join(reversed(parts))
        elif isinstance(node.func, ast.Call):
            # Handle nested calls, e.g., func()()
            return _name_of_call(node.func)
        return None

    class SummaryVisitor(ast.NodeVisitor):
        def __init__(self) -> None:
            self.in_class: Optional[str] = None

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            class_names.append(node.name)
            ds = ast.get_docstring(node)
            if ds:
                docstrings.append(_doc_clean(ds))
            prev = self.in_class
            self.in_class = node.name
            self.generic_visit(node)
            self.in_class = prev

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            tgt = method_names if self.in_class else function_names
            tgt.append(node.name)
            ds = ast.get_docstring(node)
            if ds:
                docstrings.append(_doc_clean(ds))
            for arg in [*node.args.posonlyargs, *node.args.args, *node.args.kwonlyargs]:
                param_names.append(arg.arg)
                if arg.annotation:
                    type_hints.append(ast.unparse(arg.annotation))
            if node.args.vararg:
                param_names.append(node.args.vararg.arg)
            if node.args.kwarg:
                param_names.append(node.args.kwarg.arg)
            if node.returns:
                type_hints.append(ast.unparse(node.returns))
            self.generic_visit(node)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
            if isinstance(node.target, ast.Name):
                variable_names.append(node.target.id)
            if node.annotation:
                type_hints.append(ast.unparse(node.annotation))
            self.generic_visit(node)

        def visit_Assign(self, node: ast.Assign) -> None:
            for target in node.targets:
                if isinstance(target, ast.Name):
                    variable_names.append(target.id)
                elif isinstance(target, ast.Tuple):
                    for elt in target.elts:
                        if isinstance(elt, ast.Name):
                            variable_names.append(elt.id)
            self.generic_visit(node)

        def visit_With(self, node: ast.With) -> None:
            for item in node.items:
                if item.optional_vars and isinstance(item.optional_vars, ast.Name):
                    variable_names.append(item.optional_vars.id)
            self.generic_visit(node)

        def visit_Import(self, node: ast.Import) -> None:
            for alias in node.names:
                imports.append(alias.name)
                if alias.asname:
                    import_aliases.append(alias.asname)
            self.generic_visit(node)

        def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
            module = node.module or ""
            for alias in node.names:
                name = f"{module}.{alias.name}" if module else alias.name
                from_imports.append(name)
                if alias.asname:
                    import_aliases.append(alias.asname)
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            name = _name_of_call(node)
            if name:
                calls.append(name)
                if name in SIDE_EFFECT_FUNCS:
                    side_effect_calls.append(name)
            self.generic_visit(node)

    module_doc = _doc_clean(ast.get_docstring(tree) or "")
    visitor = SummaryVisitor()
    visitor.visit(tree)

    name_tokens = ([split_ident(n) for n in function_names + method_names + class_names + variable_names + param_names])
    flat_tokens = [t for toks in name_tokens for t in toks]

    metrics = {
        "num_functions": len(function_names), "num_methods": len(method_names),
        "num_classes": len(class_names), "num_variables": len(set(variable_names)),
        "num_params": len(param_names), "num_imports": len(set(imports)) + len(set(from_imports)),
        "num_docstrings": len(docstrings) + (1 if module_doc else 0),
        "has_type_hints": int(bool(type_hints)), "num_calls": len(calls),
        "num_side_effect_calls": len(side_effect_calls), "vocab_size": len(set(flat_tokens)),
    }

    return {
        "function_names": sorted(set(function_names)), "method_names": sorted(set(method_names)),
        "class_names": sorted(set(class_names)), "variable_names": sorted(set(variable_names)),
        "param_names": sorted(set(param_names)), "imports": sorted(set(imports)),
        "import_aliases": sorted(set(import_aliases)), "from_imports": sorted(set(from_imports)),
        "docstrings": docstrings, "module_doc": module_doc, "type_hints": sorted(set(type_hints)),
        "calls": calls, "side_effect_calls": sorted(set(side_effect_calls)), "metrics": metrics,
    }

