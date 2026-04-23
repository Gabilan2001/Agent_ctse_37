# tools/read_and_parse_code.py
import ast
import os
from typing import TypedDict, List


class ParsedCode(TypedDict):
    raw_code: str
    functions: List[str]
    imports: List[str]
    complexity_score: int


def read_and_parse_code(file_path: str) -> ParsedCode:
    """
    Reads a Python source file and extracts structural
    information using Python's built-in AST module.

    Args:
        file_path (str): Absolute or relative path to
                         the .py file to be parsed.

    Returns:
        ParsedCode: A dict containing raw_code, list of
                    function names, list of imports, and
                    an estimated complexity score.

    Raises:
        FileNotFoundError: If the file does not exist.
        SyntaxError: If the file is not valid Python.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as f:
        raw_code = f.read()

    # Parse the AST
    tree = ast.parse(raw_code)

    # Extract function names
    functions = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]

    # Extract imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "unknown")

    # Estimate complexity by counting branches
    complexity = sum(
        1 for node in ast.walk(tree)
        if isinstance(node, (
            ast.If, ast.For, ast.While,
            ast.Try, ast.ExceptHandler
        ))
    )

    return {
        "raw_code": raw_code,
        "functions": functions,
        "imports": imports,
        "complexity_score": complexity
    }# tools/read_and_parse_code.py
import ast
import os
from typing import TypedDict, List


class ParsedCode(TypedDict):
    raw_code: str
    functions: List[str]
    imports: List[str]
    complexity_score: int


def read_and_parse_code(file_path: str) -> ParsedCode:
    """
    Reads a Python source file and extracts structural
    information using Python's built-in AST module.

    Args:
        file_path (str): Absolute or relative path to
                         the .py file to be parsed.

    Returns:
        ParsedCode: A dict containing raw_code, list of
                    function names, list of imports, and
                    an estimated complexity score.

    Raises:
        FileNotFoundError: If the file does not exist.
        SyntaxError: If the file is not valid Python.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with open(file_path, "r", encoding="utf-8") as f:
        raw_code = f.read()

    # Parse the AST
    tree = ast.parse(raw_code)

    # Extract function names
    functions = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]

    # Extract imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "unknown")

    # Estimate complexity by counting branches
    complexity = sum(
        1 for node in ast.walk(tree)
        if isinstance(node, (
            ast.If, ast.For, ast.While,
            ast.Try, ast.ExceptHandler
        ))
    )

    return {
        "raw_code": raw_code,
        "functions": functions,
        "imports": imports,
        "complexity_score": complexity
    }