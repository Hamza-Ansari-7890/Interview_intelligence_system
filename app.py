from flask import Flask, render_template, request, session, redirect, url_for, jsonify, flash
from functools import wraps
from itertools import zip_longest
from database.init_db import init_db
from config import get_connection
import os
from dotenv import load_dotenv
import csv
import io

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize database only when explicitly requested (avoid dropping production DB)
if os.getenv('INIT_DB', 'false').lower() in ('1', 'true') or os.getenv('FLASK_ENV') == 'development':
    init_db()
else:
    print('init_db skipped. Set INIT_DB=1 to initialize the database (this will DROP existing data).')


# -----------------------
# AUTHENTICATION HELPERS
# -----------------------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# -----------------------
# AUTHENTICATION ROUTES
# -----------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, don't show login page
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, username, role, email FROM users WHERE username=%s AND password=%s",
                    (username, password))
        user = cur.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[2]
            session['email'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')


@app.after_request
def add_security_headers(response):
    # Prevent caching so back button cannot show authenticated pages after logout
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# -----------------------
# MAIN ROUTES
# -----------------------
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', username=session.get('username'), role=session.get('role'))


@app.route('/submit-interview', methods=['GET', 'POST'])
@login_required
def submit_interview():
    if request.method == 'POST':
        conn = get_connection()
        cur = conn.cursor()

        # Verify authenticated user still exists in DB
        cur.execute('SELECT id FROM users WHERE id=%s', (session.get('user_id'),))
        if not cur.fetchone():
            conn.close()
            session.clear()
            return jsonify({'success': False, 'error': 'Authenticated user not found in database. Please login again.'}), 400

        # Insert interview submission
        cur.execute("""
            INSERT INTO interview_submissions (user_id, company, role, interview_round, mode, experience_level)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            session['user_id'],
            request.form.get('company'),
            request.form.get('role'),
            request.form.get('interview_round'),
            request.form.get('mode'),
            request.form.get('experience_level')
        ))
        
        submission_id = cur.fetchone()[0]
        
        # Insert questions with topic and answered status
        questions = request.form.getlist('questions')
        topics = request.form.getlist('topics')
        answered_list = request.form.getlist('answered')

        # Use zip_longest to handle missing fields; default topic empty and answered 'No'
        for question, topic, answered in zip_longest(questions, topics, answered_list, fillvalue=None):
            q = (question or '').strip()
            t = (topic or '').strip() if topic is not None else ''
            a = (answered or 'No').strip() if answered is not None else 'No'
            if q:
                # normalize answered to Yes/No
                a_norm = 'Yes' if a.lower().startswith('y') else 'No'
                cur.execute("""
                    INSERT INTO questions (submission_id, question, topic, answered)
                    VALUES (%s, %s, %s, %s)
                """, (submission_id, q, t, a_norm))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'submission_id': submission_id})
    
    return render_template('submit_interview.html')


@app.route('/question-bank')
@login_required
def question_bank():
    # Public question bank: show all submissions/questions but hide user details.
    # Supports optional filters via query params: topic, company, role, answered
    conn = get_connection()
    cur = conn.cursor()

    filters = []
    params = []

    topic = request.args.get('topic')
    company = request.args.get('company')
    role = request.args.get('role')
    answered = request.args.get('answered')

    if topic:
        filters.append("LOWER(q.topic) LIKE LOWER(%s)")
        params.append(f"%{topic}%")
    if company:
        filters.append("LOWER(i.company) LIKE LOWER(%s)")
        params.append(f"%{company}%")
    if role:
        filters.append("LOWER(i.role) LIKE LOWER(%s)")
        params.append(f"%{role}%")
    if answered:
        # accept Yes/No or partial
        filters.append("LOWER(q.answered) = LOWER(%s)")
        params.append(answered)

    where_clause = ''
    if filters:
        where_clause = 'WHERE ' + ' AND '.join(filters)

    query = f"""
        SELECT q.id, q.question, q.topic, q.answered, i.company, i.role, i.created_at
        FROM questions q
        JOIN interview_submissions i ON q.submission_id = i.id
        {where_clause}
        ORDER BY i.created_at DESC, q.id DESC
    """

    cur.execute(query, tuple(params))
    questions = cur.fetchall()
    conn.close()

    # Render the public question bank (no user-identifying info)
    return render_template('question_bank.html', questions=questions, filters={
        'topic': topic or '', 'company': company or '', 'role': role or '', 'answered': answered or ''
    })


@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    conn = get_connection()
    cur = conn.cursor()
    
    # Get total users
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    
    # Get total submissions
    cur.execute("SELECT COUNT(*) FROM interview_submissions")
    total_submissions = cur.fetchone()[0]
    
    # Get total questions
    cur.execute("SELECT COUNT(*) FROM questions")
    total_questions = cur.fetchone()[0]
    
    # Get recent submissions
    cur.execute("""
        SELECT i.id, u.username, i.company, i.role, i.created_at
        FROM interview_submissions i
        JOIN users u ON i.user_id = u.id
        ORDER BY i.created_at DESC
        LIMIT 10
    """)
    
    recent_submissions = cur.fetchall()
    conn.close()
    
    stats = {
        'total_users': total_users,
        'total_submissions': total_submissions,
        'total_questions': total_questions
    }
    
    return render_template('admin_dashboard.html', stats=stats, recent_submissions=recent_submissions)


@app.route('/admin/bulk-update', methods=['GET', 'POST'])
@admin_required
def admin_bulk_update():
    result = {
        'created': 0,
        'updated': 0,
        'errors': []
    }

    if request.method == 'POST':
        uploaded = request.files.get('file')
        if not uploaded:
            flash('No file uploaded', 'error')
            return render_template('admin_bulk_update.html', result=None)

        try:
            content = uploaded.stream.read().decode('utf-8')
            reader = csv.DictReader(io.StringIO(content))
        except Exception as e:
            flash(f'Failed to read file: {e}', 'error')
            return render_template('admin_bulk_update.html', result=None)

        conn = get_connection()
        cur = conn.cursor()

        for i, row in enumerate(reader, start=1):
            try:
                email = (row.get('email') or '').strip()
                if not email:
                    result['errors'].append(f'Row {i}: missing email')
                    continue

                role = (row.get('role') or 'student').strip() or 'student'
                batch = (row.get('batch') or '').strip() or None
                password = (row.get('password') or '').strip() or None

                # Check if user exists
                cur.execute('SELECT id FROM users WHERE email=%s', (email,))
                existing = cur.fetchone()

                if existing:
                    # Update existing user
                    update_fields = []
                    params = []
                    if role is not None:
                        update_fields.append('role=%s')
                        params.append(role)
                    if batch is not None:
                        update_fields.append('batch=%s')
                        params.append(batch)
                    if password is not None and password != '':
                        update_fields.append('password=%s')
                        params.append(password)

                    if update_fields:
                        params.append(email)
                        cur.execute(f"UPDATE users SET {', '.join(update_fields)} WHERE email=%s", tuple(params))
                        result['updated'] += 1
                else:
                    # Create new user (username from email prefix)
                    username = email.split('@')[0]
                    cur.execute(
                        'INSERT INTO users (username, email, password, role, batch) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (email) DO NOTHING RETURNING id',
                        (username, email, password or '', role, batch)
                    )
                    inserted = cur.fetchone()
                    if inserted:
                        result['created'] += 1

            except Exception as e:
                result['errors'].append(f'Row {i}: {str(e)}')

        conn.commit()
        conn.close()

        flash('Bulk update completed', 'success')
        return render_template('admin_bulk_update.html', result=result)

    return render_template('admin_bulk_update.html', result=None)


# -----------------------
# API ENDPOINTS
# -----------------------
@app.route('/api/submissions')
@login_required
def get_submissions():
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, company, role, interview_round, mode, experience_level, created_at
        FROM interview_submissions
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session['user_id'],))
    
    submissions = cur.fetchall()
    conn.close()
    
    return jsonify([{
        'id': s[0],
        'company': s[1],
        'role': s[2],
        'interview_round': s[3],
        'mode': s[4],
        'experience_level': s[5],
        'created_at': str(s[6])
    } for s in submissions])


@app.route('/api/questions/<int:submission_id>')
@login_required
def get_submission_questions(submission_id):
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT q.id, q.question, q.topic, q.answered
        FROM questions q
        JOIN interview_submissions i ON q.submission_id = i.id
        WHERE q.submission_id = %s AND i.user_id = %s
    """, (submission_id, session['user_id']))
    
    questions = cur.fetchall()
    conn.close()
    
    return jsonify([{
        'id': q[0],
        'question': q[1],
        'topic': q[2],
        'answered': q[3]
    } for q in questions])


# -----------------------
# ERROR HANDLERS
# -----------------------
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
