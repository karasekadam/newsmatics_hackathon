from json_data_processing import merge_all_time_series, extract_df, add_predictions
from process_sentiment_csv import remove_old_data, process_time_series
from download_articles import get_keyword_articles
from sentiment_analysis import run_sentiment_analysis


if __name__ == "__main__":
    # download data
    key_word = "prostejov"
    df = get_keyword_articles(key_word)
    df.to_csv(key_word + ".csv")

    # runs sentiment analysis
    run_sentiment_analysis(key_word)

    # process the downloaded articles with sentiments
    remove_old_data(f"datasets/{key_word}_sentiment.csv", 2017)
    process_time_series(key_word)

    # adds averages and predictions
    add_predictions(key_word)
    merge_all_time_series(True)
