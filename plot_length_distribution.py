import json
import pandas as pd
import altair as alt
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
            'match': 'Match' if item['body'] == item['pred_body'] else 'No Match'
        })
    return pd.DataFrame(processed_data)

def plot_distribution(df):
    for repo in df['repo'].unique():
        repo_df = df[df['repo'] == repo]
        
        base = alt.Chart(repo_df).mark_area(
            opacity=0.5,
            interpolate='step'
        ).encode(
            alt.X('body_length:Q', bin=alt.Bin(maxbins=30), title='Body Length'),
            alt.Y('count():Q', stack=None, title='Count'),
            alt.Color('match:N', legend=alt.Legend(title='Match'))
        ).properties(
            title=f'Distribution of Function Body Length for {repo}',
            width=500,
            height=300
        )

        chart = base.encode(
            alt.X('body_length:Q', bin=alt.Bin(maxbins=30), title='Length (tokens)')
        )

        chart.save(f'plots/length_distribution_{repo}.pdf')

def main():
    # Load the Sonnet tokenizer
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-3.1-70B-Instruct")

    # Load and process the data
    data = load_data('results.json')
    df = process_data(data, tokenizer)

    # Plot the distribution
    plot_distribution(df)

    print("Plots saved as length_distribution_<repo>.pdf for each repo")

if __name__ == "__main__":
    main()

