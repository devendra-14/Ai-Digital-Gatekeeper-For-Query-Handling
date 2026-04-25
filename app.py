import traceback
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from config import *
from database import db
from classifier import classifier

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.config['SECRET_KEY'] = JWT_SECRET_KEY


# ════════════════════════════════════════════════════════════════
#  EMAIL AUTO-REPLY
# ════════════════════════════════════════════════════════════════

def send_resolution_email(query):
    """Send auto-reply email to student when query is Resolved/Closed."""
    if not SMTP_USER or not SMTP_PASS:
        print("⚠️  SMTP not configured — skipping auto email")
        return False
    try:
        student_email = query['student_email']
        student_name  = query['student_name']
        subject_line  = query.get('subject', 'Your Query')
        status        = query.get('status', 'Resolved')
        remedy        = query.get('suggested_remedy', '')
        admin_notes   = query.get('admin_notes') or ''
        department    = query.get('department', 'Student Affairs')
        category      = query.get('category', 'N/A')

        body = f"""Dear {student_name},

Your query has been {status.lower()} by our administration team.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Query Details
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subject    : {subject_line}
Category   : {category}
Department : {department}
Status     : {status}

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
        msg['From']    = f"{SMTP_FROM_NAME} <{SMTP_USER}>"
        msg['To']      = student_email
        msg['Subject'] = f"[{status}] Your Query: {subject_line}"
        msg.attach(MIMEText(body, 'plain'))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)

        db.mark_email_sent(query['id'])
        print(f"✅ Resolution email sent to {student_email}")
        return True
    except Exception as e:
        print(f"❌ Email error: {e}")
        return False


# ════════════════════════════════════════════════════════════════
#  AUTH DECORATORS
# ════════════════════════════════════════════════════════════════

def token_required(f):
    """Validates JWT. Passes current_admin as first argument."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '')
        if not token:
            return jsonify({'error': 'Token missing — please login'}), 401
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            data          = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
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
    """Must be stacked AFTER @token_required.
    Only role='admin' can proceed; sub_admin gets 403."""
    @wraps(f)
    def decorated(current_admin, *args, **kwargs):
        if current_admin.get('role') != 'admin':
            return jsonify({'error': 'Full admin access required for this action'}), 403
        return f(current_admin, *args, **kwargs)
    return decorated


# ════════════════════════════════════════════════════════════════
#  FRONTEND
# ════════════════════════════════════════════════════════════════

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception:
        return f"<pre>{traceback.format_exc()}</pre>", 500


# ════════════════════════════════════════════════════════════════
#  ADMIN AUTH
# ════════════════════════════════════════════════════════════════

