import re
from config import COLLEGE_NAME, COLLEGE_EMAIL, COLLEGE_PHONE

# ── Hinglish / typo normalizer ────────────────────────────────
WORD_MAP = {
    "halticket":"hall ticket","hall tkt":"hall ticket","admitcard":"admit card",
    "hosptal":"hospital","hospitl":"hospital","aksedent":"accident","acident":"accident",
    "emergancy":"emergency","urgant":"urgent","abhi":"right now","aaj":"today",
    "kal":"tomorrow","jaldi":"urgent","kal subah":"tomorrow morning",
    "fess":"fees","feee":"fees","pament":"payment","paymant":"payment",
    "scholrship":"scholarship","attendnce":"attendance","attndance":"attendance",
    "attendence":"attendance","upasthiti":"attendance","exm":"exam","priksha":"exam",
    "resullt":"result","rsult":"result","divison":"division","divsion":"division",
    "documnt":"document","bonafied":"bonafide","marsheet":"marksheet",
    "hostle":"hostel","portl":"portal","nahi":"not","nhi":"not","plz":"please",
}

def clean(text):
    t = (text or "").lower()
    for w, r in WORD_MAP.items():
        t = re.sub(r'\b' + re.escape(w) + r'\b', r, t)
    return t


# ── Fixed policy emails for LOW priority ─────────────────────
LOW_EMAIL = {

"Attendance Query": ("Re: Attendance Query", """Dear {N},

Thank you for writing to us.

As per university policy, attendance records are finalized by the faculty and cannot be altered once recorded. The minimum required attendance is 75% to be eligible for examinations.

If you believe there is a recording error, please:
  1. Submit a written application to your HOD within 3 working days
  2. Attach supporting proof (medical certificate, gate pass, etc.)
  3. Visit: Academic Office – Room 103

You can track your attendance on the student portal anytime.

Regards,
{C} | {E}"""),

"Division / Section Change": ("Re: Division/Section Change Request", """Dear {N},

Thank you for reaching out.

As per university regulations, division/section changes are only permitted during the FIRST WEEK of each semester. That window is currently closed and no changes can be processed.

You may reapply at the start of the next semester.

Academic Office – Room 103 | Office hours: 9AM–5PM Mon–Sat

Regards,
{C} | {E}"""),

"Timetable Query": ("Re: Timetable Query", """Dear {N},

The latest timetable is available on the student portal:
  Portal → Dashboard → Academic Schedule

For any discrepancy, visit Academic Office – Room 103.

Regards,
{C} | {E}"""),

"Result / Marks Query": ("Re: Result/Marks Query", """Dear {N},

Your semester results are available on the university examination portal:
  Portal → Exam → Results → Select Semester

Login with your enrollment number and date of birth.

For portal issues contact IT Helpdesk – Room 108 or helpdesk@college.edu

Regards,
{C} | {E}"""),

"Bonafide Certificate": ("Re: Bonafide Certificate Request", """Dear {N},

Bonafide certificates are issued within 2 working days. To apply:
  1. Visit Admin Office – Room 102
  2. Bring your enrollment card
  3. Submit a written application mentioning the purpose

You will be notified via SMS/email when ready.

Regards,
{C} | {E}"""),

"TC / Migration Certificate": ("Re: TC/Migration Certificate", """Dear {N},

TC/Migration certificates require:
  1. Written application at Admin Office – Room 102
  2. No-Due clearance (Library, Hostel, Accounts, Lab)
  3. Valid college ID

Processing time: 5–7 working days after clearance.

Regards,
{C} | {E}"""),

"Gap Certificate": ("Re: Gap Certificate Request", """Dear {N},

Gap certificates require:
  1. Written application with reason
  2. Self-declaration affidavit (notarized if gap > 1 year)

Visit Admin Office – Room 102. Processing: 3 working days.

Regards,
{C} | {E}"""),

"Duplicate Marksheet": ("Re: Duplicate Marksheet Request", """Dear {N},

For a duplicate marksheet please submit:
  1. Written application
  2. FIR copy if original is lost
  3. Affidavit on stamp paper
  4. Processing fee

Exam Section – Room 201. Processing: 7–10 working days.

Regards,
{C} | {E}"""),

"Name Correction": ("Re: Name Correction Request", """Dear {N},

Name correction requires:
  1. Written application to the Principal
  2. Original ID proof (Aadhar / PAN / Birth Certificate)
  3. Affidavit on stamp paper for major corrections

Subject to university approval. Processing: 10–15 working days.
Visit Admin Office – Room 102.

Regards,
{C} | {E}"""),

"Caution Money Refund": ("Re: Caution Money Refund", """Dear {N},

Caution money refunds are processed after:
  1. Final year completion
  2. All-department clearance certificate
  3. Original caution money receipt

Visit Accounts Office – Room 104. Processing: 15–20 working days.

Regards,
{C} | {E}"""),

"Fine / Penalty": ("Re: Fine/Penalty Inquiry", """Dear {N},

Fine details are in your fee receipt and the student portal under 'Due Fees'.

For disputes, bring your payment proof to:
  Accounts Office – Room 104 | 10AM–4PM Mon–Sat

Regards,
{C} | {E}"""),

"Internship NOC": ("Re: Internship NOC Request", """Dear {N},

NOC letters are issued within 3 working days. Please submit at Placement Cell – Room 110:
  1. Written application with company name, duration and address
  2. Copy of offer/appointment letter
  3. Enrollment card

Regards,
{C} | {E}"""),

"Sports Leave": ("Re: Sports Leave Application", """Dear {N},

Sports leave is granted subject to:
  1. Written application at least 2 days BEFORE the event
  2. Selection certificate from an authorized sports body
  3. HOD and Sports Officer approval

Retroactive applications are NOT accepted.
Sports Officer – Room 115.

Regards,
{C} | {E}"""),

"Cultural / Event Leave": ("Re: Cultural/Event Leave Application", """Dear {N},

Cultural/event leave requires:
  1. Written application at least 2 days in advance
  2. Participation proof signed by Cultural Committee
  3. HOD approval

Retroactive applications are NOT entertained.
Cultural Committee – Room 116.

Regards,
{C} | {E}"""),

"Mess / Food Complaint": ("Re: Mess/Food Complaint", """Dear {N},

Thank you for bringing this to our attention. Your complaint has been noted and will be forwarded to the Hostel Warden for immediate review.

For urgent concerns visit Hostel Office – Ground Floor (8AM–10PM daily).
We will address this within 24 hours.

Regards,
{C} | {E}"""),

"Backlog Exam Problem": ("Re: Backlog Exam Registration", """Dear {N},

Backlog registration is available on the portal during the announced window:
  Portal → Exam → Backlog Registration

If facing a portal error:
  1. Clear browser cache and retry
  2. Use Chrome or Firefox
  3. If issue persists visit Exam Section – Room 201

Please register before the deadline.

Regards,
{C} | {E}"""),

"College Leaving Certificate": ("Re: College Leaving Certificate", """Dear {N},

College Leaving Certificates require:
  1. Written application to the Principal
  2. No-Due clearance from all departments
  3. Original fee receipt of last semester

Admin Office – Room 102. Processing: 3–5 working days.

Regards,
{C} | {E}"""),

"IT / Portal Issue": ("Re: Technical/Portal Issue", """Dear {N},

Please try these steps first:
  1. Clear browser cache (Ctrl + Shift + Del)
  2. Open in incognito/private mode
  3. Use Chrome or Firefox
  4. Check your internet connection

If the issue persists:
  Email: helpdesk@college.edu  |  Visit: IT Helpdesk – Room 108 (9AM–5PM Mon–Sat)
  Please attach a screenshot of the error.

Regards,
{C} | {E}"""),

"Library Issue": ("Re: Library Query", """Dear {N},

For library queries:
  Email: library@college.edu
  Visit: Library – Ground Floor | Mon–Sat 8AM–8PM

Regards,
{C} | {E}"""),

"General Information": ("Re: Your Inquiry", """Dear {N},

Thank you for reaching out. For general information:
  Website: www.college.edu
  Visit:   Admin Office – Room 102 | 9AM–5PM Mon–Sat
  Phone:   {P}

Regards,
{C} | {E}"""),
}

