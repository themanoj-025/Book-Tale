"""
Fix the unescaped apostrophe on line 2675 of web_app.py.
The specific problem: '...we'll send...' should be '...we\\'ll send...'
"""
import sys, os

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

with open(WEB_APP, 'rb') as f:
    data = f.read()

# Find the exact problematic byte sequence
# The line is: '<p class="auth-subtitle">Enter your email or User ID and we'll send you a reset link</p>'
# The problem is: we'll  (apostrophe inside single-quoted Python string)

# Try multiple approaches
old_versions = [
    b"we'll send you",           # plain text
    b"we\\'ll send you",         # already escaped once
    b"we\\\\'ll send you",       # double escaped  
]

fixed = b"we\\'ll send you"

for old in old_versions:
    if old in data:
        data = data.replace(old, fixed)
        print(f"Fixed using pattern: {old}")

# Verify no more unescaped instances of the problem
# Check if the string is properly escaped now
text = data.decode('utf-8')
lines = text.split('\n')
if len(lines) >= 2675:
    line = lines[2674]
    # Count unescaped single quotes in the line
    in_string = False
    escaped = False
    quote_positions = []
    for i, c in enumerate(line):
        if c == "'" and not escaped:
            quote_positions.append(i)
        escaped = (c == '\\' and not escaped)
    print(f"Line 2675 has {len(quote_positions)} unescaped single quotes")

with open(WEB_APP, 'wb') as f:
    f.write(data)

print("Done. File size:", len(data), "bytes")
