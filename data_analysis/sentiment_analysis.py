import pandas as pd
import torch
from tqdm import tqdm
from transformers import AutoModelForSequenceClassification, AutoTokenizer

torch.cuda.empty_cache()

# make python show tqdm progress bar
tqdm.pandas()

# check gpu availability
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

def analyze_aspect_sentiment(article: str, aspect: str, tokenizer, model) -> tuple[str, float, float, float]:
    """
    Predicts the sentiment of a word or phrase in a given context - article.
    :param article: Analyzed article
    :param aspect: Keyword for which we measure the sentiment
    :param tokenizer: Used loaded tokenizer
    :param model: Used loaded model
    :return: Tuple of predicted sentiment label and probability for each sentiment label in order "negative",
    "neutral", "positive"
    """
    # Format the input with aspect
    aspect_article = f"{article} [ASP] {aspect}"

    # Tokenize input
    inputs = tokenizer(aspect_article, return_tensors="pt", padding=True, truncation=True).to(device)

    # Perform inference
    with torch.no_grad():
        outputs = model(**inputs)

    # Get sentiment prediction
    predictions = torch.argmax(outputs.logits, dim=-1).item()
    predictions_softmax = torch.softmax(outputs.logits, dim=-1).tolist()[0]

    # Map predictions to sentiment labels
    sentiment_labels = ["negative", "neutral", "positive"]
    return sentiment_labels[predictions], predictions_softmax[0], predictions_softmax[1], predictions_softmax[2]


def give_sentiment_aspect(df: pd.DataFrame, aspect: str, tokenizer, model) -> pd.DataFrame:
    """
    Processes all downloaded articles to include sentiment analysis
    :param df: Dataframe of downloaded articles.
    :param aspect: Analyzed key word
    :param tokenizer: Used loaded tokenizer
    :param model: Used loaded model
    :return: Dataframe of articles with columns for sentiment analysis
    """
    # option for reducing the size of huge datasets
    # df = df.copy().sample(frac=0.5).reset_index(drop=True)
    # Filters out large texts for performance reasons
    df = df[df['text'].str.len() <= 10000]

    df.loc[:, ["sentiment_label", "negative_score", "neutral_score", "positive_score"]] = df["text"].progress_apply(
        lambda x: pd.Series(analyze_aspect_sentiment(x, aspect, tokenizer, model))
    ).values

    df = df[df["sentiment_label"].notnull()]

    return df.copy()


def run_sentiment_analysis(key_word: str):
    # Load model and tokenizer
    model_name = "yangheng/deberta-v3-base-absa-v1.1"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name).to(device)

    # load articles
    df = pd.read_csv(key_word + ".csv")

    df_sentiment = give_sentiment_aspect(df, key_word, tokenizer, model)
    df_sentiment = df_sentiment.dropna()
    df_sentiment.to_csv(key_word + "_sentiment.csv")

    print(df_sentiment.head(4))


if __name__ == "__main__":
    run_sentiment_analysis("boeing")