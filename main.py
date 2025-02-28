import pandas as pd
import json
import numpy as np
from tqdm import tqdm


filters = ["all", "Left-wing", "Center-left", "Neutral", "Public Broadcaster",
           "Gov't Institution", "Center-right", "Right-wing", "Pro-Government",
           "Gov't Propaganda", "Indeterminate"]


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


def process_to_json(df: pd.DataFrame, freq: str = 'D'):
    """
    Processes the DataFrame to calculate sentiment analysis and the most average article.

    Parameters:
    - df: DataFrame with article data
    - freq: Frequency for grouping ('D' for day, 'W' for week, 'M' for month)
    """
    df["date"] = pd.to_datetime(df["published_at"]).dt.date

    # Group by the specified frequency (day, week, month)
    df["group"] = df["date"].apply(
        lambda x: x.strftime('%Y-%m-%d') if freq == 'D' else x.to_period(freq).strftime('%Y-%m-%d'))

    # Group by the selected period (day, week, or month)
    df_by_period = df.groupby("group").agg(
        average_sentiment=("sentiment_sum", "mean"),
        row_count=("date", "count"),
        neutral_count=("sentiment_label", lambda x: (x == "neutral").sum()),
        positive_count=("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count=("sentiment_label", lambda x: (x == "negative").sum())
    )

    # Initialize the result JSON structure
    result_json_period = {}

    # Loop through each date/period and process the most average article
    for period, row in tqdm(df_by_period.iterrows(), total=len(df_by_period), desc=f"Processing {freq}"):
        # Filter data for the current period
        period_df = df[df["group"] == period].copy()

        # Calculate the most average article for the current period
        most_average_article = calculate_most_average_article(period_df)

        # Construct the result for this period
        result_json_period[period] = {
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


def process_to_json_2(grouped_df: pd.DataFrame, full_df: pd.DataFrame):
    """df["date"] = pd.to_datetime(df["published_at"]).dt.date

    # Group by Day
    df_by_day = df.groupby("date").agg(
        average_sentiment=("sentiment_sum", "mean"),
        row_count=("date", "count"),
        neutral_count=("sentiment_label", lambda x: (x == "neutral").sum()),
        positive_count=("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count=("sentiment_label", lambda x: (x == "negative").sum())
    )"""

    # Initialize the result JSON structure
    result_json_day = {}

    # Loop through each date and process the most average article
    for date, row in tqdm(grouped_df.iterrows(), total=len(grouped_df), desc="Processing days"):
        daily_df = full_df[full_df["date"] == date].copy()

        # Calculate mean sentiment probabilities for the day
        mean_sentiments = daily_df[['negative_score', 'neutral_score', 'positive_score']].mean()

        # Compute Euclidean distance for each article
        daily_df["distance"] = daily_df.apply(
            lambda row: np.sqrt(
                (row["negative_score"] - mean_sentiments["negative_score"])**2 +
                (row["neutral_score"] - mean_sentiments["neutral_score"])**2 +
                (row["positive_score"] - mean_sentiments["positive_score"])**2
            ),
            axis=1
        )

        # Find the article with the smallest distance
        most_average_article = daily_df.loc[daily_df["distance"].idxmin()]

        # Construct the result for this day
        result_json_day[date.strftime("%d.%m.%Y")] = {
            "avg_sentiment": row["average_sentiment"],
            "counts": int(row["row_count"]),
            "neutral_count": int(row["neutral_count"]),
            "positive_count": int(row["positive_count"]),
            "negative_count": int(row["negative_count"]),
            "most_average_article": {
                "url": most_average_article["url"],
                "sentiments": {
                    "negative_score": most_average_article["negative_score"],
                    "neutral_score": most_average_article["neutral_score"],
                    "positive_score": most_average_article["positive_score"]
                }
            }
        }

    return result_json_day


def process_to_json_3(df: pd.DataFrame):
    df["date"] = pd.to_datetime(df["published_at"]).dt.date
    df["week"] = pd.to_datetime(df["published_at"]).dt.to_period("W").apply(lambda r: r.start_time.date())
    df["month"] = pd.to_datetime(df["published_at"]).dt.to_period("M").apply(lambda r: r.start_time.date())

    # Group by Day
    df_by_day = df.groupby("date").agg(
        average_sentiment=("sentiment_sum", "mean"),
        row_count=("date", "count"),
        neutral_count=("sentiment_label", lambda x: (x == "neutral").sum()),
        positive_count=("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count=("sentiment_label", lambda x: (x == "negative").sum())
    )

    result_json_day = process_to_json_2(df_by_day, df)

    # Group by Week
    df_by_week = df.groupby("week").agg(
        average_sentiment=("sentiment_sum", "mean"),
        row_count=("week", "count"),
        neutral_count=("sentiment_label", lambda x: (x == "neutral").sum()),
        positive_count=("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count=("sentiment_label", lambda x: (x == "negative").sum())
    )

    # Group by Month
    df_by_month = df.groupby("month").agg(
        average_sentiment=("sentiment_sum", "mean"),
        row_count=("month", "count"),
        neutral_count=("sentiment_label", lambda x: (x == "neutral").sum()),
        positive_count=("sentiment_label", lambda x: (x == "positive").sum()),
        negative_count=("sentiment_label", lambda x: (x == "negative").sum())
    )

    result_json_day = {
        date.strftime("%d.%m.%Y"): {
            "avg_sentiment": row["average_sentiment"],
            "counts": int(row["row_count"]),
            "neutral_count": int(row["neutral_count"]),
            "positive_count": int(row["positive_count"]),
            "negative_count": int(row["negative_count"]),
        }
        for date, row in df_by_day.iterrows()
    }

    result_json_week = {
        date.strftime("%d.%m.%Y"): {
            "avg_sentiment": row["average_sentiment"],
            "counts": int(row["row_count"]),
            "neutral_count": int(row["neutral_count"]),
            "positive_count": int(row["positive_count"]),
            "negative_count": int(row["negative_count"]),
        }
        for date, row in df_by_week.iterrows()
    }

    result_json_month = {
        date.strftime("%m.%Y"): {
            "avg_sentiment": row["average_sentiment"],
            "counts": int(row["row_count"]),
            "neutral_count": int(row["neutral_count"]),
            "positive_count": int(row["positive_count"]),
            "negative_count": int(row["negative_count"]),
        }
        for date, row in df_by_month.iterrows()
    }

    return result_json_day, result_json_week, result_json_month


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

        # process_to_json_2(df_filtered)
        # filtered_json_day, filtered_json_week, filtered_json_month = process_to_json(df_filtered)
        filtered_json_day = process_to_json(df_filtered, freq='D')  # Day-wise
        filtered_json_week = process_to_json(df_filtered, freq='W')  # Week-wise
        filtered_json_month = process_to_json(df_filtered, freq='M')  # Month-wise

        output[keyword] = {
            filter: {
                "day": filtered_json_day,
                "week": filtered_json_week,
                "month": filtered_json_month,
            }
        }

    with open("time_series/" + keyword + ".json", "w") as f:
        json.dump(output, f, indent=2)



if __name__ == '__main__':
    process_time_series("Tesla Model Y")
