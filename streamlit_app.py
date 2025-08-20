# Epidemic Care – single-file Flask app
# Features:
# - Sign up & log in (first page is signup)
# - Symptom intake with simple rule-based "AI" triage
# - Generates a clear, safety-first treatment plan
# - Daily check‑ins with progress tracking
# - Reminder banner + downloadable .ics calendar for daily reminders
# - SQLite persistence; tables auto-create on first run
# - Bootstrap 5 UI with a soft gradient for a little flair
#
# How to run:
#   1) pip install flask flask-login
#   2) python app.py
#   3) Open http://127.0.0.1:5000
#
# (Optional) Email reminders are not implemented to avoid config complexity,
# but a calendar (.ics) feed is provided; add it to your calendar app.

from __future__ import annotations
import json
import os
import sqlite3
from datetime import datetime, date, timedelta, time
from typing import Dict, Any, Optional

from flask import (
    Flask, request, redirect, url_for, render_template_string, flash, Response
)
from flask_login import (
    LoginManager, UserMixin, login_user, login_required, logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------- App & DB ----------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-this')
app.config['DATABASE'] = os.path.join(os.path.dirname(__file__), 'epidemic_care.db')

login_manager = LoginManager(app)
login_manager.login_view = 'login'


def get_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS users (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               email TEXT UNIQUE NOT NULL,
               password_hash TEXT NOT NULL,
               name TEXT NOT NULL,
               reminder_time TEXT DEFAULT '09:00'
           )'''
    )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS assessments (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_id INTEGER NOT NULL,
               created_at TEXT NOT NULL,
               data_json TEXT NOT NULL,
               risk_level TEXT NOT NULL,
               plan TEXT NOT NULL,
               FOREIGN KEY(user_id) REFERENCES users(id)
           )'''
    )
    cur.execute(
        '''CREATE TABLE IF NOT EXISTS checkins (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               user_id INTEGER NOT NULL,
               day TEXT NOT NULL,
               symptom_score INTEGER NOT NULL,
               took_meds INTEGER NOT NULL DEFAULT 0,
               fever REAL,
               spo2 INTEGER,
               notes TEXT,
               FOREIGN KEY(user_id) REFERENCES users(id),
               UNIQUE(user_id, day)
           )'''
    )
    conn.commit()
    conn.close()


@app.before_first_request
def on_start():
    init_db()

# ---------------------- User Model ----------------------
class User(UserMixin):
    def __init__(self, id: int, email: str, name: str, password_hash: str, reminder_time: str):
        self.id = id
        self.email = email
        self.name = name
        self.password_hash = password_hash
        self.reminder_time = reminder_time

    @staticmethod
    def from_row(row: sqlite3.Row) -> 'User':
        return User(row['id'], row['email'], row['name'], row['password_hash'], row['reminder_time'])


@login_manager.user_loader
def load_user(user_id: str) -> Optional[User]:
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE id=?', (user_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return User.from_row(row)
    return None

# ---------------------- Utilities ----------------------

def parse_time_str(t: str) -> time:
    try:
        hh, mm = [int(x) for x in t.split(':')]
        return time(hh, mm)
    except Exception:
        return time(9, 0)


def today_str() -> str:
    return date.today().isoformat()


def now_str() -> str:
    return datetime.now().isoformat(timespec='seconds')


# Simple rule-based triage & plan generator.
# This is NOT medical advice. It points users to appropriate care levels.

