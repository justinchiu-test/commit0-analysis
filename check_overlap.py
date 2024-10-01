import ast
from pathlib import Path

""" gold directory structure will have
gold_dir / {repo}
for each repo, we need to look at all functions with docstrings
and align them to the SAME function in
prediction_dir / {repo}

the repo structures will be IDENTICAL
"""

gold_dir = Path("/Users/justinchiu/code/commit0/repos")
prediction_dir = Path("/Users/justinchiu/code/commit0-analysis/sonnet_output")

# use this function to extract the functions
def extract_functions_with_docstring(filename):
    """
    Example usage
    ```
    filename = "your_python_file.py"  # Replace with your filename
    functions_with_docstring = extract_functions_with_docstring(filename)

    # Print the functions with docstrings
    for func_name, func_body in functions_with_docstring.items():
        print(f"Function Name: {func_name}\nFunction Body:\n{func_body}\n")
    ```
    """

    # Open the file and read its content
    with open(filename, 'r') as file:
        file_content = file.read()

    # Parse the content of the file into an AST
    tree = ast.parse(file_content)

    # Dictionary to store functions with docstrings
    function_dict = {}

    # Iterate over the nodes of the AST
    for node in ast.walk(tree):
        # We're only interested in function definitions
        if isinstance(node, ast.FunctionDef):
            # Check if the function has a docstring
            docstring = ast.get_docstring(node)
            if docstring:
                # Get the function name (id)
                function_name = node.name
                
                # Extract the full source code of the function
                function_code = ast.get_source_segment(file_content, node)
                
                # Add the function to the dictionary
                function_dict[function_name] = function_code

    return function_dict

def main():
    print("Hello from commit0-analysis!")


if __name__ == "__main__":
    main()
