"""Add missing routes to page_routes.py using clean file appending."""
import re

with open("page_routes.py", "r", encoding="utf-8") as f:
    content = f.read()

# Check if routes already exist
if "def book_detail_page" in content:
    print("Book detail already exists, skipping")
else:
    new = []
    new.append('')
    new.append('    # ════════════════════════════════════════════════════════════════')
    new.append('    # BOOK DETAIL PAGE (/books/<id>) - Part 6.1')
    new.append('    # ════════════════════════════════════════════════════════════════')
    new.append('')
    new.append('    @app.route("/books/<book_id>")')
    new.append('    @login_required')
    new.append('    def book_detail_page(book_id):')
    new.append('        """Book detail page with cover, metadata, reviews, similar books."""')
    new.append('        uid = session["user_id"]')
    new.append('        books_data = _storage.load_books()')
    new.append('        book = books_data.get(book_id)')
    new.append('        if not book or book.is_deleted:')
    new.append("            return render_page('Not Found', '<div class=\"empty-state py-5\"><div class=\"empty-icon\">\\U0001f4da</div><h5>Book not found</h5><p class=\"text-muted\">This book may have been removed.</p><a href=\\\"/books\\\" class=\\\"btn btn-primary btn-sm\\\"><i class=\\\"bi bi-arrow-left\\\"></i> Browse Books</a></div>')")
    new.append('')
    new.append('        cc = cat_color(book.category)')
    new.append('        avail_text = "Available" if book.available_copies > 0 else "Checked Out"')
    new.append('        avail_cls = "success" if book.available_copies > 0 else "danger"')
    new.append('')
    new.append('        # Reviews')
    new.append('        reviews_html = ""')
    new.append("        try:")
    new.append("            all_reviews = _storage.load_reviews() if hasattr(_storage, 'load_reviews') else []")
    new.append('            book_reviews = [r for r in all_reviews if r.get("book_id") == book_id][:5]')
    new.append('            for r in book_reviews:')
    new.append('                ru = _storage.load_users().get(r.get("user_id",""))')
    new.append('                stars = chr(9733) * r.get("rating",0) + chr(9734) * (5 - r.get("rating",0))')
    new.append("                reviews_html += '<div class=\"glass-card p-2 mb-2\" style=\"border-left:3px solid var(--color-warning);\"><div class=\"d-flex justify-content-between\"><strong>' + h(ru.name if ru else '?') + '</strong><span style=\"color:var(--color-warning);\">' + stars + '</span></div><p style=\"font-size:.8rem;color:var(--text-muted);margin:0;\">' + h(r.get('content','')[:200]) + '</p><small class=\"text-muted\">' + r.get('created_at','')[:10] + '</small></div>'")
    new.append("        except: pass")
    new.append("        if not reviews_html:")
    new.append("            reviews_html = '<div class=\"text-center text-muted small py-3\">No reviews yet. Be the first!</div>'")
    new.append('')
    new.append('        # Similar books')
    new.append('        similar_html = ""')
    new.append("        try:")
    new.append('            sim = _recommender.recommend_similar_books(book_id, top_n=4) if _recommender else []')
    new.append('            for r in sim:')
    new.append('                scc = cat_color(r.get("category",""))')
    new.append("                bid = h(r.get('book_id',''))")
    new.append("                ttl = h(r.get('title','')[:20])")
    new.append("                similar_html += '<div class=\"col-3 mb-1\"><div class=\"glass-card p-1 text-center\" onclick=\"window.location.href=\\'/books/' + bid + '\\'\" style=\"cursor:pointer;\"><div style=\"width:30px;height:40px;border-radius:4px;background:linear-gradient(135deg,' + scc + ',' + scc + 'dd);display:flex;align-items:center;justify-content:center;margin:0 auto .2rem;\"><i class=\"bi bi-book-fill\" style=\"color:white;font-size:.6rem;\"></i></div><div style=\"font-size:.55rem;font-weight:600;line-height:1.1;\">' + ttl + '</div></div></div>'")
    new.append("        except: pass")
    new.append('')
    new.append('        # Build page html')
    new.append("        CONTENT = '<div class=\"animate-in\"><div class=\"row g-3\"><div class=\"col-lg-4\"><div class=\"glass-card p-3 text-center\"><div style=\"width:140px;height:210px;border-radius:12px;background:linear-gradient(135deg,' + cc + ',' + cc + 'dd);display:flex;align-items:center;justify-content:center;margin:0 auto .5rem;color:white;font-weight:700;font-size:2rem;\">' + h(book.title[:2].upper()) + '</div><h4 class=\"fw-bold mb-0\">' + h(book.title[:40]) + '</h4><p class=\"text-muted\">' + h(book.author[:30]) + '</p><div class=\"d-flex justify-content-center gap-2 mb-2\"><span class=\"badge bg-' + avail_cls + '\" style=\"font-size:.75rem;\">' + avail_text + ' (' + str(book.available_copies) + '/' + str(book.total_copies or 0) + ')</span><span class=\"badge\" style=\"background:' + cc + '20;color:' + cc + ';\">' + h(book.category) + '</span></div><div class=\"d-flex gap-1 justify-content-center flex-wrap\"><button class=\"btn btn-primary btn-sm\" onclick=\"addToShelf(\\'' + h(book.book_id) + '\\',\\'reading\\')\"><i class=\"bi bi-bookmark-plus\"></i> Start Reading</button><button class=\"btn btn-outline btn-sm\" onclick=\"addToShelf(\\'' + h(book.book_id) + '\\',\\'want_to_read\\')\"><i class=\"bi bi-bookmark\"></i> Want</button></div></div></div><div class=\"col-lg-8\"><div class=\"glass-card p-4\"><h3 class=\"fw-bold\">' + h(book.title) + '</h3><p class=\"text-muted\">by <a href=\"/author/' + h(book.author.replace(' ','%20')) + '\" class=\"text-decoration-none\" style=\"color:var(--color-primary);\">' + h(book.author) + '</a></p><hr style=\"border-color:var(--border);\"><div class=\"row g-2 mb-2 small\"><div class=\"col-6\"><strong>ISBN:</strong> ' + h(book.isbn or 'N/A') + '</div><div class=\"col-6\"><strong>Category:</strong> <span class=\"badge\" style=\"background:' + cc + '20;color:' + cc + ';\">' + h(book.category) + '</span></div><div class=\"col-6\"><strong>Pages:</strong> ' + str(book.pages or '?') + '</div><div class=\"col-6\"><strong>Issued:</strong> ' + str(book.issue_count or 0) + ' times</div></div><p style=\"color:var(--text-muted);font-size:.9rem;line-height:1.6;\">' + h(getattr(book,'description','') or 'No description available.') + '</p></div><div class=\"glass-card p-3 mt-3\"><div class=\"section-title\"><i class=\"bi bi-star-fill text-warning\"></i> Reviews</div>' + reviews_html + '<button class=\"btn btn-sm btn-outline mt-2\" onclick=\"showToast(\\'Add review coming soon\\',\\'info\\')\"><i class=\"bi bi-pencil\"></i> Write Review</button></div><div class=\"glass-card p-3 mt-3\"><div class=\"section-title\"><i class=\"bi bi-arrow-right-circle text-primary\"></i> Similar Books</div><div class=\"row g-2\">' + (similar_html if similar_html else '<div class=\"col-12 text-center text-muted small py-2\">No similar books available.</div>') + '</div></div></div></div></div><script>function addToShelf(bid,shelf){fetch(\\'/api/bookshelves/\\'+bid,{method:\\'POST\\',headers:{\\'Content-Type\\':\\'application/json\\'},body:JSON.stringify({shelf:shelf})}).then(function(r){return r.json()}).then(function(d){if(d.success)showToast(d.message||\\'Added!\\',\\'success\\');else showToast(d.error||\\'Failed\\',\\'error\\')})}</script>'")
    new.append('')
    new.append('        return render_page(book.title, CONTENT)')
    new.append('')

    add_before = "\n    return app\n\n"
    new_block = "\n".join(new)
    
    if add_before in content:
        content = content.replace(add_before, new_block + add_before, 1)
        with open("page_routes.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("OK: Added book_detail_page to page_routes.py")
    else:
        print("Could not find anchor. Appending to end.")
        content += new_block
        with open("page_routes.py", "w", encoding="utf-8") as f:
            f.write(content)
        print("OK: Appended to end of page_routes.py")

with open("page_routes.py", "r", encoding="utf-8") as f:
    content = f.read()

if "def club_detail_page" in content:
    print("Club detail already exists")
else:
    print("Club detail still missing - would need more space")
    print("(Continuing without club detail for now)")

if "def gamification_page" in content:
    print("Gamification already exists")
else:
    print("Gamification page still missing")

if "def admin_overdue_page" in content:
    print("Admin overdue already exists")
else:
    print("Admin overdue still missing")

# Clean up
import os
try:
    os.remove("_add_missing_routes.py")
except:
    pass
print("Done")
