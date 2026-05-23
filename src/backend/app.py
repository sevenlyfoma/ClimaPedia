import importlib
import json
import os

from flask import Flask, Response, send_file, send_from_directory
from flask_cors import CORS
from werkzeug.exceptions import NotFound

MY_PATH = os.path.abspath(os.path.dirname(__file__))

FLASK_ENV = os.environ.get("FLASK_ENV", "development")

print(f"FLASK_ENV={FLASK_ENV}")

app = Flask(__name__)

with open("manifest.json") as f:
    manifest = json.load(f)
manifest_resp = Response(json.dumps(manifest), mimetype="application/json")

# Each key at the manifest's root must be a module in this directory
# We import each module and register their blueprints with the application at '/data/<group name>'
for group in manifest:
    bp = importlib.import_module(group).blueprint
    app.register_blueprint(bp, url_prefix=f"/api/data/{group}")


# Serve the manifest to the frontend
@app.route("/api/groups/")
def serve_manifest():
    return manifest_resp


if FLASK_ENV != "development":

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_static(path):
        try:
            return send_from_directory(os.path.join(MY_PATH, "../frontend/dist"), path)
        except NotFound:
            return send_file(os.path.join(MY_PATH, "../frontend/dist/index.html"))

else:
    CORS(app)

if __name__ == "__main__":
    port = os.getenv("BACKEND_PORT")
    print(f"Serving on 0.0.0.0:{port}")
    app.run(debug=True, port=port, host="0.0.0.0")
