import os
from google import genai

api_key = "AIzaSyB0oRtQXrj7AvQSbI52s-DEX8q194fO5Yw"
client = genai.Client(api_key=api_key)

try:
    for model in client.models.list():
        print(model.name)
except Exception as e:
    print("Error:", e)
