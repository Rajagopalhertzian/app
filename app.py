import requests
from flask import Flask, request, jsonify

# Flask setup
app = Flask(__name__)

# Step 1: Obtain Authorization Code and Access Token
url = "https://login.procore.com/oauth/token"
payload = {
    "grant_type": "authorization_code",
    "code": "<AUTHORIZATION_CODE>",
    "client_id": "5QZrxCaoj8gzTSJjxrqdUF-bIy_b0uJJyF3gSlCWx6o",
    "client_secret": "On3oTtWjtFENHGMekuSpzGNDw8Yg3pHedN2WuZB69bA",
    "redirect_uri": "http://localhost",
}

response = requests.post(url, json=payload)
token_data = response.json()
access_token = token_data['access_token']

# Step 2: Fetching Projects using Access Token
@app.route('/api/projects', methods=['GET'])
def get_projects():
    headers = {"Authorization": f"Bearer {access_token}"}
    url = "https://api.procore.com/vapid/v1/projects"
    response = requests.get(url, headers=headers)
    projects = response.json()
    return jsonify(projects)

# Step 3: Handling Webhook Notifications
@app.route('/webhook/procore', methods=['POST'])
def webhook_handler():
    data = request.json
    # You can log the data or perform any processing here
    print(data)
    return '', 200

if __name__ == '__main__':
    app.run(port=5000)