def generate_plan(form: Dict[str, Any]) -> Dict[str, str]:
    # Extract values safely
    temp = float(form.get('temperature', '0') or 0)
    spo2 = int(form.get('spo2', '0') or 0)
    sob = form.get('shortness_of_breath') == 'on'
    chest_pain = form.get('chest_pain') == 'on'
    confusion = form.get('confusion') == 'on'
    lips_blue = form.get('lips_blue') == 'on'
    severe_red_flags = sob or chest_pain or confusion or lips_blue or spo2 and spo2 < 90

    fever = temp >= 38.0
    cough = form.get('cough') == 'on'
    sore_throat = form.get('sore_throat') == 'on'
    headache = form.get('headache') == 'on'
    myalgia = form.get('myalgia') == 'on'
    gi = (form.get('nausea') == 'on') or (form.get('diarrhea') == 'on')

    comorb = any([
        form.get('diabetes') == 'on',
        form.get('hypertension') == 'on',
        form.get('immunocompromised') == 'on',
        form.get('chronic_lung') == 'on'
    ])

    exposure = form.get('exposure_contact') == 'on'

    # Risk scoring
    score = 0
    score += 2 if severe_red_flags else 0
    score += 1 if fever else 0
    score += 1 if cough else 0
    score += 1 if sore_throat else 0
    score += 1 if headache else 0
    score += 1 if myalgia else 0
    score += 1 if gi else 0
    score += 1 if exposure else 0
    score += 2 if comorb else 0
    score += 2 if spo2 and spo2 < 94 else 0

    if severe_red_flags:
        risk = 'EMERGENCY'
        steps = [
            'Seek emergency medical care immediately (call local emergency number).',
            'Avoid public transport; wear a high-quality mask if you must move.',
            'If available, monitor oxygen saturation continuously and keep airway clear.',
        ]
    elif score >= 6:
        risk = 'HIGH'
        steps = [
            'Arrange urgent evaluation with a clinician within 24 hours.',
            'Rest, hydrate, and isolate from others if respiratory symptoms are present.',
            'Consider a rapid test if an infectious disease is suspected; follow local guidance.',
            'Track temperature and oxygen saturation twice daily.',
            'Prepare a list of current medications and conditions for your clinician.'
        ]
    elif score >= 3:
        risk = 'MODERATE'
        steps = [
            'Home care: rest, fluids, and symptomatic relief (e.g., acetaminophen for fever).',
            'Self-isolate if you have cough/fever and follow local health authority advice.',
            'Check temperature daily; if SpO₂ monitor is available, check once daily.',
            'If symptoms worsen or new red flags appear, seek medical care immediately.'
        ]
    else:
        risk = 'LOW'
        steps = [
            'Monitor symptoms for the next 48–72 hours.',
            'Maintain hydration, nutrition, and sleep.',
            'Practice hand hygiene and mask in crowded indoor settings if respiratory symptoms.',
            'If symptoms persist or worsen, consult a clinician.'
        ]

    plan = f"Risk Level: {risk}\n\nRecommended Steps:\n- " + "\n- ".join(steps) + "\n\nSafety Note: This tool does not provide a diagnosis. Always follow clinician advice and local health guidance."

    return {"risk": risk, "plan": plan}

# ---------------------- Templates ----------------------

