#!/usr/bin/env python3
"""
generate_page.py — Generate publication, project, or teaching detail pages.

Usage:
    python3 generate_page.py publication <slug>    # Generate from JSON entry
    python3 generate_page.py publication --add     # Add new entry interactively
    python3 generate_page.py publication --all     # Regenerate ALL pages
    python3 generate_page.py publication --extract # Re-extract data from existing HTML

    python3 generate_page.py project <slug>
    python3 generate_page.py project --add
    python3 generate_page.py project --all

    python3 generate_page.py teaching <slug>
    python3 generate_page.py teaching --add
    python3 generate_page.py teaching --all

JSON files:
    publications-data.json  -- one entry per publication
    projects-data.json      -- one entry per project
    teaching-data.json      -- one entry per course
"""

import os, re, sys, json
from urllib.parse import quote

try:
    from PIL import Image as PILImage
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

SITE_ROOT = os.path.dirname(os.path.abspath(__file__))

# -- Publication template constants -------------------------------------------
PUB_ROOT     = os.path.join(SITE_ROOT, 'publication')
PUB_TEMPLATE = os.path.join(PUB_ROOT, '_template.html')
T_SLUG    = 'hu-longnav-2026'
T_TITLE   = 'LongNav-R1: Horizon-Adaptive Multi-Turn RL for Long-Horizon VLA Navigation [RSS 2026]'
T_DATE    = 'April 2026'
T_VENUE   = 'Robotics: Science and Systems (RSS 2026)'
T_PAPER   = 'https://arxiv.org/pdf/2602.12351'
T_AUTHORS = [
    'Paulo Ricardo M. de Araujo', 'Avery Xi', 'Qixin Xiao',
    'Seth Isaacson', 'Henry X Liu', 'Ram Vasudevan', 'Maani Ghaffari',
]


# =============================================================================
# Shared helpers
# =============================================================================

def load_json(path):
    with open(path) as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f'[ok] Updated {os.path.basename(path)}')

def img_display_dims(img_path):
    """Return (w, h) scaled to 720 px width, preserving aspect ratio."""
    try:
        if HAS_PIL:
            with PILImage.open(img_path) as im:
                ow, oh = im.size
            return 720, round(720 * oh / ow)
    except Exception:
        pass
    return 720, 480

def _btn(label, url, icon_class=''):
    icon = f'<i class="{icon_class} mr-1"></i>' if icon_class else ''
    return (
        f'<a class="btn btn-outline-primary btn-page-header" href="{url}"'
        f' target="_blank" rel="noopener">{icon}{label}</a>'
    )

def _ask(prompt, required=False):
    val = input(prompt).strip()
    if required and not val:
        print('  (field is required)')
        return _ask(prompt, required)
    return val or None


# =============================================================================
# Publication page generator  (uses _template.html + targeted replacements)
# =============================================================================

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
        return (
            '<div class="pub-video article-container mt-4 mb-4">'
            f'<video controls style="width:100%;">'
            f'<source src="{url}" type="video/mp4">'
            'Your browser does not support the video tag.'
            '</video></div>\n'
        )

def _build_authors_html(authors):
    spans = ', '.join(f'<span >\n      {a}</span>' for a in authors)
    return f'\n  <div>\n    \n\n  {spans}\n  </div>\n  '

def _build_authors_html_template():
    spans = ', '.join(f'<span >\n      {a}</span>' for a in T_AUTHORS)
    return f'\n  <div>\n    \n\n  {spans}\n  </div>\n  '

