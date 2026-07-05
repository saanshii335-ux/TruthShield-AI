from flask import Flask, render_template, request
import pickle
import sqlite3
import os
import easyocr
from werkzeug.utils import secure_filename
import re


DATABASE = "detections.db"
UPLOAD_FOLDER = "uploads"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
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

reader = None

# -------------------------------
# Home Page
# -------------------------------


@app.route("/", methods=["GET", "POST"])
def home():

    prediction = None
    confidence = None
    explanation = None
    evidence = None
    ocr_text = None 

    if request.method == "POST":
        post_text = request.form.get("post", "").strip()
        post_text = clean_ocr_text(post_text)
        image = request.files.get("image")
        
        #If an image is uploaded, extract text using OCR
        if image and image.filename != "":
            
            filename = secure_filename(image.filename)
            image_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            
            # Save the uploaded image to the uploads folder
            image.save(image_path)
            
            ocr_text = extract_text_from_image(image_path)
            ocr_text = clean_ocr_text(ocr_text)
            post_text = ocr_text  # Use the extracted text for prediction

        if not post_text:
            return render_template(
                "index.html",
                prediction="⚠️ Please enter text or upload an image.",
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
        else:
            prediction = "🔴 FAKE" 
        # Generate a dynamic explanation and evidence
        explanation, evidence = generate_explanation(post_text, prediction)

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
        evidence=evidence,
        ocr_text=ocr_text
    )


def extract_text_from_image(image_path):
    global reader
    if reader is None:
        reader = easyocr.Reader(['en'])
    result = reader.readtext(image_path)
    extracted_text = " ".join([item[1] for item in result])
    return extracted_text      
def clean_ocr_text(text):

    # Remove URLs
    text = re.sub(r"http\S+|www\S+", "", text)

    # Remove hashtags
    text = re.sub(r"#\w+", "", text)

    # Remove usernames
    text = re.sub(r"@\w+", "", text)

    # Remove like/comment/share counts
    text = re.sub(r"\b\d+(\.\d+)?[KMB]?\b", "", text)

    # Remove time indicators
    text = re.sub(
        r"\b\d+\s*(second|seconds|minute|minutes|hour|hours|day|days|week|weeks|month|months|year|years)\s+ago\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove emojis and symbols
    text = re.sub(r"[^\w\s.,!?-]", " ", text)

    # Remove extra spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text

def generate_explanation(post_text, prediction):

    text = post_text.lower()

    explanation_parts = []
    evidence = []

    official_sources = [
        "ministry", "government", "police", "who", "un",
        "health", "department", "official", "president",
        "parliament", "hospital", "unicef"
    ]

    clickbait_words = [
        "breaking", "shocking", "secret", "viral",
        "must share", "share now", "forward this",
        "100%", "guaranteed", "miracle"
    ]

    medical_claims = [
        "cure", "cures", "treat", "vaccine",
        "medicine", "cancer", "covid"
    ]

    # -------------------------------
    # Official organization detection
    # -------------------------------
    found_sources = [word for word in official_sources if word in text]

    if found_sources:
        evidence.append("✓ Mentions official organization(s): " +
                        ", ".join(found_sources[:3]))
        explanation_parts.append(
            "The content references recognized organizations or institutions."
        )
    else:
        evidence.append("⚠ No official organization mentioned.")
        explanation_parts.append(
            "No identifiable official organization is referenced."
        )

    # -------------------------------
    # Clickbait detection
    # -------------------------------
    found_clickbait = [word for word in clickbait_words if word in text]

    if found_clickbait:
        evidence.append("⚠ Clickbait language detected.")
        explanation_parts.append(
            "The post contains sensational or attention-grabbing wording."
        )
    else:
        evidence.append("✓ No obvious clickbait language detected.")
        explanation_parts.append(
            "The writing style is generally neutral."
        )

    # -------------------------------
    # Medical misinformation
    # -------------------------------
    found_medical = [word for word in medical_claims if word in text]

    if found_medical:
        evidence.append("⚠ Contains medical-related claims.")
        explanation_parts.append(
            "Medical statements should always be verified with trusted health authorities."
        )

    # -------------------------------
    # Numbers and dates
    # -------------------------------
    if re.search(r"\d", text):
        evidence.append("✓ Contains numbers or dates.")
        explanation_parts.append(
            "The post includes measurable information such as numbers or dates."
        )

    # -------------------------------
    # Prediction-based conclusion
    # -------------------------------
    if "REAL" in prediction:

        explanation = (
            " ".join(explanation_parts) +
            " Overall, the writing style and content are more consistent "
            "with legitimate news articles, although users should always "
            "verify important information using trusted news sources."
        )

    else:

        explanation = (
            " ".join(explanation_parts) +
            " Overall, the content contains characteristics that are "
            "commonly associated with misinformation or misleading posts. "
            "Users should verify the claim before sharing it."
        )

    return explanation, evidence
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