import os
import json
from collections import defaultdict
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)

# your raw HTML lives here
DATASHEET_DIR = os.path.join(os.path.dirname(__file__), 'datasheets')
# persistent JSON state
STATE_FILE    = os.path.join(os.path.dirname(__file__), 'game_state.json')

def load_datasheets():
    out = []
    for faction in sorted(os.listdir(DATASHEET_DIR)):
        faction_dir = os.path.join(DATASHEET_DIR, faction)
        if not os.path.isdir(faction_dir):
            continue
        for fn in sorted(os.listdir(faction_dir)):
            if fn.lower().endswith('.html'):
                label = f"{faction.replace('-', ' ').title()} – {fn[:-5]}"
                path  = f"{faction}/{fn}"
                out.append({'label': label, 'path': path})
    return out

def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    return {
        'team1': {'name': 'Team 1', 'roster': []},
        'team2': {'name': 'Team 2', 'roster': []},
        'points': {str(r): [0,0] for r in range(1,6)}
    }

def save_state(st):
    with open(STATE_FILE, 'w') as f:
        json.dump(st, f, indent=2)

datasheets = load_datasheets()
state       = load_state()

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == 'POST':
        state['team1']['name'] = request.form.get('team1_name', state['team1']['name'])
        state['team2']['name'] = request.form.get('team2_name', state['team2']['name'])
        save_state(state)

    # group by faction for two-step selector
    grouped = defaultdict(list)
    for ds in datasheets:
        fac = ds['path'].split('/',1)[0]
        grouped[fac].append(ds)

    return render_template(
        'index.html',
        ds_by_faction=dict(grouped),
        state=state,
        team1=state['team1'],
        team2=state['team2']
    )

@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    team, path = data.get('team'), data.get('path')
    if team in state and path and path not in state[team]['roster']:
        state[team]['roster'].append(path)
        save_state(state)
    return jsonify(success=True)

@app.route('/remove', methods=['POST'])
def remove():
    data = request.get_json()
    team, path = data.get('team'), data.get('path')
    if team in state and path in state[team]['roster']:
        state[team]['roster'].remove(path)
        save_state(state)
    return jsonify(success=True)

@app.route('/roster')
def roster():
    return render_template('roster.html', state=state)

@app.route('/points', methods=['GET','POST'])
def points():
    if request.method == 'POST':
        if 'reset' in request.form:
            for r in range(1,6):
                state['points'][str(r)] = [0,0]
        else:
            for r in range(1,6):
                p1 = request.form.get(f'p1_{r}', type=int, default=0)
                p2 = request.form.get(f'p2_{r}', type=int, default=0)
                state['points'][str(r)] = [p1,p2]
        save_state(state)
    return render_template(
        'points.html',
        team1=state['team1'],
        team2=state['team2'],
        points=state['points']
    )

# NEW: Serve datasheets directly from the datasheets/ directory
@app.route('/datasheets/<path:filename>')
def serve_datasheet(filename):
    return send_from_directory(DATASHEET_DIR, filename)

if __name__ == '__main__':
    app.run(debug=True)
