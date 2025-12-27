# test_improved.py
import requests
import json

url = "http://127.0.0.1:8000/api/ask"

new_doc_id = "fbe958bf-94a7-42eb-8eb2-1fd88d36f051"

questions = [
    "Describe the uploaded images",
    "What type of content is in PolyGlot Connect business model canvas.png?",
    "Are there any AI-related images?",
    "What can you tell me about the images?",
    "Do any images contain text?"
]

for i, question in enumerate(questions):
    print(f"\n{'='*60}")
    print(f"Question {i+1}: {question}")
    print('='*60)
    
    data = {"question": question}
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"Answer: {result['answer'][:200]}...")
        if result.get('sources'):
            print(f"Sources found: {len(result['sources'])}")
    else:
        print(f"Error: {response.text}")