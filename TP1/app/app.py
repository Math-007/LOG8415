import os

from flask import Flask, jsonify
import requests
import platform

app = Flask(__name__)

cluster_id = os.environ.get("CLUSTER_ID", "unknown cluster")
instance_id = None

try:
    # https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
    r = requests.get("http://169.254.169.254/latest/meta-data/instance-id", timeout=1)
    if (r.status_code == 200):
        instance_id = r.text
except requests.ConnectionError:
    instance_id = platform.node()

@app.route('/')
@app.route('/<path:path>')
def route(path="/"):
    return jsonify({
        "message": "Hello world !",
        "cluster": cluster_id,
        "instance": instance_id,
        "path": path
    })


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
