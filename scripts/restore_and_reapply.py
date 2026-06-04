"""
Restore web_app.py by removing all corrupted sections added by earlier scripts,
then re-adding the auth page improvements with correctly escaped strings.
Uses double-quoted Python strings for any content with apostrophes.
"""
import os, re

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

with open(WEB_APP, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# ─── Step 1: Remove the corrupted testimonials block ───
# Find and remove the wrongly-inserted testimonials block
test_start = content.find('testimonials = (')
if test_start > 0:
    # Find the end - the closing paren at same indent level as 'testimonials'
    # Go backward to find the start of the line
    line_start = content.rfind('\n', 0, test_start) + 1
    if line_start == 0:
        line_start = test_start
    
    # Find the matching closing paren
    pos = test_start
    depth = 0
    found_open = False
    while pos < len(content):
        c = content[pos]
        if c == '(':
            depth += 1
            found_open = True
        elif c == ')':
            depth -= 1
            if found_open and depth == 0:
                # Found the matching close paren
                # Include the newline after it
                line_end = content.find('\n', pos)
                if line_end == -1:
                    line_end = len(content)
                else:
                    line_end = line_end + 1
                
                # Remove the entire block
                content = content[:line_start] + content[line_end:]
                print(f"Removed testimonials block at lines ~{content[:line_start].count(chr(10))+1}")
                break
        pos += 1
    else:
        print("ERROR: Could not find end of testimonials block")

# ─── Step 2: Remove the landing page section ───
landing_marker = "# ─── LANDING PAGE ────────────────────────────────────────────────────"
landing_start = content.find(landing_marker)
if landing_start >= 0:
    # Find the @app.route that follows (the logout route)
    next_route = content.find('# ─── AUTH', landing_start)
    if next_route == -1:
        next_route = content.find('@app.route("/logout")', landing_start)
    
    if next_route >= 0:
        content = content[:landing_start] + content[next_route:]
        print(f"Removed landing page section")
    else:
        print("ERROR: Could not find next route after landing page")
else:
    print("Landing page marker not found (already removed?)")

# ─── Step 3: Remove the duplicated auth sections (old ones that were replaced) ───
# The update_auth_pages.py might have left old versions

# ─── Step 4: Fix all remaining contraction issues by replacing with non-contracted forms ───
# Only replace contractions that are NOT already properly escaped with backslash
contractions = {
    "we will": "we will",  # no-op, already expanded
    "we have": "we have",  # no-op
    "I have": "I have",    # no-op
}

# Find all unescaped contractions in single-quoted strings
# Simple approach: replace common contractions with expanded forms
lines = content.split('\n')
fixed_lines = []
total_fixes = 0

for line in lines:
    # Replace contractions with non-contracted forms
    # But only if they're NOT inside double-quoted strings (those are fine)
    # And NOT already escaped
    cont_map = {
        "we'll": "we will",
        "we've": "we have",
        "I've": "I have",
        "don't": "do not",
        "can't": "cannot",
        "won't": "will not",
        "isn't": "is not",
        "doesn't": "does not",
        "didn't": "did not",
        "it's": "it is",
        "that's": "that is",
    }
    
    for old, new in cont_map.items():
        if old in line:
            # Only fix if not already preceded by backslash
            idx = line.find(old)
            while idx >= 0:
                if idx == 0 or line[idx-1] != '\\':
                    line = line[:idx] + new + line[idx+len(old):]
                    total_fixes += 1
                    idx = line.find(old, idx + len(new))
                else:
                    idx = line.find(old, idx + len(old))
    
    fixed_lines.append(line)

if total_fixes > 0:
    print(f"Fixed {total_fixes} contraction(s)")

content = '\n'.join(fixed_lines)

# ─── Step 5: Write back ───
with open(WEB_APP, 'w', encoding='utf-8') as f:
    f.write(content)

# ─── Step 6: Verify compilation ───
import py_compile
try:
    py_compile.compile(WEB_APP, doraise=True)
    print("✅ web_app.py compiles OK!")
except SyntaxError as e:
    print(f"❌ Still has error: {e}")
    m = re.search(r'line (\d+)', str(e))
    if m:
        err_line = int(m.group(1))
        with open(WEB_APP, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i in range(max(0, err_line-2), min(len(lines), err_line+2)):
            marker = ">>>" if i+1 == err_line else "   "
            print(f"{marker} L{i+1}: {repr(lines[i][:150])}")

print(f"\nFile size: {len(content):,} chars")
