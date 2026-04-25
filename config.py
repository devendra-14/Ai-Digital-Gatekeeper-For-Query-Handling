import os
from dotenv import load_dotenv
load_dotenv()

# MongoDB Atlas
MONGO_URL = os.getenv('MONGO_URL', 'mongodb+srv://admin:Silveroak123@cluster0.lgxvgfh.mongodb.net/?appName=Cluster0')
DB_NAME   = os.getenv('DB_NAME', 'ai_digital_gatekeeper_db')

# Gemini AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyAWU7kYjXQNHx4Og_JVqo5DWk0Ug3SapGc3')

# JWT
JWT_SECRET_KEY       = os.getenv('JWT_SECRET_KEY', 'gatekeeper_secret_2024')
JWT_ALGORITHM        = "HS256"
JWT_EXPIRATION_HOURS = 24

# Flask
FLASK_PORT = int(os.getenv('PORT', 5000))
FLASK_HOST = '0.0.0.0'
DEBUG_MODE = os.getenv('DEBUG', 'False') == 'True'

# ── SMTP Email (for auto-reply when query resolved) ────────────
# Use Gmail: enable 2FA → generate App Password → paste below
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', '')          # Your Gmail address
SMTP_PASS = os.getenv('SMTP_PASS', '')          # Gmail App Password (16 chars)
SMTP_FROM_NAME = os.getenv('SMTP_FROM_NAME', 'AI Digital Gatekeeper')
COLLEGE_NAME   = os.getenv('COLLEGE_NAME', 'Silver Oak University')

# ── College Contact Info ───────────────────────────────────────
COLLEGE_EMAIL = os.getenv('COLLEGE_EMAIL', 'admin@silveroak.edu.in')
COLLEGE_PHONE = os.getenv('COLLEGE_PHONE', '1800-XXX-XXXX')

QUERY_CATEGORIES = [
    'Attendance Issues','Exam Related','Result / Marksheet Issue',
    'Internal Marks Dispute','Re-evaluation Request','Backlog / Compartment',
    'Assignment / Project Submission','Course Registration Problem',
    'Timetable / Schedule Issue','Lab Access Problem',
    'Bonafide Certificate','Transfer Certificate (TC)','Migration Certificate',
    'Character Certificate','No Objection Certificate (NOC)','ID Card Issue',
    'Degree / Provisional Certificate','Document Verification',
    'Fee Related','Scholarship Issue','Refund Request',
    'Fine / Penalty Dispute','Bank / Demand Draft Issue',
    'Medical Issues','Mental Health / Counseling',
    'Ragging / Harassment Complaint','Grievance / Complaint','Insurance Claim',
    'Hostel / Accommodation','Mess / Canteen Issue','Classroom / Infrastructure',
    'Washroom / Hygiene Issue','Electricity / Water Problem',
    'Wi-Fi / Internet Issue','Parking Issue','Technical Support',
    'ERP / Portal Login Issue','Email / Account Access',
    'Online Exam Technical Problem','Software / Lab System Issue',
    'Placement / Internship','Resume / Profile Help','Industry Visit Query',
    'Higher Education / Gap Year','Entrepreneurship / Startup Support',
    'Sports / Extra-curricular','Cultural Event Query','Club / Society Membership',
    'Competition / Hackathon Support','NSS / NCC Issue',
    'Transport / Bus Pass','Bus Route Issue','Library Issues',
    'Book Issue / Return','Digital Library Access','Late Fine Dispute',
    'Faculty / Staff Complaint','Discrimination Complaint','Others'
]

PRIORITY_LEVELS = ['Low', 'Medium', 'High', 'Critical']
STATUS_OPTIONS  = ['Pending', 'In Progress', 'Escalated', 'Resolved', 'Closed', 'Rejected']

CATEGORY_TO_DEPARTMENT = {
    'Attendance Issues':'Academic Office','Exam Related':'Examination Cell',
    'Result / Marksheet Issue':'Examination Cell','Internal Marks Dispute':'Department Office',
    'Re-evaluation Request':'Examination Cell','Backlog / Compartment':'Examination Cell',
    'Assignment / Project Submission':'Department Office',
    'Course Registration Problem':'Academic Office','Timetable / Schedule Issue':'Academic Office',
    'Lab Access Problem':'Department Office','Bonafide Certificate':'Administrative Office',
    'Transfer Certificate (TC)':'Administrative Office','Migration Certificate':'Administrative Office',
    'Character Certificate':'Administrative Office','No Objection Certificate (NOC)':'Administrative Office',
    'ID Card Issue':'Administrative Office','Degree / Provisional Certificate':'Examination Cell',
    'Document Verification':'Administrative Office','Fee Related':'Accounts Office',
    'Scholarship Issue':'Scholarship Cell','Refund Request':'Accounts Office',
    'Fine / Penalty Dispute':'Accounts Office','Bank / Demand Draft Issue':'Accounts Office',
    'Medical Issues':'Medical / Health Center','Mental Health / Counseling':'Student Counseling Cell',
    'Ragging / Harassment Complaint':'Anti-Ragging Committee','Grievance / Complaint':'Grievance Cell',
    'Insurance Claim':'Administrative Office','Hostel / Accommodation':'Hostel Office',
    'Mess / Canteen Issue':'Hostel Office','Classroom / Infrastructure':'Estate / Maintenance',
    'Washroom / Hygiene Issue':'Estate / Maintenance','Electricity / Water Problem':'Estate / Maintenance',
    'Wi-Fi / Internet Issue':'IT Department','Parking Issue':'Security Office',
    'Technical Support':'IT Department','ERP / Portal Login Issue':'IT Department',
    'Email / Account Access':'IT Department','Online Exam Technical Problem':'IT Department',
    'Software / Lab System Issue':'IT Department','Placement / Internship':'Training & Placement Cell',
    'Resume / Profile Help':'Training & Placement Cell','Industry Visit Query':'Training & Placement Cell',
    'Higher Education / Gap Year':'Student Affairs','Entrepreneurship / Startup Support':'Entrepreneurship Cell',
    'Sports / Extra-curricular':'Sports Department','Cultural Event Query':'Student Affairs',
    'Club / Society Membership':'Student Affairs','Competition / Hackathon Support':'Student Affairs',
    'NSS / NCC Issue':'NSS/NCC Cell','Transport / Bus Pass':'Transport Office',
    'Bus Route Issue':'Transport Office','Library Issues':'Library',
    'Book Issue / Return':'Library','Digital Library Access':'Library',
    'Late Fine Dispute':'Library','Faculty / Staff Complaint':'Principal / Dean Office',
    'Discrimination Complaint':'Grievance Cell','Others':'Student Affairs'
}
