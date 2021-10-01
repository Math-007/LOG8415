import os

from flask import Flask, jsonify
import requests

app = Flask(__name__)

cluster_id = os.environ.get("CLUSTER_ID")
instance_id = None

r = requests.get("http://169.254.169.254/latest/meta-data/instance-id")
if (r.status_code == 200):
    instance_id = r.text

@app.route('/')
def index():
    return jsonify({
        "message": "Hello world !",
        "cluster": cluster_id,
        "instance": instance_id
    })


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
