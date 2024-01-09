from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
import unittest
import os

class TestOpenAI(unittest.TestCase):
  
  def test_mistralai_conn(self):
    api_key = os.environ["MISTRAL_API_KEY"]
    model = "mistral-tiny"
    client = MistralClient(api_key=api_key)

    messages = [
      ChatMessage(role="user", content="What is the best French cheese?")
    ]

    for chunk in client.chat_stream(model=model, messages=messages):
      print(chunk)
    

if __name__ == "__main__":
  unittest.main()