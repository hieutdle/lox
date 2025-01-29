import os


def define_ast(output_dir, base_name, types):
    output_dir = os.path.abspath(output_dir)  # Get absolute path

    path = os.path.join(output_dir, f"{base_name.lower()}.py")
    with open(path, "w") as f:  # HEADER
        f.write(
            "# THIS CODE IS GENERATED AUTOMATICALLY. DO NOT CHANGE IT MANUALLY!\n\n"
        )
        f.write("import typing\n")
        f.write("from abc import ABC, abstractmethod\n\n")

        if base_name == "Stmt":
            f.write("from pylox.expr import Expr\n\n")
        f.write("from pylox.tokens import Token\n\n")

        f.write(f"class {base_name}Visitor(ABC):\n")

        for expr_type in types:
            class_name = expr_type.split(":")[0].strip()
            f.write("    @abstractmethod\n")
            f.write(
                f"    def visit_{class_name.lower()}_{base_name.lower()}(self, {base_name.lower()}) -> typing.Any:\n"
            )
            f.write("        pass\n\n")

        f.write(f"\nclass {base_name}(ABC):\n")
        f.write("    @abstractmethod\n")
        f.write(f"    def accept(self, visitor: {base_name}Visitor)-> typing.Any:\n")
        f.write("        pass\n\n")
        for expr_type in types:
            class_name = expr_type.split(":")[0].strip()
            fields = expr_type.split(":")[1].strip() if ":" in expr_type else ""

            f.write(f"class {class_name}({base_name}):\n")
            if fields:  # If there are fields, generate a constructor
                field_list = fields.split(", ")
                params = ", ".join(
                    f"{field.split(' ')[1].lower()}: {field.split(' ')[0]}"
                    for field in field_list
                )
                f.write(f"    def __init__(self, {params}):\n")
                for field in field_list:
                    name = field.split(" ")[1].lower()
                    f.write(f"        self.{name} = {name}\n")
            else:  # No fields, so generate a default constructor
                f.write("    def __init__(self):\n")
                f.write("        super().__init__()\n")

            f.write(
                f"\n    def accept(self, visitor: {base_name}Visitor) -> typing.Any:\n"
            )
            f.write(
                f"        return visitor.visit_{class_name.lower()}_{base_name.lower()}(self)\n\n"
            )


if __name__ == "__main__":
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )  # lox/pylox/
    default_output_dir = os.path.join(
        project_root, "pylox"
    )  # This will resolve to lox/pylox/pylox

    os.makedirs(default_output_dir, exist_ok=True)
    define_ast(
        default_output_dir,
        "Expr",
        [
            "Assign   : Token name, Expr value",
            "Binary   : Expr left, Token operator, Expr right",
            "Grouping : Expr expression",
            "Literal  : object value",
            "Logical  : Expr left, Token operator, Expr right",
            "Unary    : Token operator, Expr right",
            "Variable : Token name",
            "Call     : Expr callee, Token paren, typing.List[Expr] arguments",
            "Get      : Expr obj, Token name",
            "Set      : Expr obj, Token name, Expr value",
            "This     : Token keyword",
        ],
    )
    define_ast(
        default_output_dir,
        "Stmt",
        [
            "If         : Expr condition, Stmt then_branch, typing.Optional[Stmt] else_branch",
            "Block      : typing.List[Stmt] statements",
            "Expression : Expr expression",
            "Print      : Expr expression",
            "Var        : Token name, typing.Optional[Expr] initializer",
            "While      : Expr condition, Stmt body",
            "Break",
            "Function   : Token name, typing.List[Token] params, typing.List[Stmt] body",
            "Return     : Token keyword, typing.Optional[Expr] value",
            "Class      : Token name, typing.List[Function] methods",
        ],
    )
