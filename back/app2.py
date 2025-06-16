import os
from flask_cors import CORS
from flask import Flask , request, jsonify, session, redirect
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests  import Request
from googleapiclient.discovery import build
import datetime
from werkzeug.serving import WSGIRequestHandler
import awsgi

from langchain_openai import ChatOpenAI
import requests

from flask import url_for
from dotenv import load_dotenv

from chalicelib.agents.components.state import State
from chalicelib.agents.general_agent import GeneralAgent

try:
    from flask_lambda import FlaskLambda
except ImportError:
    # ローカル開発用にFlaskLambdaがない場合のフォールバック
    FlaskLambda = Flask

load_dotenv()

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"  # 開発用: HTTPSでなくても許可

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

SCOPE = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.readonly",
]

app = FlaskLambda(__name__)
CORS(app, supports_credentials=True)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

def get_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ.get("GOOGLE_CLIENT_ID"),
                "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "userinfo_uri": "https://www.googleapis.com/oauth2/v3/userinfo",
            }
        },
        scopes=SCOPE,
        redirect_uri=url_for("callback", _external=True),
    )

@app.route("/")
def root():
    return "Welcome to the General Agent API!"

@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok"}), 200

@app.route("/api/logout")
def logout():
    session.clear()
    url = os.environ.get("FRONTEND_TOP_URL")
    return redirect(url)

@app.route("/api/login")
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt='consent',
    )
    session["state"] = state
    return redirect(authorization_url)

@app.route("/auth/callback")
def callback():
    flow = get_flow()
    flow.fetch_token(authorization_response=request.url)

    credentials = flow.credentials
    
    session["refresh_token"] = credentials.refresh_token
    session["id_token"] = credentials.id_token
    session["access_token"] = credentials.token

    url = os.environ.get("FRONTEND_TOP_URL")
    return redirect(url)

@app.route("/api/agent_request", methods=["POST"])
def agent_request():
    data = request.json
    print("Received data:", data)
    query = data.get("query", "")
    location = data.get("location", "")
    today = datetime.datetime.utcnow().date().isoformat()

    llm = ChatOpenAI(model="gpt-4o", temperature=0.0, max_tokens=1000)
    agent = GeneralAgent(llm)

    initial_state = State(
        query=query,
        location=location,
        today=today,
    )
    result = agent.build_workflow().invoke(initial_state)

    response = {
        "result": result['general_answer'],
        "kana": result['kana_answer'],
    }
    
    return jsonify(response), 200

@app.route("/api/check_auth")
def check_auth():
    if "access_token" in session:
        return jsonify({"authenticated": True})
    else:
        return jsonify({"authenticated": False})

def lambda_handler(event, context):
    return awsgi.response(app, event, context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=54916)