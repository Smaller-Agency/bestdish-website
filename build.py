"""BestDish site generator.
Builds the static site from data.py into the current directory."""
import os, sys, html, shutil
from pathlib import Path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from data import RESTAURANTS, DISHES, FARMS, BUILDINGS, NAV, FOOTER_NAV

ROOT = Path(__file__).parent
e = html.escape

def img_exists(rel):
    return (ROOT / rel).exists()

# ---------- Dish colourways (drawn from the packaging sleeves) ----------
DISH_ACCENT = {
    "100-layer-lasagna":     "blueberry",
    "beef-bourguignon":      "shrimp",
    "butter-chicken":        "pistachios",
    "cheesemaster-mac":      "honeydew",
    "cheeseburger-pot-pie":  "orange",
    "le-grand-fromage":      "pistachios",
    "pitmaster-platter":     "orange",
    "nutella-tiramisu":      "honeydew",
    "butter-tarts":          "pistachios",
    "chocolate-chip-cookies":"blueberry",
}

def accent(slug):
    return DISH_ACCENT.get(slug, "orange")

def pat(colorway, base=""):
    """Inline style var pointing at a damask colourway tile."""
    return f"--pat:url({base}assets/patterns/damask-{colorway}.svg)"

def ribbon():
    return ('<div class="bd-ribbon"><span>From farm</span>'
            '<span>to chef</span><span>to you</span></div>')

# ---------- Brand icon set (recreated from the Website graphics, as crisp
# inline SVG so they recolour per surface) ----------
ICONS = {
    # ring + hands — "ready 24/7"
    "clock": '<circle cx="50" cy="50" r="40"/><path d="M50 27 V51 H69" stroke-linecap="round" stroke-linejoin="round"/>',
    # bold $ — "no tip, no tax"
    "dollar": '<path d="M50 16 V84" stroke-linecap="round"/><path d="M65 31 C62 24 54 22 47 24 C33 27 33 45 50 49 C68 53 67 73 52 76 C44 77 37 74 34 67" stroke-linecap="round" stroke-linejoin="round"/>',
    # 4-point concave star — "iconic / premium"
    "spark": '<path d="M50 9 C53 34 66 47 91 50 C66 53 53 66 50 91 C47 66 34 53 9 50 C34 47 47 34 50 9 Z" stroke-linejoin="round"/>',
    # lightning — "minutes to plate"
    "bolt": '<path d="M56 10 L28 55 H49 L44 90 L74 43 H52 Z" stroke-linejoin="round"/>',
    # two concentric rings — "a real dish / restaurant"
    "plate": '<circle cx="50" cy="50" r="40"/><circle cx="50" cy="50" r="24"/>',
    # loop arrows — "restocked / repeat"
    "repeat": '<path d="M24 38 H66" stroke-linecap="round"/><path d="M58 29 L69 38 L58 47" stroke-linecap="round" stroke-linejoin="round"/><path d="M76 62 H34" stroke-linecap="round"/><path d="M42 53 L31 62 L42 71" stroke-linecap="round" stroke-linejoin="round"/>',
    # takeout bag — villain: delivery
    "bag": '<path d="M30 40 H70 L66 86 H34 Z" stroke-linejoin="round"/><path d="M41 40 C41 27 59 27 59 40" stroke-linecap="round"/>',
    # snowflake — villain: frozen grocery
    "snow": '<path d="M50 14 V86 M21 31 L79 69 M79 31 L21 69" stroke-linecap="round"/>',
    # shelved box — villain: typical vending
    "box": '<rect x="22" y="18" width="56" height="64" rx="6"/><path d="M22 40 H78 M22 60 H78 M41 71 H59" stroke-linecap="round"/>',
    # downward arrow — vertical flow connector
    "arrow-down": '<path d="M50 18 V78" stroke-linecap="round"/><path d="M30 60 L50 80 L70 60" stroke-linecap="round" stroke-linejoin="round"/>',
    # chevron — horizontal flow connector
    "chevron": '<path d="M40 26 L66 50 L40 74" stroke-linecap="round" stroke-linejoin="round"/>',
}

def bd_icon(name, cls="bd-icon"):
    return (f'<svg class="{cls}" viewBox="0 0 100 100" fill="none" stroke="currentColor" '
            f'stroke-width="7" aria-hidden="true">{ICONS[name]}</svg>')

def step_flow(steps, cols=4):
    """Numbered-circle step flow — the brand's signature how-it-works graphic.
    steps: list of (title_html, body) tuples. Renders blueberry numbered circles
    with the cherry numeral, joined by gold chevrons within each row."""
    out = []
    n = len(steps)
    for i, (title, body) in enumerate(steps):
        end_of_row = (i % cols == cols - 1)
        arrow = "" if (end_of_row or i == n - 1) else bd_icon("chevron", "bd-flow__arrow")
        out.append(f"""<li class="bd-flow__step bd-reveal">
      <span class="bd-flow__num">{i + 1}{arrow}</span>
      <h3 class="bd-flow__title">{title}</h3>
      <p class="bd-flow__body">{body}</p>
    </li>""")
    return f'<ol class="bd-flow bd-flow--c{cols}">{"".join(out)}</ol>'

def pack_panel(d, base="", bg="var(--bd-cherry)"):
    """Faux packaging front panel — the signature object from the sleeves."""
    r = RESTAURANTS[d["restaurant"]]
    cw = accent(d["slug"])
    ground = f"color-mix(in srgb, var(--bd-{cw}) 13%, {bg})"
    return f"""<div class="bd-pack" style="{pat(cw, base)}; --pack-bg:{ground};">
  <img class="bd-pack__badge" src="{base}assets/logos/bd-orange.png" alt="BestDish">
  {ribbon()}
  <p class="bd-pack__rest">{e(r['name'])}</p>
  <h3 class="bd-pack__name">{e(d['name'])}</h3>
  <span class="bd-pack__rule"></span>
  <p class="bd-pack__meta">CHEF-MADE&nbsp;· FLASH-FROZEN&nbsp;· {e(d['weight']).upper().replace(' ', '&nbsp;')}</p>
</div>"""

# ---------- Chrome ----------

