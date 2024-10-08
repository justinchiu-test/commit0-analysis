import ast
import os
from pathlib import Path
from difflib import SequenceMatcher
from pydantic import BaseModel
import evaluate
import json
from nltk.translate.bleu_score import sentence_bleu
from nltk.tokenize import word_tokenize
from nltk.util import ngrams

""" gold directory structure will have
gold_dir / {repo}
for each repo, we need to look at all functions with docstrings
and align them to the SAME function in
prediction_dir / {repo}

the repo structures will be IDENTICAL
"""

gold_dir = Path("/Users/justinchiu/code/commit0/repos")
prediction_dir = Path("/Users/justinchiu/code/commit0-analysis/sonnet_output")

class Function(BaseModel):
    repo: str
    path: str
    code: str
    name: str
    docstring: str
    body: str

# use this function to extract the functions
def extract_functions_with_docstring(filename, repo, path):
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
    try:
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
                    if (
                        isinstance(node.body[0], ast.Expr)
                        and isinstance(node.body[0].value, ast.Constant)
                        and isinstance(node.body[0].value.value, str)
                    ):
                        body_nodes = node.body[1:]
                    else:
                        body_nodes = node.body
                    body = ast.unparse(body_nodes)
                    # Add the function to the dictionary
                    function_dict[function_name] = Function(
                        repo=repo,
                        path=path,
                        code=function_code,
                        name=function_name,
                        docstring=docstring,
                        body=body,
                    )

        return function_dict
    except:
        print("Could not process", filename)
        return {}

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
                repo = relative_path.split("/")[0]
                functions = extract_functions_with_docstring(file_path, repo, relative_path)
                if functions:
                    all_functions[relative_path] = functions
    return all_functions


def calculate_ngram_overlap(text1, text2, n=5):
    """
    Calculate the n-gram overlap between two texts.
    """
    tokens1 = word_tokenize(text1)
    tokens2 = word_tokenize(text2)
    
    ngrams1 = set(ngrams(tokens1, n))
    ngrams2 = set(ngrams(tokens2, n))
    
    overlap = len(ngrams1.intersection(ngrams2))
    total = len(ngrams1.union(ngrams2))
    
    return overlap / total if total > 0 else 0

def main():
    # TODO: average by repo
    # analysis of length distribution for match vs not
    gold_functions = process_directory(gold_dir)
    prediction_functions = process_directory(prediction_dir)

    num_f = 0
    exact_matches = 0
    bleu = evaluate.load("bleu")

    predictions = []
    references = []

    data = []

    for repo in gold_functions:
        if repo in prediction_functions:
            for func_name, gold_func in gold_functions[repo].items():
                if func_name in prediction_functions[repo]:
                    pred_func = prediction_functions[repo][func_name]

                    gb = gold_func.body
                    pb = pred_func.body

                    if gb == pb:
                        exact_matches += 1
                    num_f += 1

                    predictions.append(pb)
                    references.append([gb])

                    # Tokenize the body and pred_body
                    reference = [word_tokenize(gold_func.body)]
                    candidate = word_tokenize(pred_func.body)

                    # Calculate sentence BLEU score
                    sentence_bleu_score = sentence_bleu(reference, candidate, smoothing_function=None)

                    # Calculate 5-gram overlap
                    five_gram_overlap = calculate_ngram_overlap(gold_func.body, pred_func.body, n=5)
                    ten_gram_overlap = calculate_ngram_overlap(gold_func.body, pred_func.body, n=10)

                    data.append({
                        "repo": gold_func.repo,
                        "path": gold_func.path,
                        "name": gold_func.name,
                        "docstring": gold_func.docstring,
                        "pred_docstring": pred_func.docstring,
                        "body": gold_func.body,
                        "pred_body": pred_func.body,
                        "sentence_bleu": sentence_bleu_score,
                        "five_gram_overlap": five_gram_overlap,
                        "ten_gram_overlap": ten_gram_overlap,
                    })

                    """
                    print(repo, gold_func.name)
                    print(gold_func.docstring)
                    print("GOLD BODY")
                    print(gb)
                    print("PRED BODY")
                    print(pb)
                    print("MATCH:", gb == pb)
                    """

    results = bleu.compute(predictions=predictions, references=references)
    print(results)
    print(f"Num exact matches: {exact_matches} / {num_f} total")
    output = json.dumps(data)
    with open("results.json", "w") as f:
        f.write(output)

if __name__ == "__main__":
    main()
