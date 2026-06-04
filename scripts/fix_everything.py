"""
Fix all remaining syntax errors in web_app.py.
The corrupted strings were introduced by imperfect automated fix scripts.
This script surgically finds and replaces ALL corrupted patterns.
"""
import os, re, py_compile

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

with open(WEB_APP, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the specific corrupted text at line 834
# Original: '<p class="auth-subtitle">If an account exists, w\e've sent a password reset link.</p>'
# Fixed: use double quotes and no contractions

fixes = [
    # The corrupted we've -> we have
    ("we've sent a password reset link.", "we have sent a password reset link."),
    ("we have sent a password reset link.", "we have sent a password reset link."),  # no-op if already fixed
    # Any remaining \e sequences
    ("w\\e've sent a password reset link.", "we have sent a password reset link."),
    ("w\\e have sent a password reset link.", "we have sent a password reset link."),
    # Fix the quotation issue around this string
    # The string might be wrapped in single quotes with unescaped internal quotes
    "'If an account exists, we have sent a password reset link.'",
    "'If an account exists, "
]

# Find ALL lines that have SyntaxError issues and fix them
# Strategy: Try to compile the file, find the error line, fix it, repeat
max_iterations = 20
for iteration in range(max_iterations):
    try:
        py_compile.compile(WEB_APP, doraise=True)
        print(f"✅ web_app.py compiles OK! (after {iteration} fix iterations)")
        break
    except SyntaxError as e:
        msg = str(e)
        print(f"Iteration {iteration + 1}: {msg}")
        
        m = re.search(r'line (\d+)', msg)
        if not m:
            print("Could not find error line number!")
            break
        
        err_line = int(m.group(1))
        lines = content.split('\n')
        
        if err_line > len(lines):
            print(f"Error line {err_line} exceeds file length {len(lines)}")
            break
        
        # Read the problematic line
        line = lines[err_line - 1]
        print(f"  L{err_line}: {repr(line[:150])}")
        
        # Fix common patterns on the problematic line
        fixed = False
        
        # Pattern 1: Unescaped apostrophe in single-quoted string like '...we've...'
        # Fix: use double-quoted string
        if line.strip().startswith("'") and "'ve" in line:
            # Find the opening quote and change it to double quote
            # And escape all double quotes inside to make it a valid double-quoted string
            idx = line.find("'")
            line_chars = list(line)
            line_chars[idx] = '"'
            
            # Find the closing quote (assumed to be at the end of the string part)
            # The line might have more content after the string
            # For now, just change opening single to double
            line = ''.join(line_chars)
            
            # Also close with double quote
            if line.rstrip().endswith("'"):
                line = line.rstrip()
                line = line[:-1] + '"' + '\n'
            
            fixed = True
        
        # Pattern 2: Invalid escape sequences like \e
        if not fixed and '\\e' in line:
            line = line.replace('\\e', 'e')
            fixed = True
        
        # Pattern 3: Over-escaped backslashes
        if not fixed:
            # Replace N backslashes + ' with just \' (for N >= 3)
            line = re.sub(r'\\{3,}"', "\\'", line)
            line = re.sub(r'\\{3,}' "'", "\\'", line)
            fixed = True
        
        lines[err_line - 1] = line
        content = '\n'.join(lines)
        
        with open(WEB_APP, 'w', encoding='utf-8') as f:
            f.write(content)
else:
    print(f"❌ File still has errors after {max_iterations} iterations")

print(f"File size: {len(content):,} chars")