def rel(href, base):
    """Convert a leading-slash path to a depth-aware relative path.
    Leaves external (http/mailto/tel/#) and already-relative paths alone."""
    if not href or href[0] != "/":
        return href
    return base + href[1:]

def head(title, desc=None, base=""):
    desc = desc or "Iconic restaurant dishes, in your building. Chef-made. Flash-frozen at peak. Finished in your kitchen."
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)} — BestDish</title>
<meta name="description" content="{e(desc)}">
<link rel="icon" href="{base}assets/logos/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Special+Gothic+Expanded+One&family=Nunito+Sans:wght@300;400;500;700;900&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{base}css/tokens.css">
<link rel="stylesheet" href="{base}css/base.css">
<link rel="stylesheet" href="{base}css/components.css">
<link rel="stylesheet" href="{base}css/site.css">
</head>
<body class="bd-site">
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <filter id="bd-grit"><feTurbulence baseFrequency="0.9" numOctaves="2" seed="3"/><feColorMatrix values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 -1.5 1.1"/><feComposite in="SourceGraphic" operator="in"/></filter>
</svg>
"""

def nav(base=""):
    links = "".join(f'<a href="{rel(u, base)}">{e(t)}</a>' for t, u in NAV)
    return f"""<nav class="bd-nav">
  <a class="bd-nav__brand" href="{base or './'}">
    <img src="{base}assets/logos/bd-orange.png" alt="BestDish">
    <span class="bd-nav__brand-name">BestDish</span>
  </a>
  <div class="bd-nav__links">
    {links}
    <a class="bd-btn bd-btn--primary" href="{base}buildings.html">Find a building</a>
  </div>
</nav>
"""

def footer(base=""):
    nav_links = "".join(f'<li><a href="{rel(u, base)}">{e(t)}</a></li>' for t, u in FOOTER_NAV)
    return f"""<footer class="bd-footer">
  <div class="bd-footer__top">
    <div>
      <p class="bd-footer__brand-line">From farm,<br>to chef,<br>to <em style="color:var(--bd-orange); font-style: normal;">you</em>.</p>
      <p style="opacity:.7; max-width: 28ch; margin-top: var(--bd-space-4);">BestDish Foods Inc. Toronto, Ontario.</p>
    </div>
    <div class="bd-footer__col"><h4>Eat</h4><ul>{nav_links}</ul></div>
    <div class="bd-footer__col"><h4>Partner</h4><ul>
      <li><a href="{base}for-properties.html">For properties</a></li>
      <li><a href="{base}for-restaurants.html">For restaurants</a></li>
      <li><a href="{base}farms.html">Farms</a></li>
    </ul></div>
    <div class="bd-footer__col"><h4>Visit</h4><ul>
      <li>507 King St E<br>Toronto, ON, M5A 1M3</li>
      <li><a href="mailto:hello@bestdish.ca">hello@bestdish.ca</a></li>
      <li><a href="tel:+14168246626">(416) 824-6626</a></li>
    </ul></div>
  </div>
  <div class="bd-footer__bottom">
    <span>© 2026 BestDish Foods Inc.</span>
    <span>HACCP-compliant · CFIA-labelled · PIPEDA-aligned</span>
  </div>
</footer>
<script src="{base}js/site.js" defer></script>
</body></html>"""

def page(title, body, desc=None, base=""):
    return head(title, desc, base) + nav(base) + body + footer(base)

# ---------- Page parts ----------

def dish_card(d, base="", big=False):
    r = RESTAURANTS[d["restaurant"]]
    img_rel = f"assets/images/{d['image']}"
    has_img = img_exists(img_rel)
    cw = accent(d["slug"])
    if has_img:
        media = f'<img src="{base}{img_rel}" alt="{e(d["name"])} by {e(r["name"])}" class="bd-dish-card__img" loading="lazy">'
    else:
        # No photo yet — render the dish as its wrapped package (colourway + damask + badge).
        media = (f'<div class="bd-dish-card__fill" style="{pat(cw, base)}; '
                 f'--pack-bg:color-mix(in srgb, var(--bd-{cw}) 17%, var(--bd-gravy));">'
                 f'<img class="bd-dish-card__badge" src="{base}assets/logos/bd-orange.png" alt="">'
                 f'<span class="bd-dish-card__frozen">Flash-frozen</span></div>')
    return f"""<a class="bd-dish-card bd-reveal" href="{base}meals/{d['slug']}.html">
  {media}
  <span class="bd-dish-card__tab">{e(r['name'])}</span>
  <span class="bd-dish-card__chip">{e(d['category'])}</span>
  <div class="bd-dish-card__overlay">
    <h3 class="bd-dish-card__name">{e(d['name'])}</h3>
    <span class="bd-dish-card__cta">View dish →</span>
  </div>
</a>"""

# ---------- Home ----------

def home():
    base = ""
    dishes = "".join(dish_card(d, base=base) for d in DISHES)
    marquee_items = "".join(f"<span>{e(r['name'])}</span>" for r in RESTAURANTS.values())
    by_slug = {d["slug"]: d for d in DISHES}
    hero_dish = by_slug["butter-chicken"]
    show = [by_slug[s] for s in ("100-layer-lasagna", "pitmaster-platter", "nutella-tiramisu")]
    showcase = "".join(pack_panel(d, base=base, bg="var(--bd-gravy)") for d in show)
    return page("Toronto's best meals — in your lobby", f"""
<header class="bd-hero-wrap bd-hero--split bd-hero--textured">
  <div class="bd-container">
    <div>
      <span class="bd-loc bd-reveal">Toronto · live in your building</span>
      <h1 class="bd-hero-headline bd-reveal" style="margin-top: var(--bd-space-5);">Toronto's<br>best meals.<br><em>In your lobby.</em></h1>
      <p class="bd-hero-lede bd-reveal">Iconic dishes from the city's best restaurants — chef-made, flash-frozen at peak, waiting in the freezer in your lobby. Heat. Eat. No delivery, no tip, no tax.</p>
      <div class="bd-strapline bd-reveal">
        <span>Made in real restaurants</span>
        <span>By the chefs you love</span>
        <span>Ready 24/7 downstairs</span>
      </div>
      <div style="display:flex; gap: var(--bd-space-3); flex-wrap: wrap; margin-top: var(--bd-space-7);" class="bd-reveal">
        <a class="bd-btn bd-btn--primary" href="meals.html">Browse the menu</a>
        <a class="bd-btn bd-btn--secondary" href="buildings.html">Is it in my building?</a>
      </div>
    </div>
    <div class="bd-hero__art bd-reveal">
      {pack_panel(hero_dish, base=base, bg="var(--bd-cherry)")}
    </div>
  </div>
