import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from config import *
from database import db
from classifier import classifier

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.config['SECRET_KEY'] = JWT_SECRET_KEY

IST = timezone(timedelta(hours=5, minutes=30))


# ════════════════════════════════════════════════════════════════
# EMAIL AUTO-REPLY
# ════════════════════════════════════════════════════════════════

def send_resolution_email(query):
    """Send auto-reply email to student when query is Resolved/Closed."""

    # ── Validate config ──────────────────────────────────────────
    if not SMTP_USER or not SMTP_PASS:
        print("❌ EMAIL FAILED: SMTP_USER or SMTP_PASS is empty in .env file")
        print(f" SMTP_USER = '{SMTP_USER}'")
        print(f" SMTP_PASS = '{'*' * len(SMTP_PASS) if SMTP_PASS else 'EMPTY'}'")
        return False

    try:
        student_email = query.get('student_email', '').strip()
        student_name = query.get('student_name', 'Student')
        subject_line = query.get('subject', 'Your Query')
        status = query.get('status', 'Resolved')
        remedy = query.get('suggested_remedy', 'Please visit the relevant department.')
        admin_notes = query.get('admin_notes') or ''
        department = query.get('department', 'Student Affairs')
        category = query.get('category', 'N/A')

        if not student_email:
            print("❌ EMAIL FAILED: student_email is empty")
            return False

        print(f"📧 Sending email to: {student_email}")
        print(f" SMTP Host : {SMTP_HOST}:{SMTP_PORT}")
        print(f" From : {SMTP_USER}")

        body = f"""Dear {student_name},

Your query has been {status.lower()} by our administration team.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Query Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject : {subject_line}
Category : {category}
Department : {department}
Status : {status}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Resolution / Action Steps
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{remedy}

{('Administrator Note:\n' + admin_notes) if admin_notes.strip() else ''}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
If your issue is still not resolved, please submit a new query
through the portal and reference this query.

Regards,
AI Digital Gatekeeper Team
{COLLEGE_NAME}
"""

        msg = MIMEMultipart('alternative')
        msg['From'] = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg['To'] = student_email
        msg['Subject'] = f"[{status}] Your Query: {subject_line}"
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # ── Gmail SMTP with full debug ───────────────────────────
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30)
        server.set_debuglevel(0) # set to 1 if you want raw SMTP logs
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, [student_email], msg.as_string())
        server.quit()

        db.mark_email_sent(query['id'])
        print(f"✅ Resolution email sent successfully to {student_email}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("❌ EMAIL FAILED: Gmail authentication error!")
        print(" Fix: Go to Google Account → Security → App Passwords")
        print(" Generate a NEW 16-character App Password and paste in .env as SMTP_PASS")
        print(" Make sure 2-Step Verification is ON for your Gmail account")
        return False

    except smtplib.SMTPRecipientsRefused as e:
        print(f"❌ EMAIL FAILED: Recipient email refused — {e}")
        return False

    except smtplib.SMTPException as e:
        print(f"❌ EMAIL FAILED (SMTP error): {e}")
        traceback.print_exc()
        return False

    except Exception as e:
        print(f"❌ EMAIL FAILED (unexpected error): {e}")
        traceback.print_exc()
        return False


# ════════════════════════════════════════════════════════════════
# AUTH DECORATORS
# ════════════════════════════════════════════════════════════════

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if not token:
            return jsonify({'error': 'Token missing — please login'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            current_admin = db.get_admin_by_id(data['admin_id'])
            if not current_admin:
                return jsonify({'error': 'Admin account not found'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Session expired — please login again'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Invalid token'}), 401
        return f(current_admin, *args, **kwargs)
    return decorated


def admin_only(f):
    @wraps(f)
    def decorated(current_admin, *args, **kwargs):
        if current_admin.get('role') != 'admin':
            return jsonify({'error': 'Full admin access required for this action'}), 403
        return f(current_admin, *args, **kwargs)
    return decorated


# ════════════════════════════════════════════════════════════════
# FRONTEND
# ════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500


# ════════════════════════════════════════════════════════════════
# ADMIN AUTH
# ════════════════════════════════════════════════════════════════

@app.route('/api/admin/login', methods=['POST'])
def login_admin():
    try:
        data = request.json or {}
        admin = db.get_admin_by_username(data.get('username', ''))
        if not admin or not check_password_hash(admin['password_hash'], data.get('password', '')):
            return jsonify({'error': 'Invalid username or password'}), 401
        token = jwt.encode(
            {'admin_id': admin['id'],
             'exp': datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)},
            JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        )
        return jsonify({
            'access_token': token,
            'admin': {
                'id': admin['id'],
                'username': admin['username'],
                'email': admin['email'],
                'role': admin.get('role', 'sub_admin'),
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/me', methods=['GET'])
@token_required
def get_me(current_admin):
    return jsonify({
        'id': current_admin['id'],
        'username': current_admin['username'],
        'email': current_admin['email'],
        'role': current_admin.get('role', 'sub_admin'),
    })


# ════════════════════════════════════════════════════════════════
# TEAM MANAGEMENT
# ════════════════════════════════════════════════════════════════

@app.route('/api/admin/register', methods=['POST'])
@token_required
@admin_only
def register_admin(current_admin):
    try:
        data = request.json or {}
        if not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password are required'}), 400
        if db.get_admin_by_username(data['username']):
            return jsonify({'error': 'Username already exists'}), 400
        role = data.get('role', 'sub_admin')
        if role not in ['admin', 'sub_admin']:
            role = 'sub_admin'
        admin_id = db.create_admin(
            data['username'],
            data.get('email', ''),
            generate_password_hash(data['password']),
            role=role,
            created_by=current_admin['username']
        )
        return jsonify({'message': f'{role} account created', 'admin_id': admin_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/team', methods=['GET'])
@token_required
@admin_only
def get_team(current_admin):
    try:
        return jsonify(db.get_all_admins())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/team/<member_id>', methods=['DELETE'])
@token_required
@admin_only
def remove_team_member(current_admin, member_id):
    try:
        if member_id == current_admin['id']:
            return jsonify({'error': 'You cannot remove your own account'}), 400
        result = db.delete_admin(member_id)
        if result:
            return jsonify({'message': 'Team member removed successfully'})
        return jsonify({'error': 'Admin not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════════════════
# QUERIES — STUDENT SUBMIT (public)
# ════════════════════════════════════════════════════════════════

@app.route('/api/queries', methods=['POST'])
def create_query():
    try:
        data = request.json or {}
        if not data.get('student_name') or not data.get('student_email') or not data.get('message'):
            return jsonify({'error': 'Name, email and message are required'}), 400

        ai_result = classifier.classify_query(
            data.get('subject', ''),
            data['message']
        )
        query = db.create_query({
            'student_name': data['student_name'],
            'student_email': data['student_email'],
            'enrollment_no': data.get('enrollment_no', ''),
            'division': data.get('division', ''),
            'subject': data.get('subject', ''),
            'message': data['message'],
            'category': ai_result['category'],
            'priority': ai_result['priority'],
            'department': ai_result.get('department', 'Student Affairs'),
            'ai_analysis': ai_result['analysis'],
            'suggested_remedy': ai_result['remedy'],
            'is_policy': ai_result.get('is_policy', False),
        })
        return jsonify(query), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════════════════
# QUERIES — ADMIN ENDPOINTS
# ════════════════════════════════════════════════════════════════

@app.route('/api/queries', methods=['GET'])
@token_required
def get_queries(current_admin):
    try:
        filters = {}
        for k in ['status', 'priority', 'category', 'department']:
            if request.args.get(k):
                filters[k] = request.args.get(k)
        return jsonify(db.get_all_queries(filters))
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/queries/stats/overview', methods=['GET'])
@token_required
def get_stats(current_admin):
    try:
        return jsonify(db.get_query_stats())
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/queries/stats/charts', methods=['GET'])
@token_required
def get_charts(current_admin):
    try:
        stats = db.get_query_stats()
        return jsonify({
            'status': {
                'labels': ['Pending','In Progress','Escalated','Resolved','Closed','Rejected'],
                'data': [stats.get('pending_queries',0), stats.get('in_progress_queries',0),
                           stats.get('escalated_queries',0), stats.get('resolved_queries',0),
                           stats.get('closed_queries',0), stats.get('rejected_queries',0)],
                'colors': ['#f59e0b','#6366f1','#ef4444','#10b981','#6b7280','#f87171']
            },
            'priority': {
                'labels': ['Critical','High','Medium','Low'],
                'data': [stats.get('critical_count',0), stats.get('high_priority_count',0),
                           stats.get('medium_priority_count',0), stats.get('low_priority_count',0)],
                'colors': ['#ef4444','#f59e0b','#6366f1','#10b981']
            },
            'category': {
                'labels': [c[0] for c in sorted(stats.get('category_breakdown',{}).items(), key=lambda x:x[1], reverse=True)[:8]],
                'data': [c[1] for c in sorted(stats.get('category_breakdown',{}).items(), key=lambda x:x[1], reverse=True)[:8]],
                'colors': ['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#84cc16']
            },
            'department': {
                'labels': [d[0] for d in sorted(stats.get('department_breakdown',{}).items(), key=lambda x:x[1], reverse=True)[:6]],
                'data': [d[1] for d in sorted(stats.get('department_breakdown',{}).items(), key=lambda x:x[1], reverse=True)[:6]],
                'colors': ['#6366f1','#f59e0b','#10b981','#ef4444','#8b5cf6','#06b6d4']
            },
            'trend': db.get_daily_trend(7)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/queries/<query_id>', methods=['GET'])
@token_required
def get_query(current_admin, query_id):
    try:
        q = db.get_query_by_id(query_id)
        return jsonify(q) if q else (jsonify({'error': 'Not found'}), 404)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/queries/<query_id>', methods=['PATCH'])
@token_required
def update_query(current_admin, query_id):
    """
    Both admin and sub_admin can update queries.
    Auto-email fires when status changes to Resolved or Closed.
    """
    try:
        q = db.get_query_by_id(query_id)
        if not q:
            return jsonify({'error': 'Query not found'}), 404

        update_data = dict(request.json or {})
        update_data['updated_by'] = current_admin['username']

        new_status = update_data.get('status', '')
        was_pending = q.get('status') not in ['Resolved', 'Closed', 'Rejected']

        # Merge admin_notes into query object for email body
        if 'admin_notes' in update_data:
            q['admin_notes'] = update_data['admin_notes']

        # ── Auto-email on first resolution ───────────────────────
        if new_status in ['Resolved', 'Closed'] and was_pending and not q.get('email_sent'):
            q['status'] = new_status
            email_sent = send_resolution_email(q)
            update_data['email_sent'] = email_sent
            db.increment_resolved(current_admin['id'])

        db.update_query(query_id, update_data)
        return jsonify({'message': 'Updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/queries/<query_id>', methods=['DELETE'])
@token_required
@admin_only
def delete_query(current_admin, query_id):
    try:
        return jsonify({'message': 'Deleted'}) if db.delete_query(query_id) \
            else (jsonify({'error': 'Not found'}), 404)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'app': 'ai_digital_gatekeeper'})


# ════════════════════════════════════════════════════════════════
# EMAIL TEST ENDPOINT ← use this to verify email works
# ════════════════════════════════════════════════════════════════

@app.route('/api/test-email', methods=['GET'])
@token_required
def test_email(current_admin):
    """
    Hit this endpoint to test if email is working.
    GET /api/test-email (with admin JWT token)
    A test email will be sent to SMTP_USER itself.
    """
    test_query = {
        'id': 'test-001',
        'student_name': 'Test Student',
        'student_email': SMTP_USER, # sends to your own Gmail
        'subject': 'Test Query',
        'category': 'Others',
        'department': 'Student Affairs',
        'status': 'Resolved',
        'suggested_remedy': 'This is a test email to verify SMTP is working correctly.',
        'admin_notes': 'Sent from /api/test-email endpoint',
        'email_sent': False,
    }
    success = send_resolution_email(test_query)
    if success:
        return jsonify({'message': f'✅ Test email sent to {SMTP_USER} — check your inbox!'})
    else:
        return jsonify({'error': '❌ Email failed — check terminal/console for exact error'}), 500


# ════════════════════════════════════════════════════════════════
# STARTUP
# ════════════════════════════════════════════════════════════════

def create_default_admin():
    if db.admins.count_documents({}) == 0:
        db.create_admin(
            username='admin',
            email='admin@silveroakuni.ac.in',
            password_hash=generate_password_hash('Admin@123'),
            role='admin',
            created_by='system'
        )
        print("=" * 52)
        print(" ✅ Default admin account created!")
        print(" Username : admin")
        print(" Password : Admin@123")
        print(" ⚠️ Please change the password immediately!")
        print("=" * 52)


if __name__ == '__main__':
    create_default_admin()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)

