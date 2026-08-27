# Roadmap

Where rootle is going. The north star: *the terminal source browser
for all the repositories you don't have checked out* — one interface,
code wherever it lives. The plan documents live in the app repo under
[`plans/`](https://github.com/rootledev/rootle/tree/main/plans) —
numbered, status in each header.

## Shipped

- The core browser: orgs → repos → trees in miller columns, syntax-
  highlighted preview with a line cursor, editor handoff, line-anchored
  URL yanking, `/` filters on every list
- Search parity: file find and grep with quoted literals, negation and
  `language:` qualifiers; results stream as they arrive (protocol
  v1.3), render as decorated per-file boxes, expand to the whole file
  at the match line, and facet by repo/language
- The clone wizard: VISUAL multi-select, org expansion, archived repos
  greyed, sorted by last push (protocol v1.4)
- Eleven palettes with a picker, `[ui] border` shapes, optional
  Nerd Font powerline chrome, hot-reloading `:settings`
- Providers: GitHub in-tree; GitLab and Bitbucket as one-binary
  adapters speaking NDJSON-RPC over stdio (protocol through v1.4 —
  streaming, honesty chips, error taxonomy, bounded compute)
- The provider manager: checksum-verified installs from GitHub
  releases *or* plain-HTTP artifact hosts, `update`/`upgrade`/`pin`,
  `--path` for config-managed deployments
- [forge-conformance](https://github.com/rootledev/forge-conformance):
  every protocol gotcha as a numbered case (FC-001..080) — all three
  providers run it in CI; it caught two real bugs on landing
- Four-platform releases (linux + macOS, both arches), crates.io,
  homebrew formula + cask, checksum-verified `install.sh`

## Next

- **Revision navigation** — the current focus. `rootle owner/repo@branch`,
  an in-app refs switcher (`␣ b`), file history and a blame lens in the
  preview submode (`␣ p` — the pane focuses and zooms, vim motions
  included). Mock stage reviewed on the app repo's
  `feat/revision-mocks` branch; wire work (`repo/refs`, `ref?`,
  `repo/log`, `repo/blame`) follows the mock. See
  [plans/0016](https://github.com/rootledev/rootle/blob/main/plans/0016-product-direction.md).
- **Symbol search** — `␣ s` for symbols: the tree-sitter spike passed
  (320 files/s single-threaded, ~13 MiB on a 908-file corpus), so every
  forge gets it via the blob cache, with provider indexes preferred
  when they exist. [plans/0013](https://github.com/rootledev/rootle/blob/main/plans/0013-symbol-search-gate.md).
- **In-app provider management** — browse/install/switch providers
  without leaving the TUI (the manager is CLI-only today).
- **The demo tape tells a workflow story** — find → browse → grep →
  expand → yank, not just palettes.

## Evaluating

- **Nerd Font chrome by default** — the powerline modeline is opt-in
  because a terminal can't report its font and tofu-on-first-launch is
  the worst first impression. Open: a reliable probe or a better
  first-run hint. Meanwhile: `:settings` → ui.
- **Bitbucket private workspaces** — the adapter is validated against
  public workspaces; the private path is validated by construction and
  waits on a first real workspace.
- **`$/progress` (work-done notifications)** — a v2 protocol question;
  decided with its first consumer (cold-org enumeration), not before.

## Decidedly not

- **PRs / issues / notifications dashboards** — gh-dash and the web
  own that. rootle stays on code.
- **A generic git frontend** — revisions are for browsing, not
  staging/committing.
- **AI features** — the value here is speed, deterministic navigation,
  and composability.

## North star

Jump across repos, search code, inspect files, and open exactly what
you need — without cloning a dozen repositories or leaving your
terminal. GitHub, GitLab, Bitbucket are bundled adapters; your
company's forge is [four methods away](providers/your-forge.html),
and the conformance suite is how it earns the badge.
