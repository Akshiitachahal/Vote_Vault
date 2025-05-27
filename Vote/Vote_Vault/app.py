from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_mail import Mail
import sqlite3
from datetime import datetime
from collections import Counter

from config import SECRET_KEY, DEBUG, MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD, ALLOWED_DOMAIN
from utils.encryption import encrypt_vote, decrypt_vote
from utils.email_otp import send_otp_email

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.debug = DEBUG

# Mail Setup
app.config.update(
    MAIL_SERVER=MAIL_SERVER,
    MAIL_PORT=MAIL_PORT,
    MAIL_USE_TLS=MAIL_USE_TLS,
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
)
mail = Mail(app)

# Flask-Login Setup
login_manager = LoginManager()
login_manager.init_app(app)

DATABASE = 'database/db.sqlite3'

class User(UserMixin):
    def __init__(self, id, email, password, is_admin):
        self.id = id
        self.email = email
        self.password = password
        self.is_admin = bool(is_admin)

@login_manager.user_loader
def load_user(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password, is_admin FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return User(*user)
    return None

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS candidates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    ''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS votes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        vote TEXT,
                        timestamp TEXT,
                        FOREIGN KEY(user_id) REFERENCES users(id)
                    )''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY,
                        voting_open INTEGER,
                        start_time TEXT,
                        end_time TEXT,
                        position TEXT
                    )''')
    cursor.execute("INSERT OR IGNORE INTO settings (id, voting_open, start_time, end_time, position) VALUES (1, 0, NULL, NULL, NULL)")
    # Add position column if missing (for existing DBs)
    cursor.execute("PRAGMA table_info(settings)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'position' not in columns:
        cursor.execute("ALTER TABLE settings ADD COLUMN position TEXT")
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if not email.endswith(f"@{ALLOWED_DOMAIN}"):
            flash(f"Only {ALLOWED_DOMAIN} emails allowed.", "danger")
            return redirect(url_for('register'))

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
        except sqlite3.IntegrityError:
            flash("Email already registered.", "warning")
            return redirect(url_for('register'))
        conn.close()
        flash("Registration successful. Login now!", "success")
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, is_admin FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()

        if user and password == user[1]:
            session['email'] = email
            session['uid'] = user[0]
            session['is_admin'] = bool(user[2])
            send_otp_email(email)
            flash("OTP sent to your email.", "info")
            return redirect(url_for('verify_otp'))

        flash("Invalid credentials.", "danger")
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        user_input = request.form['otp']
        if user_input == session.get('otp'):
            # Fetch password from DB
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute("SELECT password FROM users WHERE id = ?", (session['uid'],))
            result = cursor.fetchone()
            conn.close()
            if result:
                password = result[0]
                user_obj = User(session['uid'], session['email'], password, session['is_admin'])
                login_user(user_obj)
                flash("Login successful!", "success")
                return redirect(url_for('admin_dashboard' if user_obj.is_admin else 'user_dashboard'))
            else:
                flash("User not found.", "danger")
                return redirect(url_for('home'))
        else:
            flash("Invalid OTP.", "danger")
            return redirect(url_for('verify_otp'))
    return render_template('otp.html')

@app.route('/user-dashboard')
@login_required
def user_dashboard():
    if current_user.is_admin:
        return redirect(url_for('admin_dashboard'))

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT voting_open, start_time, end_time FROM settings WHERE id = 1")
    setting = cursor.fetchone()
    cursor.execute("SELECT * FROM votes WHERE user_id = ?", (current_user.id,))
    vote_record = cursor.fetchone()
    conn.close()

    voting_open = setting[0]
    return render_template('user_dashboard.html', voting_open=voting_open, voted=bool(vote_record))

@app.route('/vote', methods=['GET', 'POST'])
@login_required
def vote():
    if request.method == 'POST':
        vote = request.form['vote']
        encrypted_vote = encrypt_vote(vote)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO votes (user_id, vote, timestamp) VALUES (?, ?, ?)", (current_user.id, encrypted_vote, now))
        conn.commit()
        conn.close()
        flash("Vote cast successfully!", "success")
        return redirect(url_for('user_dashboard'))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    cursor.execute("SELECT position FROM settings WHERE id=1")
    position = cursor.fetchone()
    conn.close()
    return render_template('vote.html', candidates=candidates, position=position[0] if position else None)

@app.route('/admin-dashboard', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'refresh':
            cursor.execute("DELETE FROM votes")
            cursor.execute("DELETE FROM candidates")
            cursor.execute("UPDATE settings SET position = NULL, voting_open = 0, start_time = NULL, end_time = NULL WHERE id = 1")
            conn.commit()
            flash("Election has been refreshed. All candidates and votes cleared.", "success")
            return redirect(url_for('admin_dashboard'))
        if action == 'set_position':
            position = request.form['position']
            cursor.execute("UPDATE settings SET position = ? WHERE id = 1", (position,))
            conn.commit()
        if action == 'start':
            start_time = request.form['start_time']
            end_time = request.form['end_time']
            cursor.execute("DELETE FROM votes")
            cursor.execute("UPDATE settings SET voting_open = 1, start_time = ?, end_time = ? WHERE id = 1", (start_time, end_time))
        elif action == 'end':
            cursor.execute("UPDATE settings SET voting_open = 0 WHERE id = 1")
        elif action == 'declare_results':
            # Just a placeholder, you can add extra logic if needed
            flash("Results declared!", "success")
        conn.commit()

    # --- Auto-close voting if end_time has passed ---
    cursor.execute("SELECT voting_open, start_time, end_time, position FROM settings WHERE id=1")
    settings = cursor.fetchone()
    voting_open, start_time, end_time, position = settings
    if voting_open and end_time:
        now = datetime.now()
        try:
            end_dt = datetime.strptime(end_time, "%Y-%m-%dT%H:%M")
        except ValueError:
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        if now > end_dt:
            cursor.execute("UPDATE settings SET voting_open = 0 WHERE id = 1")
            conn.commit()
            voting_open = 0
            settings = (voting_open, start_time, end_time, position)
            flash("Voting has ended automatically as the end time passed.", "info")

    cursor.execute("SELECT email FROM users")
    users = cursor.fetchall()
    cursor.execute("SELECT vote FROM votes")
    votes = cursor.fetchall()
    decrypted_votes = [decrypt_vote(v[0]) for v in votes]
    vote_count = {}
    for v in decrypted_votes:
        if v in vote_count:
            vote_count[v] += 1
        else:
            vote_count[v] = 1
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    conn.close()

    # Pass a flag to show the "Declare Results" button if voting is closed
    show_declare = not voting_open and votes

    return render_template(
        'admin_dashboard.html',
        users=users,
        votes=decrypted_votes,
        settings=settings,
        vote_count=vote_count,
        candidates=candidates,
        show_declare=show_declare
    )

@app.route('/manage-candidates', methods=['GET', 'POST'])
@login_required
def manage_candidates():
    if not current_user.is_admin:
        return redirect(url_for('user_dashboard'))
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            candidate_name = request.form['candidate_name']
            cursor.execute("INSERT INTO candidates (name) VALUES (?)", (candidate_name,))
        elif action == 'delete':
            candidate_id = request.form['candidate_id']
            cursor.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        conn.commit()
    cursor.execute("SELECT * FROM candidates")
    candidates = cursor.fetchall()
    conn.close()
    return render_template('manage_candidates.html', candidates=candidates)

@app.route('/results')
@login_required
def results():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT voting_open FROM settings WHERE id=1")
    voting_open = cursor.fetchone()[0]
    cursor.execute("SELECT vote FROM votes")
    votes = cursor.fetchall()
    conn.close()
    
    decrypted_votes = [decrypt_vote(v[0]) for v in votes]
    vote_count = dict(Counter(decrypted_votes))

    # Only allow access if voting is closed or user is admin
    if voting_open and not current_user.is_admin:
        flash("Results will be available after voting ends.", "warning")
        return redirect(url_for('user_dashboard'))

    return render_template('results.html', vote_count=vote_count)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()  # This ensures your database and tables are created before the app runs
    app.run(debug=True)