def instant_reply(name: str, category: str) -> dict:
    """Return instant fixed email for Low priority — NO AI needed."""
    first = name.strip().split()[0]
    subj, body = LOW_EMAIL.get(category, LOW_EMAIL["General Information"])
    return {
        "email_subject": subj,
        "auto_reply": body.format(N=first, C=COLLEGE_NAME, E=COLLEGE_EMAIL, P=COLLEGE_PHONE),
        "problem_summary": f"Student query about {category.lower()}.",
    }


# ── Priority detection ────────────────────────────────────────

def detect(subject: str, message: str) -> dict:
    """
    Returns { priority, category, is_low }
    is_low = True  → use instant_reply (no AI)
    is_low = False → send to Gemini AI
    """
    c = clean(subject + " " + message)

    now  = bool(re.search(r'right now|today|tonight|in an hour|this morning|abhi|aaj', c))
    soon = bool(re.search(r'tomorrow|kal subah|next 2 days', c))
    exam = bool(re.search(r'exam|practical|paper|viva|test', c))

    # SPAM
    if re.search(r'earn money|click here|win prize|lottery|promo code|free recharge', c):
        return dict(priority="Spam", category="Spam", is_low=False)

    # ── IMMEDIATE ──────────────────────────────────────────
    if re.search(r'hall ticket|admit card|roll number', c) and (now or soon or exam):
        return dict(priority="Immediate", category="Hall Ticket Issue", is_low=False)

    if re.search(r'accident|hospital|hospitalized|medical emergency|icu|surgery|ambulance', c):
        return dict(priority="Immediate", category="Medical Emergency", is_low=False)

    if exam and now:
        return dict(priority="Immediate", category="Exam Issue", is_low=False)

    if re.search(r'fees|fee|payment', c) and re.search(r'today|last date|deadline|right now', c):
        return dict(priority="Immediate", category="Fee Payment", is_low=False)

    # ── HIGH ────────────────────────────────────────────────
    if re.search(r'fees|fee payment|financial|installment|cannot pay|afford', c) and 'scholarship' not in c:
        return dict(priority="High", category="Fee Payment", is_low=False)

    if 'scholarship' in c and re.search(r'not credited|not received|pending|rejected|apply', c):
        return dict(priority="High", category="Scholarship Issue", is_low=False)

    if re.search(r'result|marks', c) and re.search(r'wrong|error|revaluation|discrepancy|incorrect', c):
        return dict(priority="High", category="Revaluation Request", is_low=False)

    if 'hostel' in c and re.search(r'problem|issue|unsafe|harassment|complaint', c):
        return dict(priority="High", category="Hostel Issue", is_low=False)

    if re.search(r'document|certificate|bonafide|marksheet|migration|\bnoc\b|\btc\b', c) \
            and re.search(r'urgent|today|tomorrow|deadline|urgently|asap', c):
        return dict(priority="High", category="Document Request", is_low=False)

    if re.search(r're.?admission|readmission', c):
        return dict(priority="High", category="Re-Admission Request", is_low=False)

    if re.search(r'admission|cap round', c) and re.search(r'problem|stuck|not done', c):
        return dict(priority="High", category="Admission Issue", is_low=False)

    if re.search(r'backlog|supplementary|back paper', c) \
            and re.search(r'error|cannot register|not opening|problem', c):
        return dict(priority="High", category="Backlog Exam Problem", is_low=False)

    # ── LOW (instant policy reply) ───────────────────────────
    rules = [
        (r'attendance|present|absent',              "Attendance Query"),
        (r'division|section|batch',                 "Division / Section Change"),
        (r'timetable|time table|schedule',          "Timetable Query"),
        (r'\bresult\b|\bmarks\b|grade',             "Result / Marks Query"),
        (r'bonafide|bona fide',                     "Bonafide Certificate"),
        (r'\btc\b|migration cert|transfer cert',    "TC / Migration Certificate"),
        (r'college leaving cert|leaving cert',      "College Leaving Certificate"),
        (r'gap certificate',                        "Gap Certificate"),
        (r'duplicate marksheet',                    "Duplicate Marksheet"),
        (r'name correction|name change|wrong name', "Name Correction"),
        (r'caution money|caution fee|refund',       "Caution Money Refund"),
        (r'\bfine\b|penalty|challan',              "Fine / Penalty"),
        (r'sports.*leave|leave.*sports',            "Sports Leave"),
        (r'cultural.*leave|event.*leave',           "Cultural / Event Leave"),
        (r'\bnoc\b|internship',                    "Internship NOC"),
        (r'mess|food.*complaint|canteen',           "Mess / Food Complaint"),
        (r'backlog|supplementary',                  "Backlog Exam Problem"),
        (r'portal|login|password|website|otp|not loading|technical', "IT / Portal Issue"),
        (r'library|book|return',                    "Library Issue"),
    ]
    for pat, cat in rules:
        if re.search(pat, c):
            return dict(priority="Low", category=cat, is_low=True)

    return dict(priority="Low", category="General Information", is_low=True)


