"""
Simple fix: replace all contractions in web_app.py with non-contracted forms.
This avoids the apostrophe-in-single-quoted-string issue entirely.
"""
import os, re

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

with open(WEB_APP, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Replace contractions with non-contracted forms
replacements = {
    "we'll": "we will",
    "we've": "we have",
    "I've": "I have",
    "don't": "do not",
    "can't": "cannot",
    "won't": "will not",
    "isn't": "is not",
    "doesn't": "does not",
    "didn't": "did not",
    "hasn't": "has not",
    "haven't": "have not",
    "wasn't": "was not",
    "weren't": "were not",
    "couldn't": "could not",
    "wouldn't": "would not",
    "shouldn't": "should not",
    "it's": "it is",
    "that's": "that is",
    "there's": "there is",
    "what's": "what is",
    "who's": "who is",
    "where's": "where is",
    "how's": "how is",
    "let's": "let us",
    "I'm": "I am",
    "you're": "you are",
    "they're": "they are",
    "we're": "we are",
    "I'll": "I will",
    "you'll": "you will",
    "they'll": "they will",
}

count = 0
for old, new in replacements.items():
    # Only replace if directly present (not already escaped)
    c = content.count(old)
    if c > 0:
        content = content.replace(old, new)
        count += c
        print(f"Replaced '{old}' -> '{new}' ({c} times)")

with open(WEB_APP, 'w', encoding='utf-8') as f:
    f.write(content)

# Verify
import py_compile
try:
    py_compile.compile(WEB_APP, doraise=True)
    print(f"\n✅ web_app.py compiles OK! Total replacements: {count}")
except SyntaxError as e:
    print(f"\n❌ Still has error: {e}")
    m = re.search(r'line (\d+)', str(e))
    if m:
        err_line = int(m.group(1))
        with open(WEB_APP, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i in range(max(0, err_line-2), min(len(lines), err_line+2)):
            marker = ">>>" if i+1 == err_line else "   "
            r = repr(lines[i][:150])
            print(f"{marker} L{i+1}: {r}")
