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
4. **anonymous** — public repository browsing; global code search requires
   authentication and failures remain visible in the search result pane

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

- **Browse** — owners → repos → trees → files, live syntax-highlighted preview
- **Find** (`␣ f`) and **grep** (`␣ g`) — Zed-style full-screen search
- **Open** any file read-only in your editor (`Enter`)
- **Yank** browser URLs (`␣ y`)
- **Clone** through the wizard (`v` marks, `:clone`)
- **Global code search** requires authentication;
  syntax: [GitHub's code-search
  syntax](https://docs.github.com/en/search-github/github-code-search/understanding-github-code-search-syntax)
  plus rootle's own grammar (quoted literals, `-` negation,
  `language:`) — see [search syntax](./index.html#search-syntax). Young
  or low-activity repos aren't in GitHub's index: a scoped grep there
  gets a local tarball grep (0.8.4+) instead of a quiet zero

## Personal accounts and saved owners

`rootle owner/repo` loads that repository directly; it does not infer that
`owner` is an organization. Saved legacy owner names remain available without
an eager organization lookup on launch. Fresh profiles open repository search;
warm profiles retain their browsing history.

When you explicitly open an owner's repository list, the built-in backend
resolves GitHub's account type and uses the personal-account or organization
endpoint. Genuine authentication, rate-limit and not-found errors remain errors.

## GitHub Enterprise

The built-in backend currently targets `api.github.com`; a token does not select
another API host. For GHES, use a [stdio provider](../provider-protocol.html)
configured for your instance.
