import pandas as pd
import json
import numpy as np
from tqdm import tqdm


filters = ["all", "Left-wing", "Center-left", "Neutral", "Public Broadcaster",
           "Gov't Institution", "Center-right", "Right-wing", "Pro-Government",
           "Gov't Propaganda", "Indeterminate"]


def remove_old_data():
    pass



def calculate_most_average_article(daily_df):
    """
    Helper function to calculate the most average article for a given period.
    """
    # Calculate mean sentiment probabilities
    mean_sentiments = daily_df[['negative_score', 'neutral_score', 'positive_score']].mean()

    # Compute Euclidean distance for each article
    daily_df["distance"] = daily_df.apply(
        lambda row: np.sqrt(
            (row["negative_score"] - mean_sentiments["negative_score"]) ** 2 +
            (row["neutral_score"] - mean_sentiments["neutral_score"]) ** 2 +
            (row["positive_score"] - mean_sentiments["positive_score"]) ** 2
        ),
        axis=1
    )

    # Find the article with the smallest distance
    most_average_article = daily_df.loc[daily_df["distance"].idxmin()]
    return most_average_article


def process_to_json(df: pd.DataFrame, group_by: str = 'date'):
    """
    Processes the DataFrame to calculate sentiment analysis and the most average article.

    Parameters:
    - df: DataFrame with article data
    - freq: Frequency for grouping ('D' for day, 'W' for week, 'M' for month)
    """
    # Group by the selected period (day, week, or month)
    df_by_period = df.groupby(group_by).agg(
        average_sentiment=("sentiment_sum", "mean"),
        row_count=("date", "count"),
        neutral_count=("sentiment_label", lambda x: (x == "neutral").sum()),
        positive_count=("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count=("sentiment_label", lambda x: (x == "negative").sum())
    )

    # Initialize the result JSON structure
    result_json_period = {}

    # Loop through each date/period and process the most average article
    for period, row in tqdm(df_by_period.iterrows(), total=len(df_by_period), desc=f"Processing {group_by}"):
        # Filter data for the current period
        period_df = df[df[group_by] == period].copy()

        # Calculate the most average article for the current period
        most_average_article = calculate_most_average_article(period_df)

        # Construct the result for this period
        result_json_period[str(period)] = {
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


def process_time_series(keyword: str):
    df = pd.read_csv("datasets/" + keyword + "_sentiment.csv", index_col=0)
    df = df.drop(columns=["title", "text", "ownership", "abstract"])
    sentiment_label_occur = df["sentiment_label"].value_counts()
    print(df["publisher"].value_counts())
    # most_common_label = sentiment_label_occur.idxmax()
    df["sentiment_sum"] = df["positive_score"] - df["negative_score"]

    output = {
        keyword: {}
    }

    for filter in filters:
        if filter == "all":
            df_filtered = df.copy()
        else:
            df_filtered = df[df["classification"] == filter].copy()

        df_filtered["date"] = pd.to_datetime(df["published_at"]).dt.date
        df_filtered["week"] = pd.to_datetime(df["published_at"]).dt.to_period("W").apply(lambda r: r.start_time.date())
        df_filtered["month"] = pd.to_datetime(df["published_at"]).dt.to_period("M").apply(lambda r: r.start_time.date())

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
    process_time_series("Honda CR-V")
