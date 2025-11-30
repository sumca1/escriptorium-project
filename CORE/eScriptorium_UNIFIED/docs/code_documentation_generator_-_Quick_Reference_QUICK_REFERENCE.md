# code_documentation_generator - API Reference

## Classes

### `ParameterInfo`

Information about a function parameter.

| Method | Description |
|--------|-------------|

### `MethodInfo`

Complete information about a method/function.

| Method | Description |
|--------|-------------|

### `ClassInfo`

Information about a class.

| Method | Description |
|--------|-------------|

### `ModuleInfo`

Information about a Python module.

| Method | Description |
|--------|-------------|

### `CodeParser`

Parse Python source code and extract documentation-relevant information.

| Method | Description |
|--------|-------------|
| `__init__()` | Initialize parser with a Python file. |
| `analyze_module()` | Analyze entire module. |
| `find_method()` | Find a specific method/function in the module. |
| `get_all_public_methods()` | Get all public methods/functions (not starting with _). |

### `TestExtractor`

Extract code examples from test files.

| Method | Description |
|--------|-------------|
| `__init__()` | Initialize test extractor. |
| `find_test_files()` | Find test files related to a source file. |
| `extract_test_examples()` | Extract code examples from test file. |
| `convert_test_to_example()` | Convert test code to documentation example. |
| `find_examples_for_method()` | Find all example usages of a specific method. |

### `DocumentationGenerator`

Generate complete documentation from source code.

| Method | Description |
|--------|-------------|
| `__init__()` | Initialize documentation generator. |
| `generate_method_documentation()` | Generate documentation for a specific method. |
| `generate_class_documentation()` | Generate documentation for an entire class. |
| `generate_module_documentation()` | Generate complete API documentation for the module. |
| `generate_api_reference()` | Generate concise API reference (just signatures and brief descriptions). |