</header>

<div class="bd-marquee"><div class="bd-marquee__track">{marquee_items}{marquee_items}</div></div>

<section class="bd-section" style="padding-block: var(--bd-space-8);">
  <div class="bd-container">
    <div class="bd-statband">
      <div class="bd-stat bd-reveal">{bd_icon('plate', 'bd-stat__icon')}<p class="bd-stat__n">11</p><p class="bd-stat__l">Iconic Toronto restaurants on the menu.</p></div>
      <div class="bd-stat bd-reveal">{bd_icon('clock', 'bd-stat__icon')}<p class="bd-stat__n">24/7</p><p class="bd-stat__l">In your lobby. No hours, no waiting.</p></div>
      <div class="bd-stat bd-reveal">{bd_icon('dollar', 'bd-stat__icon')}<p class="bd-stat__n">$0</p><p class="bd-stat__l">Delivery fees, tips, or tax. Ever.</p></div>
      <div class="bd-stat bd-reveal">{bd_icon('bolt', 'bd-stat__icon')}<p class="bd-stat__n">~10<span style="font-size:.5em;">min</span></p><p class="bd-stat__l">From the freezer to your plate.</p></div>
    </div>
  </div>
</section>

<section class="bd-section bd-section--alt">
  <div class="bd-container">
    <div class="bd-sec-head">
      <div>
        <p class="bd-eyebrow bd-reveal">The menu</p>
        <h2 class="bd-headline bd-reveal">The city's best,<br>in your lobby.</h2>
      </div>
      <a class="bd-btn bd-btn--ghost bd-reveal" href="meals.html">All meals →</a>
    </div>
    <div class="bd-reel">{dishes}</div>
  </div>
</section>

<section class="bd-section">
  <div class="bd-container">
    <div class="bd-lobby">
      <div class="bd-lobby__media bd-reveal">
        <img class="bd-lobby__img" src="assets/marketing/freezer-mockup.jpg" alt="A BestDish freezer in a residential lobby">
        <span class="bd-lobby__tag">The freezer in your lobby</span>
      </div>
      <div class="bd-reveal">
        <p class="bd-eyebrow">Dinner is downstairs</p>
        <h2 class="bd-headline" style="max-width: 16ch;">Skip the wait. Take the elevator.</h2>
        <p class="bd-lede" style="margin-top: var(--bd-space-5);">A curated BestDish freezer sits in your building — stocked with real restaurant dishes, ready when you are.</p>
        <div class="bd-bullets" style="margin-top: var(--bd-space-6);">
          <span>Tap your card</span>
          <span>Pick your dish</span>
          <span>Heat &amp; eat upstairs</span>
        </div>
        <a class="bd-btn bd-btn--primary" style="margin-top: var(--bd-space-7);" href="buildings.html">Find a building</a>
      </div>
    </div>
  </div>
</section>

<section class="bd-section bd-section--alt">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">How it works</p>
    <h2 class="bd-headline bd-reveal" style="max-width:22ch;">Four steps. From the pass to your plate.</h2>
    {step_flow([
      ("Made by chefs", "Cooked by the chefs who made them famous — same techniques, same ingredients, same standards as service."),
      ("Flash frozen", "Locked in at peak the moment they leave the kitchen. Flavour, texture, and nutrients stay intact."),
      ("In your building", "A curated freezer of chef meals in your lobby. Tap your card, pick your dish, done."),
      ("Finished by you", "Cooked fresh in your own oven in minutes — exactly the way the chef designed it."),
    ])}
  </div>
</section>

<section class="bd-section">
  <div class="bd-container">
    <div class="bd-sec-head">
      <div>
        <p class="bd-eyebrow bd-reveal">The packaging</p>
        <h2 class="bd-headline bd-reveal" style="max-width: 16ch;">Every dish carries its story.</h2>
      </div>
      <a class="bd-btn bd-btn--secondary bd-reveal" href="farms.html">Meet the farms →</a>
    </div>
    <p class="bd-lede bd-reveal" style="max-width: 60ch; margin-bottom: var(--bd-space-8);">The restaurant. The chef. The farm. Heating instructions in the chef's own words, batch-tracked and CFIA-labelled. From farm, to chef, to you — printed on the box.</p>
    <div class="bd-grid-3 bd-reveal">
      {showcase}
    </div>
  </div>
</section>

<section class="bd-section bd-section--alt">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">Why BestDish is different</p>
    <h2 class="bd-headline bd-reveal" style="max-width:22ch;">This isn't a vending machine.</h2>
    <div class="bd-compare" style="margin-top: var(--bd-space-7);">
      <div class="bd-compare__row">
        <div class="bd-compare__cell">{bd_icon('bag', 'bd-compare__icon')}<strong>Delivery apps</strong>Restaurant, but travelled. 30–60 min later, often compromised — plus fees, tip, and tax.</div>
        <div class="bd-compare__cell">{bd_icon('snow', 'bd-compare__icon')}<strong>Frozen grocery</strong>Mass-produced. No chef, no story, no consistency.</div>
        <div class="bd-compare__cell">{bd_icon('box', 'bd-compare__icon')}<strong>Typical vending</strong>Packaged snacks. Convenience only, no quality.</div>
        <div class="bd-compare__cell bd-compare__cell--win"><img class="bd-compare__badge" src="assets/logos/bd-orange.png" alt="BestDish"><strong>BestDish</strong>Chef-prepared, small batch. In your building. Finished fresh at home.</div>
      </div>
    </div>
  </div>
</section>

