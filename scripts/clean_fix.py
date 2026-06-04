"""
Fix all syntax errors in web_app.py by correcting over-escaped and under-escaped
apostrophes in single-quoted Python strings.
"""
import os, re

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

# Read raw bytes
with open(WEB_APP, 'rb') as f:
    data = f.read()

# Fix 1: Triple backslash + quote → single backslash + quote
# Pattern: \\\' (3 backslashes + apostrophe inside single-quoted string)
# These should be \' (1 backslash + apostrophe) which escapes the apostrophe
data = data.replace(b"\\\\\\'", b"\\'")

# Fix 2: Double backslash + quote → single backslash + quote  
# Pattern: \\' (2 backslashes + apostrophe) 
# In Python source: \\ → literal \, ' → end of string (bad!)
# Should be: \' → escape sequence for apostrophe
data = data.replace(b"\\\\'", b"\\'")

# Fix 3: Now verify all common contractions are properly escaped
# These patterns should appear as: we\'ll, we\'ve, don\'t, etc.
# NOT as: we'll, we\\'ll, we\\\'ll, etc.
import py_compile
import tempfile

# Write fixed file
with open(WEB_APP, 'wb') as f:
    f.write(data)

# Test compilation
try:
    py_compile.compile(WEB_APP, doraise=True)
    print("✅ web_app.py compiles OK!")
except SyntaxError as e:
    print(f"❌ Still has error: {e}")
    # Find the error line and print context
    m = re.search(r'line (\d+)', str(e))
    if m:
        err_line = int(m.group(1))
        with open(WEB_APP, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
        for i in range(max(0, err_line-3), min(len(lines), err_line+2)):
            marker = ">>>" if i+1 == err_line else "   "
            raw = lines[i].encode('utf-8', errors='replace')
            print(f"{marker} L{i+1}: {raw[:200]}")
