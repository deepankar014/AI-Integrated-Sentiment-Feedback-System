from flask import Flask, render_template, request
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from scipy.special import softmax

app = Flask(__name__)

# Load model & tokenizer once
MODEL = "cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL)
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    comments = request.form['comments'].split("\n")
    results = []
    counts = {"positive": 0, "negative": 0, "neutral": 0}

    for sentence in comments:
        if sentence.strip():  # skip empty lines
            encoded = tokenizer(sentence, return_tensors='pt', truncation=True, padding=True)
            output = model(**encoded)
            scores = softmax(output.logits[0].detach().numpy())
            pred_idx = scores.argmax()
            sentiment = ['negative', 'neutral', 'positive'][pred_idx]
            confidence = float(scores[pred_idx])

            results.append({
                "comment": sentence,
                "sentiment": sentiment,
                "confidence": round(confidence, 2)
            })
            counts[sentiment] += 1

    # Convert counts to percentages
    total = sum(counts.values())
    percentages = {k: round(v/total*100, 2) for k, v in counts.items()}

    return render_template("results.html", results=results, counts=percentages)

if __name__ == "__main__":
    app.run(debug=True) 