<section class="bd-section">
  <div class="bd-container">
    <div class="bd-finalcta bd-reveal">
      <p class="bd-eyebrow">Dinner is already here</p>
      <h2 class="bd-finalcta__head">Is BestDish in your building yet?</h2>
      <p class="bd-lede bd-finalcta__lede">Find your building to see what's waiting in the freezer downstairs. Not there yet? We'll add it to the list — the more residents ask, the faster we install.</p>
      <div class="bd-finalcta__actions">
        <a class="bd-btn bd-btn--primary" href="buildings.html">Find a building</a>
        <a class="bd-btn bd-btn--secondary" href="meals.html">Browse the menu</a>
      </div>
    </div>
    <p class="bd-finalcta__partners bd-reveal">Manage a building or run a restaurant?
      <a href="for-properties.html">Add a freezer →</a>
      <a href="for-restaurants.html">Partner your kitchen →</a>
    </p>
  </div>
</section>

<section class="bd-section bd-section--cream">
  <div class="bd-container" style="text-align:center;">
    <p class="bd-pullquote bd-reveal" style="margin: 0 auto;">
      "The best restaurants are built on passion, creativity, and quality. If a company can translate that into a frozen meal without losing its soul, it will be a game-changer."
      <span class="bd-pullquote__attr">— Chef Thomas Keller</span>
    </p>
  </div>
</section>
""")

# ---------- Browse meals ----------

def meals_page():
    base = ""
    savoury = [d for d in DISHES if d["category"] == "Savoury"]
    sweet   = [d for d in DISHES if d["category"] == "Sweet"]
    return page("Browse meals", f"""
<header class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">The menu</p>
    <h1 class="bd-hero-headline bd-reveal" style="font-size:clamp(48px,7vw,112px); margin-bottom: var(--bd-space-5);">Every dish.<br>Every chef.</h1>
    <p class="bd-hero-lede bd-reveal">Real dishes from Toronto's iconic restaurants. Made in the originating kitchen, flash-frozen at peak, finished fresh in your kitchen in minutes.</p>
  </div>
</header>

<section class="bd-section" style="padding-top:0;">
  <div class="bd-container">
    <h2 class="bd-headline bd-reveal" style="margin-bottom: var(--bd-space-6);">Savoury</h2>
    <div class="bd-reel">{"".join(dish_card(d, base=base) for d in savoury)}</div>
  </div>
</section>

<section class="bd-section">
  <div class="bd-container">
    <h2 class="bd-headline bd-reveal" style="margin-bottom: var(--bd-space-6);">Sweet</h2>
    <div class="bd-reel">{"".join(dish_card(d, base=base) for d in sweet)}</div>
  </div>
</section>
""")

# ---------- Dish detail ----------

def dish_page(d):
    base = "../"
    r = RESTAURANTS[d["restaurant"]]
    img_rel = f"assets/images/{d['image']}"
    has_img = img_exists(img_rel)
    photo = (f'<img class="bd-dish-hero__photo" src="{base}{img_rel}" alt="{e(d["name"])} by {e(r["name"])}">' if has_img
             else pack_panel(d, base=base, bg="var(--bd-cherry)"))

    nutrition_rows = "".join(
        f'<div class="bd-nutri__row"><span>{e(k)}</span><span>{e(v)}</span></div>'
        for k, v in d["nutrition"].items() if k != "Calories")

    return page(f"{d['name']} — {r['name']}", base=base, body=f"""
<section class="bd-section" style="padding-top: var(--bd-space-7); padding-bottom: 0;">
  <div class="bd-container">
    <div class="bd-dish-hero">
      <div class="bd-reveal">
        {photo}
      </div>
      <div class="bd-reveal">
        <p class="bd-dish-hero__category">{e(d["category"])}</p>
        <a class="bd-dish-hero__restaurant" href="{base}chefs.html#{d['restaurant']}">{e(r["name"])}</a>
        <h1 class="bd-dish-hero__name">{e(d["name"])}</h1>
        <p class="bd-dish-hero__tagline">{e(d["tagline"])}</p>
        <div class="bd-dish-meta">
          <div class="bd-dish-meta__cell"><p class="bd-dish-meta__label">Chef</p><p class="bd-dish-meta__value">{e(d["chef_signature"])}</p></div>
          <div class="bd-dish-meta__cell"><p class="bd-dish-meta__label">Serving</p><p class="bd-dish-meta__value">{e(d["serving"])}</p></div>
          <div class="bd-dish-meta__cell"><p class="bd-dish-meta__label">Net weight</p><p class="bd-dish-meta__value">{e(d["weight"])}</p></div>
          <div class="bd-dish-meta__cell"><p class="bd-dish-meta__label">Calories</p><p class="bd-dish-meta__value">{e(d["nutrition"]["Calories"])}</p></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="bd-section bd-section--alt">
  <div class="bd-container">
    <p class="bd-pullquote bd-reveal" style="margin-bottom: var(--bd-space-3);">"{e(d["chef_note"])}"
      <span class="bd-pullquote__attr">— {e(d["chef_signature"])}, {e(r["name"])}</span>
    </p>
  </div>
</section>

<section class="bd-section">
  <div class="bd-container">
    <div class="bd-info-grid">
      <div class="bd-panel bd-reveal">
        <h3>Heating instructions</h3>
        <div class="bd-heat-cols">
          <div><p class="bd-heat__method">Oven</p><p class="bd-heat__steps">{e(d["heat"]["oven"])}</p></div>
          <div><p class="bd-heat__method">Microwave</p><p class="bd-heat__steps">{e(d["heat"]["microwave"])}</p></div>
        </div>
        <p class="bd-heat__steps" style="margin-top: var(--bd-space-5); opacity:.7;">Keep frozen until use. Do not refreeze after thawing.</p>
      </div>
      <div class="bd-panel bd-reveal">
        <h3>Ingredients</h3>
        <p style="line-height: var(--bd-lh-relaxed); margin: 0 0 var(--bd-space-4);">{e(d["ingredients"])}</p>
        <p style="font-size: var(--bd-size-sm); margin: 0;"><strong style="color:var(--bd-orange); font-weight:900;">Contains:</strong> {e(d["contains"])}</p>
        <p style="font-size: var(--bd-size-sm); margin: var(--bd-space-1) 0 0; opacity:.7;"><strong>May contain:</strong> {e(d["may_contain"])}</p>
        <p style="font-size: var(--bd-size-xs); margin: var(--bd-space-5) 0 0; opacity:.6;">Made in Canada with domestic and imported ingredients.</p>
      </div>
    </div>
  </div>
