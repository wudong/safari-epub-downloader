from flask import Flask
from flask import jsonify, request

from epubgen.SafariApi import SafariApi
from epubgen.job import Identity
import uuid

app = Flask(__name__)

# store the identity cache.
identity_cache = {}
job_cache = {}


@app.route('/ping')
def ping():
    return jsonify('Pong!')


@app.route('/status')
def status():
    return ""


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if identity_cache[username]:
        return jsonify(identity_cache[username].get_identity().get_id())
    else:
        identity = Identity(username, password)
        api = SafariApi(identity)
        if api.do_login():
            identity_cache[username] = api
            return jsonify(identity.get_id())
        else:
            return jsonify("Login Failed")


@app.route('/download')
def download():
    return ""


@app.route('/convert/<uid>/<book_id>')
def convert(uid, book_id):



if __name__ == "__main__":
    app.run()
