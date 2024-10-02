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
    chart = alt.Chart(df).mark_boxplot().encode(
        x='repo:N',
        y='body_length:Q',
        color='match:N',
        column='match:N'
    ).properties(
        title='Distribution of Body Length by Repo and Match Status',
        width=400,
        height=300
    ).configure_axis(
        labelAngle=45
    )

    chart.save('length_distribution.html')

def main():
    # Load the Sonnet tokenizer
    tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large")

    # Load and process the data
    data = load_data('results.json')
    df = process_data(data, tokenizer)

    # Plot the distribution
    plot_distribution(df)

    print("Plot saved as length_distribution.html")

if __name__ == "__main__":
    main()