</section>

<section class="bd-section bd-section--cream">
  <div class="bd-container">
    <div class="bd-info-grid">
      <div class="bd-reveal">
        <p class="bd-eyebrow">Nutrition facts</p>
        <h2 class="bd-headline" style="font-size:var(--bd-size-3xl); margin-bottom: var(--bd-space-5);">Per {e(d["serving"])}.</h2>
        <p style="line-height:var(--bd-lh-relaxed); max-width:42ch;">All values reflect the dish as cooked and packaged. Daily values based on a 2,000 calorie diet.</p>
      </div>
      <div class="bd-nutri bd-reveal">
        <h3 class="bd-nutri__title">Nutrition Facts</h3>
        <p class="bd-nutri__serving">Per {e(d["serving"])}</p>
        <div class="bd-nutri__cal"><span class="bd-nutri__cal-label">Calories</span><span class="bd-nutri__cal-value">{e(d["nutrition"]["Calories"])}</span></div>
        {nutrition_rows}
      </div>
    </div>
  </div>
</section>

<section class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">From the restaurant</p>
    <h2 class="bd-headline bd-reveal" style="max-width:22ch;">{e(r["name"])}.</h2>
    <p class="bd-lede bd-reveal" style="max-width: 60ch;">{e(r["blurb"])}</p>
    <p style="margin-top: var(--bd-space-5); font-family: var(--bd-font-mono); font-size: var(--bd-size-sm); color: var(--bd-orange);" class="bd-reveal">
      Visit them at<br>
      <span style="font-family: var(--bd-font-display); font-weight: 700; font-size: var(--bd-size-xl); color: var(--bd-cream); letter-spacing: var(--bd-track-tight); text-transform: uppercase;">{e(r["address"])}</span><br>
      <span style="color: var(--bd-cream); font-family: var(--bd-font-body); font-size: var(--bd-size-sm); opacity: .8;">{e(r["city"])} · {e(r["postal"])}</span>
    </p>
  </div>
</section>

<section class="bd-section bd-section--alt">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">More from the menu</p>
    <div class="bd-reel" style="margin-top: var(--bd-space-6);">
      {"".join(dish_card(other, base=base) for other in DISHES if other["slug"] != d["slug"])}
    </div>
  </div>
</section>
""")

# ---------- How it works ----------

def how_it_works_page():
    return page("How it works", f"""
<header class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">How it works</p>
    <h1 class="bd-hero-headline bd-reveal" style="font-size:clamp(48px,7vw,112px);">From the kitchen<br>to your kitchen.</h1>
    <p class="bd-hero-lede bd-reveal">Restaurant meals only work in your building if every step is right. Here's every step.</p>
  </div>
</header>

<section class="bd-section">
  <div class="bd-container">
    {step_flow([
      ("In the restaurant", "Every dish is made in the originating restaurant kitchen. Same techniques, same ingredients, same standards as service."),
      ("At peak", "Each meal is portioned and frozen the moment it leaves the kitchen. The cold-chain begins at the pass."),
      ("Through the cold chain", "HACCP-compliant cold-chain. CFIA-labelled. Temperature logged from kitchen to freezer."),
      ("In your building", "Smart freezer, premium installation. Tap your card, pick your dish. Telemetry keeps it restocked within 48 hours."),
      ("In your hand", "No delivery driver. No waiting. No tip, no tax. Freezer to kitchen in the time it takes to ride the elevator."),
      ("In your oven", "Heating instructions on every package — per dish, per restaurant. The chef tells you how to finish their food."),
    ], cols=3)}
  </div>
</section>

<section class="bd-section bd-section--cream">
  <div class="bd-container">
    <div class="bd-info-grid">
      <div class="bd-reveal">
        <p class="bd-eyebrow">The numbers</p>
        <h2 class="bd-headline" style="font-size:var(--bd-size-3xl);">Operational discipline.</h2>
      </div>
      <div class="bd-stack bd-reveal">
        <div style="display:flex; align-items:baseline; gap:var(--bd-space-3); border-top: 4px solid var(--bd-orange); padding-top: var(--bd-space-3);"><strong style="font-family:var(--bd-font-display); font-size: var(--bd-size-3xl); font-weight: 900; color: var(--bd-orange);">98.5%</strong><span>uptime target across every freezer.</span></div>
        <div style="display:flex; align-items:baseline; gap:var(--bd-space-3); border-top: 4px solid var(--bd-orange); padding-top: var(--bd-space-3);"><strong style="font-family:var(--bd-font-display); font-size: var(--bd-size-3xl); font-weight: 900; color: var(--bd-orange);">≤48h</strong><span>restock SLA from stock-out to refill.</span></div>
        <div style="display:flex; align-items:baseline; gap:var(--bd-space-3); border-top: 4px solid var(--bd-orange); padding-top: var(--bd-space-3);"><strong style="font-family:var(--bd-font-display); font-size: var(--bd-size-3xl); font-weight: 900; color: var(--bd-orange);">≤5%</strong><span>waste target. Every batch tracked.</span></div>
        <div style="display:flex; align-items:baseline; gap:var(--bd-space-3); border-top: 4px solid var(--bd-orange); padding-top: var(--bd-space-3);"><strong style="font-family:var(--bd-font-display); font-size: var(--bd-size-3xl); font-weight: 900; color: var(--bd-orange);">5%</strong><span>of sales returned to the building.</span></div>
      </div>
    </div>
  </div>
