"""Update dashboard_page to include user data (gamification, reading stats, leaderboard)."""
import re

with open('page_routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find dashboard_page function boundaries (lines 1404-1466 based on earlier search)
start_line = None
end_line = None
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped == '@app.route("/dashboard")':
        start_line = i
    if start_line is not None and stripped.startswith('def dashboard_page()'):
        # Already found start, find end
        pass
    if start_line is not None and stripped == 'return render_page("Dashboard", CONTENT)':
        end_line = i
        break

if start_line is None or end_line is None:
    print(f"ERROR: Could not find dashboard_page boundaries. start={start_line}, end={end_line}")
    exit(1)

print(f"Found dashboard_page from line {start_line+1} to {end_line+1}")

# Read the new function from a separate file
with open('_dashboard_new.py', 'r', encoding='utf-8') as f:
    new_func = f.read()

# Replace the old lines with the new function
new_lines = lines[:start_line] + [new_func + '\n'] + lines[end_line+1:]

with open('page_routes.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"SUCCESS: Replaced dashboard_page ({end_line-start_line+1} lines) with new version ({new_func.count(chr(10))} lines)")
