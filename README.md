# Web Chatbot with Flask & GPT-4

#### Simple GUI for OpenAI GPT-4 using Flask, SQLAlchemy and Google Search.

#### It has the following features:
 1. **Chatbot:** It uses GPT-4 to generate responses to user queries.
 2. **Google Search:** It uses Google Search API to search for the user query and return the top results.
 3. **Database:** It uses SQLAlchemy to save conversations in a SQLite database.

## Local Setup:
 1. `pip install -r requirements.txt`
 2. In the root folder create .env file with the following content:
    ```
    OPENAI_API_KEY=<your_openai_api_key>
    FLASK_SECRET_KEY=<your_flask_secret_key>
    ```
 3. Run *app.py* with `python app.py`.
 4. The demo will be live at [http://localhost:5000/](http://localhost:5000/)
