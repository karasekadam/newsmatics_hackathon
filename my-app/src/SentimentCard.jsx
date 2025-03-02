import React from "react";
import "./SentimentCard.css";

const SentimentCard = ({data}) => {
    console.log("sentimentcard", data);
    return (
        <div className="sentiment-card-container">
            <div className="sentiment-card">
                <div className="card-header">
                    <h2>{data.str_date}</h2>
                </div>
                <div className="card-body">
                    <p>
                        <a href={data.most_average_article.url}><strong>Representative
                            article</strong>{" "}</a>
                    </p>
                    <p>
                        <strong>Average Sentiment:</strong>{" "}
                        {data.moving_average_sentiment.toFixed(3)}
                    </p>
                    <p>
                        <strong>Total Count:</strong> {data.counts}
                    </p>
                    <div className="counts">
                        <p>
                            <strong>Positive:</strong> {data.positive_count}
                        </p>
                        <p>
                            <strong>Neutral:</strong> {data.neutral_count}
                        </p>
                        <p>
                            <strong>Negative:</strong> {data.negative_count}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default SentimentCard;