BASE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Epidemic Care</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css" rel="stylesheet">
  <style>
    body { background: linear-gradient(135deg, #eef7ff 0%, #f7f9ff 40%, #fff 100%); min-height: 100vh; }
    .brand { font-weight: 800; letter-spacing: .5px; }
    .card-soft { border: 0; border-radius: 1.2rem; box-shadow: 0 10px 30px rgba(0,0,0,.06); }
    .nav-link.active { font-weight: 600; }
  </style>
</head>
<body>
<nav class="navbar navbar-expand-lg bg-white shadow-sm">
  <div class="container">
    <a class="navbar-brand brand" href="{{ url_for('dashboard') if current_user.is_authenticated else url_for('signup') }}">
      <i class="bi bi-activity"></i> Epidemic Care
    </a>
    <div class="ms-auto">
      {% if current_user.is_authenticated %}
        <span class="me-3">Hello, {{ current_user.name.split(' ')[0] }}!</span>
        <a href="{{ url_for('logout') }}" class="btn btn-outline-danger btn-sm">Logout</a>
      {% endif %}
    </div>
  </div>
</nav>

<div class="container py-4">
  {% with messages = get_flashed_messages(with_categories=true) %}
    {% if messages %}
      {% for cat, msg in messages %}
        <div class="alert alert-{{cat}} alert-dismissible fade show" role="alert">
          {{ msg }}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      {% endfor %}
    {% endif %}
  {% endwith %}

  {% block content %}{% endblock %}
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
'''

SIGNUP = '''
{% extends 'base.html' %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-6 col-lg-5">
    <div class="card card-soft p-4 mt-4">
      <h2 class="mb-3">Create your account</h2>
      <p class="text-muted">Track symptoms, get guidance, and set daily reminders.</p>
      <form method="post">
        <div class="mb-3">
          <label class="form-label">Full name</label>
          <input name="name" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input name="email" type="email" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input name="password" type="password" minlength="6" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Daily reminder time</label>
          <input name="reminder_time" type="time" class="form-control" value="09:00">
        </div>
        <button class="btn btn-primary w-100">Sign up</button>
      </form>
      <hr>
      <p class="mb-0">Already have an account? <a href="{{ url_for('login') }}">Log in</a></p>
    </div>
  </div>
</div>
{% endblock %}
'''

LOGIN = '''
{% extends 'base.html' %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-md-6 col-lg-5">
    <div class="card card-soft p-4 mt-4">
      <h2 class="mb-3">Welcome back</h2>
      <form method="post">
        <div class="mb-3">
          <label class="form-label">Email</label>
          <input name="email" type="email" class="form-control" required>
        </div>
        <div class="mb-3">
          <label class="form-label">Password</label>
          <input name="password" type="password" class="form-control" required>
        </div>
        <button class="btn btn-primary w-100">Log in</button>
      </form>
      <hr>
      <p class="mb-0">New here? <a href="{{ url_for('signup') }}">Create an account</a></p>
    </div>
  </div>
</div>
{% endblock %}
'''

DASHBOARD = '''
{% extends 'base.html' %}
{% block content %}
  {% if reminder_due %}
    <div class="alert alert-warning d-flex align-items-center" role="alert">
      <i class="bi bi-bell me-2"></i>
      <div>
        It's time for your daily check‑in. <a href="{{ url_for('checkin') }}">Log it now</a>.
        <a class="ms-2" href="{{ url_for('ics') }}">Add to Calendar (.ics)</a>
      </div>
    </div>
  {% endif %}

  <div class="row g-4">
    <div class="col-md-6">
      <div class="card card-soft p-4 h-100">
        <h4><i class="bi bi-clipboard2-pulse me-2"></i>New Assessment</h4>
        <p class="text-muted">Answer a few questions and get a personalized guidance plan.</p>
        <a href="{{ url_for('assessment') }}" class="btn btn-primary">Start now</a>
      </div>
    </div>
    <div class="col-md-6">
      <div class="card card-soft p-4 h-100">
        <h4><i class="bi bi-graph-up-arrow me-2"></i>Progress</h4>
        <p class="text-muted">Today's check‑in: <strong>{{ todays_status }}</strong></p>
        <a href="{{ url_for('checkin') }}" class="btn btn-outline-primary">Daily Check‑in</a>
      </div>
    </div>
  </div>

  <div class="row g-4 mt-1">
    <div class="col-12">
      <div class="card card-soft p-4">
        <h5 class="mb-3">Recent Assessments</h5>
        {% if assessments %}
          <div class="list-group">
            {% for a in assessments %}
              <a class="list-group-item list-group-item-action" href="{{ url_for('plan', assess_id=a['id']) }}">
                <div class="d-flex w-100 justify-content-between">
                  <h6 class="mb-1">{{ a['created_at'] }}</h6>
                  <span class="badge bg-{{ 'danger' if a['risk_level']=='EMERGENCY' else ('warning' if a['risk_level']=='HIGH' else ('info' if a['risk_level']=='MODERATE' else 'success')) }}">{{ a['risk_level'] }}</span>
                </div>
                <small>Click to view plan</small>
              </a>
            {% endfor %}
          </div>
        {% else %}
          <p class="text-muted">No assessments yet.</p>
        {% endif %}
      </div>
    </div>
  </div>

  <p class="text-muted small mt-4">This tool provides general guidance only and is not a medical diagnosis. For emergencies, seek immediate care.</p>
{% endblock %}
'''

ASSESS = '''
{% extends 'base.html' %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-lg-10">
    <div class="card card-soft p-4">
      <h3 class="mb-3">Symptom Check</h3>
      <form method="post">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Temperature (°C)</label>
            <input class="form-control" name="temperature" type="number" step="0.1" min="30" max="45">
          </div>
          <div class="col-md-4">
            <label class="form-label">Oxygen Saturation (SpO₂)</label>
            <input class="form-control" name="spo2" type="number" min="50" max="100">
          </div>
          <div class="col-md-4">
            <label class="form-label">Exposure to a known case?</label>
            <div class="form-check">
              <input class="form-check-input" type="checkbox" name="exposure_contact" id="exposure">
              <label class="form-check-label" for="exposure">Yes</label>
            </div>
          </div>
        </div>
        <hr>
        <div class="row g-3">
          <div class="col-md-6">
            <label class="form-label">Common Symptoms</label>
            <div class="row">
              {% for s in ['cough','sore_throat','headache','myalgia','nausea','diarrhea'] %}
              <div class="col-6">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" name="{{s}}" id="{{s}}">
                  <label class="form-check-label" for="{{s}}">{{ s.replace('_',' ').title() }}</label>
                </div>
              </div>
              {% endfor %}
            </div>
          </div>
          <div class="col-md-6">
            <label class="form-label">Red Flags</label>
            <div class="row">
              {% for s in ['shortness_of_breath','chest_pain','confusion','lips_blue'] %}
              <div class="col-6">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" name="{{s}}" id="{{s}}">
                  <label class="form-check-label" for="{{s}}">{{ s.replace('_',' ').title() }}</label>
                </div>
              </div>
              {% endfor %}
            </div>
          </div>
        </div>
        <hr>
        <div class="row g-3">
          <div class="col-md-12">
            <label class="form-label">Existing Conditions</label>
            <div class="row">
              {% for s in ['diabetes','hypertension','immunocompromised','chronic_lung'] %}
              <div class="col-6 col-md-3">
                <div class="form-check">
                  <input class="form-check-input" type="checkbox" name="{{s}}" id="{{s}}">
                  <label class="form-check-label" for="{{s}}">{{ s.replace('_',' ').title() }}</label>
                </div>
              </div>
              {% endfor %}
            </div>
          </div>
        </div>
        <div class="mt-4 d-flex gap-2">
          <a href="{{ url_for('dashboard') }}" class="btn btn-outline-secondary">Cancel</a>
          <button class="btn btn-primary">Generate Plan</button>
        </div>
      </form>
    </div>
  </div>
</div>
{% endblock %}
'''

PLAN = '''
{% extends 'base.html' %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-lg-9">
    <div class="card card-soft p-4">
      <div class="d-flex justify-content-between align-items-start">
        <h3 class="mb-3">Your Guidance Plan</h3>
        <span class="badge fs-6 bg-{{ 'danger' if risk=='EMERGENCY' else ('warning' if risk=='HIGH' else ('info' if risk=='MODERATE' else 'success')) }}">{{ risk }}</span>
      </div>
      <pre class="p-3 bg-light rounded" style="white-space: pre-wrap;">{{ plan }}</pre>
      <a class="btn btn-outline-primary" href="{{ url_for('dashboard') }}">Back to Dashboard</a>
    </div>
  </div>
</div>
{% endblock %}
'''

CHECKIN = '''
{% extends 'base.html' %}
{% block content %}
<div class="row justify-content-center">
  <div class="col-lg-8">
    <div class="card card-soft p-4">
      <h3 class="mb-3">Daily Check‑in</h3>
      <form method="post">
        <div class="row g-3">
          <div class="col-md-4">
            <label class="form-label">Overall Symptom Score (0–10)</label>
            <input class="form-control" name="symptom_score" type="number" min="0" max="10" required>
          </div>
          <div class="col-md-4">
            <label class="form-label">Fever (°C)</label>
            <input class="form-control" name="fever" type="number" step="0.1" min="30" max="45">
          </div>
          <div class="col-md-4">
            <label class="form-label">SpO₂</label>
            <input class="form-control" name="spo2" type="number" min="50" max="100">
          </div>
        </div>
        <div class="form-check my-3">
          <input class="form-check-input" type="checkbox" name="took_meds" id="took_meds">
          <label class="form-check-label" for="took_meds">I took my medications as advised</label>
        </div>
        <div class="mb-3">
          <label class="form-label">Notes / Side effects</label>
          <textarea class="form-control" name="notes" rows="3"></textarea>
        </div>
        <div class="d-flex gap-2">
          <a href="{{ url_for('dashboard') }}" class="btn btn-outline-secondary">Cancel</a>
          <button class="btn btn-primary">Save Check‑in</button>
        </div>
      </form>
    </div>

    <div class="card card-soft p-4 mt-4">
      <h5 class="mb-3">Recent Check‑ins</h5>
      {% if rows %}
        <div class="table-responsive">
          <table class="table table-sm">
            <thead>
              <tr><th>Date</th><th>Score</th><th>Fever</th><th>SpO₂</th><th>Meds?</th><th>Notes</th></tr>
            </thead>
            <tbody>
              {% for r in rows %}
                <tr>
                  <td>{{ r['day'] }}</td>
                  <td>{{ r['symptom_score'] }}</td>
                  <td>{{ (r['fever'] or '') }}</td>
                  <td>{{ (r['spo2'] or '') }}</td>
                  <td>{{ 'Yes' if r['took_meds'] else 'No' }}</td>
                  <td>{{ r['notes'] or '' }}</td>
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      {% else %}
        <p class="text-muted">No check‑ins yet.</p>
      {% endif %}
    </div>
  </div>

  <div class="col-lg-4">
    <div class="card card-soft p-4">
      <h5 class="mb-3">Your Reminder</h5>
      <form method="post" action="{{ url_for('update_reminder') }}">
        <div class="mb-3">
          <label class="form-label">Daily time</label>
          <input class="form-control" type="time" name="reminder_time" value="{{ current_user.reminder_time }}">
        </div>
        <button class="btn btn-outline-primary">Update Reminder</button>
        <a class="btn btn-link" href="{{ url_for('ics') }}">Download .ics</a>
      </form>
    </div>
  </div>
</div>
{% endblock %}
'''

# ---------------------- Routes ----------------------

@app.route('/')
def root():
    # First page = signup, as requested
    return redirect(url_for('signup'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name','').strip()
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        reminder_time = request.form.get('reminder_time','09:00')
        if not name or not email or not password:
            flash(('danger','All fields are required.'))
            return render_template_string(SIGNUP)
        pw_hash = generate_password_hash(password)
        try:
            conn = get_db()
            cur = conn.cursor()
            cur.execute('INSERT INTO users (email, password_hash, name, reminder_time) VALUES (?,?,?,?)',
                        (email, pw_hash, name, reminder_time))
            conn.commit()
            cur.execute('SELECT * FROM users WHERE email=?', (email,))
            row = cur.fetchone()
            conn.close()
            user = User.from_row(row)
            login_user(user)
            flash(('success', 'Account created! Welcome to Epidemic Care.'))
            return redirect(url_for('dashboard'))
        except sqlite3.IntegrityError:
            flash(('danger','Email already in use. Please log in.'))
            return redirect(url_for('login'))
    return render_template_string(SIGNUP)


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email','').strip().lower()
        password = request.form.get('password','')
        conn = get_db()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE email=?', (email,))
        row = cur.fetchone()
        conn.close()
        if not row:
            flash(('danger','Invalid credentials.'))
            return render_template_string(LOGIN)
        user = User.from_row(row)
        if not check_password_hash(user.password_hash, password):
            flash(('danger','Invalid credentials.'))
            return render_template_string(LOGIN)
        login_user(user)
        flash(('success','Logged in successfully.'))
        return redirect(url_for('dashboard'))
    return render_template_string(LOGIN)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(('info','You have been logged out.'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    # Reminder banner logic
    rt = parse_time_str(current_user.reminder_time)
    now = datetime.now().time()
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT 1 FROM checkins WHERE user_id=? AND day=?', (current_user.id, today_str()))
    done_today = cur.fetchone() is not None
    cur.execute('SELECT id, created_at, risk_level FROM assessments WHERE user_id=? ORDER BY id DESC LIMIT 5', (current_user.id,))
    assessments = cur.fetchall()
    conn.close()

    reminder_due = (now >= rt) and (not done_today)
    todays_status = 'Done' if done_today else 'Not yet'

    return render_template_string(DASHBOARD, reminder_due=reminder_due, todays_status=todays_status, assessments=assessments)


@app.route('/assessment', methods=['GET','POST'])
@login_required
def assessment():
    if request.method == 'POST':
        data = request.form.to_dict()
        result = generate_plan(data)
        conn = get_db()
        cur = conn.cursor()
        cur.execute('INSERT INTO assessments (user_id, created_at, data_json, risk_level, plan) VALUES (?,?,?,?,?)',
                    (current_user.id, now_str(), json.dumps(data), result['risk'], result['plan']))
        conn.commit()
        assess_id = cur.lastrowid
        conn.close()
        return redirect(url_for('plan', assess_id=assess_id))
    return render_template_string(ASSESS)


@app.route('/plan/<int:assess_id>')
@login_required
def plan(assess_id: int):
    conn = get_db()
    cur = conn.cursor()
    cur.execute('SELECT plan, risk_level FROM assessments WHERE id=? AND user_id=?', (assess_id, current_user.id))
    row = cur.fetchone()
    conn.close()
    if not row:
        flash(('danger','Plan not found.'))
        return redirect(url_for('dashboard'))
    return render_template_string(PLAN, plan=row['plan'], risk=row['risk_level'])


@app.route('/checkin', methods=['GET','POST'])
@login_required
def checkin():
    conn = get_db()
    if request.method == 'POST':
        symptom_score = int(request.form.get('symptom_score','0') or 0)
        fever = request.form.get('fever')
        fever_val = float(fever) if fever not in (None, '') else None
        spo2 = request.form.get('spo2')
        spo2_val = int(spo2) if spo2 not in (None, '') else None
        took_meds = 1 if request.form.get('took_meds') == 'on' else 0
        notes = request.form.get('notes','').strip()

        cur = conn.cursor()
        try:
            cur.execute('INSERT INTO checkins (user_id, day, symptom_score, took_meds, fever, spo2, notes) VALUES (?,?,?,?,?,?,?)',
                        (current_user.id, today_str(), symptom_score, took_meds, fever_val, spo2_val, notes))
        except sqlite3.IntegrityError:
            # Already exists for today → update
            cur.execute('UPDATE checkins SET symptom_score=?, took_meds=?, fever=?, spo2=?, notes=? WHERE user_id=? AND day=?',
                        (symptom_score, took_meds, fever_val, spo2_val, notes, current_user.id, today_str()))
        conn.commit()
        flash(('success','Check‑in saved.'))
        # fall through to GET display

    cur = conn.cursor()
    cur.execute('SELECT * FROM checkins WHERE user_id=? ORDER BY day DESC LIMIT 14', (current_user.id,))
    rows = cur.fetchall()
    conn.close()
    return render_template_string(CHECKIN, rows=rows)


@app.route('/reminder', methods=['POST'])
@login_required
def update_reminder():
    t = request.form.get('reminder_time','09:00')
    conn = get_db()
    cur = conn.cursor()
    cur.execute('UPDATE users SET reminder_time=? WHERE id=?', (t, current_user.id))
    conn.commit()
    conn.close()
    flash(('success', f'Reminder updated to {t}.'))
    return redirect(url_for('checkin'))


@app.route('/reminder.ics')
@login_required
def ics():
    # Generate a simple daily recurring event
    rt = parse_time_str(current_user.reminder_time)
    dtstart = datetime.combine(date.today(), rt).strftime('%Y%m%dT%H%M%S')
    ics_text = f"""BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Epidemic Care//EN\nBEGIN:VEVENT\nUID:{current_user.id}-{today_str()}@epidemic-care\nDTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}\nDTSTART:{dtstart}\nRRULE:FREQ=DAILY\nSUMMARY:Daily health check‑in\nDESCRIPTION:Open Epidemic Care and log your daily symptoms.\nEND:VEVENT\nEND:VCALENDAR\n"""
    return Response(ics_text, mimetype='text/calendar', headers={'Content-Disposition':'attachment; filename=reminder.ics'})

# ---------------------- Template registration ----------------------
# Register string templates with Flask's loader
from jinja2 import DictLoader
app.jinja_loader = DictLoader({
    'base.html': BASE,
    'signup.html': SIGNUP,
    'login.html': LOGIN,
    'dashboard.html': DASHBOARD,
    'assess.html': ASSESS,
    'plan.html': PLAN,
    'checkin.html': CHECKIN,
})

# ---------------------- Run ----------------------
if __name__ == '__main__':
    app.run(debug=True)
