import time

import pandas as pd
import requests

headers = {
    "Authorization": "Bearer ", # include your token here
    "Accept": "application/json"
  }


def api_request(request_url: str):
  url_base = "https://www.newsmatics.com/news-index"
  url = url_base + request_url

  response = requests.get(url, headers=headers)
  return response.json()


def get_keyword_articles(keyword: str) -> pd.DataFrame:
  articles = []

  first_url = f"https://www.newsmatics.com/news-index/api/v1/articles?&page%5Bsize%5D=1000&filter%5Bquery%5D={keyword}&include-ownership=1&include-text=1"

  response = requests.get(first_url, headers=headers).json()
  next_url = response["pagination"]["next"] if "next" in response["pagination"] else None
  articles.extend(response["articles"])

  while next_url is not None:
    print(next_url)
    time.sleep(0.1)
    next_url = next_url + "&include-ownership=1&include-text=1"
    response = api_request(next_url)
    articles.extend(response["articles"])
    next_url = response["pagination"].get("next", None)

  return pd.DataFrame(articles)


if __name__ == "__main__":
    key_word = "boeing"
    df = get_keyword_articles(key_word)
    df.to_csv(key_word + ".csv")
