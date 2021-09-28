import os

from flask import Flask, jsonify

app = Flask(__name__)

cluster_id = os.environ.get("CLUSTER_ID")
instance_id = os.environ.get("INSTANCE_ID")


@app.route('/')
def index():
    return jsonify({
        "message": "Hello world !",
        "cluster": cluster_id,
        "instance": instance_id
    })


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=8000)