</section>
""")

# ---------- Chefs ----------

CHEF_PHOTOS = {
    "Taylor Well":          "taylor-well.jpg",
    "Afrim Pristine":        "afrim-pristine.jpg",
    "Brett Feeley":          "brett-feeley.jpeg",
    "Derek Valleau & Dinesh Butola": "dinesh-butola.webp",
    "Victor Barry":          "victor-barry.webp",
    "Michael Angeloni":      "michael-angeloni.jpg",
    "Craig Harding":         "craig-harding.jpg",
    "Duncan Simpson":        "duncan-simpson.jpg",
    "The Nunes Family":      "the-nunes-family.jpg",
    "Andrea Mastrandrea":    None,
}

def chefs_page():
    cards = []
    for slug, r in RESTAURANTS.items():
        chef = r["chef"]
        photo_file = CHEF_PHOTOS.get(chef)
        if photo_file and (ROOT/"assets/chefs"/photo_file).exists():
            photo = f'<img class="bd-person__photo" src="assets/chefs/{photo_file}" alt="Portrait of Chef {e(chef)}">'
        else:
            initials = "".join(w[0] for w in chef.replace("&", "and").split() if w[0].isalpha())[:2]
            photo = f'<div class="bd-person__photo bd-person__photo--placeholder">{e(initials)}</div>'
        cards.append(f"""<article class="bd-person bd-reveal" id="{slug}">
          {photo}
          <h3 class="bd-person__name">{e(chef)}</h3>
          <p class="bd-person__role">{e(r['name'])}</p>
          <p class="bd-person__bio">{e(r['blurb'])}</p>
          <p style="font-size:var(--bd-size-xs); opacity:.7;">{e(r['address'])} · {e(r['city'])}</p>
        </article>""")
    return page("The chefs", f"""
<header class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">The chefs</p>
    <h1 class="bd-hero-headline bd-reveal" style="font-size:clamp(48px,7vw,112px);">The people<br>behind the food.</h1>
    <p class="bd-hero-lede bd-reveal">Every dish on BestDish is built by the chef who made it famous. No outsourced recipes. No reformulations. The restaurant cooks it. We carry it.</p>
  </div>
</header>

<section class="bd-section" style="padding-top:0;">
  <div class="bd-container">
    <div class="bd-people">{"".join(cards)}</div>
  </div>
</section>
""")

# ---------- Farms ----------

FARM_HERO = "assets/farms/100km Truck Edit.jpg"

def farms_page():
    farm_blocks = []
    for f in FARMS:
        farm_blocks.append(f"""<article class="bd-person bd-reveal">
          <div class="bd-person__photo bd-person__photo--placeholder">{e(f["name"].split()[0])}</div>
          <h3 class="bd-person__name">{e(f["name"])}</h3>
          <p class="bd-person__role">{e(f["region"])} · {e(f["people"])}</p>
          <p class="bd-person__bio">{e(f["blurb"])}</p>
          <p style="font-size:var(--bd-size-xs); opacity:.7;">Supplies: {e(f["supplies"])}</p>
        </article>""")
    has_hero = (ROOT/FARM_HERO).exists()
    hero_img = (f'<img src="{FARM_HERO}" alt="From the farm" style="width:100%; aspect-ratio:21/9; object-fit:cover; border-radius: var(--bd-radius-lg); margin-bottom: var(--bd-space-7);">' if has_hero else '')
    return page("Farms", f"""
<header class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">The farms</p>
    <h1 class="bd-hero-headline bd-reveal" style="font-size:clamp(48px,7vw,112px);">From farm,<br>to chef,<br>to you.</h1>
    <p class="bd-hero-lede bd-reveal">Most frozen meals start in a factory. Ours start in soil. Every BestDish dish traces back to a named farm in our regenerative network.</p>
    {hero_img}
    <div class="bd-people">{"".join(farm_blocks)}</div>
  </div>
</header>

<section class="bd-section bd-section--alt">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">Why farms first</p>
    <h2 class="bd-headline bd-reveal" style="max-width: 22ch;">Predictable demand. Visible attribution.</h2>
    <div class="bd-info-grid" style="margin-top: var(--bd-space-7);">
      <div class="bd-reveal"><p>BestDish guarantees baseline orders to participating farms. That stability lets them plant longer-horizon crops, hire more seasonal staff, and invest in regenerative practice.</p></div>
      <div class="bd-reveal"><p>Every package and dish page names the farm. Residents see where their food comes from. The farm gets credit at point of sale.</p></div>
    </div>
  </div>
</section>
""")

# ---------- Buildings ----------

def buildings_page():
    rows = []
    live_count = sum(1 for b in BUILDINGS if b["status"] == "Live")
    for i, b in enumerate(BUILDINGS, 1):
        status_cls = "bd-building-row__status--live" if b["status"] == "Live" else ""
        rows.append(f"""<div class="bd-building-row bd-reveal">
          <span class="bd-building-row__num">{i:02d}</span>
          <div>
            <h3 class="bd-building-row__name">{e(b["name"])}</h3>
            <span class="bd-building-row__address">{e(b["address"])}</span>
          </div>
          <span class="bd-building-row__type">{e(b["type"])}</span>
          <span class="bd-building-row__status {status_cls}">{e(b["status"])}</span>
        </div>""")
    return page("Find a building", f"""
<header class="bd-section">
  <div class="bd-container">
    <div style="display:grid; gap: var(--bd-space-7); grid-template-columns: 1fr; align-items: end;" class="bd-buildings-hero">
      <div>
        <p class="bd-eyebrow bd-reveal">Find a building</p>
        <h1 class="bd-hero-headline bd-reveal" style="font-size:clamp(48px,7vw,112px);">Is it in<br>your building?</h1>
        <p class="bd-hero-lede bd-reveal">BestDish freezers are installed in premium residential buildings, co-working spaces, and members' clubs across Toronto. Find yours below — or ask your property manager to bring it in.</p>
      </div>
      <div class="bd-reveal" style="display:grid; gap: var(--bd-space-3); grid-template-columns: 1fr 1fr; padding-bottom: var(--bd-space-4);">
        <div style="border-top: 4px solid var(--bd-orange); padding-top: var(--bd-space-3);"><p style="font-family: var(--bd-font-display); font-weight:900; font-size: var(--bd-size-5xl); color: var(--bd-orange); line-height: 1; margin: 0;">{live_count}</p><p style="font-family: var(--bd-font-body); font-weight: 900; text-transform: uppercase; letter-spacing: var(--bd-track-wider); font-size: var(--bd-size-xs); margin: var(--bd-space-2) 0 0;">Live in Toronto</p></div>
        <div style="border-top: 4px solid var(--bd-orange); padding-top: var(--bd-space-3);"><p style="font-family: var(--bd-font-display); font-weight:900; font-size: var(--bd-size-5xl); color: var(--bd-orange); line-height: 1; margin: 0;">{len(BUILDINGS) - live_count}</p><p style="font-family: var(--bd-font-body); font-weight: 900; text-transform: uppercase; letter-spacing: var(--bd-track-wider); font-size: var(--bd-size-xs); margin: var(--bd-space-2) 0 0;">Coming this year</p></div>
      </div>
    </div>
  </div>
