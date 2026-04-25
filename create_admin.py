from database import db
from werkzeug.security import generate_password_hash

# Pehle purane sab admins delete karo
db.admins.delete_many({})
print("🗑️  Purane admins delete kiye")

# Naya admin banao - db ka apna create_admin use karo
admin_id = db.create_admin(
    username      = "admin",
    email         = "admin@silveroak.edu.in",
    password_hash = generate_password_hash("Admin@123"),
    role          = "super_admin",
    created_by    = "system"
)

print(f"✅ Admin created! ID: {admin_id}")
print()
print("=" * 40)
print("LOGIN DETAILS:")
print("  Username : admin")
print("  Password : Admin@123")
print("  URL      : http://127.0.0.1:5000")
print("=" * 40)