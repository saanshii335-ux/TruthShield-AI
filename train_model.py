import pandas as pd
import pickle

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report

# Load datasets
fake = pd.read_csv("datasets/Fake.csv")
true = pd.read_csv("datasets/True.csv")

buzz_fake = pd.read_csv("datasets/BuzzFeed_fake_news_content.csv")
buzz_real = pd.read_csv("datasets/BuzzFeed_real_news_content.csv")

politifact_fake = pd.read_csv("datasets/PolitiFact_fake_news_content.csv")
politifact_real = pd.read_csv("datasets/PolitiFact_real_news_content.csv")


# Add labels
fake["label"] = 0
true["label"] = 1

buzz_fake["label"] = 0
buzz_real["label"] = 1

politifact_fake["label"] = 0
politifact_real["label"] = 1

fake = fake[["text", "label"]]
true = true[["text", "label"]]
buzz_fake = buzz_fake[["text", "label"]]
buzz_real = buzz_real[["text", "label"]]
politifact_fake = politifact_fake[["text", "label"]]
politifact_real = politifact_real[["text", "label"]]

# Combine datasets
df = pd.concat([fake, true, buzz_fake, buzz_real, politifact_fake, politifact_real],ignore_index=True)

# Keep only required columns
df = df[["text", "label"]]

# Drop missing values
df.dropna(inplace=True)

# Drop duplicates
df.drop_duplicates(inplace=True)

# Filter out short texts
df = df[df["text"].str.strip().str.len() > 20]

#after cleaning, print the number of samples and the distribution of labels
print("Total samples after cleaning:", len(df))
print(df["label"].value_counts())

# Features and labels
X = df["text"]
y = df["label"]

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Convert text to numerical features
vectorizer = TfidfVectorizer(stop_words="english")
X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# Train model
model = MultinomialNB()
model.fit(X_train_vec, y_train)

# Evaluate model
predictions = model.predict(X_test_vec)
accuracy = accuracy_score(y_test, predictions)
report = classification_report(y_test, predictions)

print("Model Accuracy:", round(accuracy * 100, 2), "%")
print("Classification Report:\n", report)

# Save model
pickle.dump(model, open("model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

print("Model saved successfully!")