def _gen_pub_page(pub, force=False):
    slug     = pub['slug']
    folder   = os.path.join(PUB_ROOT, slug)
    out_path = os.path.join(folder, 'index.html')

    if not force and os.path.exists(out_path):
        print(f'[skip] {slug}/index.html already exists (use --all to force-regenerate)')
        return

    os.makedirs(folder, exist_ok=True)
    with open(PUB_TEMPLATE) as f:
        html = f.read()

    title      = pub['title']
    authors    = pub['authors']
    date_label = pub['date_label']
    venue      = pub.get('venue', '')
    paper_url  = pub.get('paper_url', '')
    code_url   = pub.get('code_url', '')
    abstract   = pub.get('abstract', '')
    featured   = pub.get('featured_img', 'featured.png')
    pub_type   = pub.get('pub_type', 'conference')
    video_url  = pub.get('video_url') or ''

    # 1. Slug URLs (plain and URL-encoded for share buttons)
    html = html.replace(f'/publication/{T_SLUG}/', f'/publication/{slug}/')
    html = html.replace(f'publication/{T_SLUG}/', f'publication/{slug}/')
    t_slug_enc = quote(f'/publication/{T_SLUG}/', safe='')
    n_slug_enc = quote(f'/publication/{slug}/', safe='')
    html = html.replace(t_slug_enc, n_slug_enc)

    # 1b. Domain
    html = html.replace('yuehu.github.io', 'paaraujo.github.io')

    # 2. Title
    html = html.replace(T_TITLE, title)

    # 3. URL-encoded title in share buttons
    t_enc  = quote(T_TITLE, safe='')
    t_enc2 = T_TITLE.replace(' ', '&#43;').replace(':', '%3A').replace('[', '%5B').replace(']', '%5D')
    n_enc  = quote(title,   safe='')
    n_enc2 = title.replace(' ', '&#43;').replace(':', '%3A').replace('[', '%5B').replace(']', '%5D')
    html = html.replace(t_enc, n_enc)
    html = html.replace(t_enc2, n_enc2)

    # 4. Date
    html = re.sub(
        r'(<span class="article-date"[^>]*>)(.*?)(</span>)',
        lambda m: m.group(1) + '\n    \n    \n      \n    \n    ' + date_label + '\n  ' + m.group(3),
        html, count=1, flags=re.DOTALL
    )

    # 5. Venue
    html = html.replace(f'<em>{T_VENUE}</em>', f'<em>{venue}</em>' if venue else '')

    # 6. Authors
    old_block = _build_authors_html_template()
    new_block = _build_authors_html(authors)
    if old_block in html:
        html = html.replace(old_block, new_block, 1)
    else:
        for old_a, new_a in zip(T_AUTHORS, authors):
            html = html.replace(f'<span >\n      {old_a}</span>', f'<span >\n      {new_a}</span>', 1)

    # 7. Paper URL
    if paper_url:
        html = html.replace(T_PAPER, paper_url)
    else:
        html = re.sub(
            r'<a class="btn btn-outline-primary btn-page-header"[^>]*href="' + re.escape(T_PAPER) + r'"[^>]*>.*?</a>',
            '', html, flags=re.DOTALL
        )

    # 8. Code button
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

    # 9. Featured image
    has_image = featured and os.path.exists(os.path.join(folder, featured))
    if has_image:
        img_w, img_h = img_display_dims(os.path.join(folder, featured))
        html = re.sub(
            r'src="/publication/' + re.escape(slug) + r'/[^"]+\.(webp|png|jpg|gif)"(\s+width="\d+")?(\s+height="\d+")?',
            f'src="/publication/{slug}/{featured}" width="{img_w}" height="{img_h}"',
            html
        )
        html = re.sub(
            r'(class="article-header article-container featured-image-wrapper[^"]*"[^>]*style="[^"]*max-width:\s*\d+px;\s*)max-height:\s*\d+px',
            rf'\g<1>max-height:{img_h}px',
            html
        )
    else:
        html = re.sub(
            r'\n?<div class="article-header article-container featured-image-wrapper[^>]*>.*?</div>\n?</div>\n?',
            '\n', html, flags=re.DOTALL
        )

    # 10. Publication type
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

    # 11. Video
    if video_url:
        video_html = _video_embed(video_url)
        if 'article-header article-container featured-image-wrapper' in html:
            html = re.sub(
                r'(</div>\n</div>\n\n\n\n)(\s*<div class="article-container">)',
                lambda m: m.group(1) + video_html + m.group(2),
                html, count=1
            )
        else:
            html = html.replace(
                '<div class="article-container">\n',
                '<div class="article-container">\n' + video_html + '\n', 1
            )

    # 12. Abstract
    if abstract:
        html = html.replace(
            '<div class="article-style"></div>',
            f'<div class="article-style"><p>{abstract}</p></div>'
        )

    with open(out_path, 'w') as f:
        f.write(html)
    print(f'[ok] Generated {slug}/index.html')

    # cite.bib
    bib_path = os.path.join(folder, 'cite.bib')
    bibtex   = pub.get('bibtex', '')
    if bibtex:
        with open(bib_path, 'w') as f:
            f.write(bibtex + '\n')
        print(f'[ok] Wrote {slug}/cite.bib')
    elif not os.path.exists(bib_path):
        bib_key     = slug.replace('-', '_')
        placeholder = (
            f'@article{{{bib_key},\n'
            f'  title  = {{{title}}},\n'
            f'  author = {{{" and ".join(authors)}}},\n'
            f'  year   = {{{pub.get("year", "")}}},\n'
            f'  journal = {{{venue}}},\n'
            f'}}\n'
        )
        with open(bib_path, 'w') as f:
            f.write(placeholder)
        print(f'[placeholder] Wrote {slug}/cite.bib')


