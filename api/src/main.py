from flask import Flask
app = Flask('SteadyBreezeAPI')

@app.route("/get_cheapest_pricezone")
def get_data():
    return "fi1"