from flask import Flask, request, jsonify
from openai import OpenAI
import os
import traceback
from indicator import analyze_technical

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

@app.route("/indicator", methods=["POST"])
def indicator():
    data = request.get_json()
    symbol = data.get("symbol")

    if not symbol:
        return jsonify({"error": "Missing 'symbol' field"}), 400

    try:
        result = analyze_technical(symbol)
        if "error" in result:
            return jsonify({"error": result["error"]}), 400
        return jsonify(result)
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()

    symbol = data.get("symbol")
    content = data.get("content")
    title = data.get("title")
    link = data.get("link")
    source = data.get("source")
    pub_date = data.get("pub_date")

    if not content:
        return jsonify({"error": "Missing 'content' field"}), 400

    prompt = f"다음 뉴스 기사에 대해 감성 점수를 0~1 사이의 숫자로 매겨줘. 숫자만 정확히 반환해:\n\n{title}\n\n{content}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        score = float(response.choices[0].message.content.strip())
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return jsonify({
        "symbol": symbol,
        "title": title,
        "content": content,
        "link": link,
        "source": source,
        "pub_date": pub_date,
        "sentiment": score
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5050)