def _pub_add(json_path):
    pubs    = load_json(json_path)
    existing = {p['slug'] for p in pubs}
    print('\n-- Add New Publication ------------------------------------------')
    slug = input('Slug (e.g. smith-collab-2025): ').strip()
    if not slug:
        print('Slug cannot be empty.'); return None
    if slug in existing:
        print(f"Slug '{slug}' already exists."); return None
    title      = input('Title: ').strip()
    authors_s  = input('Authors (comma-separated): ').strip()
    authors    = [a.strip() for a in authors_s.split(',') if a.strip()]
    date_label = input('Date label (e.g. June 2025): ').strip()
    year_m     = re.search(r'\b(20\d{2})\b', date_label)
    year       = int(year_m.group(1)) if year_m else None
    venue      = input('Venue: ').strip()
    paper_url  = _ask('Paper URL (optional): ')
    code_url   = _ask('Code URL (optional): ')
    video_url  = _ask('Video URL (optional): ')
    abstract   = _ask('Abstract (optional): ')
    bibtex     = _ask('BibTeX (optional): ')
    JOURNAL_KW = ['transactions', 'letters', 'journal', 'magazine']
    auto_type  = 'journal' if any(kw in venue.lower() for kw in JOURNAL_KW) else 'conference'
    pub_type   = input(f'Type [conference/journal/preprint/workshop] (default: {auto_type}): ').strip() or auto_type
    entry = {
        'slug': slug, 'title': title, 'authors': authors, 'year': year,
        'date_label': date_label, 'venue': venue, 'abstract': abstract or '',
        'paper_url': paper_url or '', 'code_url': code_url or '',
        'video_url': video_url, 'pub_type': pub_type,
        'featured_img': 'featured.png',
        'thumb_webp': None, 'large_webp': None, 'bibtex': bibtex or '',
    }
    pubs.append(entry)
    pubs.sort(key=lambda p: (p['year'] or 0, p['slug']), reverse=True)
    save_json(json_path, pubs)
    return entry


def _pub_extract(json_path):
    """Re-extract all publication data from existing HTML pages."""
    slugs = sorted(d for d in os.listdir(PUB_ROOT) if os.path.isdir(os.path.join(PUB_ROOT, d)))
    pubs  = []
    for slug in slugs:
        folder = os.path.join(PUB_ROOT, slug)
        html_p = os.path.join(folder, 'index.html')
        bib_p  = os.path.join(folder, 'cite.bib')
        if not os.path.exists(html_p):
            continue
        with open(html_p) as f:
            html = f.read()
        title_m  = re.search(r'<meta property="og:title" content="(.*?)\s*\|\s*Paulo Ricardo', html)
        title    = title_m.group(1).strip() if title_m else slug
        meta_m   = re.search(r'<div class="article-metadata">(.*?)</span>\s*\n\s*\n', html, re.DOTALL)
        authors  = re.findall(r'<span\s*>\s*(.*?)\s*</span>', meta_m.group(1), re.DOTALL) if meta_m else []
        authors  = [a.strip() for a in authors if a.strip()]
        date_m   = re.search(r'<span class="article-date"[^>]*>.*?(\w+ \d{4})\s*</span>', html, re.DOTALL)
        date_str = date_m.group(1).strip() if date_m else ''
        year_m   = re.search(r'\b(20\d{2})\b', date_str)
        year     = int(year_m.group(1)) if year_m else None
        paper_m  = re.search(r'<a class="btn btn-outline-primary btn-page-header"[^>]*href="([^"]+)"[^>]*>\s*<i class="fab fa-Arxiv', html)
        code_m   = re.search(r'<a class="btn btn-outline-primary btn-page-header"[^>]*href="([^"]+)"[^>]*>\s*<i class="fab fa-github', html)
        venue_m  = re.search(r'pub-row-heading">Publication</div>\s*<div class="col-12 col-md-9">(.*?)</div>', html, re.DOTALL)
        venue    = re.sub(r'<[^>]+>', '', venue_m.group(1)).strip() if venue_m else ''
        featured_img = next(
            (f'featured.{ext}' for ext in ('png','jpg','jpeg','gif')
             if os.path.exists(os.path.join(folder, f'featured.{ext}'))), None
        )
        all_files  = os.listdir(folder)
        thumb_webp = next((f for f in all_files if '150x0' in f and f.endswith('.webp')), None)
        large_webp = next((f for f in all_files if ('720x' in f or '1200x' in f) and f.endswith('.webp')), None)
        bibtex = ''
        if os.path.exists(bib_p):
            with open(bib_p) as f:
                bibtex = f.read().strip()
        JOURNAL_KW = ['transactions', 'letters', 'journal', 'magazine']
        pub_type   = 'journal' if any(kw in venue.lower() for kw in JOURNAL_KW) else 'conference'
        pubs.append({
            'slug': slug, 'title': title, 'authors': authors, 'year': year,
            'date_label': date_str, 'venue': venue, 'abstract': '',
            'paper_url': paper_m.group(1) if paper_m else '',
            'code_url':  code_m.group(1)  if code_m  else '',
            'video_url': None, 'pub_type': pub_type,
            'featured_img': featured_img,
            'thumb_webp': thumb_webp, 'large_webp': large_webp, 'bibtex': bibtex,
        })
    pubs.sort(key=lambda p: (p['year'] or 0, p['slug']), reverse=True)
    save_json(json_path, pubs)
    print(f'Extracted {len(pubs)} publications -> {os.path.basename(json_path)}')


