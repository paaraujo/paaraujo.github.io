#!/usr/bin/env python3
"""
generate_pub_page.py — Generate a publication detail page from publications-data.json.

Usage:
    # Generate page for a slug already in publications-data.json:
    python3 generate_pub_page.py <slug>

    # Add a new publication interactively and generate its page:
    python3 generate_pub_page.py --add

    # Regenerate ALL pages from JSON (useful after bulk edits):
    python3 generate_pub_page.py --all

    # Refresh publications-data.json from existing HTML pages (re-extraction):
    python3 generate_pub_page.py --extract

Example for a new paper:
    1. Add an entry to publications-data.json manually (or use --add).
    2. Place featured.png (or .jpg) in publication/<slug>/ (optional).
    3. Run: python3 generate_pub_page.py <slug>
"""

import os, re, sys, json, shutil
from urllib.parse import quote

SITE_ROOT   = os.path.dirname(os.path.abspath(__file__))
PUB_ROOT    = os.path.join(SITE_ROOT, 'publication')
JSON_PATH   = os.path.join(SITE_ROOT, 'publications-data.json')
TEMPLATE    = os.path.join(PUB_ROOT, '_template.html')

# ── Template constants (must match what is actually in the template file) ──────
T_SLUG   = 'hu-longnav-2026'
T_TITLE  = 'LongNav-R1: Horizon-Adaptive Multi-Turn RL for Long-Horizon VLA Navigation [RSS 2026]'
T_DATE   = 'April 2026'
T_VENUE  = 'Robotics: Science and Systems (RSS 2026)'
T_PAPER  = 'https://arxiv.org/pdf/2602.12351'
T_AUTHORS = [
    'Paulo Ricardo M. de Araujo', 'Avery Xi', 'Qixin Xiao',
    'Seth Isaacson', 'Henry X Liu', 'Ram Vasudevan', 'Maani Ghaffari',
]
T_FEATURED_WEBP = (
    'featured_hueb54c0561b2b394309b840b0e098356b_3599944_720x2500_fit_q75_h2_lanczos_3.webp'
)


def _video_embed(url):
    """Return an HTML block for embedding a video (YouTube, Vimeo, or local MP4)."""
    yt = re.search(r'(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)', url)
    vm = re.search(r'vimeo\.com/(\d+)', url)
    if yt:
        vid = yt.group(1)
        src = f'https://www.youtube-nocookie.com/embed/{vid}'
        return (
            '<div class="pub-video article-container mt-4 mb-4">'
            '<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;">'
            f'<iframe src="{src}" style="position:absolute;top:0;left:0;width:100%;height:100%;"'
            ' frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media;'
            ' gyroscope; picture-in-picture" allowfullscreen></iframe>'
            '</div></div>\n'
        )
    elif vm:
        vid = vm.group(1)
        src = f'https://player.vimeo.com/video/{vid}'
        return (
            '<div class="pub-video article-container mt-4 mb-4">'
            '<div style="position:relative;padding-bottom:56.25%;height:0;overflow:hidden;">'
            f'<iframe src="{src}" style="position:absolute;top:0;left:0;width:100%;height:100%;"'
            ' frameborder="0" allow="autoplay; fullscreen; picture-in-picture" allowfullscreen></iframe>'
            '</div></div>\n'
        )
    else:
        # local file or direct URL
        return (
            '<div class="pub-video article-container mt-4 mb-4">'
            f'<video controls style="width:100%;">'
            f'<source src="{url}" type="video/mp4">'
            'Your browser does not support the video tag.'
            '</video></div>\n'
        )


def load_json():
    with open(JSON_PATH) as f:
        return json.load(f)

def save_json(pubs):
    with open(JSON_PATH, 'w') as f:
        json.dump(pubs, f, indent=2, ensure_ascii=False)


def build_authors_html(authors):
    """Build the <div>...</div> author list for the article-metadata section."""
    spans = ', '.join(f'<span >\n      {a}</span>' for a in authors)
    return f'\n  <div>\n    \n\n  {spans}\n  </div>\n  '


