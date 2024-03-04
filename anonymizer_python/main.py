import json
import random
from enum import Enum
import re

class WordType(Enum):
    ANIMALS = "animals"
    DINOSAURS = "dinosaurs"
    FRUITS = "fruits"

word_lists = {
    WordType.ANIMALS: json.load(open("animals.json")),
    WordType.DINOSAURS: json.load(open("dinosaurs.json")),
    WordType.FRUITS: json.load(open("fruits.json"))
}

def preserve_case(target_case, value_to_format):
    if to_camel(target_case) == target_case:
        return to_camel(value_to_format)

    if to_pascal(target_case) == target_case:
        return to_pascal(value_to_format)

    if to_snake(target_case) == target_case:
        return to_snake(value_to_format)

    return value_to_format


def get_word(word_type, seed):
    used_indexes = {
        WordType.ANIMALS: [],
        WordType.DINOSAURS: [],
        WordType.FRUITS: [],
    }
    list_random = random.Random(seed)
    word_random = random.Random(seed)

    def get_word_internal():
        list_obj = word_type if word_type else random.choice(list(word_lists.values()))
        word_index = None
        while word_index is None or word_index in used_indexes[list_obj]:
        word_index = list_random.randint(0, len(list_obj) - 1)
        used_indexes[list_obj].append(word_index)
        return list_obj[word_index]

    return get_word_internal

def transform_code(code, word_type, seed):
    used_names = set()
    get_word_fn = get_word(word_type, seed)
    def transform_node(node):
        if isinstance(node, (ast.Variable, ast.FunctionDef, ast.ClassDef)):
        new_name = preserve_case(node.name, get_word_fn())
        if new_name not in used_names:
            used_names.add(new_name)
            node.name = new_name
        return node
        elif isinstance(node, (ast.Arg, ast.Attribute)):
        if node.name and node.name != "props":
            new_name = preserve_case(node.name, get_word_fn())
            if new_name not in used_names:
            used_names.add(new_name)
            node.name = new_name
        return node
        else:
        return ast.NodeTransformer().visit(node)

    import ast
    tree = ast.parse(code)
    ast.NodeTransformer().visit(tree)
    return ast.unparse(tree)

# Example usage
code = """
    def my_function(param1, param2):
    class MyClass:
        def __init__(self, prop1):
        self.prop1 = prop1

    return MyClass(10)
    """

transformed_code = transform_code(code, WordType.ANIMALS, 123)
print(transformed_code)


# SOURCE CODE FROM: Pydantic 2.0, pydantic.alias_generators
def to_camel(snake: str) -> str:
    """Convert a snake_case string to camelCase.

    Args:
        snake: The string to convert.

    Returns:
        The converted camelCase string.
    """
    camel = to_pascal(snake)
    return re.sub('(^_*[A-Z])', lambda m: m.group(1).lower(), camel)


def to_pascal(snake: str) -> str:
    """Convert a snake_case string to PascalCase.

    Args:
        snake: The string to convert.

    Returns:
        The PascalCase string.
    """
    camel = snake.title()
    return re.sub('([0-9A-Za-z])_(?=[0-9A-Z])', lambda m: m.group(1), camel)


def to_snake(camel: str) -> str:
    """Convert a PascalCase or camelCase string to snake_case.

    Args:
        camel: The string to convert.

    Returns:
        The converted string in snake_case.
    """
    snake = re.sub(r'([a-zA-Z])([0-9])', lambda m: f'{m.group(1)}_{m.group(2)}', camel)
    snake = re.sub(r'([a-z0-9])([A-Z])', lambda m: f'{m.group(1)}_{m.group(2)}', snake)
    return snake.lower()