# =============================================================================
# Project / Teaching page generator  (uses listing page as structural base)
# =============================================================================

def _featured_image_block(page_type, slug, featured_img):
    if not featured_img:
        return ''
    img_path = os.path.join(SITE_ROOT, page_type, slug, featured_img)
    if not os.path.exists(img_path):
        return ''
    iw, ih = img_display_dims(img_path)
    return (
        f'\n<div class="article-header article-container featured-image-wrapper mt-4 mb-4"'
        f' style="max-width: {iw}px; max-height: {ih}px;">\n'
        f'  <div style="position: relative">\n'
        f'    <img src="/{page_type}/{slug}/{featured_img}"'
        f' width="{iw}" height="{ih}" alt="" class="featured-image">\n'
        f'  </div>\n'
        f'</div>\n'
    )


def _project_content(p):
    title        = p.get('title', '')
    summary      = p.get('summary', '')
    description  = p.get('description', '')
    start_year   = str(p.get('start_year') or '')
    end_year     = str(p.get('end_year') or '')
    tags         = p.get('tags') or []
    external_url = p.get('external_url')
    paper_url    = p.get('paper_url')
    code_url     = p.get('code_url')
    if start_year and end_year:
        date_str = f'{start_year}\u2013{end_year}'
    elif start_year:
        date_str = f'{start_year}\u2013Present'
    else:
        date_str = ''
    sep        = '\n    <span class="middot-divider"></span>\n    '
    meta_parts = []
    if date_str:
        meta_parts.append(f'<span>{date_str}</span>')
    for t in tags:
        meta_parts.append(f'<span class="badge badge-light border">{t}</span>')
    meta_html = sep.join(meta_parts)
    btns = []
    if external_url: btns.append(_btn('Website', external_url))
    if paper_url:    btns.append(_btn('Paper',   paper_url))
    if code_url:     btns.append(_btn('Code',    code_url, 'fab fa-github'))
    btns_html = '\n    '.join(btns)
    lines = ['<div class="article-container">',
             f'\n  <h1 class="page-title">{title}</h1>']
    if summary:    lines.append(f'\n  <p class="pub-abstract">{summary}</p>')
    if meta_html:  lines.append(f'\n  <div class="article-metadata mb-3">\n    {meta_html}\n  </div>')
    if btns:       lines.append(f'\n  <div class="btn-links mb-3">\n    {btns_html}\n  </div>')
    desc = f'<p>{description}</p>' if description else ''
    lines.append(f'\n  <div class="article-style">\n    {desc}\n  </div>\n\n</div>')
    return '\n'.join(lines) + '\n'


