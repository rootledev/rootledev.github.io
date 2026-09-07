# Settings reference

Every rootle setting: key, acceptable values, meaning, default. Config
lives at `~/.config/rootle/config.toml` (`$ROOTLE_CONFIG` does not apply —
use `rootle --config PATH` for an alternate file). Missing keys fall
back to defaults; malformed configuration is reported in the status line
without blocking startup. The `:settings` popup edits these in place and writes the same file —
hot-reloads the theme on save. Sections live in a sidebar (Tab/h/l);
themes and the provider kind are radio lists, booleans are ●/○ dots,
and text fields edit in place — ␣/enter activates the row. Committing
a theme recolors the popup immediately. Provider changes save too but
apply after restart.

```toml
[editor]
program = "hx"          # string, optional
args = []               # list of strings
read_only = true        # boolean

[theme]
name = "catppuccin-mocha"   # string
# path = "/abs/or/~/theme.toml"   # string, optional — overrides name

[cache]
max_mb = 512            # integer

[provider]
kind = "github"         # "github" | "stdio"
command = []            # list of strings (kind = "stdio")
timeout_ms = 30000      # per-request read deadline (kind = "stdio")
# stderr = "inherit"    # pass child stderr through (kind = "stdio")
```

## `[editor]` — opening files

| Key | Type | Default | Meaning |
|---|---|---|---|
| `program` | string, optional | unset | Editor binary. Unset → `$VISUAL` → `$EDITOR` → first of `hx`, `nvim`, `vim`, `vi` on PATH. |
| `args` | list of strings | `[]` | Extra arguments inserted before the file path. |
| `read_only` | boolean | `true` | With `true`, the vim family (`vim`, `nvim`, `vi`, `view`) opens with `-R`. Editors without a read-only flag (e.g. helix) edit the cache copy — rootle never writes back either way. |

Files open from `~/.cache/rootle/edit/<owner>__<repo>/<path>`; rootle
suspends the terminal while the editor runs and fully redraws on
return.

## `[theme]` — colors

| Key | Type | Default | Meaning |
|---|---|---|---|
| `name` | string | `"catppuccin-mocha"` | Palette to load. Embedded dark: `catppuccin-mocha`, `dracula`, `gruvbox-dark`, `nord`, `one-dark`, `solarized-dark`, `tokyo-night`. Embedded light: `catppuccin-latte`, `github-light`, `one-light`, `solarized-light`. Unknown name → Catppuccin Mocha. |
| `path` | string, optional | unset | Explicit palette file; wins over `name`. |

`--theme NAME` (CLI) overrides `name` for one session. To write your
own palette, place a TOML file under `~/.config/rootle/themes/` with
`[semantic]` role names mapped to hex colors, or select it with `path`.

Since v0.11.0, syntax highlighting uses statically linked Tree-sitter
grammars and maps captures onto the active palette. A palette change
recolors cached previews automatically.

The embedded set covers Rust, Python, JavaScript/JSX, TypeScript/TSX,
Go, C/C++, Java, C#, Ruby, PHP, Bash, Lua, JSON, TOML, YAML, HTML,
CSS and Markdown. Supported-language Markdown fences and HTML scripts
are highlighted with their embedded grammars. Unknown file types remain
plain text. No grammar downloads or shared-library installation are needed.

Commit deltas use `diff_add_fg`, `diff_del_fg`, `diff_add_bg`,
`diff_del_bg`, `diff_add_strong`, `diff_del_strong` and `diff_band`.
Unspecified diff colors follow the active light/dark palette; explicit
overrides win.

## Commit inspection

Since v0.12.0, select or open a repository and press `␣ h` to
see its commits at the current branch/tag. `Enter` opens commit detail.
For a single file, `␣ p` focuses the preview and `h` opens file history;
`Enter` opens that file at the selected commit, while `d` opens full detail.

The commit's changed files stay on the left, with the full message or
selected diff on the right. `Enter` opens a file's diff; `Tab` switches
files/preview focus in either view. Use `j/k` and `gg/G` in the focused
pane, `/` to filter files, `]f`/`[f` to step matching files, `h/l` to
scroll a diff horizontally, and `Y` for the provider's commit permalink.
`Esc` clears a filter, returns from the diff to the message, then unwinds
to history. Narrow terminals stack the same panes.

Diffs retain add/delete and changed-span background tints under
Tree-sitter syntax colors. Highlighting uses the available old/new hunk
fragments; it does not fetch or reconstruct missing whole-file context.

Providers may omit binary or large patches or truncate a file list.
Those states are labeled; an unavailable patch is not an empty change.
The viewer is read-only and never stages, commits or reverts code.

### Fresh profiles and input modes

Fresh profiles start with repository search and no seeded organizations
or repositories. Existing user recents are preserved. Modal search fields
show `❯` in INSERT and `●` in NORMAL; `Esc` switches to NORMAL and `i`
returns to INSERT. Transient `/` filters still cancel directly on `Esc`.

## `[cache]` — content store

| Key | Type | Default | Meaning |
|---|---|---|---|
| `max_mb` | integer | `512` | Blob cache cap in MiB. Least-recently-used blobs are evicted past it at startup; orphaned trees/blobs are swept. |

Blobs/trees are content-addressed and immutable (never invalidated,
only evicted); repo refs revalidate via ETag (a `304` is free).
The GitHub provider's store lives at
`~/.cache/rootle/providers/github/` (the TUI-level `edit/` scratch stays
at `~/.cache/rootle/`); deleting either is always safe. stdio providers
manage their own caches under `~/.cache/rootle/providers/<name>/`.