# ═══════════════════════════════════════════════════════════════
#  Classifier class — used by app.py as: classifier.classify_query()
# ═══════════════════════════════════════════════════════════════
import json
import google.generativeai as genai
from config import GEMINI_API_KEY, CATEGORY_TO_DEPARTMENT, COLLEGE_NAME, COLLEGE_EMAIL, COLLEGE_PHONE

genai.configure(api_key=GEMINI_API_KEY)

POLICY_NOTE = (
    "\n\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "ℹ️  College Policy Notice\n"
    "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    "As per college regulations, this matter is governed by a fixed institutional policy "
    "and cannot be changed or overridden on an individual basis. "
    "Please follow the steps mentioned above. "
    "For further assistance, visit the relevant office during working hours (9AM–5PM, Mon–Sat)."
)

class Classifier:
    def classify_query(self, subject: str, message: str) -> dict:
        result     = detect(subject, message)
        priority   = result['priority']
        category   = result['category']
        is_low     = result['is_low']
        department = CATEGORY_TO_DEPARTMENT.get(category, 'Student Affairs')

        # ── LOW / SPAM → instant policy reply, no AI ────────────
        if is_low or priority == 'Spam':
            reply = instant_reply("Student", category)
            remedy = reply.get('auto_reply', '')
            # Append policy notice for low priority
            remedy_with_policy = remedy + POLICY_NOTE
            return {
                'priority':   priority,
                'category':   category,
                'department': department,
                'analysis':   reply.get('problem_summary', f'Routine query about {category.lower()}.'),
                'remedy':     remedy_with_policy,
                'is_policy':  True,
            }

        # ── HIGH / IMMEDIATE → Gemini AI ────────────────────────
        try:
            model  = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"""You are an AI assistant for {COLLEGE_NAME} student grievance portal.
Analyze this student query carefully and respond ONLY in valid JSON (no markdown, no extra text):
{{
  "analysis": "Clear 1-2 sentence summary of the student's problem",
  "remedy": "Step-by-step action plan the student should follow to resolve this issue",
  "department": "Most relevant department name from college"
}}

Subject: {subject}
Message: {message}
Detected Category: {category}
Priority Level: {priority}

Be specific, helpful, and empathetic."""

            response = model.generate_content(prompt)
            text     = response.text.strip()
            # Remove markdown fences if present
            text = text.replace('```json', '').replace('```', '').strip()
            ai = json.loads(text)
            return {
                'priority':   priority,
                'category':   category,
                'department': ai.get('department', department),
                'analysis':   ai.get('analysis', 'Query received and under review.'),
                'remedy':     ai.get('remedy', 'Please visit the relevant department office for assistance.'),
                'is_policy':  False,
            }
        except Exception as e:
            print(f"⚠️  Gemini error: {e}")
            return {
                'priority':   priority,
                'category':   category,
                'department': department,
                'analysis':   f'Your {priority.lower()} priority query about {category} has been received.',
                'remedy':     'Please visit the relevant department office immediately for assistance.',
                'is_policy':  False,
            }

classifier = Classifier()