def build_authors_html_template(authors):
    """Exact multiline block matching the template author section."""
    spans = ', '.join(f'<span >\n      {a}</span>' for a in T_AUTHORS)
    return f'\n  <div>\n    \n\n  {spans}\n  </div>\n  '


def generate_page(pub, force=False):
    slug = pub['slug']
    folder = os.path.join(PUB_ROOT, slug)
    out_path = os.path.join(folder, 'index.html')

    if not force and os.path.exists(out_path):
        print(f"[skip] {slug}/index.html already exists (use --all to force-regenerate)")
        return

    os.makedirs(folder, exist_ok=True)

    with open(TEMPLATE) as f:
        html = f.read()

    title       = pub['title']
    authors     = pub['authors']
    date_label  = pub['date_label']
    venue       = pub.get('venue', '')
    paper_url   = pub.get('paper_url', '')
    code_url    = pub.get('code_url', '')
    abstract    = pub.get('abstract', '')
    featured    = pub.get('featured_img', 'featured.png')
    pub_type    = pub.get('pub_type', 'conference')
    video_url   = pub.get('video_url') or ''

    # ── 1. Slug URLs (plain and URL-encoded for share buttons) ──────────────────
    html = html.replace(f'/publication/{T_SLUG}/', f'/publication/{slug}/')
    html = html.replace(f'publication/{T_SLUG}/', f'publication/{slug}/')
    t_slug_enc = quote(f'/publication/{T_SLUG}/', safe='')
    n_slug_enc = quote(f'/publication/{slug}/', safe='')
    html = html.replace(t_slug_enc, n_slug_enc)

    # ── 1b. Domain ───────────────────────────────────────────────────────────────
    html = html.replace('yuehu.github.io', 'paaraujo.github.io')

    # ── 2. Title (plain text occurrences) ───────────────────────────────────────
    html = html.replace(T_TITLE, title)

    # ── 3. URL-encoded title in share buttons ────────────────────────────────────
    t_enc  = quote(T_TITLE,  safe='')
    t_enc2 = T_TITLE.replace(' ', '&#43;').replace(':', '%3A').replace('[', '%5B').replace(']', '%5D')
    n_enc  = quote(title,    safe='')
    n_enc2 = title.replace(' ', '&#43;').replace(':', '%3A').replace('[', '%5B').replace(']', '%5D')
    html = html.replace(t_enc, n_enc)
    html = html.replace(t_enc2, n_enc2)

    # ── 4. Date ─────────────────────────────────────────────────────────────────
    html = re.sub(
        r'(<span class="article-date"[^>]*>)(.*?)(</span>)',
        lambda m: m.group(1) + '\n    \n    \n      \n    \n    ' + date_label + '\n  ' + m.group(3),
        html, count=1, flags=re.DOTALL
    )

    # ── 5. Venue ─────────────────────────────────────────────────────────────────
    html = html.replace(f'<em>{T_VENUE}</em>', f'<em>{venue}</em>' if venue else '')

    # ── 6. Authors ───────────────────────────────────────────────────────────────
    old_author_block = build_authors_html_template(T_AUTHORS)
    new_author_block = build_authors_html(authors)
    if old_author_block in html:
        html = html.replace(old_author_block, new_author_block, 1)
    else:
        # Fallback: replace individual author spans in the metadata area
        for old_a, new_a in zip(T_AUTHORS, authors):
            html = html.replace(f'<span >\n      {old_a}</span>', f'<span >\n      {new_a}</span>', 1)

    # ── 7. Paper URL ─────────────────────────────────────────────────────────────
    if paper_url:
        html = html.replace(T_PAPER, paper_url)
    else:
        # Remove the paper button entirely
        html = re.sub(
            r'<a class="btn btn-outline-primary btn-page-header"[^>]*href="' + re.escape(T_PAPER) + r'"[^>]*>.*?</a>',
            '', html, flags=re.DOTALL
        )

    # ── 8. Code button ───────────────────────────────────────────────────────────
    # The template has no code button; insert one after the Paper button if needed
    if code_url:
        code_btn = (
            '\n\n  <a class="btn btn-outline-primary btn-page-header" '
            f'href="{code_url}" target="_blank" rel="noopener">\n'
            '    <i class="fab fa-github mr-1"></i>Code</a>\n'
        )
        html = html.replace(
            '\n</div>\n\n\n</div>\n\n\n<div class="article-header',
            code_btn + '\n</div>\n\n\n</div>\n\n\n<div class="article-header'
        )

    # ── 9. Featured image ────────────────────────────────────────────────────────
    img_folder = os.path.join(folder)
    has_image = featured and os.path.exists(os.path.join(img_folder, featured))
    if has_image:
        # Compute display dimensions from actual image size (scaled to 720px width)
        try:
            from PIL import Image as PILImage
            with PILImage.open(os.path.join(img_folder, featured)) as _im:
                _ow, _oh = _im.size
            img_w, img_h = 720, round(720 * _oh / _ow)
        except Exception:
            img_w, img_h = 720, 480

        # Replace hashed webp src and dimensions
        html = re.sub(
            r'src="/publication/' + re.escape(slug) + r'/[^"]+\.(webp|png|jpg|gif)"(\s+width="\d+")?(\s+height="\d+")?',
            f'src="/publication/{slug}/{featured}" width="{img_w}" height="{img_h}"',
            html
        )
        # Update wrapper max-height to match actual image height (prevents overflow)
        html = re.sub(
            r'(class="article-header article-container featured-image-wrapper[^"]*"[^>]*style="[^"]*max-width:\s*\d+px;\s*)max-height:\s*\d+px',
            rf'\g<1>max-height:{img_h}px',
            html
        )
    else:
        # Remove the featured-image-wrapper div entirely
        html = re.sub(
            r'\n?<div class="article-header article-container featured-image-wrapper[^>]*>.*?</div>\n?</div>\n?',
            '\n',
            html, flags=re.DOTALL
        )

    # ── 10. Publication type ─────────────────────────────────────────────────────
    TYPE_MAP = {
        'conference': ('1', 'Conference paper'),
        'journal':    ('2', 'Journal article'),
        'preprint':   ('3', 'Preprint / Working Paper'),
        'workshop':   ('1', 'Workshop paper'),
    }
    type_id, type_label = TYPE_MAP.get(pub_type, ('1', 'Conference paper'))
    html = re.sub(
        r'(<a href="/publication/#)\d+(">)\s*\n\s*Conference paper\s*\n\s*(</a>)',
        lambda m: f'{m.group(1)}{type_id}{m.group(2)}\n              {type_label}\n            {m.group(3)}',
        html
    )

    # ── 11. Video ────────────────────────────────────────────────────────────────
    if video_url:
        video_html = _video_embed(video_url)
        # Insert AFTER the featured-image-wrapper (between its closing divs and
        # the article-container), so the order is: image → video → content.
        # For pages without a featured image, insert at the top of the container.
        if 'article-header article-container featured-image-wrapper' in html:
            html = re.sub(
                r'(</div>\n</div>\n\n\n\n)(\s*<div class="article-container">)',
                lambda m: m.group(1) + video_html + m.group(2),
                html, count=1
            )
        else:
            html = html.replace(
                '<div class="article-container">\n',
                '<div class="article-container">\n' + video_html + '\n',
                1
            )

    # ── 12. Abstract ─────────────────────────────────────────────────────────────
    if abstract:
        html = html.replace(
            '<div class="article-style"></div>',
            f'<div class="article-style"><p>{abstract}</p></div>'
        )

    with open(out_path, 'w') as f:
        f.write(html)
    print(f"[ok] Generated {slug}/index.html")

    # ── 11. cite.bib ─────────────────────────────────────────────────────────────
    bib_path = os.path.join(folder, 'cite.bib')
    bibtex = pub.get('bibtex', '')
    if bibtex:
        with open(bib_path, 'w') as f:
            f.write(bibtex + '\n')
        print(f"[ok] Wrote {slug}/cite.bib")
    elif not os.path.exists(bib_path):
        # Write a placeholder
        bib_key = slug.replace('-', '_')
        placeholder = (
            f'@article{{{bib_key},\n'
            f'  title = {{{title}}},\n'
            f'  author = {{{" and ".join(authors)}}},\n'
            f'  year = {{{pub.get("year", "")}}},\n'
            f'  journal = {{{venue}}},\n'
            f'}}\n'
        )
        with open(bib_path, 'w') as f:
            f.write(placeholder)
        print(f"[placeholder] Wrote {slug}/cite.bib (fill in the real BibTeX)")


