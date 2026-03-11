import os
from lark import v_args, Tree, Token
from .common import Visitor, parse_file, discard


class Importer(Visitor):
    def __init__(self, path: str, src_dir = None) -> None:
        super().__init__()
        self.current_file = path
        self.src_dir: str = src_dir or os.path.dirname(path)
        self.past_imports: list[str] = [path]

    @v_args(tree=True)
    def program(self, tree) -> Tree:
        # start with imports
        for imp in tree.find_data("import_file"):
            path: str = os.path.join(self.src_dir, imp.children[-1].strip('"'))
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

