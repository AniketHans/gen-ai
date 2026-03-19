from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

response1 = client.embeddings.create(
        input=["dog chases cat"],
        model="text-embedding-3-small"
    )

response2 = client.embeddings.create(
        input=["cat chases dog"],
        model="text-embedding-3-small"
    )
print(response1)
print("#############################")
print(response1.data[0].embedding)
print("***********************************")
print("***********************************")
print("***********************************")
print(response2)
print("#############################")
print(response2.data[0].embedding)

print(response1 == response2) # False
print(response1.data[0].embedding == response2.data[0].embedding) # False
