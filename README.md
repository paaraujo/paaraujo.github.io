# paaraujo.github.io

Personal academic website for **Paulo Ricardo M. de Araujo**.  
Built on a pre-compiled [Wowchemy 5.7.0](https://wowchemy.com) / Hugo static site — no Hugo source is included; all pages are plain HTML/CSS/JS.

## Structure

```
paaraujo.github.io/
├── index.html               # Home page
├── publication/             # Publication detail pages
├── project/                 # Project detail pages
├── teaching/                # Teaching detail pages
├── publications-data.json   # Source data for all publications
├── projects-data.json       # Source data for all projects
├── teaching-data.json       # Source data for all courses
├── generate_page.py         # Page generator (publications, projects, teaching)
├── publication/_template.html  # Template used to generate publication pages
└── authors/admin/           # Profile photo and bio assets
```

## Generator script

`generate_page.py` is the single script for creating and regenerating detail pages.

**Requirements** — Python 3.8+, and optionally [Pillow](https://pillow.readthedocs.io/) for automatic image sizing:

```bash
pip install Pillow
```

### Publications

Pages live under `publication/<slug>/index.html` and are generated from `publications-data.json`.

| Command | Action |
|---|---|
| `python3 generate_page.py publication <slug>` | Generate (or regenerate) one page |
| `python3 generate_page.py publication --all` | Regenerate every publication page |
| `python3 generate_page.py publication --add` | Interactive wizard — add a new entry and generate its page |
| `python3 generate_page.py publication --extract` | Re-extract metadata from existing HTML pages back into the JSON |

#### Adding a publication manually

1. Add an entry to `publications-data.json`:

```json
{
  "slug": "smith-deepnav-2026",
  "title": "DeepNav: Learning Navigation from Raw Sensors",
  "authors": ["Alice Smith", "Paulo Ricardo Marques de Araujo"],
  "year": 2026,
  "date_label": "June 2026",
  "venue": "IEEE Robotics and Automation Letters (RA-L)",
  "pub_type": "journal",
  "abstract": "We propose ...",
  "paper_url": "https://arxiv.org/pdf/xxxx.xxxxx",
  "code_url": "https://github.com/example/deepnav",
  "video_url": null,
  "featured_img": "featured.png",
  "thumb_webp": null,
  "large_webp": null,
  "bibtex": "@article{...}"
}
```

Valid `pub_type` values: `conference`, `journal`, `preprint`, `workshop`.

2. Place the featured image at `publication/<slug>/featured.png` (or `.jpg`).

3. Run the generator:

```bash
python3 generate_page.py publication smith-deepnav-2026
```

---

### Projects

Pages live under `project/<slug>/index.html` and are generated from `projects-data.json`.

| Command | Action |
|---|---|
| `python3 generate_page.py project <slug>` | Generate one page |
| `python3 generate_page.py project --all` | Regenerate every project page |
| `python3 generate_page.py project --add` | Interactive wizard |

#### JSON schema

```json
{
  "slug": "lidar-slam-2024",
  "title": "LiDAR SLAM for Urban Environments",
  "summary": "One or two sentence summary shown on the listing card.",
  "description": "Longer description shown on the detail page.",
  "start_year": "2024",
  "end_year": null,
  "tags": ["SLAM", "LiDAR", "Autonomous Vehicles"],
  "featured_img": "featured.png",
  "external_url": null,
  "paper_url": "https://arxiv.org/abs/xxxx.xxxxx",
  "code_url": "https://github.com/example/lidar-slam"
}
```

Place the featured image at `project/<slug>/featured.png`, then run:

```bash
python3 generate_page.py project lidar-slam-2024
```

---

### Teaching

Pages live under `teaching/<slug>/index.html` and are generated from `teaching-data.json`.

| Command | Action |
|---|---|
| `python3 generate_page.py teaching <slug>` | Generate one page |
| `python3 generate_page.py teaching --all` | Regenerate every teaching page |
| `python3 generate_page.py teaching --add` | Interactive wizard |

#### JSON schema

```json
{
  "slug": "elec825-w2026",
  "title": "ELEC 825 – Machine Learning for Engineers",
  "code": "ELEC 825",
  "term": "Winter 2026",
  "institution": "Queen's University",
  "role": "Instructor",
  "summary": "One or two sentence summary.",
  "description": "Longer description shown on the detail page.",
  "featured_img": null,
  "url": "https://example.com/elec825",
  "syllabus_url": null
}
```

Valid `role` values: `Instructor`, `Teaching Assistant`.

Run:

```bash
python3 generate_page.py teaching elec825-w2026
```

---

## Updating the home page listing

The home page (`index.html`) and publication listing (`publication/index.html`) read from `publications-data.json` at runtime via JavaScript fetch — no rebuild needed after editing the JSON.

The projects listing (`project/index.html`) reads from `projects-data.json`, and the teaching listing (`teaching/index.html`) reads from `teaching-data.json`. These are also loaded at runtime.

## Deployment

Push to the `master` branch — GitHub Pages serves the site automatically.

```bash
git add .
git commit -m "Add publication: smith-deepnav-2026"
git push
```
