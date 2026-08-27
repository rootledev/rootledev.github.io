#!/usr/bin/env python3
"""Assemble the rootle website into public/.

Single source of truth: the landing page is website/index.html, and the
docs pages are converted from doc/*.md at build time — editing a doc in
the repo is all it takes to update the site (pages.yml redeploys on
doc/** changes). Every page shares one chrome: a left rail (brand, site
nav, on-this-page TOC on docs) and a content column — the same markup
website/index.html carries by hand.

    uv run --with markdown python website/build.py    # → public/
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import urllib.request
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "public"

# The app repo, checked out beside the site by pages.yml (version stamp
# + install.sh). Absent in bare local previews.
CODE = ROOT / "code"

REPO = "https://github.com/rootledev/rootle"

# Cache-busting: content hash of the shared assets, stamped into every
# css/js URL as ?v=… — a stale cached stylesheet after a deploy can only
# survive until the hash changes.
_ASSET_VERSION: str | None = None


def app_version() -> str:
    """The version stamped into the landing's release chip. CI reads it
    from the app checkout (deterministic); local previews fall back to
    the latest release tag, then 0.0.0."""
    cargo = CODE / "Cargo.toml"
    if cargo.exists():
        m = re.search(r'^version = "([^"]+)"', cargo.read_text(), re.M)
        if m:
            return m.group(1)
    try:
        with urllib.request.urlopen(
            "https://api.github.com/repos/rootledev/rootle/releases/latest"
        ) as r:
            return json.load(r)["tag_name"].removeprefix("v")
    except Exception:
        return "0.0.0"


def asset_version() -> str:
    global _ASSET_VERSION
    if _ASSET_VERSION is None:
        h = hashlib.sha1()
        for name in ("site.css", "site.js"):
            h.update((ROOT / "website" / "assets" / name).read_bytes())
        _ASSET_VERSION = h.hexdigest()[:8]
    return _ASSET_VERSION

# Docs pages: url-path (under docs/) -> (source file, nav label).
# Nested paths create sub-directories — the providers section is one
# page per forge plus its index (the gripsack fetchers pattern).
PAGES: dict[str, tuple[str, str]] = {
    "providers/index": ("doc/providers/index.md", "providers"),
    "providers/github": ("doc/providers/github.md", "github"),
    "providers/gitlab": ("doc/providers/gitlab.md", "gitlab"),
    "providers/bitbucket": ("doc/providers/bitbucket.md", "bitbucket"),
    "settings": ("doc/settings.md", "settings"),
    "themes": ("doc/themes.md", "themes"),
    # Trimmed site version; the app repo carries the full wire spec.
    "provider-protocol": ("website/providers.md", "protocol"),
}

# Rail shape: (href-from-root, label, css class or ""). Sub-links sit
# under their section's link, indented.
RAIL: list[tuple[str, str, str]] = [
    ("index.html", "home", ""),
    ("docs/providers/", "providers", ""),
    ("docs/providers/github.html", "github", "sub"),
    ("docs/providers/gitlab.html", "gitlab", "sub"),
    ("docs/providers/bitbucket.html", "bitbucket", "sub"),
    ("docs/provider-protocol.html", "protocol", ""),
    ("docs/settings.html", "settings", ""),
    ("docs/themes.html", "themes", ""),
]

# Links inside the site docs that point at files in the APP repo we
# do not mirror: send them to the blob/tree on GitHub instead.
GITHUB_LINKS: dict[str, str] = {
    "development.md": f"{REPO}/blob/main/doc/development.md",
    "house-style.md": f"{REPO}/blob/main/doc/house-style.md",
    "provider-protocol.md": f"{REPO}/blob/main/doc/provider-protocol.md",
    "../skills/rootle-provider/SKILL.md": f"{REPO}/tree/main/skills/rootle-provider",
    "../examples/providers/fs_provider.py": f"{REPO}/blob/main/examples/providers/fs_provider.py",
}

# Doc-local images that are not screenshots: copied alongside img/.
DOC_ASSETS = {"architecture.svg"}

# Palette roles in doc/logo.svg -> site CSS vars, so the inline logo
# re-themes with the palette picker. The mole's illustration colors
# (fur shading, whiskers, eye highlights) are character colors and stay
# hardcoded; mode_leader is warm orange in every palette, so mapping
# fur to --peach keeps the mole a mole.
LOGO_VARS = {
    "#11111b": "var(--bg)",            # crust — backdrop, eyes
    "#1e1e2e": "var(--card)",          # base — terminal card
    "#181825": "var(--deep)",          # mantle — modeline bar
    "#313244": "var(--border)",        # surface0 — selection, scrollbar track
    "#45475a": "color-mix(in srgb, var(--border) 55%, var(--border-strong))",  # surface1
    "#585b70": "var(--border-strong)",  # surface2 — unfocused borders
    "#6c7086": "var(--faint)",         # overlay0 — modeline hints
    "#a6adc8": "var(--dim)",           # subtext0 — entries, code lines
    "#cdd6f4": "var(--text)",          # wordmark
    "#89b4fa": "var(--blue)",          # border_focused
    "#a6e3a1": "var(--green)",         # mode_browse
    "#f9e2af": "var(--yellow)",        # mode_search
    "#fab387": "var(--peach)",         # mode_leader — mole fur
    "#f38ba8": "var(--red)",           # error
    "#cba6f7": "var(--mauve)",         # mode_visual
    "#94e2d5": "var(--teal)",          # mode_insert
}


def themed_svg(path: Path) -> str:
    """An SVG with palette hexes swapped for site CSS vars — inline it so
    the palette picker re-themes it (an <img> can't inherit page CSS)."""
    svg = path.read_text()
    for hex_color, var in LOGO_VARS.items():
        svg = svg.replace(hex_color, var)
    return svg.strip()


def themed_logo() -> str:
    return themed_svg(ROOT / "doc" / "logo.svg")





# Palette dots in the docs rail: name + accent color (border_focused),
# mirroring the landing's picker so themes are switchable from any page.
PALETTE_DOTS = [
    ("catppuccin-mocha", "#89b4fa"),
    ("dracula", "#bd93f9"),
    ("gruvbox-dark", "#83a598"),
    ("nord", "#88c0d0"),
    ("one-dark", "#61afef"),
    ("solarized-dark", "#268bd2"),
    ("tokyo-night", "#7aa2f7"),
    ("catppuccin-latte", "#1e66f5"),
    ("github-light", "#0969da"),
    ("one-light", "#4078f2"),
    ("solarized-light", "#268bd2"),
]


def rail(active: str, toc: list[tuple[str, str]], prefix: str = "../") -> str:
    links = "".join(
        f'    <a{" class=\"active\"" if href == active else (" class=\"" + cls + "\"" if cls else "")} href="{prefix}{href}">{label}</a>\n'
        for href, label, cls in RAIL
    )
    toc_html = "".join(f'    <a href="#{anchor}">{label}</a>\n' for label, anchor in toc)
    toc_block = (
        f'  <span class="rail-head">on this page</span>\n  <div class="rail-toc">\n{toc_html}  </div>\n'
        if toc_html
        else ""
    )
    dots = "".join(
        f'    <button data-set-palette="{name}" title="{name}" '
        f'style="--sw:{color}" aria-label="{name}"></button>\n'
        for name, color in PALETTE_DOTS
    )
    return f"""<aside class="rail">
  <a class="brand" href="{prefix}index.html">
    <img src="../assets/icon.svg" alt="rootle icon"><span class="wordmark">rootle</span>
  </a>
  <span class="rail-head">menu</span>
  <nav>
{links}    <a class="gh" href="{REPO}">github ↗</a>
  </nav>
{toc_block}  <span class="rail-head">theme</span>
  <div class="rail-palettes">
{dots}  </div>
  <span class="palette-name" data-palette-name>catppuccin-mocha</span>
</aside>"""


def page(title: str, body: str, active: str, toc: list[tuple[str, str]], prefix: str = "../") -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="rootle — a modal terminal UI for browsing remote source-control systems.">
<link rel="icon" href="{prefix}assets/favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="{prefix}assets/site.css?v={asset_version()}">
<script src="{prefix}assets/site.js?v={asset_version()}" defer></script>
</head>
<body class="docs">
<div class="shell">
{rail(active, toc, prefix)}
<main class="content">
<article class="md">
{body}
</article>
<footer>
  <span><span class="blink"></span> © 2026 <a href="https://github.com/tknawara">Tarek Nawara</a></span>
  <span>MIT license</span>
  <a href="https://github.com/rootledev">rootledev</a>
  <a href="{REPO}">source</a>
  <a href="{prefix}index.html">home</a>
  <span style="margin-left:auto"><span class="fversion">v{app_version()}</span> · a ratatui TUI · eleven palettes</span>
</footer>
</main>
</div>
</body>
</html>
"""


def extract_toc(md_body: str) -> list[tuple[str, str]]:
    """(label, anchor) for every h2 the toc extension stamped with an id.
    Labels keep their HTML entities — they are inserted as HTML."""
    toc = []
    for m in re.finditer(r'<h2 id="([^"]+)">(.*?)</h2>', md_body):
        label = re.sub(r"<[^>]+>", "", m.group(2))
        toc.append((label, m.group(1)))
    return toc


def rewrite(body: str, slugs: set[str], prefix: str = "../") -> str:
    """Fix links/images in converted doc HTML for their new home."""

    # Doc-local assets (diagrams): architecture.svg -> ../assets/…
    for name in DOC_ASSETS:
        body = body.replace(f'src="{name}"', f'src="{prefix}assets/{name}"')

    # Sibling docs that are site pages -> their page.
    for slug in slugs:
        body = body.replace(f'href="{slug}.md"', f'href="./{slug}.html"')

    # Files that live in the app repo -> GitHub.
    for src, dst in GITHUB_LINKS.items():
        body = body.replace(f'href="{src}"', f'href="{dst}"')

    return body


def build_docs() -> None:
    slugs = set(PAGES)
    for slug, (src, _) in PAGES.items():
        prefix = "../" if "/" not in slug else "../../"
        text = (ROOT / src).read_text()
        body = markdown.markdown(
            text, extensions=["fenced_code", "tables", "toc", "sane_lists"]
        )
        body = rewrite(body, slugs, prefix)
        # Inline + theme doc-local SVG diagrams (they live behind <img>
        # otherwise, which can't inherit the page's palette vars).
        for name in DOC_ASSETS:
            if name.endswith(".svg"):

                def inline_svg(m: re.Match, name: str = name) -> str:
                    alt = re.search(r'alt="([^"]*)"', m.group(0))
                    label = alt.group(1) if alt else name
                    return (
                        f'<div class="diagram" role="img" aria-label="{label}">'
                        f"{themed_svg(ROOT / 'doc' / name)}</div>"
                    )

                body = re.sub(
                    rf'<img [^>]*src="(?:\.\./)+assets/{re.escape(name)}"[^>]*>',
                    inline_svg,
                    body,
                )
        title = re.match(r"# (.+)", text).group(1).strip()
        toc = extract_toc(body)
        dst = OUT / "docs" / f"{slug}.html"
        dst.parent.mkdir(parents=True, exist_ok=True)
        active = f"docs/{slug}.html"
        if slug == "providers/index":
            active = "docs/providers/"
        dst.write_text(
            page(f"rootle — {title.lower()}", body, active, toc, prefix)
        )
        print(f"built docs/{slug}.html from {src} ({len(toc)} toc entries)")

    # Redirect stubs keep the pre-section flat URLs alive
    # (docs/github.html → docs/providers/github.html, …).
    for name in ("github", "gitlab", "bitbucket"):
        stub = OUT / "docs" / f"{name}.html"
        stub.write_text(
            '<!doctype html>\n<meta charset="utf-8">\n'
            f"<title>rootle — {name}</title>\n"
            f'<meta http-equiv="refresh" content="0;url=./providers/{name}.html">\n'
            f'<a href="./providers/{name}.html">moved</a>\n'
        )


def assemble() -> None:
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "assets" / "img").mkdir(parents=True)
    (OUT / "docs").mkdir(parents=True)

    index = (ROOT / "website" / "index.html").read_text()
    assert "<!--LOGO-->" in index, "index.html lost its <!--LOGO--> placeholder"
    assert "<!--VERSION-->" in index, "index.html lost its <!--VERSION--> placeholder"
    index = index.replace("<!--LOGO-->", themed_logo())
    index = index.replace("<!--VERSION-->", app_version())
    index = index.replace("./assets/site.css", f"./assets/site.css?v={asset_version()}")
    index = index.replace("./assets/site.js", f"./assets/site.js?v={asset_version()}")
    (OUT / "index.html").write_text(index)
    # Custom domain — GitHub Pages reads this from the deployed artifact.
    (OUT / "CNAME").write_text("rootle.dev\n")
    # Served at rootle.dev/install.sh — the curl-pipe-sh installer.
    # Authored in the app repo (it belongs to the release toolchain);
    # CI checks that repo out at code/.
    installer = CODE / "install.sh"
    if installer.exists():
        shutil.copy(installer, OUT / "install.sh")
    else:
        print("warning: no code/ checkout — skipping install.sh")
    for name in ("icon.svg", "favicon.svg", "site.css", "site.js"):
        shutil.copy(ROOT / "website" / "assets" / name, OUT / "assets" / name)
    shutil.copy(ROOT / "doc" / "logo.svg", OUT / "assets" / "logo.svg")
    shutil.copy(ROOT / "img" / "demo.gif", OUT / "assets" / "demo.gif")
    for name in DOC_ASSETS:
        shutil.copy(ROOT / "doc" / name, OUT / "assets" / name)
    for gif in (ROOT / "img").glob("demo-*.gif"):
        shutil.copy(gif, OUT / "assets" / "img" / gif.name)
    print(f"copied landing page + {len(list((ROOT / 'img').glob('demo-*.gif')))} themed demo GIFs")


if __name__ == "__main__":
    assemble()
    build_docs()
