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
dataset = load_dataset("jason23322/high-accuracy-email-classifier", split="test", token=os.environ.get("HF_TOKEN"))

# 2. Stratified Sampling (Get 30 emails per category)
dataset_categories = ["forum", "promotions", "social_media", "spam", "updates", "verify_code"]
sampled_emails = []

for category in dataset_categories:
    # Filter the dataset by the current category and take the first 30
    category_subset = dataset.filter(lambda example: example['category'] == category).shuffle().select(range(30))
    for email in category_subset:
        sampled_emails.append(email)

print(f"Loaded {len(sampled_emails)} emails for testing.")

# 3. Define the LLM Evaluation Function
def classify_with_llm(subject, body):
    prompt = f"""
    You are an email classifier. Read the email below and classify it into EXACTLY ONE of the following categories:
    forum, promotions, social_media, spam, updates, verify_code.

    CRITICAL DEFINITIONS:
    - "forum": This category classifies automated communications, discussion threads,
     and administrative notifications originating from community-driven platforms and online message boards. (even if they look like system updates).

    - "promotions": This category designates commercially driven correspondences, encompassing marketing campaigns,
     sales advertisements, and promotional offers intended to stimulate consumer engagement.

    - "social_media": This category isolates automated alerts and engagement notifications generated specifically
     by social networking platforms regarding user-centric account activity.

    - "spam": This category identifies highly unsolicited, deceptive, or malicious communications, specifically targeting phishing attempts,
     fraudulent prize schemes, and unauthorized mass mailings.

    - "updates": This category is strictly reserved for operational and technical communications, 
     including automated system alerts, software security patches, and routine service maintenance notices.

    - "verify_code": This category exclusively captures identity and access management emails that facilitate user authentication,
     such as two-factor authorization PINs and system login codes.
    
    Respond with ONLY the exact category name. Do not add any other text, punctuation, or explanation.
    
    
    Subject: {subject}
    Body: {body}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="openai/gpt-oss-20b",
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
    print(predicted_label)
    
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
#print("Classification Report:")
#print(classification_report(expected_labels, predicted_labels, labels=dataset_categories))
# Generate the full string report
full_report = classification_report(expected_labels, predicted_labels, labels=dataset_categories)

# Chop off the last 5 lines (which contain the accuracy, macro, and weighted averages)
clean_report = '\n'.join(full_report.split('\n')[:-5])

print(clean_report)

# Confusion Matrix
print("Confusion Matrix:")
print(confusion_matrix(expected_labels, predicted_labels, labels=dataset_categories))