import os
import openai
from dotenv import load_dotenv
from openai import OpenAI

from prompt_agent import GENERATE_PROMPTS

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

stream = client.chat.completions.create(
    model="gpt-4.1",
    messages=[
        {"role": "system", "content": GENERATE_PROMPTS},
        {"role": "user", "content": """
I need a prompt to create a profile for a social network. I need the agent to create the profile according to another instruction that will tell it how to create it. This is so that duplicate profiles are not created and better profiles are created. It should generate them as a JSON file with the following fields:

name
age
gender
biography
location
language
language_known
occupation
education
date_of_birth
personality
"""}
    ],
    stream=True
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
