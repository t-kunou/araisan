from chalice import Chalice
import os
import datetime
from langchain_openai import ChatOpenAI
from chalicelib.agents.components.state import State
from chalicelib.agents.general_agent import GeneralAgent

from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
import requests
import os

GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_DISCOVERY_URL = "https://accounts.google.com/.well-known/openid-configuration"
REDIRECT_URI = os.environ.get("REDIRECT_URI")

SCOPE = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.readonly",
]

def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

def get_flow():
    return Flow.from_client_config(
        {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "userinfo_uri": "https://www.googleapis.com/oauth2/v3/userinfo",
            }
        },
        scopes=SCOPE,
        redirect_uri=REDIRECT_URI,
    )

app = Chalice(app_name='chalice-app')
app.api.cors = True

@app.route('/')
def root():
    return {'message': 'Welcome to the General Agent API!'}

@app.route('/api/health')
def health_check():
    return {'status': 'ok'}

@app.route('/logout')
def logout():
    # Clear session logic here if needed
    url = os.environ.get("FRONTEND_TOP_URL")
    return {'redirect': url}

@app.route('/login')
def login():
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    flow = get_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        prompt='consent',
    )
    # Store state in session or return it for frontend handling
    return {'authorization_url': authorization_url}

@app.route('/auth/callback')
def callback():
    flow = get_flow()
    flow.fetch_token(authorization_response=app.current_request.url)

    credentials = flow.credentials
    
    # Store tokens in session or return them for frontend handling
    return {'redirect': os.environ.get("FRONTEND_TOP_URL")}

@app.route('/agent_request', methods=['POST'])
def agent_request():
    data = app.current_request.json_body
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
    
    return response

@app.route('/check_auth')
def check_auth():
    # Check authentication logic here
    return {'authenticated': True}  # Replace with actual check logic if needed