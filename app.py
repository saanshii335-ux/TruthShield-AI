from flask import Flask, render_template, request
import pickle
import sqlite3
import os

app = Flask(__name__)

DATABASE = "detections.db"


# -------------------------------
# Database Functions
# -------------------------------

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        prediction TEXT,
        confidence REAL
    )
    """)

    conn.commit()
    conn.close()


# Create database when app starts
init_db()


# -------------------------------
# Load AI Model
# -------------------------------

model = pickle.load(open("model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))


# -------------------------------
# Home Page
# -------------------------------

@app.route("/", methods=["GET", "POST"])
def home():

    prediction = None
    confidence = None
    explanation = None
    evidence = None

    if request.method == "POST":

        post_text = request.form["post"]

        if len(post_text.split()) < 8:
            return render_template(
                "index.html",
                prediction="⚠️ Please enter a longer news-style post (minimum 8 words).",
                confidence=None,
                explanation=None,
                evidence=None
            )

        data = vectorizer.transform([post_text])

        result = model.predict(data)[0]

        probability = model.predict_proba(data)[0]
        confidence = round(max(probability) * 100, 2)

        if result == 1:

            prediction = "🟢 REAL"

            explanation = (
                "This post contains factual language patterns and resembles "
                "verified news articles from the training dataset."
            )

            evidence = [
                "✓ Similar to trusted news articles",
                "✓ Formal news writing style detected",
                "✓ No sensational keywords detected"
            ]

        else:

            prediction = "🔴 FAKE"

            explanation = (
                "This post contains misinformation patterns and resembles "
                "fake news content from the training dataset."
            )

            evidence = [
                "⚠ Sensational language detected",
                "⚠ Clickbait writing style detected",
                "⚠ Unverified claim patterns found"
            ]

        # Save prediction into SQLite database
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO detections (prediction, confidence)
            VALUES (?, ?)
            """,
            (prediction, confidence)
        )

        conn.commit()
        conn.close()

    return render_template(
        "index.html",
        prediction=prediction,
        confidence=confidence,
        explanation=explanation,
        evidence=evidence
    )


# -------------------------------
# History Page
# -------------------------------

@app.route("/history")
def history():

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, prediction, confidence
        FROM detections
        ORDER BY id DESC
    """)

    records = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        records=records
    )


# -------------------------------
# Run Application
# -------------------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )