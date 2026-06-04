"""
Fix all unescaped apostrophes in web_app.py that appear inside single-quoted Python strings.
Scans for contractions like we'll, we've, don't, can't inside single-quoted strings
and escapes the apostrophe with a backslash.
"""
import sys, os

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

# Read the file as text
with open(WEB_APP, 'r', encoding='utf-8') as f:
    content = f.read()

# Find all lines that have apostrophes inside single-quoted strings
# Strategy: Find patterns like '<...word'word...>' and fix them
lines = content.split('\n')
fixed_lines = []
total_fixes = 0

for i, line in enumerate(lines):
    line_num = i + 1
    # Find single-quoted strings on this line and check for unescaped apostrophes
    # A single-quoted string starts with a ' that is NOT preceded by a backslash
    # and is NOT inside a double-quoted string
    
    # Simpler approach: just fix all contractions in single-quoted context
    # Check if line contains a single-quoted Python string pattern
    has_single_quote_string = False
    # Look for patterns like: '...' at start/end of string literal
    stripped = line.strip()
    if stripped.startswith("'") and (stripped.endswith("'") or stripped.endswith("\\")):
        has_single_quote_string = True
    
    # Even simpler: fix all contractions that have unescaped apostrophes
    contractions = {
        "we'll": "we\\'ll",
        "we've": "we\\'ve",
        "don't": "don\\'t",
        "can't": "can\\'t",
        "doesn't": "doesn\\'t",
        "it's": "it\\'s",
        "didn't": "didn\\'t",
        "won't": "won\\'t",
        "isn't": "isn\\'t",
        "haven't": "haven\\'t",
        "hasn't": "hasn\\'t",
        "wasn't": "wasn\\'t",
        "weren't": "weren\\'t",
        "couldn't": "couldn\\'t",
        "wouldn't": "wouldn\\'t",
        "shouldn't": "shouldn\\'t",
        "they're": "they\\'re",
        "they've": "they\\'ve",
        "they'll": "they\\'ll",
        "you're": "you\\'re",
        "you've": "you\\'ve",
        "you'll": "you\\'ll",
        "I'm": "I\\'m",
        "I've": "I\\'ve",
        "I'll": "I\\'ll",
    }
    
    line_fixes = 0
    for old, new in contractions.items():
        # Only fix if the apostrophe is NOT already escaped
        if old in line and ("\\" + old) not in line:
            line = line.replace(old, new)
            line_fixes += 1
    
    if line_fixes > 0:
        print(f"Line {line_num}: Fixed {line_fixes} contraction(s)")
        total_fixes += line_fixes
    
    fixed_lines.append(line)

content = '\n'.join(fixed_lines)

# Verify by compiling
try:
    compile(content, WEB_APP, 'exec')
    print(f"\nAll {total_fixes} fixes applied. File compiles OK!")
except SyntaxError as e:
    print(f"\nERROR after fixes: {e}")
    # Show the problematic line
    import re
    match = re.search(r'line (\d+)', str(e))
    if match:
        error_line = int(match.group(1))
        lines = content.split('\n')
        if error_line <= len(lines):
            for j in range(max(0, error_line - 3), min(len(lines), error_line + 2)):
                marker = " >>>" if j + 1 == error_line else "    "
                print(f"{marker} Line {j+1}: {lines[j][:120]}")

# Write back
with open(WEB_APP, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Total fixes: {total_fixes}")