def cmd_extract():
    """Re-extract all publication data from existing HTML pages."""
    slugs = sorted([d for d in os.listdir(PUB_ROOT) if os.path.isdir(os.path.join(PUB_ROOT, d))])
    pubs = []
    for slug in slugs:
        folder = os.path.join(PUB_ROOT, slug)
        html_path = os.path.join(folder, 'index.html')
        bib_path  = os.path.join(folder, 'cite.bib')
        if not os.path.exists(html_path):
            continue
        with open(html_path) as f:
            html = f.read()

        title_m = re.search(r'<meta property="og:title" content="(.*?)\s*\|\s*Paulo Ricardo', html)
        title = title_m.group(1).strip() if title_m else slug

        meta_m = re.search(r'<div class="article-metadata">(.*?)</span>\s*\n\s*\n', html, re.DOTALL)
        authors = re.findall(r'<span\s*>\s*(.*?)\s*</span>', meta_m.group(1), re.DOTALL) if meta_m else []
        authors = [a.strip() for a in authors if a.strip()]

        date_m = re.search(r'<span class="article-date"[^>]*>.*?(\w+ \d{4})\s*</span>', html, re.DOTALL)
        date_str = date_m.group(1).strip() if date_m else ''
        year_m = re.search(r'\b(20\d{2})\b', date_str)
        year = int(year_m.group(1)) if year_m else None

        paper_m = re.search(r'<a class="btn btn-outline-primary btn-page-header"[^>]*href="([^"]+)"[^>]*>\s*<i class="fab fa-Arxiv', html)
        code_m  = re.search(r'<a class="btn btn-outline-primary btn-page-header"[^>]*href="([^"]+)"[^>]*>\s*<i class="fab fa-github', html)

        venue_m = re.search(r'pub-row-heading">Publication</div>\s*<div class="col-12 col-md-9">(.*?)</div>', html, re.DOTALL)
        venue   = re.sub(r'<[^>]+>', '', venue_m.group(1)).strip() if venue_m else ''

        featured_img = None
        for ext in ['png', 'jpg', 'gif', 'jpeg']:
            if os.path.exists(os.path.join(folder, f'featured.{ext}')):
                featured_img = f'featured.{ext}'
                break

        all_files = os.listdir(folder)
        thumb_webp = next((f for f in all_files if '150x0' in f and f.endswith('.webp')), None)
        large_webp = next((f for f in all_files if ('720x' in f or '1200x' in f) and f.endswith('.webp')), None)

        bibtex = ''
        if os.path.exists(bib_path):
            with open(bib_path) as f:
                bibtex = f.read().strip()

        JOURNAL_KW = ['transactions', 'letters', 'journal', 'magazine']
        pub_type = 'journal' if any(kw in venue.lower() for kw in JOURNAL_KW) else 'conference'
        pubs.append({
            'slug': slug, 'title': title, 'authors': authors, 'year': year,
            'date_label': date_str, 'venue': venue, 'abstract': '',
            'paper_url': paper_m.group(1) if paper_m else '',
            'code_url':  code_m.group(1)  if code_m  else '',
            'video_url': None,
            'pub_type':  pub_type,
            'featured_img': featured_img,
            'thumb_webp': thumb_webp, 'large_webp': large_webp,
            'bibtex': bibtex,
        })

    pubs.sort(key=lambda p: (p['year'] or 0, p['slug']), reverse=True)
    save_json(pubs)
    print(f"Extracted {len(pubs)} publications → publications-data.json")


