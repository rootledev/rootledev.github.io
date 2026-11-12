# rootle.dev

The rootle website: landing page (`website/`), user docs (`doc/`),
demo GIFs (`img/`). This repo is the whole site — a push to `main`
redeploys via `pages.yml`. The app itself lives in
[rootledev/rootle](https://github.com/rootledev/rootle); contributor
docs (provider protocol spec, development guide, house style) stay
there.

Local preview:

```
uv run --with markdown --with pymdown-extensions --with pygments python website/build.py   # → public/
```

The build expects the app repo checked out at `code/` (CI does this)
for the version stamp and `install.sh`; without it the version falls
back to the latest release tag.

Demo GIFs are re-rendered by the app repo's `demo` workflow, which
commits them straight to `img/` here (idempotent) — never hand-edit
them.

Website palettes live in `website/assets/site.css`, with controls in
`website/index.html` and `PALETTE_DOTS` in `website/build.py`. The shared
`site.js` persists the `rootle-palette` choice across home and docs;
Hone is the default. All seventeen palettes, including Strop's Hone, Slate,
Carbide, Vellum, Paper and Paper Dark, are also selectable in the app.
Each palette has its own recording; `demo.gif` is Hone.
