from flask import Flask
app = Flask('WebServer1')

@app.route("/")
def get_data():
    return "fi1 server #2"