from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
from config import MONGO_URL, DB_NAME


class Database:
    def __init__(self):
        try:
            self.client = MongoClient(MONGO_URL, serverSelectionTimeoutMS=5000)
            self.db     = self.client[DB_NAME]
            self.admins  = self.db.admins
            self.queries = self.db.queries
            self.client.server_info()
            print("✅ MongoDB Connected!")
        except Exception as e:
            print(f"❌ MongoDB Error: {e}")
            raise e

    # ── ADMIN MANAGEMENT ─────────────────────────────────────────

    def create_admin(self, username, email, password_hash,
                     role='sub_admin', created_by='system'):
        """
        role: 'admin' (full access) | 'sub_admin' (view + update, no delete/team mgmt)
        """
        admin = {
            'id':            str(uuid.uuid4()),
            'username':      username,
            'email':         email,
            'password_hash': password_hash,
            'role':          role,
            'created_by':    created_by,
            'created_at':    datetime.utcnow().isoformat(),
            'queries_resolved': 0,
        }
        self.admins.insert_one(admin)
        return admin['id']

    def get_admin_by_username(self, username):
        return self.admins.find_one({'username': username}, {'_id': 0})

    def get_admin_by_id(self, admin_id):
        return self.admins.find_one({'id': admin_id}, {'_id': 0})

    def get_all_admins(self):
        """Return all admins/sub-admins (without password hash)."""
        return list(self.admins.find(
            {},
            {'_id': 0, 'password_hash': 0}
        ).sort('created_at', 1))

    def delete_admin(self, admin_id):
        result = self.admins.delete_one({'id': admin_id})
        return result.deleted_count > 0

    def increment_resolved(self, admin_id):
        self.admins.update_one(
            {'id': admin_id},
            {'$inc': {'queries_resolved': 1}}
        )

    # ── QUERY CRUD ───────────────────────────────────────────────

    def create_query(self, data):
        query = {
            'id':               str(uuid.uuid4()),
            'student_name':     data['student_name'],
            'student_email':    data['student_email'],
            'enrollment_no':    data.get('enrollment_no', ''),
            'division':         data.get('division', ''),
            'subject':          data.get('subject', ''),
            'message':          data['message'],
            'category':         data.get('category', 'Others'),
            'priority':         data.get('priority', 'Medium'),
            'department':       data.get('department', 'Student Affairs'),
            'status':           'Pending',
            'ai_analysis':      data.get('ai_analysis', ''),
            'suggested_remedy': data.get('suggested_remedy', ''),
            'is_policy':        data.get('is_policy', False),
            'admin_notes':      None,
            'updated_by':       None,
            'email_sent':       False,
            'created_at':       datetime.utcnow().isoformat(),
            'updated_at':       datetime.utcnow().isoformat(),
            'resolved_at':      None,
        }
        self.queries.insert_one(query)
        query.pop('_id', None)
        return query

    def get_all_queries(self, filters=None):
        qf = filters if filters else {}
        return list(self.queries.find(qf, {'_id': 0}).sort('created_at', -1))

    def get_query_by_id(self, query_id):
        return self.queries.find_one({'id': query_id}, {'_id': 0})

    def update_query(self, query_id, update_data):
        update_data['updated_at'] = datetime.utcnow().isoformat()
        if update_data.get('status') in ['Resolved', 'Closed']:
            update_data['resolved_at'] = datetime.utcnow().isoformat()
        self.queries.update_one({'id': query_id}, {'$set': update_data})
        return True

    def mark_email_sent(self, query_id):
        self.queries.update_one({'id': query_id}, {'$set': {'email_sent': True}})

    def delete_query(self, query_id):
        return self.queries.delete_one({'id': query_id}).deleted_count > 0

    def get_query_stats(self):
        all_q = list(self.queries.find({}, {'_id': 0}))
        stats = {
            'total_queries':        len(all_q),
            'pending_queries':      len([q for q in all_q if q['status'] == 'Pending']),
            'in_progress_queries':  len([q for q in all_q if q['status'] == 'In Progress']),
            'escalated_queries':    len([q for q in all_q if q['status'] == 'Escalated']),
            'resolved_queries':     len([q for q in all_q if q['status'] == 'Resolved']),
            'closed_queries':       len([q for q in all_q if q['status'] == 'Closed']),
            'rejected_queries':     len([q for q in all_q if q['status'] == 'Rejected']),
            'critical_count':       len([q for q in all_q if q['priority'] == 'Critical']),
            'high_priority_count':  len([q for q in all_q if q['priority'] == 'High']),
            'medium_priority_count':len([q for q in all_q if q['priority'] == 'Medium']),
            'low_priority_count':   len([q for q in all_q if q['priority'] == 'Low']),
            'category_breakdown':   {},
            'department_breakdown': {},
        }
        for q in all_q:
            cat  = q.get('category', 'Others')
            dept = q.get('department', 'Student Affairs')
            stats['category_breakdown'][cat]   = stats['category_breakdown'].get(cat, 0) + 1
            stats['department_breakdown'][dept] = stats['department_breakdown'].get(dept, 0) + 1
        return stats

    def get_daily_trend(self, days=7):
        result = {'labels': [], 'data': []}
        today  = datetime.utcnow().date()
        for i in range(days - 1, -1, -1):
            day       = today - timedelta(days=i)
            day_str   = day.strftime('%b %d')
            day_start = datetime.combine(day, datetime.min.time()).isoformat()
            day_end   = datetime.combine(day, datetime.max.time()).isoformat()
            count     = self.queries.count_documents(
                {'created_at': {'$gte': day_start, '$lte': day_end}}
            )
            result['labels'].append(day_str)
            result['data'].append(count)
        return result


db = Database()