</header>
<style>@media (min-width: 1024px) {{ .bd-buildings-hero {{ grid-template-columns: 2fr 1fr !important; }} }}</style>

<section class="bd-section" style="padding-top:0;">
  <div class="bd-container">
    <div class="bd-buildings">{"".join(rows)}</div>
  </div>
</section>

<section class="bd-section bd-section--alt">
  <div class="bd-container" style="text-align:center;">
    <p class="bd-eyebrow bd-reveal">Don't see your building?</p>
    <h2 class="bd-headline bd-reveal" style="max-width:22ch; margin-inline:auto;">Tell us where you live.</h2>
    <p style="max-width:54ch; margin: var(--bd-space-4) auto var(--bd-space-6);" class="bd-reveal">We'll reach out to your property manager. The more requests we have at an address, the faster we can install.</p>
    <a class="bd-btn bd-btn--primary bd-reveal" href="mailto:hello@bestdish.ca?subject=Bring%20BestDish%20to%20my%20building">Request your building</a>
  </div>
</section>
""")

# ---------- For properties ----------

def for_properties_page():
    return page("For properties", """
<header class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">For property managers, asset managers, condo boards</p>
    <h1 class="bd-hero-headline bd-reveal" style="font-size:clamp(48px,7vw,112px);">A premium<br>food amenity.<br>No kitchen.</h1>
    <p class="bd-hero-lede bd-reveal">Restaurant meals in your lobby, 24/7. We install, we operate, you earn. No capital cost. No staff lift. No admin.</p>
    <a class="bd-btn bd-btn--primary bd-reveal" href="#talk">Talk to us</a>
  </div>
</header>

<section class="bd-section bd-section--alt">
  <div class="bd-container">
    <div class="bd-info-grid">
      <div class="bd-reveal">
        <p class="bd-eyebrow">What you get</p>
        <h2 class="bd-headline" style="font-size: var(--bd-size-3xl); max-width: 22ch;">An amenity that reflects your brand.</h2>
      </div>
      <div class="bd-reveal">
        <ul style="list-style:none; padding:0; margin:0; display: grid; gap: var(--bd-space-4); font-size: var(--bd-size-md);">
          <li>· One smart freezer placed in a high-traffic area, with your approval.</li>
          <li>· Stocked with iconic dishes from Toronto's best restaurants.</li>
          <li>· Tap-to-pay, simple resident experience.</li>
          <li>· Restocked within 48 hours of any stock-out.</li>
          <li>· Full telemetry — uptime, inventory, sales, all visible to you.</li>
        </ul>
      </div>
    </div>
  </div>
</section>

<section class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">The economics</p>
    <h2 class="bd-headline bd-reveal" style="max-width:22ch;">5% of sales,<br>returned to the property.</h2>
    <div class="bd-steps-grid" style="margin-top: var(--bd-space-7);">
      <div class="bd-step-big bd-reveal"><div class="bd-step-big__num">5%</div><h3 class="bd-step-big__title">Revenue share.</h3><p class="bd-step-big__body">Of every dollar a resident spends, 5% goes to the property. Monthly statements. Transparent reconciliation.</p></div>
      <div class="bd-step-big bd-reveal"><div class="bd-step-big__num">$0</div><h3 class="bd-step-big__title">Capital cost.</h3><p class="bd-step-big__body">We supply the freezer, install it, and run it. No procurement, no maintenance contract, no facilities lift.</p></div>
      <div class="bd-step-big bd-reveal"><div class="bd-step-big__num">≤2h/mo</div><h3 class="bd-step-big__title">Staff time.</h3><p class="bd-step-big__body">Just unlock the door for our restocking team. Everything else — inventory, payments, support — sits with us.</p></div>
      <div class="bd-step-big bd-reveal"><div class="bd-step-big__num">12mo</div><h3 class="bd-step-big__title">Pilot exclusivity.</h3><p class="bd-step-big__body">Twelve-month launch term with auto-renew when KPIs are met. If it underperforms, we fix it. If we can't, we remove it.</p></div>
    </div>
  </div>
</section>

<section class="bd-section bd-section--cream" id="talk">
  <div class="bd-container">
    <div class="bd-info-grid">
      <div class="bd-reveal">
        <p class="bd-eyebrow">Book a pilot</p>
        <h2 class="bd-headline" style="font-size: var(--bd-size-3xl);">Let's launch with you.</h2>
        <p style="max-width: 42ch;">Fifteen-minute call. We walk through the placement, the install timeline, and the resident comms plan. No pressure, no contract until you've seen it work.</p>
      </div>
      <form class="bd-form bd-reveal" style="color: var(--bd-cherry);">
        <div class="bd-field"><label for="p-bldg">Building name</label><input id="p-bldg" type="text" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></div>
        <div class="bd-field"><label for="p-units">Number of units</label><input id="p-units" type="number" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></div>
        <div class="bd-field"><label for="p-role">Your role</label><input id="p-role" type="text" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></div>
        <div class="bd-field"><label for="p-email">Email</label><input id="p-email" type="email" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></div>
        <button class="bd-btn bd-btn--primary" type="button">Book a 15-minute call</button>
      </form>
    </div>
  </div>
</section>
""")

# ---------- For restaurants ----------

def for_restaurants_page():
    return page("For restaurants", """
<header class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">For chefs and restaurants</p>
    <h1 class="bd-hero-headline bd-reveal" style="font-size:clamp(48px,7vw,112px);">Monetize<br>the kitchen<br>you already have.</h1>
    <p class="bd-hero-lede bd-reveal">Royalties + execution fees on iconic dishes from your kitchen. No new storefront. No new staff. Your name on every package.</p>
    <a class="bd-btn bd-btn--primary bd-reveal" href="#apply">Apply</a>
  </div>
</header>

