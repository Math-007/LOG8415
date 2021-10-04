import os

from flask import Flask, jsonify
import requests

app = Flask(__name__)

cluster_id = os.environ.get("CLUSTER_ID")
instance_id = None

# https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/instancedata-data-retrieval.html
r = requests.get("http://169.254.169.254/latest/meta-data/instance-id")
if (r.status_code == 200):
    instance_id = r.text

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
