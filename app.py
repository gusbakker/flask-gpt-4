from flask import Flask, render_template, request
import os
import openai

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

start_chat_log = """Human: Hello, I am Human.
AI: Hello, human I am openai gpt3.
Human: How are you?
AI: I am fine, thanks for asking. 
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/get")
def get_bot_response():
    global start_chat_log
    user_text = request.args.get('msg')
    prompt = f"{start_chat_log}Human: {user_text}\nAI:"
    response = openai.Completion.create(
        engine="davinci",
        prompt=prompt,
        temperature=0.8,
        max_tokens=200,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.5,
        stop="\nHuman: "
    )
    ai_response = response.choices[0].text
    start_chat_log += f"Human: {user_text}\nAI:{ai_response}\n"
    return ai_response


if __name__ == "__main__":
    app.run()