def _teaching_content(c):
    title        = c.get('title', '')
    code         = c.get('code', '')
    term         = c.get('term', '')
    institution  = c.get('institution', '')
    role         = c.get('role', '')
    summary      = c.get('summary', '')
    description  = c.get('description', '')
    url          = c.get('url')
    syllabus_url = c.get('syllabus_url')
    meta_parts = []
    if code: meta_parts.append(f'<span class="badge badge-light border mr-1">{code}</span>')
    if term: meta_parts.append(f'<span class="badge badge-light border mr-1">{term}</span>')
    if role:
        role_cls = 'badge-primary' if role == 'Instructor' else 'badge-secondary'
        meta_parts.append(f'<span class="badge {role_cls} mr-1">{role}</span>')
    if institution: meta_parts.append(f'<span class="text-muted">{institution}</span>')
    meta_html = ' '.join(meta_parts)
    btns = []
    if url:          btns.append(_btn('Course Page', url))
    if syllabus_url: btns.append(_btn('Syllabus',    syllabus_url))
    btns_html = '\n    '.join(btns)
    lines = ['<div class="article-container">',
             f'\n  <h1 class="page-title">{title}</h1>']
    if summary:   lines.append(f'\n  <p class="pub-abstract">{summary}</p>')
    if meta_html: lines.append(f'\n  <div class="article-metadata mb-3" style="line-height:2;">\n    {meta_html}\n  </div>')
    if btns:      lines.append(f'\n  <div class="btn-links mb-3">\n    {btns_html}\n  </div>')
    desc = f'<p>{description}</p>' if description else ''
    lines.append(f'\n  <div class="article-style">\n    {desc}\n  </div>\n\n</div>')
    return '\n'.join(lines) + '\n'


def _gen_content_page(page_type, item):
    slug       = item['slug']
    title      = item.get('title', slug)
    summary    = item.get('summary', '')
    base_label = 'Projects' if page_type == 'project' else 'Teaching'
    with open(os.path.join(SITE_ROOT, page_type, 'index.html')) as f:
        html = f.read()
    # Title
    html = html.replace(
        f'<title>{base_label} | Paulo Ricardo M. de Araujo</title>',
        f'<title>{title} | Paulo Ricardo M. de Araujo</title>'
    )
    # URLs
    listing_url = f'https://paaraujo.github.io/{page_type}/'
    detail_url  = f'https://paaraujo.github.io/{page_type}/{slug}/'
    html = html.replace(listing_url, detail_url)
    # OG title
    html = html.replace(
        f'<meta property="og:title" content="{base_label} | Paulo Ricardo M. de Araujo" />',
        f'<meta property="og:title" content="{title} | Paulo Ricardo M. de Araujo" />'
    )
    # OG description
    if summary:
        html = re.sub(
            r'<meta property="og:description" content="[^"]*" />',
            f'<meta property="og:description" content="{summary}" />',
            html, count=1
        )
    # Remove card-grid JS
    html = re.sub(
        r'\n<script>\n\(function \(\) \{[\s\S]*?\}\)\(\);\n</script>\n',
        '\n', html, count=1
    )
    # Build content
    featured_img = item.get('featured_img')
    video_url    = item.get('video_url') or ''
    img_html     = _featured_image_block(page_type, slug, featured_img) if featured_img else ''
    video_html   = _video_embed(video_url) if video_url else ''
    body_html    = img_html + video_html + (_project_content(item) if page_type == 'project' else _teaching_content(item))
    m = re.search(
        r'<div class="universal-wrapper pt-3">.*?</div>\s*</div>\s*<div class="page-footer">',
        html, flags=re.DOTALL
    )
    if m:
        html = html[:m.start()] + body_html + '\n  </div>\n\n  <div class="page-footer">' + html[m.end():]
    else:
        print(f'  [warn] body pattern not found for {slug}')
    out_dir  = os.path.join(SITE_ROOT, page_type, slug)
    out_path = os.path.join(out_dir, 'index.html')
    os.makedirs(out_dir, exist_ok=True)
    with open(out_path, 'w') as f:
        f.write(html)
    print(f'[ok] Generated {page_type}/{slug}/index.html')


# =============================================================================
# Interactive add: project / teaching
# =============================================================================

