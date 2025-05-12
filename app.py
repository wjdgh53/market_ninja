import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[
        logging.FileHandler("market_ninja.log"),
        logging.StreamHandler()
    ]
)

from flask import Flask
from routes.strategy_routes import strategy_bp
from routes.indicator_routes import indicator_bp
from routes.sentiment_routes import sentiment_bp
from routes.backtest_routes import backtest_bp
from routes.market_routes import market_bp  # 새로 추가

app = Flask(__name__)
app.register_blueprint(strategy_bp)
app.register_blueprint(indicator_bp)
app.register_blueprint(sentiment_bp)
app.register_blueprint(backtest_bp)
app.register_blueprint(market_bp)  # 새로 추가

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)