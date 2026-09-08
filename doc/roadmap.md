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
- Providers: GitHub in-tree; GitLab and Bitbucket as managed one-binary
  adapters speaking NDJSON-RPC over stdio, with capability negotiation,
  streaming, honesty chips and structured errors
- The provider manager: checksum-verified installs from GitHub
  releases *or* plain-HTTP artifact hosts, `update`/`upgrade`/`pin`,
  `--path` for config-managed deployments
- Revision awareness (v0.8.0, protocol v1.5): `␣ b` switches
  branches/tags, `rootle owner/repo@ref`, `␣ p h` file history with
  open-at-commit, `␣ p b` blame run-margins, sha-anchored permalinks
- The preview submode (`␣ p`): focus + zoom, vim vertical motions
  (counts, `gg`/`G`, pages, paragraphs, `%`, `zt/zz/zb`, `:<line>`)
- A state-only modeline with a `? keys` affordance; transient modes get
  a glued hint strip — one hint surface per context
- `rootle self-update` updates tarball installs (checksum-verified,
  atomic); the modeline chips `↑ vX.Y.Z` when a newer release exists;
  CHANGELOG.md rides every release from 0.8.0
- [forge-conformance](https://github.com/rootledev/forge-conformance):
  numbered protocol cases — all three providers run it in CI
- Four-platform releases (linux + macOS, both arches), crates.io,
  homebrew formula + cask, checksum-verified `install.sh`

## 0.12.2 — P1 reliability

Implemented and verified in [plan 0031](https://github.com/rootledev/rootle/blob/main/plans/0031-provider-feedback-reliability.md):

- **Machine-readable readiness** — request-scoped tree/search outcomes and
  explicit counts in headless state; worker completion is not UI acceptance.
- **Owner-aware startup and status** — no eager organization lookup derived
  from a repository owner or warm recents, no unrelated 404 over a ready tree.
  Preserve real user history; fresh and warm profiles remain distinct.
- **Visible search failures** — durable typed errors, successful-empty versus
  unavailable distinction, and retained partial results after a failed stream.
- **Compatibility clarity** — wire major `1`, JSON-RPC envelope `2.0`, additive
  spec revision `1.6`, and independently versioned rootle/provider packages.

## Shipped in 0.12.1

[Released 2026-09-08](https://github.com/rootledev/rootle/releases/tag/v0.12.1):

- **Explicit updater ownership** — application-only `self-update`,
  combined `update`, and real `provider …` command nesting.
- **Focused diff controls** — `/` and `n/N` search the diff; `y` creates
  side-correct line links and `Y` copies source text. Page keys and help
  work without silently switching to the sidebar.
- **One commit-detail key** — `d` in either history scope; file-history
  Enter keeps its distinct open-file-at-revision operation.
- **Changed-file hierarchy** — expanded directory headings, stable
  selectable leaves, and filters that keep ancestors and renamed paths.

## Shipped in 0.12.0

[Released 2026-09-08](https://github.com/rootledev/rootle/releases/tag/v0.12.0):

- **Repository history and commit browsing** — `␣ h` opens a repository
  log without requiring a file preview. Commit files remain beside the
  message/diff, with `Tab` focus and filtered file stepping.
- **Syntax-highlighted diffs** — independent old/new hunk fragments use
  the shared Tree-sitter engine, preserving origin and changed-span tints.
  Shared preview/prose and viewport components own presentation.
- **Clean startup and modal prompts** — no seeded repository suggestions
  for fresh profiles; search fields use `❯` for INSERT and `●` for NORMAL.

## Shipped in 0.11.0

[Released 2026-09-07](https://github.com/rootledev/rootle/releases/tag/v0.11.0):

- **Tree-sitter highlighting** — statically embedded grammars, multiline
  context, Markdown fenced-language and HTML-script injections, and
  palette-following colors. Compiled queries are cached and parser state
  is reused; Linux binaries remain fully static.
- **Reliable headless waits** — `settle [ms]` waits for actual workers and
  their queued follow-ups. Timeouts fail the run instead of sampling a
  half-loaded tree. The default bound is 10 seconds; `--help` lists the
  complete script language.
- **Diagnostic sessions** — private bounded JSONL traces across input,
  actions, state, rendering, workers, provider traffic, HTTP/cache and
  CLI lifecycle. `--log-content` explicitly enables sensitive capture.
  Incomplete logs say so; existing files are never overwritten.
  [Plan 0030](https://github.com/rootledev/rootle/blob/main/plans/0030-session-diagnostics.md).

## Shipped in 0.10.0

[Released 2026-09-07](https://github.com/rootledev/rootle/releases/tag/v0.10.0):
four platform tarballs, six published crates and green Homebrew checks.
Implementation and verification details live in
[plan 0029](https://github.com/rootledev/rootle/blob/main/plans/0029-polish-release-integration.md).

- **Commit inspection** (protocol v1.6): history `d` opens the full
  message and changed files; `Enter` opens a unified delta, `]f`/`[f`
  step files and `Esc` unwinds. Independent message scrolling,
  `/` file filtering, Unicode-safe emphasis and palette-aware tints.
  Binary/unavailable/truncated patches remain explicit.
- **Six-crate workspace**: application, provider vocabulary, stdio
  transport, GitHub, provider management and typed diffs have distinct
  dependency boundaries and publish in dependency order.
- **Stable identity**: provider repo/sha/ref newtypes, domain-tagged
  request clocks and entity-scoped VISUAL marks, independent of captions.
- **Shared lists and bindings**: refs, help, settings, clone lists,
  history and commit files use one filter/selection/viewport engine.
  Typed tables supply commands and hints; item indices are not row offsets.
- **Bounded protocol verification**: ten safety invariants, type
  correctness and two fairness-qualified temporal properties; four
  deliberately faulty variants must fail by name. Production-router
  traces and real-child tests bridge to Rust, without claiming formal
  refinement or unbounded soundness/completeness.

## Next — P2 feature work

- **Symbol search** — `␣ s` for symbols: the tree-sitter spike passed
  (320 files/s single-threaded, ~13 MiB on a 908-file corpus), so every
  forge gets it via the blob cache, with provider indexes preferred
  when they exist. [plans/0013](https://github.com/rootledev/rootle/blob/main/plans/0013-symbol-search-gate.md).
- **In-app provider management** — browse/install/switch providers
  without leaving the TUI (the manager is CLI-only today).
- **The demo tape tells a workflow story** — find → browse → grep →
  expand → *inspect a commit* → yank, not just palettes.
- **Remaining domain migration** — legacy response/UI identity fields
  move from raw strings into domain types as their consumers change;
  serialized wire strings and ordinary local arithmetic stay simple.
- **Commit capability across adapters** — extend v1.6 conformance and
  out-of-tree implementations where their backend APIs support detail.
  Unsupported adapters must continue to say so rather than fake a patch.

## Deferred reviewer follow-ups

- **P1, external provider maintainer:** publish tested rootle/provider pairs,
  required capabilities and runtime/tool dependencies; document personal-owner
  enumeration and provide useful help. Rootle cannot assert a compatibility
  range for an uninspected `rootle-bbgithub` release. This does not block core
  readiness/error-display fixes.
- **P2, rootle:** explicit opt-in provider inspection with observed protocol and
  capabilities, declared versus defaulted values, and a reviewed malformed-version
  admission policy. Plain `provider list --json` stays passive: no surprise child
  execution, authentication, installation or update.
- **P2, deployment/provider validation:** run the full pinned pair on RHEL 8.10
  before claiming support. The supplied evidence covers WSL Ubuntu 24.04 / glibc
  2.39 only; a static rootle binary does not certify its child provider.
- **P2, demand-gated UX:** always opening search on warm profiles is separate
  from fixing owner provenance. Do not erase recents or infer this preference
  from an empty query.
- **P3, protocol gate:** package-version/minor-spec negotiation only after a
  concrete requirement cannot be expressed by wire major and capabilities.
  No speculative compatibility blacklist or new handshake version.

## Evaluating

- **Side-by-side diffs** — rejected for now with reasons recorded
  (strop's plan 0010 research): unified + intra-line emphasis carries
  the signal at half the geometry cost; the emphasis engine's run
  pairing is the alignment basis if a split view ever earns itself.
- **Context folding / gap expanders** — needs per-side fetch-more
  plumbing; follows side-by-side.
- **Nerd Font chrome by default** — the powerline modeline is opt-in
  because a terminal can't report its font and tofu-on-first-launch is
  the worst first impression. Open: a reliable probe or a better
  first-run hint. Meanwhile: `:settings` → ui.
- **Bitbucket private workspaces** — the adapter is validated against
  public workspaces; the private path is validated by construction and
  waits on a first real workspace.
- **`$/progress` (work-done notifications)** — a v2 protocol question;
  decided with its first consumer (cold-org enumeration), not before.
- **SBOM / `cargo auditable` builds** — provenance attestation landed
  in 0.9.0; the SBOM audit is the remaining half of the verified-
  release story.
- **Application-state verification** — mode/focus/revision invariants
  and a broader implementation-model bridge beyond the checked transport.
- **Transport OS boundaries** — stdin backpressure and inherited
  child pipes/process trees need runtime stress and deadline work;
  they are outside the current finite-state model's abstraction.
- **Pending-key hints** — reconsider a dedicated surface only if the
  sequence vocabulary outgrows the current mode hint strip.
- **Trace-to-script extraction and provider-result replay** — structured
  diagnostic recording is implemented; reproducing external service results
  and timing needs a separate contract, not an implied replay guarantee.

## Decidedly not

- **PRs / issues / notifications dashboards** — gh-dash and the web
  own that. rootle stays on code.
- **A generic git frontend** — revisions are for browsing, not
  staging/committing. The commit viewer inspects; it never mutates.
- **Generational arenas** — fixed browser/overlay ownership does not
  need one. Revisit only if rootle gains dynamically recycled panes.
- **AI features** — the value here is speed, deterministic navigation,
  and composability.

## North star

Jump across repos, search code, inspect files, and open exactly what
you need — without cloning a dozen repositories or leaving your
terminal. GitHub ships in-tree; GitLab and Bitbucket are managed
adapters. Your company's forge is [four methods away](providers/your-forge.html),
and the conformance suite is how it earns the badge.