def _add_project(json_path):
    print('\n-- Add New Project ----------------------------------------------')
    data         = load_json(json_path)
    slug         = _ask('Slug (e.g. lidar-slam-2024): ', required=True)
    title        = _ask('Title: ', required=True)
    summary      = _ask('Summary (1-2 sentences): ')
    description  = _ask('Longer description (optional): ')
    start_year   = _ask('Start year (optional): ')
    end_year     = _ask('End year or "Present" (optional): ')
    tags_raw     = _ask('Tags (comma-separated, optional): ')
    featured_img = _ask('Featured image filename (e.g. featured.png, optional): ')
    external_url = _ask('External URL (optional): ')
    paper_url    = _ask('Paper URL (optional): ')
    code_url     = _ask('Code URL (optional): ')
    video_url    = _ask('Video URL (YouTube/Vimeo/MP4, optional): ')
    tags = [t.strip() for t in tags_raw.split(',')] if tags_raw else []
    entry = {
        'slug': slug, 'title': title,
        'summary': summary or '', 'description': description or '',
        'start_year': start_year, 'end_year': end_year, 'tags': tags,
        'featured_img': featured_img, 'video_url': video_url,
        'external_url': external_url, 'paper_url': paper_url, 'code_url': code_url,
    }
    data.append(entry)
    save_json(json_path, data)
    return entry


def _add_course(json_path):
    print('\n-- Add New Course -----------------------------------------------')
    data         = load_json(json_path)
    slug         = _ask('Slug (e.g. elec999-f2026): ', required=True)
    title        = _ask('Course title: ', required=True)
    code         = _ask('Course code (e.g. ELEC 999): ')
    term         = _ask('Term (e.g. Fall 2026): ')
    institution  = _ask('Institution: ')
    role         = _ask('Role (Instructor / Teaching Assistant): ')
    summary      = _ask('Summary (1-2 sentences): ')
    description  = _ask('Longer description (optional): ')
    featured_img = _ask('Featured image filename (optional): ')
    video_url    = _ask('Video URL (YouTube/Vimeo/MP4, optional): ')
    url          = _ask('Course page URL (optional): ')
    syllabus_url = _ask('Syllabus URL (optional): ')
    entry = {
        'slug': slug, 'title': title,
        'code': code or '', 'term': term or '',
        'institution': institution or '', 'role': role or '',
        'summary': summary or '', 'description': description or '',
        'featured_img': featured_img, 'video_url': video_url,
        'url': url, 'syllabus_url': syllabus_url,
    }
    data.append(entry)
    save_json(json_path, data)
    return entry


# =============================================================================
# Dispatch
# =============================================================================

def _dispatch_publication(command):
    json_path = os.path.join(SITE_ROOT, 'publications-data.json')
    if command == '--extract':
        _pub_extract(json_path)
    elif command == '--add':
        entry = _pub_add(json_path)
        if entry:
            _gen_pub_page(entry, force=True)
            print(f'\nNext: place featured image at  publication/{entry["slug"]}/featured.png')
    elif command == '--all':
        pubs = load_json(json_path)
        for p in pubs:
            _gen_pub_page(p, force=True)
        print(f'Regenerated {len(pubs)} publication(s).')
    else:
        pubs  = load_json(json_path)
        match = next((p for p in pubs if p['slug'] == command), None)
        if not match:
            print(f"Error: slug '{command}' not found in publications-data.json")
            sys.exit(1)
        _gen_pub_page(match, force=True)


def _dispatch_content(page_type, command):
    json_path = os.path.join(
        SITE_ROOT,
        'projects-data.json' if page_type == 'project' else 'teaching-data.json'
    )
    data = load_json(json_path)
    if command == '--add':
        item = _add_project(json_path) if page_type == 'project' else _add_course(json_path)
        _gen_content_page(page_type, item)
    elif command == '--all':
        for item in data:
            _gen_content_page(page_type, item)
        print(f'Regenerated {len(data)} {page_type} page(s).')
    else:
        matches = [p for p in data if p['slug'] == command]
        if not matches:
            print(f"Error: slug '{command}' not found in {os.path.basename(json_path)}")
            sys.exit(1)
        _gen_content_page(page_type, matches[0])


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    page_type = sys.argv[1].lower()
    command   = sys.argv[2]
    if page_type == 'publication':
        _dispatch_publication(command)
    elif page_type in ('project', 'teaching'):
        _dispatch_content(page_type, command)
    else:
        print(f"Error: type must be 'publication', 'project', or 'teaching'")
        print(__doc__)
        sys.exit(1)


if __name__ == '__main__':
    main()
