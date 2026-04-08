import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv('GEMINI_API_KEY')
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
res = requests.get(url)
for m in res.json().get('models', []):
    print(m['name'])
