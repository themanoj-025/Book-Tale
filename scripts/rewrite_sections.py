"""
Rewrite the landing page and auth sections of web_app.py with clean, correct Python strings.
Uses double-quoted strings to avoid all apostrophe escaping issues.
"""
import os

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

with open(WEB_APP, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# ─── Fix 1: Landing page testimonials section ───
# Find the testimonial section and replace it with clean code
old_testimonials_start = """    testimonials = (
        '        \\'<div class=\\"row g-3 mt-2\\">\\''
        '        \\'<div class=\\"col-md-4\\"><div class=\\"testimonial-card\\"><div class=\\"stars\\">"""

# Find by searching for "testimonials = (" 
test_idx = content.find('testimonials = (')
if test_idx == -1:
    print("ERROR: testimonials not found!")
    exit(1)

# Find the end - the next non-string line (not starting with ') after a string)
search_start = test_idx
depth = 0
in_string = False
str_char = None
paren_depth = 0

# Simpler: find the closing parenthesis at the original indent level
lines = content[test_idx:].split('\n')
testimonial_end = test_idx
for i, line in enumerate(lines):
    testimonial_end = test_idx + len('\n'.join(lines[:i+1])) + 1 if i > 0 else test_idx + len(lines[0])
    stripped = line.strip()
    if stripped == ')':
        break

new_testimonials = """    testimonials = (
        "<div class=\\"row g-3 mt-2\\">"
        "<div class=\\"col-md-4\\"><div class=\\"testimonial-card\\"><div class=\\"stars\\">\\u2605\\u2605\\u2605\\u2605\\u2605</div><p>\\u201cBookTale completely transformed how I track my reading. The AI recommendations are uncanny!\\u201d</p><div class=\\"author\\">\\u2014 Sarah K., <span>Avid Reader</span></div></div></div>"
        "<div class=\\"col-md-4\\"><div class=\\"testimonial-card\\"><div class=\\"stars\\">\\u2605\\u2605\\u2605\\u2605\\u2605</div><p>\\u201cAs a librarian, this platform makes managing our collection a breeze. The community features are a bonus.\\u201d</p><div class=\\"author\\">\\u2014 Marcus J., <span>Librarian</span></div></div></div>"
        "<div class=\\"col-md-4\\"><div class=\\"testimonial-card\\"><div class=\\"stars\\">\\u2605\\u2605\\u2605\\u2605\\u2606</div><p>\\u201cI have discovered so many new books through the social feed. It is like Goodreads but better!\\u201d</p><div class=\\"author\\">\\u2014 Elena R., <span>Book Blogger</span></div></div></div>"
        "</div>"
    )"""

end_of_testimonials = test_idx + len(lines[0]) + sum(len(lines[j]) + 1 for j in range(1, len(lines))) 

# Find end - search for where the testimonials tuple ends by looking for ')' at same indent
# Walk forward to find matching paren
depth = 0
found_start = False
pos = test_idx
for pos in range(test_idx, len(content)):
    c = content[pos]
    if c == '(':
        depth += 1
        found_start = True
    elif c == ')':
        depth -= 1
        if found_start and depth == 0:
            break

content = content[:test_idx] + new_testimonials + content[pos+1:]

# ─── Fix 2: Forgot password page ───
# Replace "we've sent" with "we have sent" in the forgot-password page
content = content.replace(
    "we've sent a password reset link",
    "we have sent a password reset link"
)

# ─── Fix 3: Reset email ───
# Replace "didn't request" with "did not request"
content = content.replace(
    "didn't request this",
    "did not request this"
)

# ─── Fix 4: Any remaining double/triple escaped apostrophes ───
import re
# Replace patterns like \\\' (backslash backslash apostrophe) with just \' in the source
# These appear where \\ is in the file but should be \' (single escape)
content = content.replace("\\\\'", "'")  # This removes all double-escaping
# Now re-escape all contractions in single-quoted strings
# Actually, let's just replace common contractions with non-apostrophe versions
content = content.replace("don't", "do not")
content = content.replace("can't", "cannot")
content = content.replace("won't", "will not")
content = content.replace("isn't", "is not")
content = content.replace("doesn't", "does not")
content = content.replace("didn't", "did not")
content = content.replace("hasn't", "has not")
content = content.replace("haven't", "have not")
content = content.replace("wasn't", "was not")
content = content.replace("we'll", "we will")
content = content.replace("we've", "we have")
content = content.replace("it's", "it is")

# Write back
with open(WEB_APP, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
import py_compile
try:
    py_compile.compile(WEB_APP, doraise=True)
    print("✅ web_app.py compiles OK!")
except SyntaxError as e:
    print(f"❌ Still has error: {e}")
    import re
    m = re.search(r'line (\d+)', str(e))
    if m:
        err_line = int(m.group(1))
        with open(WEB_APP, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i in range(max(0, err_line-3), min(len(lines), err_line+2)):
            marker = ">>>" if i+1 == err_line else "   "
            print(f"{marker} L{i+1}: {lines[i][:150]}")

print("Done")
