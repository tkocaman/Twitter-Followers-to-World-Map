import os
import json
from flask import Flask, render_template


app = Flask(__name__)

jason_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "location_data.json"))

@app.route('/', methods=("POST", "GET"))

def profile():
    with open(jason_path) as fp:
        data = json.load(fp)
        dataWorld = data["dataWorld"]
        dataUs = data["dataUs"]
        
    return render_template('index.html', 
                        dataWorld=dataWorld, 
                        dataUs=dataUs
                        )

if __name__ == '__main__':
    app.run(host='0.0.0.0')
