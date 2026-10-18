# rootle.dev

The rootle website: landing page (`website/`), user docs (`doc/`),
demo GIFs (`img/`). This repo is the whole site — a push to `main`
redeploys via `pages.yml`. The app itself lives in
[rootledev/rootle](https://github.com/rootledev/rootle); contributor
docs (provider protocol spec, development guide, house style) stay
there.

Active install/support policy is **Linux / WSL x86_64 only**, with prebuilt
target `x86_64-unknown-linux-musl`. ARM, macOS and native Windows are not
supported. Homebrew uses the Linux x86_64 source formula; the macOS cask is
retired. Historical release notes and assets are retained as history.

Local preview:

```
uv run --with markdown --with pymdown-extensions --with pygments python website/build.py   # → public/
```

The build expects the app repo checked out at `code/` (CI does this)
for the version stamp, changelog and `install.sh`; without it the version
falls back to the latest release tag and the installer is omitted.
The installer is copied from that source checkout, never maintained here.
For isolated local qualification, link `code/` to the coordinated app
checkout (for this pilot, `/tmp/rootle-ci-local`) before building; do not
deploy. Pages uses the app repository's default branch, so its Linux-only
installer cutover must land before a future site deployment.

After building, preview `public/` with `python -m http.server --directory
public 8000`. Check every install-method tab and copy/update command, the
Linux / WSL x86_64 support notice, provider docs and the served installer.
Compare `public/install.sh` with `code/install.sh`; do not duplicate it.

Demo GIFs are re-rendered by the app repo's `demo` workflow, which
commits them straight to `img/` here (idempotent) — never hand-edit
them.
