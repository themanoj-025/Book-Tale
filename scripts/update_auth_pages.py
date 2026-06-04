"""
Update all auth routes in web_app.py to match PROMPT.txt Section 1 specs.
- Login: [Log In] button, show/hide password toggle, role='form' aria-label, role='alert' on errors
- Register: MEM-XXXX format, Confirm Password, 4-step strength meter, Reader/Librarian role selector
- Forgot/Reset/Verify: step indicators, icon-first heroes
- Landing page: new route with full hero, stats, carousel, features, social proof
"""
import re, os

WEB_APP_PATH = os.path.join(os.path.dirname(__file__), '..', 'web_app.py')

with open(WEB_APP_PATH, 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. Update render_auth_page to pass form_aria_label ──
old_render_auth = '''def render_auth_page(title, content, **kw):
    """Render an auth page using the split-screen auth_base.html template."""
    from flask import render_template
    return render_template('auth_base.html', title=title,
        session={}, auth_content=content, **kw)'''

new_render_auth = '''def render_auth_page(title, content, form_aria_label="", **kw):
    """Render an auth page using the split-screen auth_base.html template."""
    from flask import render_template
    return render_template('auth_base.html', title=title,
        session={}, auth_content=content, form_aria_label=form_aria_label, **kw)'''

content = content.replace(old_render_auth, new_render_auth)

# ── 2. Update login_page ──
# Find the login_page function and rebuild it
old_login_start = "@app.route(\"/login\", methods=[\"GET\", \"POST\"])\ndef login_page():"

# Find where the old login_page starts
idx = content.find(old_login_start)
if idx == -1:
    print("WARNING: login_page not found! Looking for alternative...")
    # Try alternative pattern
    alt = "@app.route(\"/login\", methods=[\"GET\",\"POST\"])"
    idx = content.find(alt)
    if idx != -1:
        # Replace with corrected version
        content = content[:idx] + old_login_start + content[idx+len(alt):]
        print("Fixed login route pattern")

# Find the end of login_page - next @app.route
idx_end = content.find("\n@app.route(", idx + len(old_login_start))
if idx_end == -1:
    print("ERROR: Could not find end of login_page!")
    exit(1)

new_login = '''@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "GET":
        s = _library_stats()
        CONTENT = (
            '<h2>Welcome Back</h2>'
            '<p class="auth-subtitle">Sign in to access your library dashboard</p>'
            '<form method="POST" role="form" aria-label="Login form">'
            '<div class="mb-3">'
            '<label class="form-label" for="loginUid">User ID</label>'
            '<input type="text" name="user_id" id="loginUid" class="form-control" placeholder="e.g. ADMIN001" required autofocus autocomplete="username">'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="loginPw">Password</label>'
            '<div class="password-wrapper">'
            '<input type="password" name="password" id="loginPw" class="form-control" placeholder="Enter your password" required autocomplete="current-password">'
            '<button type="button" class="password-toggle" onclick="togglePasswordVisibility(this)" aria-label="Toggle password visibility" aria-pressed="false" tabindex="-1"><i class="bi bi-eye-fill"></i></button>'
            '</div>'
            '</div>'
            '<div class="d-flex justify-content-between align-items-center mb-3">'
            '<div class="form-check">'
            '<input type="checkbox" class="form-check-input" id="rememberMe" name="remember" value="1">'
            '<label class="form-check-label" for="rememberMe" style="font-size:.85rem;color:var(--text-muted);">Remember me</label>'
            '</div>'
            '<a href="/forgot-password" style="font-size:.8rem;color:var(--primary);text-decoration:none;font-weight:600;">Forgot password?</a>'
            '</div>'
            '<button type="submit" class="btn btn-primary py-2"><i class="bi bi-shield-lock-fill me-2"></i>Log In</button>'
            '</form>'
            '<div class="auth-footer">New here? <a href="/register">Create an account</a></div>'
        )
        hero_script = '<script>fetch("/api/analytics/monthly").then(function(r){return r.json()}).then(function(d){if(d.values&&d.values.length){var el=document.getElementById("heroTxnsCount");if(el)el.textContent=d.values.reduce(function(a,b){return a+b},0)}}).catch(function(){})</script>'
        return render_auth_page("Login", CONTENT + hero_script, form_aria_label="Login form")

    from exceptions import AuthenticationError
    try:
        user = auth.login(request.form["user_id"],request.form["password"])
        session["user_id"]=user.user_id;session["user_name"]=user.name;session["role"]=user.role
        log("Web login",user.user_id)
        return redirect(url_for("feed_page"))
    except AuthenticationError:
        return render_auth_page("Login", (
            '<div class="alert alert-danger" role="alert" aria-live="assertive"><i class="bi bi-x-circle-fill me-1"></i> Invalid credentials. Please try again.</div>'
            '<a href="/login" class="btn btn-primary"><i class="bi bi-arrow-repeat me-2"></i> Try Again</a>'
        ), form_aria_label="Login form")\n'''

content = content[:idx] + new_login + content[idx_end:]

# ── 3. Update register_page ──
old_reg_start = "@app.route(\"/register\", methods=[\"GET\", \"POST\"])\ndef register_page():"
idx = content.find(old_reg_start)
if idx == -1:
    print("WARNING: register_page not found!")
else:
    idx_end = content.find("\n@app.route(", idx + len(old_reg_start))
    if idx_end == -1:
        print("ERROR: Could not find end of register_page!")
    else:
        new_register = '''@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "GET":
        CONTENT = (
            '<h2>Create Your Account</h2>'
            '<p class="auth-subtitle">Join BookTale and start your reading journey</p>'
            '<div class="role-selector" role="radiogroup" aria-label="Account type">'
            '<label class="role-option selected">'
            '<input type="radio" name="role" value="user" checked>'
            '<span class="role-icon">📖</span>Reader'
            '<span class="role-desc">Browse, review, and connect</span>'
            '</label>'
            '<label class="role-option">'
            '<input type="radio" name="role" value="librarian">'
            '<span class="role-icon">📚</span>Librarian'
            '<span class="role-desc">Manage library collections</span>'
            '</label>'
            '</div>'
            '<form method="POST" role="form" aria-label="Registration form">'
            '<div class="mb-3">'
            '<label class="form-label" for="regName">Full Name</label>'
            '<input type="text" name="name" id="regName" class="form-control" placeholder="e.g. Jane Doe" required>'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="regEmail">Email <span class="text-muted" style="font-weight:400;">(optional)</span></label>'
            '<input type="email" name="email" id="regEmail" class="form-control" placeholder="jane@example.com">'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="regUid">User ID</label>'
            '<input type="text" name="user_id" id="regUid" class="form-control" placeholder="e.g. MEM-0001" pattern="MEM-\\\\d{4}" title="Format: MEM-XXXX (e.g. MEM-0001)" required>'
            '<small class="text-muted" style="font-size:.7rem;">Format: MEM-XXXX (e.g. <code>MEM-0001</code>)</small>'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="regPw">Password</label>'
            '<div class="password-wrapper">'
            '<input type="password" name="password" id="regPw" class="form-control" placeholder="Create a strong password" required minlength="6" autocomplete="new-password">'
            '<button type="button" class="password-toggle" onclick="togglePasswordVisibility(this)" aria-label="Toggle password visibility" aria-pressed="false" tabindex="-1"><i class="bi bi-eye-fill"></i></button>'
            '</div>'
            '<div class="password-strength-bar" aria-hidden="true"><div class="segment"></div><div class="segment"></div><div class="segment"></div><div class="segment"></div></div>'
            '<div class="password-strength-text"></div>'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="regPw2">Confirm Password</label>'
            '<div class="password-wrapper">'
            '<input type="password" name="confirm_password" id="regPw2" class="form-control" placeholder="Repeat your password" required minlength="6" autocomplete="new-password">'
            '<button type="button" class="password-toggle" onclick="togglePasswordVisibility(this)" aria-label="Toggle password visibility" aria-pressed="false" tabindex="-1"><i class="bi bi-eye-fill"></i></button>'
            '</div>'
            '</div>'
            '<button type="submit" class="btn btn-primary py-2"><i class="bi bi-person-plus-fill me-2"></i>Create Account</button>'
            '</form>'
            '<div class="auth-footer">Already have an account? <a href="/login">Sign in</a></div>'
        )
        return render_auth_page("Register", CONTENT, form_aria_label="Registration form")

    # POST - handle registration
    user_id = request.form.get("user_id", "").strip()
    name = request.form.get("name", "").strip()
    password = request.form.get("password", "")
    confirm_pw = request.form.get("confirm_password", "")
    email = request.form.get("email", "").strip()
    role = request.form.get("role", "user")

    errors = []
    if not user_id or not name or not password:
        errors.append("All required fields must be filled")
    if password != confirm_pw:
        errors.append("Passwords do not match")
    if len(password) < 6:
        errors.append("Password must be at least 6 characters")
    if user_id and not user_id.startswith("MEM-"):
        errors.append("User ID must follow MEM-XXXX format")

    if errors:
        error_html = '<div class="alert alert-danger" role="alert" aria-live="assertive"><i class="bi bi-exclamation-triangle-fill me-1"></i> ' + '<br>'.join(errors) + '</div>'
        return render_auth_page("Register", error_html + '<a href="/register" class="btn btn-primary"><i class="bi bi-arrow-repeat me-2"></i> Try Again</a>', form_aria_label="Registration form")

    users = storage.load_users()
    if user_id in users:
        return render_auth_page("Register", (
            '<div class="alert alert-danger" role="alert" aria-live="assertive"><i class="bi bi-exclamation-triangle-fill me-1"></i> User ID already exists</div>'
            '<a href="/register" class="btn btn-primary"><i class="bi bi-arrow-repeat me-2"></i> Try Again</a>'
        ), form_aria_label="Registration form")

    from auth import hash_password as _hp, generate_verify_token as _gvt
    lib.register_user(user_id, name, email, "", role, _hp(password), actor="registration")

    # Send welcome email with verification link
    if email:
        try:
            from email_notifier import send_email
            token = _gvt(user_id)
            verify_url = request.host_url.rstrip("/") + "/verify-email?token=" + token
            send_email(email, "Welcome to BookTale!", (
                "<h2>Welcome to BookTale!</h2>"
                "<p>Thanks for joining, " + name + "!</p>"
                "<p>Please verify your email address:</p>"
                '<p><a href="' + verify_url + '" style="display:inline-block;padding:.6rem 1.2rem;background:#4f46e5;color:white;text-decoration:none;border-radius:8px;">Verify Email</a></p>'
                "<p>Or copy this link: " + verify_url + "</p>"
                "<p>Happy reading!</p>"
            ))
        except Exception as e:
            print("Welcome email error:", e)

    CONTENT = (
        '<div class="text-center">'
        '<div style="font-size:4rem;margin-bottom:1rem;">🎉</div>'
        '<h2>Welcome, ' + name + '!</h2>'
        '<p class="auth-subtitle">Your account has been created successfully.</p>'
        '</div>'
        '<a href="/login" class="btn btn-primary"><i class="bi bi-shield-lock-fill me-2"></i> Sign In</a>'
    )
    if email:
        CONTENT = (
            '<div class="text-center">'
            '<div style="font-size:4rem;margin-bottom:1rem;">📧</div>'
            '<h2>Check Your Email</h2>'
            '<p class="auth-subtitle">We sent a verification link to <strong>' + email + '</strong></p>'
            '<p style="font-size:.8rem;color:var(--text-muted);">Please verify your email to access all features.</p>'
            '</div>'
            '<a href="/login" class="btn btn-primary"><i class="bi bi-shield-lock-fill me-2"></i> Sign In</a>'
        )
    return render_auth_page("Registered", CONTENT)\n'''

        content = content[:idx] + new_register + content[idx_end:]

# ── 4. Update forgot_password_page ──
old_forgot_start = "@app.route(\"/forgot-password\", methods=[\"GET\", \"POST\"])\ndef forgot_password_page():"
idx = content.find(old_forgot_start)
if idx == -1:
    print("WARNING: forgot_password_page not found!")
else:
    idx_end = content.find("\n@app.route(", idx + len(old_forgot_start))
    if idx_end == -1:
        print("ERROR: Could not find end of forgot_password_page!")
    else:
        new_forgot = '''@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password_page():
    if request.method == "GET":
        CONTENT = (
            '<div class="step-indicator" aria-label="Step 1 of 3: Identify account">'
            '<div class="step active"><span class="step-num">1</span> Identify</div>'
            '<div class="step-line"></div>'
            '<div class="step"><span class="step-num">2</span> Verify</div>'
            '<div class="step-line"></div>'
            '<div class="step"><span class="step-num">3</span> Reset</div>'
            '</div>'
            '<div class="text-center mb-3">'
            '<div style="font-size:3rem;margin-bottom:.5rem;">🔐</div>'
            '<h2>Forgot Password?</h2>'
            '<p class="auth-subtitle">Enter your email or User ID and we\'ll send you a reset link</p>'
            '</div>'
            '<form method="POST" role="form" aria-label="Password reset form">'
            '<div class="mb-3">'
            '<label class="form-label" for="fpIdent">Email or User ID</label>'
            '<div class="input-group">'
            '<span class="input-group-text"><i class="bi bi-envelope-fill"></i></span>'
            '<input type="text" name="identity" id="fpIdent" class="form-control" placeholder="jane@example.com or MEM-0001" required autofocus>'
            '</div>'
            '</div>'
            '<button type="submit" class="btn btn-primary py-2"><i class="bi bi-send-fill me-2"></i>Send Reset Link</button>'
            '</form>'
            '<div class="auth-footer">Remember your password? <a href="/login">Sign in</a></div>'
        )
        return render_auth_page("Forgot Password", CONTENT, form_aria_label="Password reset form")

    # POST - anti-enumeration: always show success
    CONTENT = (
        '<div class="step-indicator" aria-label="Step 2 of 3: Check email">'
        '<div class="step completed"><span class="step-num">✓</span> Identify</div>'
        '<div class="step-line completed"></div>'
        '<div class="step active"><span class="step-num">2</span> Verify</div>'
        '<div class="step-line"></div>'
        '<div class="step"><span class="step-num">3</span> Reset</div>'
        '</div>'
        '<div class="text-center">'
        '<div style="font-size:4rem;margin-bottom:1rem;">📧</div>'
        '<h2>Check Your Email</h2>'
        '<p class="auth-subtitle">If an account exists, we\'ve sent a password reset link.</p>'
        '<p style="font-size:.8rem;color:var(--text-muted);">Please check your inbox and spam folder. The link expires in 1 hour.</p>'
        '</div>'
        '<a href="/login" class="btn btn-primary"><i class="bi bi-arrow-left me-2"></i> Back to Login</a>'
    )

    identity = request.form.get("identity", "").strip()
    if identity:
        try:
            from auth import generate_reset_token as _grt
            users = storage.load_users()
            target_user = None
            for u in users.values():
                if u.user_id == identity or u.email == identity:
                    target_user = u
                    break
            if target_user and target_user.email:
                from email_notifier import send_email
                token = _grt(target_user.user_id)
                reset_url = request.host_url.rstrip("/") + "/reset-password?token=" + token
                send_email(target_user.email, "Reset your BookTale password", (
                    "<h2>Password Reset Request</h2>"
                    "<p>Hi " + target_user.name + ",</p>"
                    "<p>Click the button below to reset your password:</p>"
                    '<p><a href="' + reset_url + '" style="display:inline-block;padding:.6rem 1.2rem;background:#4f46e5;color:white;text-decoration:none;border-radius:8px;">Reset Password</a></p>'
                    "<p>Or copy this link: " + reset_url + "</p>"
                    "<p>This link expires in 1 hour.</p>"
                    "<p>If you didn't request this, you can safely ignore this email.</p>"
                ))
        except Exception as e:
            print("Reset email error:", e)

    return render_auth_page("Email Sent", CONTENT)\n'''

        content = content[:idx] + new_forgot + content[idx_end:]

# ── 5. Update verify_email_page ──
old_verify_start = "@app.route(\"/verify-email\")\ndef verify_email_page():"
idx = content.find(old_verify_start)
if idx == -1:
    print("WARNING: verify_email_page not found!")
else:
    idx_end = content.find("\n@app.route(", idx + len(old_verify_start))
    if idx_end == -1:
        print("ERROR: Could not find end of verify_email_page!")
    else:
        new_verify = '''@app.route("/verify-email")
def verify_email_page():
    token = request.args.get("token", "")
    if not token:
        CONTENT = (
            '<div class="text-center">'
            '<div style="font-size:4rem;margin-bottom:1rem;">🔗</div>'
            '<h2>Invalid Link</h2>'
            '<p class="auth-subtitle">No verification token provided.</p>'
            '</div>'
            '<a href="/login" class="btn btn-primary"><i class="bi bi-arrow-left me-2"></i> Back to Login</a>'
        )
        return render_auth_page("Verify Email", CONTENT)

    from auth import consume_verify_token as _cvt
    user_id = _cvt(token)

    if not user_id:
        CONTENT = (
            '<div class="text-center">'
            '<div style="font-size:4rem;margin-bottom:1rem;">⏰</div>'
            '<h2>Invalid or Expired Link</h2>'
            '<p class="auth-subtitle">This verification link has expired or is invalid. Please register again for a new link.</p>'
            '</div>'
            '<a href="/register" class="btn btn-primary"><i class="bi bi-person-plus-fill me-2"></i> Register Again</a>'
        )
        return render_auth_page("Verify Email", CONTENT)

    users = storage.load_users()
    if user_id in users:
        users[user_id].email_verified = True
        storage.save_users(users)

    CONTENT = (
        '<div class="text-center">'
        '<div style="font-size:4rem;margin-bottom:1rem;">✅</div>'
        '<h2>Email Verified!</h2>'
        '<p class="auth-subtitle">Your email has been verified. You can now access all features.</p>'
        '</div>'
        '<a href="/login" class="btn btn-primary"><i class="bi bi-shield-lock-fill me-2"></i> Sign In</a>'
    )
    return render_auth_page("Email Verified", CONTENT)\n'''

        content = content[:idx] + new_verify + content[idx_end:]

# ── 6. Update reset_password_page ──
old_reset_start = "@app.route(\"/reset-password\", methods=[\"GET\", \"POST\"])\ndef reset_password_page():"
idx = content.find(old_reset_start)
if idx == -1:
    print("WARNING: reset_password_page not found!")
else:
    idx_end = content.find("\n@app.route(", idx + len(old_reset_start))
    if idx_end == -1:
        print("ERROR: Could not find end of reset_password_page!")
    else:
        new_reset = '''@app.route("/reset-password", methods=["GET", "POST"])
def reset_password_page():
    if request.method == "GET":
        token = request.args.get("token", "")
        from auth import verify_reset_token as _vrt
        user_id = _vrt(token)
        if not user_id:
            CONTENT = (
                '<div class="text-center">'
                '<div style="font-size:4rem;margin-bottom:1rem;">🔗</div>'
                '<h2>Invalid Link</h2>'
                '<p class="auth-subtitle">This password reset link is invalid or has expired.</p>'
                '</div>'
                '<a href="/forgot-password" class="btn btn-primary"><i class="bi bi-arrow-repeat me-2"></i> Request New Link</a>'
            )
            return render_auth_page("Reset Password", CONTENT)

        from auth import consume_reset_token as _crt
        _crt(token)  # consume it so it's one-time-use
        # Re-generate for the form (simplified: pass user_id in hidden field)
        CONTENT = (
            '<div class="step-indicator" aria-label="Step 3 of 3: Reset password">'
            '<div class="step completed"><span class="step-num">✓</span> Identify</div>'
            '<div class="step-line completed"></div>'
            '<div class="step completed"><span class="step-num">✓</span> Verify</div>'
            '<div class="step-line completed"></div>'
            '<div class="step active"><span class="step-num">3</span> Reset</div>'
            '</div>'
            '<div class="text-center mb-3">'
            '<div style="font-size:3rem;margin-bottom:.5rem;">🔑</div>'
            '<h2>Reset Your Password</h2>'
            '<p class="auth-subtitle">Choose a new password for your account</p>'
            '</div>'
            '<form method="POST" role="form" aria-label="Reset password form">'
            '<input type="hidden" name="token" value="' + token + '">'
            '<div class="mb-3">'
            '<label class="form-label" for="rpPw">New Password</label>'
            '<div class="password-wrapper">'
            '<input type="password" name="password" id="rpPw" class="form-control" placeholder="At least 6 characters" required minlength="6" autocomplete="new-password">'
            '<button type="button" class="password-toggle" onclick="togglePasswordVisibility(this)" aria-label="Toggle password visibility" aria-pressed="false" tabindex="-1"><i class="bi bi-eye-fill"></i></button>'
            '</div>'
            '<div class="password-strength-bar" aria-hidden="true"><div class="segment"></div><div class="segment"></div><div class="segment"></div><div class="segment"></div></div>'
            '<div class="password-strength-text"></div>'
            '</div>'
            '<div class="mb-3">'
            '<label class="form-label" for="rpPw2">Confirm New Password</label>'
            '<div class="password-wrapper">'
            '<input type="password" name="confirm_password" id="rpPw2" class="form-control" placeholder="Repeat new password" required minlength="6" autocomplete="new-password">'
            '<button type="button" class="password-toggle" onclick="togglePasswordVisibility(this)" aria-label="Toggle password visibility" aria-pressed="false" tabindex="-1"><i class="bi bi-eye-fill"></i></button>'
            '</div>'
            '</div>'
            '<button type="submit" class="btn btn-primary py-2"><i class="bi bi-shield-check-fill me-2"></i> Reset Password</button>'
            '</form>'
            '<div class="auth-footer"><a href="/login">Back to Login</a></div>'
        )
        return render_auth_page("Reset Password", CONTENT, form_aria_label="Reset password form")

    # POST - process password reset
    token = request.form.get("token", "")
    password = request.form.get("password", "")
    confirm_pw = request.form.get("confirm_password", "")

    if not token or not password:
        return render_auth_page("Reset Password", '<div class="alert alert-danger" role="alert" aria-live="assertive">Missing required fields</div><a href="/forgot-password" class="btn btn-primary">Try Again</a>', form_aria_label="Reset password form")

    if password != confirm_pw:
        return render_auth_page("Reset Password", '<div class="alert alert-danger" role="alert" aria-live="assertive">Passwords do not match</div><a href="/forgot-password" class="btn btn-primary">Try Again</a>', form_aria_label="Reset password form")

    if len(password) < 6:
        return render_auth_page("Reset Password", '<div class="alert alert-danger" role="alert" aria-live="assertive">Password must be at least 6 characters</div><a href="/forgot-password" class="btn btn-primary">Try Again</a>', form_aria_label="Reset password form")

    from auth import consume_reset_token as _crt, hash_password as _hp
    user_id = _crt(token)
    if not user_id:
        return render_auth_page("Reset Password", '<div class="alert alert-danger" role="alert" aria-live="assertive">Invalid or expired token</div><a href="/forgot-password" class="btn btn-primary">Try Again</a>', form_aria_label="Reset password form")

    users = storage.load_users()
    user = users.get(user_id)
    if not user:
        return render_auth_page("Reset Password", '<div class="alert alert-danger" role="alert" aria-live="assertive">User not found</div>', form_aria_label="Reset password form")

    user.password_hash = _hp(password)
    storage.save_users(users)

    CONTENT = (
        '<div class="text-center">'
        '<div style="font-size:4rem;margin-bottom:1rem;">🔐</div>'
        '<h2>Password Reset!</h2>'
        '<p class="auth-subtitle">Your password has been updated successfully.</p>'
        '</div>'
        '<a href="/login" class="btn btn-primary"><i class="bi bi-shield-lock-fill me-2"></i> Sign In with New Password</a>'
    )
    return render_auth_page("Password Reset", CONTENT)\n'''

        content = content[:idx] + new_reset + content[idx_end:]

# ── 7. Add Landing Page Route ──
# Insert before the auth routes (before logout)
idx_logout = content.find("@app.route(\"/logout\")")
if idx_logout == -1:
    print("WARNING: logout not found!")
else:
    landing_route = '''
# ─── LANDING PAGE ────────────────────────────────────────────────────

@app.route("/landing")
@app.route("/")
def landing_page():
    """Public landing page with hero, stats, features, and social proof."""
    if "user_id" in session:
        return redirect(url_for("feed_page"))
    
    from flask import render_template
    
    # Build featured books carousel
    books = [b for b in storage.load_books().values() if not b.is_deleted]
    random.shuffle(books)
    featured = books[:6]
    carousel_html = ""
    for i, b in enumerate(featured):
        cc = cat_color(b.category)
        initials = _initials(b.title)
        carousel_html += (
            '<div class="carousel-item' + (' active' if i == 0 else '') + '">'
            '<div class="featured-book" style="perspective:1000px;">'
            '<div class="book-card-3d" style="transform:rotateY(' + str((i - 2) * 3) + 'deg);transition:transform .5s var(--ease);">'
            '<div class="book-cover-wrapper" style="width:160px;aspect-ratio:2/3;border-radius:8px;overflow:hidden;box-shadow:0 8px 32px rgba(0,0,0,.2);margin:0 auto;background:linear-gradient(135deg,' + cc + ',' + cc + 'dd);display:flex;align-items:center;justify-content:center;">'
            '<span style="color:white;font-size:1.5rem;font-weight:700;">' + initials + '</span>'
            '</div>'
            '<div class="mt-2 text-center"><div class="fw-bold" style="font-size:.85rem;">' + h(b.title) + '</div><div class="text-muted" style="font-size:.75rem;">' + h(b.author) + '</div>'
            '<span class="badge" style="background:' + cc + '20;color:' + cc + ';font-size:.65rem;margin-top:4px;">' + h(b.category) + '</span></div>'
            '</div></div></div>'
        )
    
    features_grid = (
        '<div class="row g-3">'
        '<div class="col-md-4"><div class="feature-card"><div class="feature-icon"><i class="bi bi-chat-dots-fill"></i></div><h3>Social Feed</h3><p>Share reviews, follow readers, and discover books through your network.</p></div></div>'
        '<div class="col-md-4"><div class="feature-card"><div class="feature-icon"><i class="bi bi-journal-text"></i></div><h3>Reading Diary</h3><p>Log your reading journey with ratings, notes, and personal reflections.</p></div></div>'
        '<div class="col-md-4"><div class="feature-card"><div class="feature-icon"><i class="bi bi-stars"></i></div><h3>AI Recommendations</h3><p>Get personalized book suggestions based on your reading history and taste.</p></div></div>'
        '<div class="col-md-4"><div class="feature-card"><div class="feature-icon"><i class="bi bi-trophy-fill"></i></div><h3>Challenges</h3><p>Set reading goals, track progress, and compete with friends.</p></div></div>'
        '<div class="col-md-4"><div class="feature-card"><div class="feature-icon"><i class="bi bi-people-fill"></i></div><h3>Book Clubs</h3><p>Join communities, discuss books, and participate in group reads.</p></div></div>'
        '<div class="col-md-4"><div class="feature-card"><div class="feature-icon"><i class="bi bi-phone"></i></div><h3>PWA Ready</h3><p>Install on your device for offline access and a native-like experience.</p></div></div>'
        '</div>'
    )
    
    testimonials = (
        '<div class="row g-3 mt-2">'
        '<div class="col-md-4"><div class="testimonial-card"><div class="stars">★★★★★</div><p>"BookTale completely transformed how I track my reading. The AI recommendations are uncanny!"</p><div class="author">— Sarah K., <span>Avid Reader</span></div></div></div>'
        '<div class="col-md-4"><div class="testimonial-card"><div class="stars">★★★★★</div><p>"As a librarian, this platform makes managing our collection a breeze. The community features are a bonus."</p><div class="author">— Marcus J., <span>Librarian</span></div></div></div>'
        '<div class="col-md-4"><div class="testimonial-card"><div class="stars">★★★★☆</div><p>"I\'ve discovered so many new books through the social feed. It\'s like Goodreads but better!"</p><div class="author">— Elena R., <span>Book Blogger</span></div></div></div>'
        '</div>'
    )
    
    return render_template('landing.html',
        title="BookTale",
        session=session,
        carousel_html=carousel_html,
        features_html=features_grid,
        testimonials_html=testimonials,
        has_books=len(featured) > 0
    )\n'''

    content = content[:idx_logout] + landing_route + content[idx_logout:]

# Write back
with open(WEB_APP_PATH, 'w', encoding='utf-8') as f:
    f.write(content)

print("All auth routes updated successfully!")
print(f"File size: {len(content):,} chars")