<section class="bd-section bd-section--alt">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">Why it works</p>
    <div class="bd-steps-grid">
      <div class="bd-step-big bd-reveal"><div class="bd-step-big__num">01</div><h3 class="bd-step-big__title">Idle hours,<br>real revenue.</h3><p class="bd-step-big__body">Your kitchen sits empty for most of the day. We use those hours to produce one dish, in batches, on a schedule that doesn't disturb service.</p></div>
      <div class="bd-step-big bd-reveal"><div class="bd-step-big__num">02</div><h3 class="bd-step-big__title">Royalties +<br>execution fees.</h3><p class="bd-step-big__body">You earn on every unit sold — royalty for the IP, execution fee for the prep. Transparent unit economics. Monthly statements.</p></div>
      <div class="bd-step-big bd-reveal"><div class="bd-step-big__num">03</div><h3 class="bd-step-big__title">Your brand,<br>in premium buildings.</h3><p class="bd-step-big__body">Every package carries your name, your chef, your story. Buildings become a new top-of-funnel for the dining room.</p></div>
      <div class="bd-step-big bd-reveal"><div class="bd-step-big__num">04</div><h3 class="bd-step-big__title">No delivery apps.<br>No grocery.</h3><p class="bd-step-big__body">Your dishes are exclusive to BestDish. They don't appear on Uber Eats. They don't appear in Loblaws. The integrity of your dining room is protected.</p></div>
    </div>
  </div>
</section>

<section class="bd-section bd-section--cream" id="apply">
  <div class="bd-container">
    <div class="bd-info-grid">
      <div class="bd-reveal">
        <p class="bd-eyebrow">Apply</p>
        <h2 class="bd-headline" style="font-size: var(--bd-size-3xl);">Tell us your dish.</h2>
        <p style="max-width: 42ch;">Take five minutes. Tell us which dish would translate. We'll come visit your kitchen, taste it, and propose unit economics within two weeks.</p>
      </div>
      <form class="bd-form bd-reveal" style="color: var(--bd-cherry);">
        <div class="bd-field"><label for="r-rest">Restaurant</label><input id="r-rest" type="text" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></div>
        <div class="bd-field"><label for="r-chef">Chef</label><input id="r-chef" type="text" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></div>
        <div class="bd-field"><label for="r-dish">The dish</label><input id="r-dish" type="text" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></div>
        <div class="bd-field"><label for="r-why">Why this dish</label><textarea id="r-why" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></textarea></div>
        <div class="bd-field"><label for="r-email">Email</label><input id="r-email" type="email" style="border-bottom-color: var(--bd-cherry); color: var(--bd-cherry);"></div>
        <button class="bd-btn bd-btn--primary" type="button">Send application</button>
      </form>
    </div>
  </div>
</section>
""")

# ---------- FAQ ----------

def faq_page():
    qs = [
        ("Is BestDish actually as good as the restaurant?",
         "It's made in the restaurant by the same chefs using the same ingredients, then frozen at peak quality. For most dishes the result is genuinely indistinguishable. The chef's note on each dish page tells you what to expect."),
        ("How does the freezer work?",
         "Tap your card, the door unlocks, take the dish you want, close the door. Charge is calculated automatically based on what you took. No app required — but there is one if you want to track orders or get notified when your favourites are back in stock."),
        ("How long do meals keep?",
         "Up to 21 days frozen from production. Every package carries the production batch and expiry. We rotate stock weekly and never restock past 70% sell-through on a SKU."),
        ("What if I take something and it's bad?",
         "Tell us — credit goes back to your card within 24 hours. We trace it to the batch and act. Food safety isn't a marketing line for us; it's an operational discipline with HACCP, CFIA labelling, and full cold-chain monitoring."),
        ("Is it cheaper than delivery?",
         "Almost always. No delivery fee, no tip, no tax — those three usually add 40%+ to the listed price. BestDish dishes are CAD $20–35 all-in."),
        ("How do I bring it to my building?",
         "Ask your property manager to email hello@bestdish.ca, or fill out the form on the Find a building page. We can install within 4 weeks of a signed pilot agreement."),
        ("Is my data private?",
         "Yes. We're PIPEDA-compliant. We use your purchase history to keep your favourites in stock and personalize the menu. We never sell it."),
    ]
    items = "".join(f"""<details class="bd-panel bd-reveal" style="cursor:pointer;">
      <summary style="font-family: var(--bd-font-display); font-weight: 700; text-transform: uppercase; letter-spacing: var(--bd-track-tight); font-size: var(--bd-size-lg); list-style: none;">{e(q)}</summary>
      <p style="margin-top: var(--bd-space-4); line-height: var(--bd-lh-relaxed);">{e(a)}</p>
    </details>""" for q, a in qs)
    return page("FAQ", f"""
<header class="bd-section">
  <div class="bd-container">
    <p class="bd-eyebrow bd-reveal">FAQ</p>
    <h1 class="bd-hero-headline bd-reveal" style="font-size:clamp(48px,7vw,112px);">The honest answers.</h1>
  </div>
</header>
<section class="bd-section" style="padding-top:0;">
  <div class="bd-container">
    <div class="bd-stack" style="display:grid; gap: var(--bd-space-4);">{items}</div>
  </div>
</section>
""")

# ---------- Build ----------

def build():
    (ROOT / "index.html").write_text(home())
    (ROOT / "meals.html").write_text(meals_page())
    (ROOT / "how-it-works.html").write_text(how_it_works_page())
    (ROOT / "chefs.html").write_text(chefs_page())
    (ROOT / "farms.html").write_text(farms_page())
    (ROOT / "buildings.html").write_text(buildings_page())
    (ROOT / "for-properties.html").write_text(for_properties_page())
    (ROOT / "for-restaurants.html").write_text(for_restaurants_page())
    (ROOT / "faq.html").write_text(faq_page())
    (ROOT / "meals").mkdir(exist_ok=True)
    for d in DISHES:
        (ROOT / "meals" / f"{d['slug']}.html").write_text(dish_page(d))
    print(f"Built site at {ROOT}")
    print(f"  - Pages: {len(list(ROOT.glob('*.html'))) + len(list((ROOT/'meals').glob('*.html')))} total")

if __name__ == "__main__":
    build()
