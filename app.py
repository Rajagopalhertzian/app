import os
import requests
from flask import Flask, request, jsonify
from db import db, init_db, Project
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')
init_db(app)

@app.before_first_request
def create_tables():
    db.create_all()

# OAuth Callback
@app.route('/api/oauth/callback', methods=['GET'])
def oauth_callback():
    code = request.args.get('code')
    try:
        response = requests.post(
            'https://login.procore.com/oauth/token',
            json={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': os.getenv('REDIRECT_URI'),
                'client_id': os.getenv('CLIENT_ID'),
                'client_secret': os.getenv('CLIENT_SECRET'),
            },
        )
        response.raise_for_status()
        data = response.json()
        return jsonify(data)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

# Import Projects API
@app.route('/api/projects/import', methods=['GET'])
def import_projects():
    company_id = request.args.get('company_id')
    access_token = request.args.get('access_token')

    try:
        response = requests.get(
            f'https://api.procore.com/vapid/projects?company_id={company_id}',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        response.raise_for_status()
        projects = response.json()

        for project in projects:
            db_project = Project.query.get(project['id'])
            if not db_project:
                db_project = Project(
                    id=project['id'],
                    name=project['name'],
                    created_at=project['created_at'],
                    updated_at=project['updated_at'],
                )
                db.session.add(db_project)
            else:
                db_project.name = project['name']
                db_project.updated_at = project['updated_at']
        
        db.session.commit()
        return jsonify({'message': 'Projects imported successfully', 'projects': projects})
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 500

# Webhook Listener
@app.route('/api/webhook/notification', methods=['POST'])
def webhook_listener():
    payload = request.json
    try:
        event_type = payload.get('event_type')
        resource = payload.get('resource')
        data = payload.get('data')

        if resource == 'Project' and event_type in ['created', 'updated']:
            db_project = Project.query.get(data['id'])
            if not db_project:
                db_project = Project(
                    id=data['id'],
                    name=data['name'],
                    created_at=data['created_at'],
                    updated_at=data['updated_at'],
                )
                db.session.add(db_project)
            else:
                db_project.name = data['name']
                db_project.updated_at = data['updated_at']

            db.session.commit()
        return jsonify({'message': 'Webhook processed successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=int(os.getenv('PORT', 3000)), debug=True)
