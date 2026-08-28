# GitLab (installable)

GitLab support is the first out-of-tree provider — one Rust binary
speaking rootle's stdio protocol, talking to GitLab's REST v4 API.

## Install

The provider manager (rootle v0.5.0+):

```sh
rootle provider install gitlab
rootle provider use gitlab
```

Or from source / crates.io:

```sh
cargo install rootle-gitlab
```

Or grab a [prebuilt binary](https://github.com/rootledev/rootle-gitlab/releases)
(linux + macOS, x86_64 + aarch64) and put it on your PATH.

## Authentication

The provider reads `GITLAB_TOKEN` from the environment — lazily, on
first API call, so a respawned provider doesn't re-authenticate:

```sh
# gitlab.com — create at https://gitlab.com/-/user_settings/personal_access_tokens
# scopes: read_api + read_repository
export GITLAB_TOKEN=glpat-…

rootle provider use gitlab
rootle               # browse, search, grep, clone GitLab
```

Self-hosted GitLab:

```sh
rootle provider use gitlab -- --instance https://gitlab.example.com
```

## What works

Everything the GitHub backend does, through the same protocol:

- **Browse** — groups → projects (nested subgroups included: `group/sub/project`
  ids are opaque and flow untouched)
- **Find** (`␣ f`) and **grep** (`␣ g`) — GitLab's blob search with real
  line numbers (hits arrive located, no client-side locate pass)
- **Open** any file read-only in your editor
- **Yank** GitLab URLs (`/-/blob/main/src/main.rs#L42` grammar)
- **Clone** through the wizard
- **Advisory cache budget** — your `[cache] max_mb` setting governs this
  provider's disk cache too (LRU eviction past the cap)

## Notes

- Nested groups (`group/subgroup/project`) are first-class — rootle
  treats repos as opaque strings and never parses them.
- Code search on self-managed GitLab requires advanced search (a
  license); the provider surfaces the honest error rather than failing
  silently. Query syntax: [GitLab's advanced-search
  syntax](https://docs.gitlab.com/user/search/advanced_search_syntax/)
  plus rootle's own grammar — see [search syntax](./index.html#search-syntax).
- The disk cache lives at `~/.cache/rootle/providers/rootle-gitlab/` —
  content-addressed, immutable, safe to delete at any time.

## The provider itself

[`rootledev/rootle-gitlab`](https://github.com/rootledev/rootle-gitlab) —
Rust, one binary, no shared code with rootle. The wire protocol is the
entire interface; it's the reference implementation for writing your
own provider.
