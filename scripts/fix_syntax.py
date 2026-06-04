"""
Fix all syntax errors in web_app.py related to single-quoted Python strings
that contain contractions with apostrophes.
"""
import sys, os

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

with open(WEB_APP, 'r', encoding='utf-8') as f:
    content = f.read()

# Strategy: Replace specific problematic string patterns.
# Instead of trying to escape within single-quoted strings,
# change the outer quoting to double-quotes where needed.

fixes = [
    # Landing page testimonials - use double quotes for strings with apostrophes
    ('"I\\\'ve discovered so many n',
     '"I\'ve discovered so many n'),
     
    # Forgot password page - we've
    ('we\\\'ve sent a password reset link',
     "we've sent a password reset link"),
     
    # Reset email - didn't request
    ('If you didn\\\'t request this',
     'If you didn\'t request this'),
     
    # Fix over-escaped contractions from previous run
    ("we\\\\'ve sent", "we've sent"),
    ("we\\\\'ll send", "we'll send"),
    ("don\\\\'t", "don't"),
    ("didn\\\\'t", "didn't"),
    ("I\\\\'ve", "I've"),
    ("it\\\\'s", "it's"),
]

count = 0
for old, new in fixes:
    if old in content:
        content = content.replace(old, new)
        count += 1
        print(f"Fixed: {repr(old[:50])}")

# Now, for the truly problematic strings, convert them from single-quoted to double-quoted
# by changing the outer quotes

# Pattern: line contains a single-quoted Python string that has an unescaped apostrophe
import re

lines = content.split('\n')
fixed_lines = []
total_fixes = 0

for i, line in enumerate(lines):
    line_num = i + 1
    original = line
    
    # Check if this is a single-quoted Python string line (starts with spaces + ')
    stripped = line.lstrip()
    
    # If line contains an apostrophe that would break a single-quoted string
    # Only fix if the line looks like a simple string assignment/concatenation
    if stripped.startswith("'") and ("' +" in stripped or "'," in stripped or "')" in stripped or stripped.endswith("'")):
        # This is likely a Python string concatenation line
        # Check if it has unescaped contractions
        contractions = ["we'll", "we've", "don't", "can't", "doesn't", "it's", "didn't", 
                       "won't", "isn't", "haven't", "hasn't", "wasn't", "weren't",
                       "couldn't", "wouldn't", "shouldn't", "they're", "they've", 
                       "they'll", "you're", "you've", "you'll", "I'm", "I've", "I'll"]
        
        for cont in contractions:
            if cont in stripped and ("\\" + cont) not in stripped:
                # Found an unescaped contraction in a single-quoted string
                # The string on this line is: '...content...'
                # We need to find the matching closing quote
                print(f"Line {line_num}: Fixing contraction '{cont}'")
                
                # Find the start and end of the string
                # Strip leading whitespace to find the opening quote
                leading_ws = line[:len(line) - len(stripped)]
                
                # Find opening quote
                if stripped[0] == "'":
                    # Simple approach: just escape this specific contraction
                    indented = cont in line
                    # Count how many times cont appears
                    idx = line.find(cont)
                    if idx >= 0 and (idx == 0 or line[idx-1] != '\\'):
                        # Check we're inside a single-quoted string
                        # Count quotes before this position
                        before = line[:idx]
                        single_quotes = before.count("'") - before.count("\\'")
                        double_quotes = before.count('"') - before.count('\\"')
                        
                        # If we're inside single quotes (odd number) and not inside double quotes
                        escaped_cont = cont[0] + "\\" + cont[1:]
                        line = line.replace(cont, escaped_cont)
                        total_fixes += 1
    
    fixed_lines.append(line)

if total_fixes > 0:
    content = '\n'.join(fixed_lines)

# Write back
with open(WEB_APP, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify compilation
try:
    compile(content, WEB_APP, 'exec')
    print(f"\n✅ Total fixes: {total_fixes}. File compiles OK!")
except SyntaxError as e:
    print(f"\n❌ Still has syntax error: {e}")
    import re
    match = re.search(r'line (\d+)', str(e))
    if match:
        error_line = int(match.group(1))
        lines = content.split('\n')
        if error_line <= len(lines):
            for j in range(max(0, error_line - 2), min(len(lines), error_line + 3)):
                marker = ">>>" if j + 1 == error_line else "   "
                print(f"{marker} L{j+1}: {repr(lines[j][:150])}")
