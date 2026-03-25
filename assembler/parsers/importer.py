import os
from lark import v_args, Tree, Token
from .common import Visitor, parse_file, discard


class Importer(Visitor):
    def __init__(self, path: str, src_dir = None) -> None:
        super().__init__()
        self.current_file = path
        self.src_dir: str = src_dir or os.path.dirname(path)
        self.past_imports: list[str] = [path]

    def find_import(self, base: str) -> str:
        relative = os.path.join(self.src_dir, base)
        stdlib = os.path.join(os.path.curdir, "stdlib/", base)
        if base.startswith('/') or os.path.exists(relative):
            return relative
        elif os.path.exists(stdlib):
            return stdlib
        else:
            raise ValueError(f"Could not find import `{base}`")

    @v_args(tree=True)
    def program(self, tree) -> Tree:
        # start with imports
        for imp in tree.find_data("import_file"):
            base: str = imp.children[-1].strip('"')
            path: str = self.find_import(base)
            if path not in self.past_imports:
                print(f"Importing {path}...")
                self.current_file = path
                imported: Tree = self.visit(parse_file(path))
                self.past_imports.append(path)
                tree.children += imported.children
        return tree

    WS = discard
    WS_INLINE = discard
    NEWLINE = discard

