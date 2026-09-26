import os
import json
import time
from datasets import load_dataset
from groq import Groq
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

# 1. Load the Hugging Face Dataset
print("Loading dataset...")
# Make sure to keep your token here!
dataset = load_dataset("jason23322/high-accuracy-email-classifier", split="test", token="HF_TOKEN")

# 2. Stratified Sampling (Get 20 emails per category)
# FIXED: Using the exact lowercase/underscore format found in the dataset backend
dataset_categories = ["forum", "promotions", "social_media", "spam", "updates", "verify_code"]
sampled_emails = []

for category in dataset_categories:
    # Filter the dataset by the current category and take the first 20
    category_subset = dataset.filter(lambda example: example['category'] == category).select(range(20))
    for email in category_subset:
        sampled_emails.append(email)

print(f"Loaded {len(sampled_emails)} emails for testing.")

# 3. Define the LLM Evaluation Function
def classify_with_llm(subject, body):
    prompt = f"""
    You are an email classifier. Read the email below and classify it into EXACTLY ONE of the following categories:
    forum, promotions, social_media, spam, updates, verify_code.
    
    Respond with ONLY the exact category name. Do not add any other text, punctuation, or explanation.
    For example if the category you clasified the email is "forum", DO NOT write "Category:forum" Or "Forum" with a capital letter
    JUST WRITE THE CATEGORY "forum" nothing more.
    
    Subject: {subject}
    Body: {body}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
            temperature=0, # Temperature 0 ensures the most deterministic/logical answer
            max_tokens=10
        )
        return response.choices[0].message.content.strip().lower()
    except Exception as e:
        print(f"API Error: {e}")
        return "Error"

# 4. Run the Pipeline
expected_labels = []
predicted_labels = []

print("Starting LLM classification... (This may take a few minutes)")
for index, email in enumerate(sampled_emails):
    print(f"Processing {index + 1}/{len(sampled_emails)}...")
    
    true_label = email['category'].lower()
    predicted_label = classify_with_llm(email['subject'], email['body'])
    
    expected_labels.append(true_label)
    
    # Clean up the output just in case the LLM added a period or extra space
    clean_prediction = predicted_label.replace(".", "").strip()
    predicted_labels.append(clean_prediction)

    time.sleep(1.5)

# 5. Calculate and Print the Results
print("\n" + "="*50)
print("EVALUATION RESULTS")
print("="*50)

# Accuracy
accuracy = accuracy_score(expected_labels, predicted_labels)
print(f"Overall Accuracy: {accuracy * 100:.2f}%\n")

# Precision, Recall, and F1-Score
print("Classification Report:")
print(classification_report(expected_labels, predicted_labels, labels=dataset_categories))

# Confusion Matrix
print("Confusion Matrix:")
print(confusion_matrix(expected_labels, predicted_labels, labels=dataset_categories))