def cmd_add():
    """Interactive wizard to add a new publication."""
    pubs = load_json()
    existing_slugs = {p['slug'] for p in pubs}

    print("\n=== Add New Publication ===\n")
    slug = input("Slug (folder name, e.g. smith-collab-2025): ").strip()
    if not slug:
        print("Slug cannot be empty."); return
    if slug in existing_slugs:
        print(f"Slug '{slug}' already exists in JSON. Edit it directly if needed."); return

    title      = input("Title (include venue tag, e.g. My Paper [CVPR 2025]): ").strip()
    authors_s  = input("Authors (comma-separated, exact names): ").strip()
    authors    = [a.strip() for a in authors_s.split(',') if a.strip()]
    date_label = input("Date label (e.g. June 2025): ").strip()
    year_m     = re.search(r'\b(20\d{2})\b', date_label)
    year       = int(year_m.group(1)) if year_m else None
    venue      = input("Venue (e.g. IEEE Conference on Computer Vision...): ").strip()
    paper_url  = input("Paper URL (arXiv/PDF, or leave blank): ").strip()
    code_url   = input("Code URL (GitHub, or leave blank): ").strip()
    video_url  = input("Video URL (YouTube/Vimeo/local .mp4, or leave blank): ").strip()
    abstract   = input("Abstract (or leave blank): ").strip()
    bibtex     = input("BibTeX (paste one-liner, or leave blank for placeholder): ").strip()
    JOURNAL_KW = ['transactions', 'letters', 'journal', 'magazine']
    auto_type  = 'journal' if any(kw in venue.lower() for kw in JOURNAL_KW) else 'conference'
    pub_type   = input(f"Publication type [conference/journal/preprint/workshop] (default: {auto_type}): ").strip() or auto_type

    new_pub = {
        'slug': slug, 'title': title, 'authors': authors, 'year': year,
        'date_label': date_label, 'venue': venue, 'abstract': abstract,
        'paper_url': paper_url, 'code_url': code_url, 'video_url': video_url or None,
        'pub_type': pub_type,
        'featured_img': 'featured.png',  # place featured.png in publication/<slug>/
        'thumb_webp': None,  # not needed — JS falls back to featured_img
        'large_webp': None,  # not needed — generator uses featured_img
        'bibtex': bibtex,
    }
    pubs.append(new_pub)
    pubs.sort(key=lambda p: (p['year'] or 0, p['slug']), reverse=True)
    save_json(pubs)
    print(f"\nAdded '{slug}' to publications-data.json")

    generate_page(new_pub, force=True)
    print(f"\nNext steps:")
    print(f"  1. Place your featured image at  publication/{slug}/featured.png")
    if new_pub.get('video_url'):
        print(f"  (video embedded from: {new_pub['video_url']})")
    print("  2. Commit and push — the list pages update automatically from the JSON.")


def main():
    args = sys.argv[1:]
    if not args or args[0] in ('-h', '--help'):
        print(__doc__)
        return

    if args[0] == '--extract':
        cmd_extract()
    elif args[0] == '--add':
        cmd_add()
    elif args[0] == '--all':
        pubs = load_json()
        for p in pubs:
            generate_page(p, force=True)
        print(f"Regenerated {len(pubs)} pages.")
    else:
        slug = args[0]
        pubs = load_json()
        match = next((p for p in pubs if p['slug'] == slug), None)
        if not match:
            print(f"Error: slug '{slug}' not found in publications-data.json")
            print("Available slugs:", [p['slug'] for p in pubs])
            sys.exit(1)
        generate_page(match, force=True)


if __name__ == '__main__':
    main()
