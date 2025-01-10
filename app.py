from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    event_type = data.get('event_type')
    project_id = data.get('data', {}).get('project_id')

    # Log the event data (can be extended for more processing)
    print(f"Event Type: {event_type}, Project ID: {project_id}, Data: {json.dumps(data)}")

    return jsonify({'status': 'success'}), 200

if __name__ == '__main__':
    app.run(port=8000)
