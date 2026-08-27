# Bitbucket (installable)

Bitbucket Cloud support ships as an out-of-tree provider — one Rust
binary speaking rootle's stdio protocol, talking to Bitbucket's REST
2.0 API.

## Install

From source / crates.io:

```sh
cargo install rootle-bitbucket
```

Or build it from the repo:

```sh
git clone https://github.com/rootledev/rootle-bitbucket
cd rootle-bitbucket && cargo install --path .
```

## Authentication

The provider reads credentials lazily, on first API call (a respawned
provider never re-authenticates at startup). Two shapes — **pick one,
they don't mix**:

```sh
# App password: create at
# https://bitbucket.org/account/settings/app-passwords/
# scopes: Account — Read; Repositories — Read
export BITBUCKET_USERNAME=you
export BITBUCKET_TOKEN=your-app-password

# …or an Atlassian API token (id.atlassian.com) rides alone as a
# Bearer header — pairing it with a username sends Basic, which
# Bitbucket rejects for API tokens:
export BITBUCKET_TOKEN=your-api-token
# API token scopes: Account — Read (workspace discovery),
# Repositories — Read
```

Then point rootle at it — `~/.config/rootle/config.toml`:

```toml
[provider]
kind = "stdio"
command = ["rootle-bitbucket"]
```

A token scoped to repositories only (no Account — Read) can't discover
workspaces — CHANGE-2770 removed the old cross-workspace listings and
the replacement wants the account scope. Name your workspaces instead:

```toml
command = ["rootle-bitbucket", "--workspace", "myteam"]
```

(`BITBUCKET_WORKSPACES=a,b` works too.)

## What works

- **Browse** — workspaces → repos → full recursive trees. Bitbucket
  lists one directory per API call; the provider walks eight
  directories in flight (a real repo lands in seconds), bounded and
  cached per commit, so the miller columns behave like every other
  forge.
- **Find** (`␣ f`) — filename search over the walked tree, served as
  path-only hits. Repo- or workspace-scoped `path:` queries work over
  the same cache.
- **Preview** — syntax-highlighted blobs, pinned to commit hashes
  (Bitbucket's API exposes no git object ids, so `<commit>:<path>` is
  the content id).
- **Yank** — browser URLs with `#lines-N` fragments.
- **Clone** — through the wizard, using the repo's https clone URL.
- **Advisory cache budget** — your `[cache] max_mb` setting governs
  this provider's disk cache too.

## What doesn't (honestly)

**Grep** (`␣ g`): Bitbucket Cloud has **no code-search API** — not
paid, not metered, absent. The provider declares
`code_search: false, file_search: true` (the protocol's capability
split) and content searches answer with an explicit error instead of
silently returning nothing. Filename find covers the "where is this
file" case; open the file and use find-in-file (`␣ /`) for content.

## Notes

- Trees cache per commit and never invalidate (a pinned commit's
  listing is immutable); the cache lives at
  `~/.cache/rootle/providers/rootle-bitbucket/` — safe to delete.
- Cloning over https with an app password needs the password in your
  git credential store; rootle hands git the URL, not the credential.
- Rate limits map to the protocol's taxonomy — a 429 shows the
  advertised backoff on the status line.

## The provider itself

[`rootledev/rootle-bitbucket`](https://github.com/rootledev/rootle-bitbucket) —
Rust, one binary, no shared code with rootle. The first consumer of
the protocol's `file_search` capability split.
