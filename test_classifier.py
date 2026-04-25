
from classifier import classifier

tests = [
    ("hall ticket", "sir my hall ticket is not issued"),
    ("exam", "mera exam kal hai aur mujhe appear nahi karne de rahe"),
    ("fees", "my fees deadline is today I cannot pay"),
    ("attendance", "sir my attendance is low"),
    ("result", "my result is wrong please check"),
    ("general", "hello I need help"),
]

print("── Priority Test Results ──")
for subj, msg in tests:
    r = classifier.classify_query(subj, msg)
    print(f"  [{r['priority']:10}] {subj}")

print()
print("Agar sab sahi hai toh High/Immediate dikhe pehle 3 mein")
