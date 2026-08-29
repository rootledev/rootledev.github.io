# Providers

rootle talks to backends through one seam — GitHub ships in-tree,
anything else is a child process speaking the [stdio protocol](../provider-protocol.html). This section is one page per forge:

- **[github](github.html)** — built-in, nothing to install. The
  reference implementation of the seam.
- **[gitlab](gitlab.html)** — the first out-of-tree provider: browse,
  search, grep, clone, one static binary. Also the reference for
  writing your own.
- **[bitbucket](bitbucket.html)** — Bitbucket Cloud via REST 2.0: the
  first consumer of the protocol's `file_search` capability split
  (Bitbucket has no code-search API — the page says exactly what that
  means in practice).

Rolling your own forge? The [wire spec](../provider-protocol.html) and
the [scaffolding skill](https://github.com/rootledev/rootle/tree/main/skills/rootle-provider)
are the whole contract — the reference adapter
([fs_provider.py](https://github.com/rootledev/rootle/blob/main/examples/providers/fs_provider.py),
~200 lines of Python serving a local directory) is the worked example.

## Search syntax

The query grammar is rootle's own and the same on every forge —
quoted literals, negation, qualifiers:

| You type | It means |
| --- | --- |
| `handle_request` | the term, case-insensitive |
| `"exact phrase"` | one literal — spaces don't split it |
| `struct -derive` / `struct -NOT json` | subtract the term (client-side honesty chip when the backend can't negate natively) |
| `language:rs` | files of that language only |
| `extension:toml` | or use the extension field — same thing |

The fields row carries scope (global · org · repo) and extension;
facet chips under it filter by repo/language as results stream.
Scoped greps run against the forge's index first; when the index
can't cover the repo (young repos on GitHub aren't indexed yet), 0.8.4
falls back to a local grep over the repo tarball instead of showing a
quiet zero.

Forge-native syntax links: [GitHub code
search](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax),
[GitLab advanced search](https://docs.gitlab.com/user/search/advanced_search_syntax/)
(self-managed needs the advanced-search backend), Bitbucket — no
code-search API; `␣ f` (find file) works there because it walks the
tree client-side.

## Lifecycle

Providers are managed binaries: `rootle provider install gitlab` to
fetch (checksum-verified), then *declare* them — `kind = "gitlab"` in
`~/.config/rootle/config.toml` (or `rootle provider use gitlab` writes
it for you). A config synced to a machine without the binary gets a
consent prompt at startup, then the verified install. Optional pins —
`tag = "v0.2.1"`, `sha = "…"` — lock the build for reproducibility.
`rootle update` sweeps the app *and* every unpinned provider.

If a configured provider won't start, 0.8.6+ asks — retry once,
browse github, or edit the config in your editor — and the modeline
keeps a sticky notice (forge chip tinted) for as long as you're on
the fallback. Fallbacks are never silent.
