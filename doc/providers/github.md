# GitHub (built-in)

rootle's GitHub backend ships in the binary — nothing to install,
nothing to configure. It's the default provider.

## Authentication

rootle finds your GitHub credentials through this chain, in order:

1. **`ROOTLE_TOKEN`** env var — a [personal access token](https://github.com/settings/tokens)
   with `repo` (or `public_repo` for public repos) scope
2. **`GITHUB_TOKEN`** env var — same token shape, CI-friendly name
3. **`gh auth login`** — if the [GitHub CLI](https://cli.github.com/) is
   authenticated, rootle uses its stored token automatically
4. **anonymous** — works everywhere except code search (rootle says so
   in the status line when it matters)

The fastest path for most people:

```sh
gh auth login        # once; rootle picks it up from here on
rootle               # browse, search, grep, clone
```

No `gh`? Create a token at [github.com/settings/tokens](https://github.com/settings/tokens)
(`public_repo` scope for public repos, `repo` for private), then:

```sh
export ROOTLE_TOKEN=ghp_…
rootle
```

## What works

- **Browse** — orgs → repos → trees → files, live syntax-highlighted preview
- **Find** (`␣ f`) and **grep** (`␣ g`) — Zed-style full-screen search
- **Open** any file read-only in your editor (`Enter`)
- **Yank** browser URLs (`␣ y`)
- **Clone** through the wizard (`v` marks, `:clone`)
- **Code search** requires authentication (anonymous gets everything else)

## GitHub Enterprise

Set `ROOTLE_TOKEN` to a GHES PAT and point rootle at your instance —
the API base is derived from the token's scope. For full GHES support
or a different forge, write a [stdio provider](provider-protocol.html).
