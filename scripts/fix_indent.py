"""
Fix indentation of the testimonials block that was inserted with wrong indentation by the rewrite script.
Also fix any unescaped apostrophes.
"""
import os

WEB_APP = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

with open(WEB_APP, 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Find the problematic "testimonials = (" block at wrong indent level
# It should be at 8 spaces indent (inside landing_page function), 
# but it was inserted with 8 spaces already (lines 657-662)
# Actually looking at the broader context, the issue is that line 656 is blank
# and line 657 has "        testimonials = ("
# The lines BEFORE (640-655) have various indentation levels because they're
# inside the landing_page function.

# Let me check what's on line 656-657
line656 = lines[655] if len(lines) > 655 else ""
line657 = lines[656] if len(lines) > 656 else ""

print(f"Line 656: {repr(line656[:80])}")
print(f"Line 657: {repr(line657[:80])}")

# The real issue: 'testimonials = (' at wrong indentation level
# It's at 8 spaces but should be at 4 or 8 depending on context
# Let me check what function we're in

# Find the function containing this area
for i in range(655, -1, -1):
    if lines[i].strip().startswith('def '):
        print(f"Function at line {i+1}: {lines[i].strip()}")
        # Check the indentation of the function
        func_line = lines[i]
        indent = len(func_line) - len(func_line.lstrip())
        print(f"Function indent: {indent}")
        break

# Check indentation of the lines around the issue
for i in range(648, 666):
    if i < len(lines):
        line = lines[i]
        stripped = line.rstrip('\n\r')
        print(f"{i+1}: {' ' if len(stripped) > 0 else '.'} |{repr(stripped[:100])}")

print("\n--- Now fixing the indent issue ---")

# Fix the testimonials block by adjusting its indentation
# The landing_page function is at 0 indent, so code inside should be at 4 spaces
# Find and fix the testimonials line

for i in range(len(lines)):
    stripped = lines[i].strip()
    if stripped.startswith('testimonials = ('):
        current_indent = len(lines[i]) - len(lines[i].lstrip())
        expected_indent = 4  # inside landing_page function with 0-indent def
        print(f"Found testimonials at line {i+1}, current indent: {current_indent}, expected: {expected_indent}")
        if current_indent != expected_indent:
            lines[i] = ' ' * expected_indent + stripped + '\n'
            print(f"Fixed indent to {expected_indent}")
        break

# Also fix the indentation of the strings that follow testimonials
for i in range(len(lines)):
    stripped = lines[i].strip()
    if stripped.startswith('<div class="row g-3 mt-2"') or stripped.startswith('<div class="col-md-4"'):
        current_indent = len(lines[i]) - len(lines[i].lstrip())
        expected_indent = 8  # inside testimonials = (...)
        print(f"Found content string at line {i+1}, current indent: {current_indent}, expected: {expected_indent}")
        if current_indent != expected_indent:
            lines[i] = ' ' * expected_indent + stripped + '\n'
            print(f"Fixed content indent to {expected_indent}")

# Fix the closing </div> and ) 
for i in range(len(lines)):
    stripped = lines[i].strip()
    if stripped == '"</div>"':
        current_indent = len(lines[i]) - len(lines[i].lstrip())
        expected_indent = 8
        if current_indent != expected_indent:
            lines[i] = ' ' * expected_indent + stripped + '\n'
            print(f"Fixed </div> indent at line {i+1}")
        break

for i in range(len(lines)):
    stripped = lines[i].strip()
    if stripped == ')':
        # This might be the closing paren of testimonials or features_grid
        # Check if it follows the testimonials block
        if i > 0 and '"</div>"' in lines[i-1]:
            current_indent = len(lines[i]) - len(lines[i].lstrip())
            expected_indent = 4
            if current_indent != expected_indent:
                lines[i] = ' ' * expected_indent + stripped + '\n'
                print(f"Fixed ) indent at line {i+1}")
            break

with open(WEB_APP, 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Verify
import py_compile
try:
    py_compile.compile(WEB_APP, doraise=True)
    print("\n✅ web_app.py compiles OK!")
except SyntaxError as e:
    print(f"\n❌ Still has error: {e}")
    import re
    m = re.search(r'line (\d+)', str(e))
    if m:
        err_line = int(m.group(1))
        with open(WEB_APP, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        for i in range(max(0, err_line-2), min(len(lines), err_line+2)):
            marker = ">>>" if i+1 == err_line else "   "
            print(f"{marker} L{i+1}: {repr(lines[i][:150])}")
