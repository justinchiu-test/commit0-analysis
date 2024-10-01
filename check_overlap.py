import ast
import os
from pathlib import Path
from difflib import SequenceMatcher

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

def process_directory(directory):
    """
    Process all Python files in a directory and extract functions with docstrings.
    """
    all_functions = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, directory)
                functions = extract_functions_with_docstring(file_path)
                if functions:
                    all_functions[relative_path] = functions
    return all_functions

def calculate_overlap(str1, str2):
    """
    Calculate the overlap between two strings using SequenceMatcher.
    """
    return SequenceMatcher(None, str1, str2).ratio()

def main():
    gold_functions = process_directory(gold_dir)
    prediction_functions = process_directory(prediction_dir)

    total_overlap = 0
    total_functions = 0

    for repo in gold_functions:
        if repo in prediction_functions:
            for func_name, gold_func in gold_functions[repo].items():
                if func_name in prediction_functions[repo]:
                    gold_docstring = ast.get_docstring(ast.parse(gold_func))
                    pred_docstring = ast.get_docstring(ast.parse(prediction_functions[repo][func_name]))
                    
                    if gold_docstring and pred_docstring:
                        overlap = calculate_overlap(gold_docstring, pred_docstring)
                        total_overlap += overlap
                        total_functions += 1
                        print(f"Repo: {repo}, Function: {func_name}, Overlap: {overlap:.2f}")

    if total_functions > 0:
        average_overlap = total_overlap / total_functions
        print(f"\nAverage overlap across all functions: {average_overlap:.2f}")
    else:
        print("No matching functions with docstrings found.")

if __name__ == "__main__":
    main()