## `[provider]` — backend selection

| Key | Type | Default | Meaning |
|---|---|---|---|
| `kind` | `"github"` \| `"stdio"` | `"github"` | `github` = the built-in provider. `stdio` = external child process speaking NDJSON-RPC ([provider-protocol.md](provider-protocol.md)). |
| `command` | list of strings | `[]` | argv for `kind = "stdio"`; element 0 is the executable, the rest its arguments. Ignored for `github`. |
| `timeout_ms` | integer | `30000` | Per-request read deadline for `kind = "stdio"`: a hung backend call fails with a timeout instead of wedging the provider. |
| `stderr` | `"null"` \| `"inherit"` | `"null"` | `inherit` passes the stdio child's stderr through — adapter debugging without a log file. |

Invalid/misfiring stdio configuration falls back to `github` with a
warning in the status line — a provider misconfiguration never blocks
startup. Scaffolding a provider:
[skills/rootle-provider](../skills/rootle-provider/SKILL.md).

## Session diagnostics

Available since v0.11.0, these switches work with the TUI, headless
scripts, provider commands and self-update:

```sh
rootle --log
rootle --log-file issue.jsonl owner/repo
rootle --headless steps.txt --log-file issue-full.jsonl --log-content
```

`--log` / `--log=ALL` prints an automatically selected path under the state
directory's `rootle/logs/`. `--log=PATH` or `--log-file PATH` selects a new
file and overrides `ROOTLE_TRACE`. Existing files/symlinks are refused,
never overwritten or appended; Unix files are private (0600).

Metadata records modes, focus, cursors, selections, worker/request identities,
HTTP/cache outcomes, errors and cell/style hashes. It excludes typed text,
file text, rendered glyphs and provider stderr. `--log-content` opts into
sensitive input/UI/stderr capture; inspect it before sharing. Neither mode
automatically dumps env values, argument vectors, authorization headers or
raw RPC/HTTP bodies. Metadata can still reveal private repository paths.

Files end with a `trace_end` verdict. Missing markers, capture failures and
limits mean incomplete; a complete capture can still describe a failed
command. Storage is bounded to 64 MiB, 100,000 events and 256 KiB per record.
This supplies evidence for investigation, not deterministic remote replay.

## Environment variables

| Variable | Meaning |
|---|---|
| `ROOTLE_TOKEN`, `GITHUB_TOKEN` | GitHub token (GitHub provider only; `gh auth token` is tried after these). Code search requires a token. |
| `VISUAL`, `EDITOR` | Editor fallbacks when `[editor].program` is unset. |
| `ROOTLE_CLIPBOARD` | Path to a file — yanks (`␣ y`) write there instead of the clipboard (scripts/CI). |
| `ROOTLE_TRACE` | Path for a new private JSONL diagnostic session; existing files are refused. |
| `ROOTLE_HEADLESS_COLS`, `ROOTLE_HEADLESS_ROWS` | `--headless` viewport (default 100×30). |
| `NO_COLOR` | Ignored by the full-screen TUI, whose colors are semantic. Provider-management and update CLI output honor it. |

## Command line

```
rootle                    # launch (search popup only on fresh state)
rootle owner/repo         # skip the popup, open a repo
rootle --config PATH      # alternate config file
rootle --theme NAME       # override [theme].name for this session
rootle --headless SCRIPT # scripted driver: keys in, frames + state JSON out (no terminal; `-` = stdin)
rootle --version | -V
```

### Headless scripts

`--headless SCRIPT` reads one directive per line; `-` reads stdin.
Blank lines and lines starting with `#` are ignored:

| Directive | Meaning |
|---|---|
| `keys <text>` | Send keys, including `<esc>`, `<cr>`, `<bs>`, `<tab>`, `<space>` and arrow-key tokens. |
| `settle [ms]` | Wait for outstanding workers and queued follow-ups; default timeout 10000ms. |
| `wait <ms>` | Process events for a fixed duration. |
| `frame` | Print the rendered cell grid. |
| `state` | Print JSON describing the current app state. |

For a tree-rendering CI check:

```sh
printf 'settle\nframe\nstate\n' | rootle owner/repo --headless -
```

Startup waits for outstanding work, with a
10-second bound. Use `settle` after navigation and before sampling
`frame` or `state`. Its optional argument changes the timeout for that
step, not startup. A timeout exits nonzero and stops the script before
later samples. Completion includes failures: inspect `state.status` and
the rendered frame to distinguish a populated tree from a provider error.

Since v0.11.0, `settle` tracks real work rather than guessing from channel
silence. Older releases used a 400ms quiet window and could return while a
slow provider was still loading. All directives are listed in `--help`.


## Where things live

| Path | Contents |
|---|---|
| `~/.config/rootle/config.toml` | configuration |
| `~/.config/rootle/themes/<name>.toml` | palette overrides (`[semantic]` role = hex) |
| `~/.local/state/rootle/state.json` | recents, last org/repo/path, last search scope/extension |
| `~/.cache/rootle/edit/` | files materialized for your editor |
| `~/.cache/rootle/providers/<name>/` | per-provider content cache (safe to delete) |

Cache layout: `trees/<sha>.json` (immutable repo trees), `blobs/<ab>/<rest>`
(blobs sharded by the first two sha chars), `index/refs/<owner>/<repo>/<branch>`
(rev → tree sha + etag, revalidated on open), `edit/` (materialized files).
At startup rootle sweeps orphans and evicts least-recently-used blobs past
`[cache].max_mb` (default 512). Deleting `~/.cache/rootle` is always safe;
state and config are separate files.
