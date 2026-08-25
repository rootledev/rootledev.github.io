# rootle.dev

The rootle website: landing page (`website/`), user docs (`doc/`),
demo GIFs (`img/`). This repo is the whole site — a push to `main`
redeploys via `pages.yml`. The app itself lives in
[rootledev/rootle](https://github.com/rootledev/rootle); contributor
docs (provider protocol spec, development guide, house style) stay
there.

Local preview:

```
uv run --with markdown python website/build.py   # → public/
```

The build expects the app repo checked out at `code/` (CI does this)
for the version stamp and `install.sh`; without it the version falls
back to the latest release tag.

Demo GIFs are re-rendered by the app repo's `demo` workflow, which
opens a `demo/artifacts` PR here — never hand-edit them.
