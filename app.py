import os
import json
from collections import defaultdict
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# where your datasheets live
DATASHEET_DIR = os.path.join(os.path.dirname(__file__), 'datasheets')

# load datasheets once
def load_datasheets():
    out = []
    for faction in sorted(os.listdir(DATASHEET_DIR)):
        fd = os.path.join(DATASHEET_DIR, faction)
        if not os.path.isdir(fd): continue
        for fn in sorted(os.listdir(fd)):
            if fn.lower().endswith('.html'):
                out.append({'path': f"{faction}/{fn}"})
    return out

datasheets = load_datasheets()

@app.route('/')
def index():
    # only pass ds_by_faction for the two-step selector
    grouped = defaultdict(list)
    for ds in datasheets:
        fac = ds['path'].split('/',1)[0]
        grouped[fac].append(ds)
    return render_template('index.html',
                           ds_by_faction=dict(grouped))

@app.route('/roster')
def roster():
    return render_template('roster.html')

@app.route('/points')
def points():
    return render_template('points.html')

@app.route('/datasheets/<path:filename>')
def serve_datasheet(filename):
    return send_from_directory(DATASHEET_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)