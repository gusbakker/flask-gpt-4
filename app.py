import os
from collections import deque
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import openai
from googlesearch import search

load_dotenv()

app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = os.getenv("FLASK_SECRET_KEY")
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(BASE_DIR, "conversations.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

openai.api_key = os.getenv("OPENAI_API_KEY")


class Conversation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(10000), nullable=False)
    role = db.Column(db.String(10), nullable=False)


def init_db():
    print("Creating the database...")
    db.create_all()


def internet_search(query, num_results=5):
    try:
        search_results = []
        for result in search(query, num_results=num_results):
            search_results.append(result)
        return search_results
    except Exception as e:
        print(f"Error during internet search: {e}")
        return []


def should_perform_search(prompt):
    conversation = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "If this prompt requires access to the internet, "
                                                "reply with the following: internet-required"}] + conversation,
        temperature=0.7,
    )
    ai_response = response['choices'][0]['message']['content'].strip().lower()

    if "internet-required" in ai_response:
        print(f"Internet access required for the following prompt: {prompt}")
        return True
    return False


def generate_response(prompt, user_id):
    conversation = deque(
        [
            {
                "role": conv.role,
                "content": conv.content,
            }
            for conv in Conversation.query.filter_by(user_id=user_id).order_by(Conversation.id)
        ],
        maxlen=10,
    )

    conversation.append({"role": "user", "content": prompt})

    if should_perform_search(prompt):
        print("Performing internet search...")
        search_query = prompt.strip()
        search_results = internet_search(search_query)
        search_results_text = "\n".join(search_results)
        conversation.append(
            {"role": "assistant", "content": f"Top search results for '{search_query}':\n{search_results_text}"})

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "system", "content": "You are talking to an AI chatbot."}] + list(conversation),
        temperature=0.9,
    )
    ai_response = response['choices'][0]['message']['content']
    conversation.append({"role": "assistant", "content": ai_response})

    new_user_msg = Conversation(user_id=user_id, content=prompt, role="user")
    new_ai_msg = Conversation(user_id=user_id, content=ai_response, role="assistant")
    db.session.add(new_user_msg)
    db.session.add(new_ai_msg)
    db.session.commit()

    return ai_response


@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_id = request.form['user_id']
        session['user_id'] = user_id
        return redirect(url_for('home'))
    return render_template("login.html")


@app.route("/get")
def get_bot_response():
    user_text = request.args.get('msg')
    user_id = session.get('user_id')
    if user_id is None:
        return "Error: User not authenticated."
    try:
        ai_response = generate_response(user_text, user_id)
        return ai_response
    except Exception as e:
        print(f"Error: {e}")
        return "Error: Failed to generate AI response."


@app.route("/logout")
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.")
    return redirect(url_for('login'))


if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run()
