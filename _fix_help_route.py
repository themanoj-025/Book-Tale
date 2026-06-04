import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

help_route = r"""
# HELP PAGE

@app.route("/help")
@login_required
def help_page():
    CONTENT = '<div class="animate-in">'
    CONTENT += '<div class="glass-card p-0 mb-4" style="overflow:hidden;">'
    CONTENT += '<div class="p-4" style="background:linear-gradient(135deg,var(--primary),#7c3aed);color:white;">'
    CONTENT += '<h4 class="fw-bold mb-0"><i class="bi bi-question-circle-fill me-2"></i> Help &amp; Support</h4>'
    CONTENT += '<p class="mb-0" style="opacity:.8;font-size:.85rem;">Guides, tips, and frequently asked questions</p>'
    CONTENT += '</div></div>'
    CONTENT += '<div class="row g-4">'
    # Getting Started
    CONTENT += '<div class="col-md-6"><div class="glass-card p-4">'
    CONTENT += '<h5 class="fw-bold mb-3"><i class="bi bi-book-fill text-primary me-2"></i>Getting Started</h5>'
    CONTENT += '<ul class="list-unstyled" style="font-size:.9rem;">'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Browse and search books from the Explore page</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Issue books from the book details page</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Write reviews and rate books you have read</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Connect with other readers in the community</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-primary me-2"></i> Create reading lists and track your progress</li>'
    CONTENT += '</ul></div>'
    # Account Settings
    CONTENT += '<div class="glass-card p-4">'
    CONTENT += '<h5 class="fw-bold mb-3"><i class="bi bi-gear-fill text-warning me-2"></i>Account Settings</h5>'
    CONTENT += '<ul class="list-unstyled" style="font-size:.9rem;">'
    CONTENT += "<li class=\"mb-2\"><i class=\"bi bi-arrow-right-circle text-warning me-2\"></i> Update your profile information in <a href='/settings'>Settings</a></li>"
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-warning me-2"></i> Change notification preferences</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-warning me-2"></i> Manage privacy settings for your profile</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-warning me-2"></i> Customize appearance with themes and font sizes</li>'
    CONTENT += '</ul></div></div>'
    # Library Rules
    CONTENT += '<div class="col-md-6"><div class="glass-card p-4">'
    CONTENT += '<h5 class="fw-bold mb-3"><i class="bi bi-shield-lock-fill text-info me-2"></i>Library Rules</h5>'
    CONTENT += '<ul class="list-unstyled" style="font-size:.9rem;">'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-info me-2"></i> Books can be issued for a limited period</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-info me-2"></i> Late returns incur a fine per day</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-info me-2"></i> Maximum borrow limit applies per user</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-arrow-right-circle text-info me-2"></i> Membership must be renewed periodically</li>'
    CONTENT += '</ul></div>'
    # Need Help
    CONTENT += '<div class="glass-card p-4">'
    CONTENT += '<h5 class="fw-bold mb-3"><i class="bi bi-envelope-fill text-success me-2"></i>Need Help?</h5>'
    CONTENT += '<p style="font-size:.9rem;">If you encounter any issues or have questions:</p>'
    CONTENT += '<ul class="list-unstyled" style="font-size:.9rem;">'
    CONTENT += '<li class="mb-2"><i class="bi bi-envelope-fill text-success me-2"></i> Contact the library staff for assistance</li>'
    CONTENT += '<li class="mb-2"><i class="bi bi-chat-dots-fill text-success me-2"></i> Post in the community for peer support</li>'
    CONTENT += "<li class=\"mb-2\"><i class=\"bi bi-journal-text text-success me-2\"></i> Check the <a href='/feed'>Feed</a> for announcements</li>"
    CONTENT += '</ul></div></div></div></div>'
    return render_page("Help & Support", CONTENT)

"""

insert_marker = "# \u2500\u2500\u2500 USER SETTINGS \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500"

if insert_marker in content:
    content = content.replace(insert_marker, help_route + '\n' + insert_marker, 1)
    print('Help route added before USER SETTINGS')
else:
    # Try a simpler match
    idx = content.find('USER SETTINGS')
    if idx >= 0:
        line_start = content.rfind('\n', 0, idx)
        full_line = content[line_start:idx + 20]
        print(f'Found USER SETTINGS at line: {repr(full_line[:80])}')
    else:
        print('USER SETTINGS not found at all')

with open('web_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done')
