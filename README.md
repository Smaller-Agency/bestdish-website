# BestDish — Website

Source for **bestdish.ca**. Static site generated from `data.py`.

## Quick start

Open Terminal and run:

```bash
cd "path/to/this/folder"
python3 -m http.server 8000
```

Then visit <http://localhost:8000>.

> Double-clicking `index.html` won't work — the pages use absolute paths (`/css/...`, `/assets/...`) which only resolve over HTTP, not `file://`.

## Editing the site

All content lives in `data.py` — restaurants, chefs, dishes, farms, buildings, navigation. Edit there, then regenerate:

```bash
python3 build.py
```

Every HTML page is rebuilt from `data.py` plus the templates in `build.py`.

## Brand system

Visual and copy decisions are driven by `/Best Dish/design-system/`. The CSS imports its tokens at the top of every page. Don't edit colours, typography, or voice in this folder — change the canonical design system, then re-run `build.py`.

## Structure

```
website/
├── index.html, meals.html, …    ← generated pages, do not edit by hand
├── meals/<slug>.html            ← generated dish detail pages
├── data.py                      ← source of truth: dishes, restaurants, etc.
├── build.py                     ← generator
├── css/                         ← design-system styles + site.css
├── js/site.js                   ← scroll reveals + micro-interactions
└── assets/                      ← logos, dish photos, chef portraits, marketing
```

## Deploy

A GitHub Actions workflow (`.github/workflows/pages.yml`) deploys the site to GitHub Pages on every push to `main`. Enable Pages in repo settings → Pages → Source: **GitHub Actions**.

For a custom domain (e.g. bestdish.ca):

1. Add a `CNAME` file in this folder with `bestdish.ca` inside.
2. In your DNS, point `bestdish.ca` to `<your-github-username>.github.io`.
3. In repo Settings → Pages, set the custom domain.

## Adding a dish

1. Drop the dish photo at `assets/images/<slug>.jpg` (use jpg, webp, or png).
2. Add a new dict to `DISHES` in `data.py` — copy the shape of an existing entry.
3. `python3 build.py`. The dish appears in the menu and gets its own detail page.

## Adding a restaurant

1. Add the logo at `assets/logos/<slug>.png` and chef portrait at `assets/chefs/<chef-slug>.jpg` if you have one.
2. Add a new entry to `RESTAURANTS` in `data.py`.
3. `python3 build.py`.
