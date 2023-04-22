from collections import deque

from flask import Flask, render_template, request
import os
import openai
from dotenv import load_dotenv


app = Flask(__name__)

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

conversation = deque(maxlen=10)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    global conversation
    user_text = request.args.get('msg')
    human = f"Human: {user_text}"
    print(human)
    prompt = f"{conversation}{human}\nAI: "
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt},
        ],
        temperature=0.9,
    )
    ai_response = response['choices'][0]['message']['content']
    conversation += f"{prompt}\n {ai_response}\n"
    print(ai_response)
    return ai_response


if __name__ == "__main__":
    app.run()
