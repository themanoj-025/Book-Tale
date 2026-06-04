import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

with open('web_app.py', 'r', encoding='utf-8') as f:
    content = f.read()

changes = 0

# 2. HTML: Replace sidebar-user with dropdown
old_html = (
    '    <div class="sidebar-user" role="button" tabindex="0" aria-label="User menu" '
    'onclick="if(event.target===this||!event.target.closest(\'a,button\'))'
    "window.location.href='/profile/{{session.user_id}}'\" "
    'onkeydown="if(event.key===\'Enter\'||event.key===\' \'){event.preventDefault();'
    "if(!event.target.closest('a,button'))window.location.href='/profile/{{session.user_id}}'}\">\n"
    "      {{ _avatar_html(session.get('user_name','?'),40)|safe }}\n"
    '      <div class="sidebar-user-name" style="flex:1;min-width:0;">'
    '<div class="fw-bold" style="font-size:.9rem;">{{session.user_name}}</div>'
    '<div style="font-size:.8rem;color:var(--text-muted);">@{{session.user_id}}</div></div>\n'
    '      <a href="/logout" style="color:var(--text-muted);font-size:1.1rem;text-decoration:none;" '
    'title="Logout" role="button"><i class="bi bi-box-arrow-right"></i></a>\n'
    '    </div>'
)

new_html = (
    '    <div class="sidebar-user" role="button" tabindex="0" aria-label="User menu" '
    'aria-haspopup="true" aria-expanded="false" '
    'onclick="toggleUserDropdown(event)" '
    'onkeydown="if(event.key===\'Enter\'||event.key===\' \')'
    '{event.preventDefault();toggleUserDropdown(event)}">\n'
    "      {{ _avatar_html(session.get('user_name','?'),40)|safe }}\n"
    '      <div class="sidebar-user-name" style="flex:1;min-width:0;">'
    '<div class="fw-bold" style="font-size:.9rem;">{{session.user_name}}</div>'
    '<div style="font-size:.8rem;color:var(--text-muted);">@{{session.user_id}}</div></div>\n'
    '      <i class="bi bi-three-dots" style="color:var(--text-muted);font-size:1.1rem;'
    'transition:transform .2s;" id="userDropdownChevron"></i>\n'
    '      <div class="user-dropdown" id="userDropdown" role="menu" '
    'aria-label="User options">\n'
    '        <button class="user-dropdown-item" role="menuitem" '
    "onclick=\"event.stopPropagation();window.location.href='/profile/{{session.user_id}}'\">"
    '<i class="bi bi-person-fill" style="color:var(--primary);"></i>'
    '<div><div class="dd-item-label">Your Profile</div>'
    '<div class="dd-item-desc">View your public profile</div></div></button>\n'
    '        <div class="user-dropdown-divider"></div>\n'
    '        <button class="user-dropdown-item" role="menuitem" '
    "onclick=\"event.stopPropagation();window.location.href='/settings'\">"
    '<i class="bi bi-gear-fill" style="color:var(--text-muted);"></i>'
    '<div><div class="dd-item-label">Settings</div>'
    '<div class="dd-item-desc">Account &amp; preferences</div></div></button>\n'
    '        <button class="user-dropdown-item" role="menuitem" '
    "onclick=\"event.stopPropagation();window.location.href='/help'\">"
    '<i class="bi bi-question-circle-fill" style="color:var(--text-muted);"></i>'
    '<div><div class="dd-item-label">Help</div>'
    '<div class="dd-item-desc">Guides &amp; support</div></div></button>\n'
    '        <div class="user-dropdown-divider"></div>\n'
    '        <button class="user-dropdown-item user-dropdown-danger" role="menuitem" '
    "onclick=\"event.stopPropagation();window.location.href='/logout'\">"
    '<i class="bi bi-box-arrow-right"></i>'
    '<div><div class="dd-item-label">Logout</div>'
    '<div class="dd-item-desc">Sign out of your account</div></div></button>\n'
    '      </div>\n'
    '    </div>'
)

if old_html in content:
    content = content.replace(old_html, new_html, 1)
    changes += 1
    print('HTML: Applied')
else:
    print('HTML: Pattern not found')

# 3. JS: Add toggleUserDropdown function before the closing </script> tag
js_code = (
    'function toggleUserDropdown(e){\n'
    '  e.stopPropagation();\n'
    '  var dd=document.getElementById(\'userDropdown\');\n'
    '  var chevron=document.getElementById(\'userDropdownChevron\');\n'
    '  if(!dd)return;\n'
    '  var isOpen=dd.classList.contains(\'show\');\n'
    '  document.querySelectorAll(\'.user-dropdown.show\').forEach(function(d){d.classList.remove(\'show\')});\n'
    '  document.querySelectorAll(\'.sidebar-user\').forEach(function(s){s.setAttribute(\'aria-expanded\',\'false\')});\n'
    '  if(!isOpen){\n'
    '    dd.classList.add(\'show\');\n'
    '    e.currentTarget.setAttribute(\'aria-expanded\',\'true\');\n'
    '    if(chevron)chevron.style.transform=\'rotate(180deg)\';\n'
    '  } else {\n'
    '    if(chevron)chevron.style.transform=\'rotate(0deg)\';\n'
    '  }\n'
    '}\n'
    'document.addEventListener(\'click\',function(e){\n'
    '  if(!e.target.closest(\'.sidebar-user\')){\n'
    '    document.querySelectorAll(\'.user-dropdown.show\').forEach(function(d){d.classList.remove(\'show\')});\n'
    '    document.querySelectorAll(\'.sidebar-user\').forEach(function(s){s.setAttribute(\'aria-expanded\',\'false\')});\n'
    '    var ch=document.getElementById(\'userDropdownChevron\');\n'
    '    if(ch)ch.style.transform=\'rotate(0deg)\';\n'
    '  }\n'
    '});\n'
    'document.addEventListener(\'keydown\',function(e){\n'
    '  if(e.key===\'Escape\'){\n'
    '    document.querySelectorAll(\'.user-dropdown.show\').forEach(function(d){d.classList.remove(\'show\')});\n'
    '    document.querySelectorAll(\'.sidebar-user\').forEach(function(s){s.setAttribute(\'aria-expanded\',\'false\')});\n'
    '    var ch=document.getElementById(\'userDropdownChevron\');\n'
    '    if(ch)ch.style.transform=\'rotate(0deg)\';\n'
    '  }\n'
    '});\n'
)

old_js_marker = 'function closeAllModals(){document.querySelectorAll(\'.modal.show\').forEach(function(m){var bs=bootstrap.Modal.getInstance(m);if(bs)bs.hide()})}\n</script>'
new_js_marker = 'function closeAllModals(){document.querySelectorAll(\'.modal.show\').forEach(function(m){var bs=bootstrap.Modal.getInstance(m);if(bs)bs.hide()})}\n' + js_code + '</script>'

if old_js_marker in content:
    content = content.replace(old_js_marker, new_js_marker, 1)
    changes += 1
    print('JS: Applied')
else:
    print('JS: Pattern not found')
    # Try to find the closeAllModals line
    idx = content.find('closeAllModals')
    if idx >= 0:
        print(f'closeAllModals found at index {idx}')
        snippet = content[idx:idx+200]
        print(f'Snippet: {repr(snippet)}')

with open('web_app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print(f'Total changes: {changes}')
