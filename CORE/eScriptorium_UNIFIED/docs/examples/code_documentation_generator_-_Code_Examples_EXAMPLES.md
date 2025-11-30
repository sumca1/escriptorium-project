# code_documentation_generator API

## Overview

🤖 Automatic Documentation Generator from Code
==============================================

Automatically generates documentation by analyzing Python source code.

Features:
- AST parsing for function signatures
- Type hint extraction
- Docstring analysis
- Test example extraction
- Auto-generation of API documentation

Usage:
    from code_documentation_generator import CodeParser
    
    parser = CodeParser("my_module.py")
    info = parser.analyze_method("my_function")
    print(info['signature'])
    print(info['parameters'])

## Quick Start

```python
from code_documentation_generator import ParameterInfo
```

## Classes

## Class: `ParameterInfo`

Information about a function parameter.


## Class: `MethodInfo`

Complete information about a method/function.


## Class: `ClassInfo`

Information about a class.


## Class: `ModuleInfo`

Information about a Python module.


## Class: `CodeParser`

Parse Python source code and extract documentation-relevant information.

Uses Python's ast module to analyze code structure.

### Methods

### Method: `CodeParser.__init__()`

Initialize parser with a Python file.

**Signature:**
```python
def __init__(self, file_path: str)
```

**Parameters:**
- `file_path` (str, required)

---

### Method: `CodeParser.analyze_module()`

Analyze entire module.

**Signature:**
```python
def analyze_module(self) -> ModuleInfo
```

**Returns:**
- `ModuleInfo`: ModuleInfo with all classes and functions

---

### Method: `CodeParser._parse_class()`

Parse a class definition.

**Signature:**
```python
def _parse_class(self, node: ast.ClassDef) -> ClassInfo
```

**Parameters:**
- `node` (ast.ClassDef, required)

**Returns:**
- `ClassInfo`

---

### Method: `CodeParser._parse_function()`

Parse a function/method definition.

**Signature:**
```python
def _parse_function(self, node: ast.FunctionDef, class_name: Optional[str] = None) -> MethodInfo
```

**Parameters:**
- `node` (ast.FunctionDef, required)
- `class_name` (Optional[str], optional): Default `None`

**Returns:**
- `MethodInfo`

---

### Method: `CodeParser._build_signature()`

Build full function signature.

**Signature:**
```python
def _build_signature(self, node: ast.FunctionDef) -> str
```

**Parameters:**
- `node` (ast.FunctionDef, required)

**Returns:**
- `str`

---

### Method: `CodeParser._parse_parameters()`

Parse function parameters with type hints and descriptions.

**Signature:**
```python
def _parse_parameters(self, args: ast.arguments, docstring: str) -> List[ParameterInfo]
```

**Parameters:**
- `args` (ast.arguments, required)
- `docstring` (str, required)

**Returns:**
- `List[ParameterInfo]`

---

### Method: `CodeParser._extract_parameter_docs()`

Extract parameter descriptions from docstring.

**Signature:**
```python
def _extract_parameter_docs(self, docstring: str) -> Dict[str, str]
```

**Parameters:**
- `docstring` (str, required)

**Returns:**
- `Dict[str, str]`

---

### Method: `CodeParser._extract_return_description()`

Extract return value description from docstring.

**Signature:**
```python
def _extract_return_description(self, docstring: str) -> str
```

**Parameters:**
- `docstring` (str, required)

**Returns:**
- `str`

---

### Method: `CodeParser._extract_raises()`

Extract exceptions raised from docstring.

**Signature:**
```python
def _extract_raises(self, docstring: str) -> List[Tuple[str, str]]
```

**Parameters:**
- `docstring` (str, required)

**Returns:**
- `List[Tuple[str, str]]`

---

### Method: `CodeParser._extract_examples()`

Extract code examples from docstring.

**Signature:**
```python
def _extract_examples(self, docstring: str) -> List[str]
```

**Parameters:**
- `docstring` (str, required)

**Returns:**
- `List[str]`

---

### Method: `CodeParser.find_method()`

Find a specific method/function in the module.

**Signature:**
```python
def find_method(self, method_name: str) -> Optional[MethodInfo]
```

**Parameters:**
- `method_name` (str, required)
  - Name of method to find (can include class: "ClassName.method_name")

**Returns:**
- `Optional[MethodInfo]`: MethodInfo if found, None otherwise

