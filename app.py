from flask import Flask
from routes.strategy_routes import strategy_bp
from routes.indicator_routes import indicator_bp
from routes.sentiment_routes import sentiment_bp
from routes.backtest_routes import backtest_bp

app = Flask(__name__)
app.register_blueprint(strategy_bp)
app.register_blueprint(indicator_bp)
app.register_blueprint(sentiment_bp)
app.register_blueprint(backtest_bp)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050, debug=True)