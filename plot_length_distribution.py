import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from transformers import AutoTokenizer

def load_data(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)

def tokenize_text(text, tokenizer):
    return len(tokenizer.encode(text))

def process_data(data, tokenizer):
    processed_data = []
    for item in data:
        processed_data.append({
            'repo': item['repo'],
            'body_length': tokenize_text(item['body'], tokenizer),
            'pred_body_length': tokenize_text(item['pred_body'], tokenizer),
            'match': item['body'] == item['pred_body']
        })
    return pd.DataFrame(processed_data)

def plot_distribution(df):
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='repo', y='body_length', hue='match', data=df)
    plt.title('Distribution of Body Length by Repo and Match Status')
    plt.xlabel('Repository')
    plt.ylabel('Body Length (tokens)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('length_distribution.png')
    plt.close()

def main():
    # Load the Sonnet tokenizer
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large")

    # Load and process the data
    data = load_data('results.json')
    df = process_data(data, tokenizer)

    # Plot the distribution
    plot_distribution(df)

    print("Plot saved as length_distribution.png")

if __name__ == "__main__":
    main()
