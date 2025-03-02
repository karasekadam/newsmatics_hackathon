import json

import numpy as np
import pandas as pd
import tqdm

filters = ["all", "Left-wing", "Center-left", "Neutral", "Public Broadcaster",
           "Gov't Institution", "Center-right", "Right-wing", "Pro-Government",
           "Gov't Propaganda", "Indeterminate"]


def remove_old_data(file_path: str, filter_year: int) -> None:
    """
    Filters out all articles older than filter_year
    :param file_path: path to the csv intended for filtering
    :param filter_year: year by which filter
    :return: None, replaces the filtered file
    """
    df = pd.read_csv(file_path, index_col=0)
    df['datetime'] = pd.to_datetime(df['published_at'], format='%Y-%m-%dT%H:%M:%SZ')
    filtered_df = df[df['datetime'].dt.year >= filter_year]
    filtered_df = filtered_df.drop(columns=['datetime'])
    print(f"original size: {len(df)}, reduced size: {len(filtered_df)}")
    filtered_df.to_csv(file_path)


def calculate_most_average_article(df: pd.DataFrame) -> pd.Series:
    """
    Calculates the article which is the closed by euclidian distance to tha mean of sentiments of all articles in
    specified time period.
    :param df: DataFrame with articles of the selected time period
    :return: Average article
    """
    # Calculate mean sentiment probabilities
    mean_sentiments = df[['negative_score', 'neutral_score', 'positive_score']].mean()

    # Compute Euclidean distance for each article
    df["distance"] = df.apply(
        lambda row: np.sqrt(
            (row["negative_score"] - mean_sentiments["negative_score"]) ** 2 +
            (row["neutral_score"] - mean_sentiments["neutral_score"]) ** 2 +
            (row["positive_score"] - mean_sentiments["positive_score"]) ** 2
        ),
        axis=1
    )

    # Find the article with the smallest distance
    most_average_article = df.loc[df["distance"].idxmin()]
    return most_average_article


def process_to_json(df: pd.DataFrame, group_by: str = 'date') -> dict[str, dict]:
    """
    Processes the tabular data of articles into aggregated data by time period.
    Parameters:
    :param df: DataFrame with article data
    :param group_by: Time period for grouping ('date' for day, 'week' for week, 'moth' for month)
    :return: Dictionary in format
        {
            "30.01.2017": {
            "avg_sentiment": 0.4175615757703781,
            "counts": 1,
            "neutral_count": 0,
            "positive_count": 1,
            "negative_count": 0,
            "most_average_article": {
                "url": "http://pulse.ng/bi/finance/elon-musk-businessman-really-isnt-as-aligned-with-trump-on-manufacturing-as-it-seems-id6135045.html",
                "sentiments": {
                    "negative_score": 0.1118781119585037,
                    "neutral_score": 0.3586821258068084,
                    "positive_score": 0.5294396877288818
                }
            }
        },
        "27.02.2017": {
            ...
        },
        ...
    """

    # Group by the selected period (day, week, or month)
    df_by_period = df.groupby(group_by).agg(
        average_sentiment=("sentiment_sum", "mean"),
        row_count=("date", "count"),
        neutral_count=("sentiment_label", lambda x: (x == "neutral").sum()),
        positive_count=("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count=("sentiment_label", lambda x: (x == "negative").sum())
    )

    result_json_period = {}

    # Loop through each time period, process the labels count, average sentiment and average article
    for period, row in tqdm(df_by_period.iterrows(), total=len(df_by_period), desc=f"Processing {group_by}"):
        # Filter data for the current period
        period_df = df[df[group_by] == period].copy()

        # Calculate the most average article for the current period
        most_average_article = calculate_most_average_article(period_df)

        # Construct the result for this period
        result_json_period[period.strftime('%d.%m.%Y')] = {
            "avg_sentiment": row["average_sentiment"],
            "counts": int(row["row_count"]),
            "neutral_count": int(row["neutral_count"]),
            "positive_count": int(row["positive_count"]),
            "negative_count": int(row["negative_count"]),
            "most_average_article": {
                "url": most_average_article["url"],  # Assuming the article has a "url" column
                "sentiments": {
                    "negative_score": most_average_article["negative_score"],
                    "neutral_score": most_average_article["neutral_score"],
                    "positive_score": most_average_article["positive_score"]
                }
            }
        }

    return result_json_period


def process_time_series(keyword: str) -> None:
    """
    Calculates aggregated data for each time period and and transforms it to json.
    :param keyword: Analyzed keyword
    :return: None, saves json file
    """
    # load csv file with articles and sentiments
    df = pd.read_csv("datasets/" + keyword + "_sentiment.csv", index_col=0)
    df = df.drop(columns=["title", "text", "ownership", "abstract"])

    # calculate sentiment difference
    df["sentiment_sum"] = df["positive_score"] - df["negative_score"]

    output = {
        keyword: {}
    }

    for filter in filters:
        if filter == "all":
            df_filtered = df.copy()
        else:
            df_filtered = df[df["classification"] == filter].copy()

        # calculate time periods
        df_filtered["date"] = pd.to_datetime(df["published_at"]).dt.date
        df_filtered["week"] = pd.to_datetime(df["published_at"]).dt.to_period("W").apply(lambda r: r.start_time.date())
        df_filtered["month"] = pd.to_datetime(df["published_at"]).dt.to_period("M").apply(lambda r: r.start_time.date())

        # transform dataframes to jsons
        filtered_json_day = process_to_json(df_filtered, group_by='date')  # Day-wise
        filtered_json_week = process_to_json(df_filtered, group_by='week')  # Week-wise
        filtered_json_month = process_to_json(df_filtered, group_by='month')  # Month-wise

        output[keyword][filter] = {
                "day": filtered_json_day,
                "week": filtered_json_week,
                "month": filtered_json_month,
            }

    with open("time_series/" + keyword + ".json", "w") as f:
        json.dump(output, f, indent=2)


if __name__ == '__main__':
    remove_old_data("datasets/boeing_sentiment.csv", 2017)
    process_time_series("boeing")

