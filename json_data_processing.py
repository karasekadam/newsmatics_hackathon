import datetime
import json
import os

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

filters = ["all", "Left-wing", "Center-left", "Neutral", "Public Broadcaster",
           "Gov't Institution", "Center-right", "Right-wing", "Pro-Government",
           "Gov't Propaganda", "Indeterminate"]


def merge_all_time_series(prediction: bool = False) -> None:
    """
    Merges time series of particular keywords into one merged json.
    :param prediction: Merge time series with predictions or without?
    :return: None
    """
    merged_json = {}

    for json_file in os.listdir("time_series/"):
        if ("_predictions" in json_file) != prediction:
            continue

        print(json_file)
        with open(f"time_series/{json_file}") as f:
            json_content = json.load(f)
            key_word = list(json_content.keys())[0]
            merged_json[key_word] = json_content[key_word]

    with open("merged.json", "w") as f:
        json.dump(merged_json, f)


def extract_df(data: dict, timeframe: str, filter: str) -> pd.DataFrame:
    """
    Transforms the data in json format into csv tabular format
    :param data: json time series
    :param timeframe: day/week/month
    :param filter: possible filters
    :return: DataFrame
    """
    rows = []

    for category, time_data in data.items():  # Iterate over categories (e.g., Tesla Model Y)
        for date, details in time_data[filter][timeframe].items():
            row = {
                "category": category,
                "date": date,
                "avg_sentiment": details.get("avg_sentiment", None),
                "counts": details.get("counts", None),
                "neutral_count": details.get("neutral_count", None),
                "positive_count": details.get("positive_count", None),
                "negative_count": details.get("negative_count", None),
                "article_url": details.get("most_average_article", {}).get("url", None),
                "neg_score": details.get("most_average_article", {}).get("sentiments", {}).get("negative_score", None),
                "neu_score": details.get("most_average_article", {}).get("sentiments", {}).get("neutral_score", None),
                "pos_score": details.get("most_average_article", {}).get("sentiments", {}).get("positive_score", None),
            }
            rows.append(row)

    return pd.DataFrame(rows)


def arma(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates from input df moving averages of sentiment and runs predictions
    :param df:
    :return: input df + predictions and averages
    """
    df = df.copy()

    df['moving_average'] = df['avg_sentiment'].rolling(window=3, min_periods=1).mean()

    df['moving_average_10'] = df['avg_sentiment'].rolling(window=10, min_periods=1).mean()
    df['moving_average_20'] = df['avg_sentiment'].rolling(window=20, min_periods=1).mean()

    df['diff_sentiment'] = df['moving_average'].diff().dropna()

    # Predikce

    model = ARIMA(df['diff_sentiment'].dropna(),
                  order=(2, 0, 0))  # ARMA(1, 2) has order=(p, d, q), d=0 for no differencing
    model_fit = model.fit()

    # Step 4: Forecast the next 3 values (in the differenced form)
    forecast_diff = model_fit.forecast(steps=3)  # Forecast all 3 steps at once

    # --------------------------------------------------------------------------------------
    # Extend

    # Extend df_day by 3 more lines with forecasted values
    last_date = df['date'].iloc[-1]

    for i in range(1, 4):
        new_date = datetime.datetime.strptime(last_date, '%d.%m.%Y') + pd.DateOffset(days=i)
        new_row = pd.DataFrame({
            'category': [df['category'].iloc[-1]],
            'date': [new_date],
            'avg_sentiment': [np.nan],
            'counts': [np.nan],  # Fill with NaN or appropriate values
            'neutral_count': [np.nan],
            'positive_count': [np.nan],
            'negative_count': [np.nan],
            'article_url': [np.nan],
            'neg_score': [np.nan],
            'neu_score': [np.nan],
            'pos_score': [np.nan],
            'diff_sentiment': [np.nan],
            'moving_average': [np.nan]

        })
        df = pd.concat([df, new_row], ignore_index=True)

    # --------------------------------------------------
    # Imput pred

    df['avg_sentiment_pred'] = df['moving_average']

    df.loc[df.index[-3], 'avg_sentiment_pred'] = df['avg_sentiment_pred'].iloc[-4] + forecast_diff.iloc[0]
    df.loc[df.index[-2], 'avg_sentiment_pred'] = df['avg_sentiment_pred'].iloc[-3] + forecast_diff.iloc[1]
    df.loc[df.index[-1], 'avg_sentiment_pred'] = df['avg_sentiment_pred'].iloc[-2] + forecast_diff.iloc[2]

    return df


def add_predictions(key_word: str) -> None:
    """
    For each filter and time period calculates moving averages of sentiment and runs arma predictions.
    :param key_word: analyzed keyword
    :return: None, saves into file keyword + "_predictions.json"
    """
    with open("time_series/" + key_word + ".json", "r") as f:
        json_data = json.load(f)

    result = {key_word: {}}
    for filter in filters:
        if filter not in result[key_word]:
            result[key_word][filter] = {}

        for timeframe in ["day", "week", "month"]:
            df = extract_df(json_data, timeframe=timeframe, filter=filter)
            prediction_df = arma(df)
            prediction_df.fillna("None", inplace=True)

            if timeframe not in result[key_word][filter]:
                result[key_word][filter][timeframe] = {}

            for _, row in prediction_df.iterrows():
                date = str(row['date'])

                result[key_word][filter][timeframe][date] = {
                    'avg_sentiment': row['avg_sentiment'],
                    'counts': row['counts'],
                    'neutral_count': row['neutral_count'],
                    'positive_count': row['positive_count'],
                    'negative_count': row['negative_count'],
                    'moving_average_sentiment': row['moving_average'],
                    'moving_average_sentiment_10': row['moving_average_10'],
                    'moving_average_sentiment_20': row['moving_average_20'],
                    'most_average_article': {
                        "url": row["article_url"],
                        "negative_score": row['neg_score'],
                        "neutral_score": row['neu_score'],
                        "positive_score": row['pos_score'],
                    }
                }

    with open("time_series/" + key_word + "_predictions.json", "w") as f:
        json.dump(result, f)


if __name__ == '__main__':
    add_predictions("boeing")
    merge_all_time_series(True)