---

### Method: `CodeParser.get_all_public_methods()`

Get all public methods/functions (not starting with _).

**Signature:**
```python
def get_all_public_methods(self) -> List[MethodInfo]
```

**Returns:**
- `List[MethodInfo]`

---


## Class: `TestExtractor`

Extract code examples from test files.

Finds unit tests and converts them into documentation examples.

### Methods

### Method: `TestExtractor.__init__()`

Initialize test extractor.

**Signature:**
```python
def __init__(self, test_file_path: Optional[str] = None)
```

**Parameters:**
- `test_file_path` (Optional[str], optional): Default `None`

---

### Method: `TestExtractor.find_test_files()`

Find test files related to a source file.

**Signature:**
```python
def find_test_files(self, source_file: Path) -> List[Path]
```

**Parameters:**
- `source_file` (Path, required)
  - Source Python file

**Returns:**
- `List[Path]`: List of test file paths found

---

### Method: `TestExtractor.extract_test_examples()`

Extract code examples from test file.

**Signature:**
```python
def extract_test_examples(self, test_file: Path, target_function: Optional[str] = None) -> List[Dict[str, str]]
```

**Parameters:**
- `test_file` (Path, required)
  - Path to test file
- `target_function` (Optional[str], optional): Default `None`
  - Specific function to find tests for (optional)

**Returns:**
- `List[Dict[str, str]]`: List of dicts with:

---

### Method: `TestExtractor._generate_description_from_test_name()`

Generate description from test function name.

**Signature:**
```python
def _generate_description_from_test_name(self, test_name: str) -> str
```

**Parameters:**
- `test_name` (str, required)

**Returns:**
- `str`

---

### Method: `TestExtractor.convert_test_to_example()`

Convert test code to documentation example.

**Signature:**
```python
def convert_test_to_example(self, test_code: str) -> str
```

**Parameters:**
- `test_code` (str, required)
  - Original test code

**Returns:**
- `str`: Simplified example code

---

### Method: `TestExtractor.find_examples_for_method()`

Find all example usages of a specific method.

**Signature:**
```python
def find_examples_for_method(self, source_file: Path, method_name: str) -> List[str]
```

**Parameters:**
- `source_file` (Path, required)
  - Source Python file
- `method_name` (str, required)
  - Name of method to find examples for

**Returns:**
- `List[str]`: List of code examples

---


## Class: `DocumentationGenerator`

Generate complete documentation from source code.

Combines CodeParser and TestExtractor to create full markdown documentation.

### Methods

### Method: `DocumentationGenerator.__init__()`

Initialize documentation generator.

**Signature:**
```python
def __init__(self, source_file: str)
```

**Parameters:**
- `source_file` (str, required)

---

### Method: `DocumentationGenerator.generate_method_documentation()`

Generate documentation for a specific method.

**Signature:**
```python
def generate_method_documentation(self, method_name: str, include_tests: bool = True) -> str
```

**Parameters:**
- `method_name` (str, required)
  - Name of method to document
- `include_tests` (bool, optional): Default `True`
  - Whether to include test examples

**Returns:**
- `str`: Markdown documentation

---

### Method: `DocumentationGenerator.generate_class_documentation()`

Generate documentation for an entire class.

**Signature:**
```python
def generate_class_documentation(self, class_name: str, include_tests: bool = True) -> str
```

**Parameters:**
- `class_name` (str, required)
  - Name of class to document
- `include_tests` (bool, optional): Default `True`
  - Whether to include test examples

**Returns:**
- `str`: Markdown documentation

---

### Method: `DocumentationGenerator.generate_module_documentation()`

Generate complete API documentation for the module.

**Signature:**
```python
def generate_module_documentation(self, title: Optional[str] = None, include_tests: bool = True, include_private: bool = False) -> str
```

**Parameters:**
- `title` (Optional[str], optional): Default `None`
  - Custom title (default: module name)
- `include_tests` (bool, optional): Default `True`
  - Whether to include test examples
- `include_private` (bool, optional): Default `False`
  - Whether to include private methods (_method)

**Returns:**
- `str`: Full markdown documentation

---

### Method: `DocumentationGenerator.generate_api_reference()`

Generate concise API reference (just signatures and brief descriptions).

**Signature:**
```python
def generate_api_reference(self) -> str
```

**Returns:**
- `str`: Markdown API reference

---