@app.route('/api/admin/login', methods=['POST'])
def login_admin():
    """Public endpoint — any admin/sub_admin can login."""
    try:
        data  = request.json or {}
        admin = db.get_admin_by_username(data.get('username', ''))
        if not admin or not check_password_hash(admin['password_hash'], data.get('password', '')):
            return jsonify({'error': 'Invalid username or password'}), 401
        token = jwt.encode(
            {'admin_id': admin['id'],
             'exp': datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)},
            JWT_SECRET_KEY, algorithm=JWT_ALGORITHM
        )
        return jsonify({
            'access_token': token,
            'admin': {
                'id':       admin['id'],
                'username': admin['username'],
                'email':    admin['email'],
                'role':     admin.get('role', 'sub_admin'),
            }
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/me', methods=['GET'])
@token_required
def get_me(current_admin):
    return jsonify({
        'id':       current_admin['id'],
        'username': current_admin['username'],
        'email':    current_admin['email'],
        'role':     current_admin.get('role', 'sub_admin'),
    })


# ════════════════════════════════════════════════════════════════
#  TEAM MANAGEMENT  (admin only — sub_admin cannot access)
# ════════════════════════════════════════════════════════════════

@app.route('/api/admin/register', methods=['POST'])
@token_required
@admin_only
def register_admin(current_admin):
    """Create a new admin or sub_admin account.
    Only logged-in full admins can do this — students/public cannot."""
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
    """Get all admins/sub-admins — admin only."""
    try:
        team = db.get_all_admins()
        return jsonify(team)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/team/<member_id>', methods=['DELETE'])
@token_required
@admin_only
def remove_team_member(current_admin, member_id):
    """Remove a team member — admin only. Cannot remove self."""
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
#  QUERIES — STUDENT SUBMIT (public, no login)
# ════════════════════════════════════════════════════════════════

@app.route('/api/queries', methods=['POST'])
def create_query():
    """Public endpoint — students submit queries without login."""
    try:
        data = request.json or {}
        if not data.get('student_name') or not data.get('student_email') or not data.get('message'):
            return jsonify({'error': 'Name, email and message are required'}), 400

        ai_result = classifier.classify_query(
            data.get('subject', ''),
            data['message']
        )
        query = db.create_query({
            'student_name':     data['student_name'],
            'student_email':    data['student_email'],
            'enrollment_no':    data.get('enrollment_no', ''),
            'division':         data.get('division', ''),
            'subject':          data.get('subject', ''),
            'message':          data['message'],
            'category':         ai_result['category'],
            'priority':         ai_result['priority'],
            'department':       ai_result.get('department', 'Student Affairs'),
            'ai_analysis':      ai_result['analysis'],
            'suggested_remedy': ai_result['remedy'],
            'is_policy':        ai_result.get('is_policy', False),
        })
        return jsonify(query), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ════════════════════════════════════════════════════════════════
#  QUERIES — ADMIN ENDPOINTS (token required)
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
                'data':   [stats.get('pending_queries',0), stats.get('in_progress_queries',0),
                           stats.get('escalated_queries',0), stats.get('resolved_queries',0),
                           stats.get('closed_queries',0), stats.get('rejected_queries',0)],
                'colors': ['#f59e0b','#6366f1','#ef4444','#10b981','#6b7280','#f87171']
            },
            'priority': {
                'labels': ['Critical','High','Medium','Low'],
                'data':   [stats.get('critical_count',0), stats.get('high_priority_count',0),
                           stats.get('medium_priority_count',0), stats.get('low_priority_count',0)],
                'colors': ['#ef4444','#f59e0b','#6366f1','#10b981']
            },
            'category': {
                'labels': [c[0] for c in sorted(stats.get('category_breakdown',{}).items(), key=lambda x:x[1], reverse=True)[:8]],
                'data':   [c[1] for c in sorted(stats.get('category_breakdown',{}).items(), key=lambda x:x[1], reverse=True)[:8]],
                'colors': ['#6366f1','#8b5cf6','#06b6d4','#10b981','#f59e0b','#ef4444','#ec4899','#84cc16']
            },
            'department': {
                'labels': [d[0] for d in sorted(stats.get('department_breakdown',{}).items(), key=lambda x:x[1], reverse=True)[:6]],
                'data':   [d[1] for d in sorted(stats.get('department_breakdown',{}).items(), key=lambda x:x[1], reverse=True)[:6]],
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

        # Merge admin_notes into the query object for email
        if 'admin_notes' in update_data:
            q['admin_notes'] = update_data['admin_notes']

        # ── Auto-email on first resolution ──────────────────────
        if new_status in ['Resolved', 'Closed'] and was_pending and not q.get('email_sent'):
            q['status'] = new_status
            send_resolution_email(q)
            update_data['email_sent'] = True
            # Give credit to resolver
            db.increment_resolved(current_admin['id'])

        db.update_query(query_id, update_data)
        return jsonify({'message': 'Updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/queries/<query_id>', methods=['DELETE'])
@token_required
@admin_only
def delete_query(current_admin, query_id):
    """Only full admin can delete queries — sub_admin cannot."""
    try:
        return jsonify({'message': 'Deleted'}) if db.delete_query(query_id) \
            else (jsonify({'error': 'Not found'}), 404)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'app': 'ai_digital_gatekeeper'})


# ════════════════════════════════════════════════════════════════
#  STARTUP — Create default admin if DB is empty
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
        print("  ✅ Default admin account created!")
        print("  Username : admin")
        print("  Password : Admin@123")
        print("  ⚠️  Please change the password immediately!")
        print("=" * 52)


if __name__ == '__main__':
    create_default_admin()
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=True)
