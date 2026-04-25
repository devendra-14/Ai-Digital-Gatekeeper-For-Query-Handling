import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Step 1: Fix Admin ─────────────────────────────────────────
from database import db
from werkzeug.security import generate_password_hash

db.admins.delete_many({})
print("✅ Old admins deleted")

admin_id = db.create_admin(
    username      = "devendra",
    email         = "devendra@silveroak.edu.in",
    password_hash = generate_password_hash("Admin@123"),
    role          = "super_admin",
    created_by    = "system"
)
print(f"✅ Admin created! ID: {admin_id}")

# Verify it was saved correctly
saved = db.admins.find_one({'username': 'devendra'})
if saved:
    print(f"✅ Verified in DB: username='{saved['username']}', role='{saved['role']}'")
else:
    print("❌ Admin NOT found in DB - something wrong")

print()

# ── Step 2: Test Classifier ───────────────────────────────────
try:
    from classifier import classifier

    tests = [
        ("hall ticket", "sir my hall ticket is issued"),
        ("exam problem", "I cannot appear in exam tomorrow"),
        ("fees", "my fees deadline is today I cannot pay"),
        ("attendance", "my attendance is low sir"),
        ("general", "hello"),
    ]

    print("── Classifier Test Results ──")
    for subj, msg in tests:
        r = classifier.classify_query(subj, msg)
        print(f"  [{r['priority']:10}] {subj} → {r['category']}")
    print()
    print("✅ Classifier working!")

except Exception as e:
    print(f"❌ Classifier error: {e}")
    print("   → classifier.py file replace karo!")

print()
print("=" * 40)
print("LOGIN DETAILS:")
print("  URL      : http://127.0.0.1:5000")
print("  Username : devendra")
print("  Password : Admin@123")
print("=" * 40)