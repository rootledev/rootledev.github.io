# Providers

rootle doesn't talk to GitHub directly — it talks to one seam (`trait
Provider`). The `github` backend ships in-tree; **anything else wraps in
as a child process speaking NDJSON-RPC over stdio** — the same model as
LSP. Your adapter can be any language; four methods make a minimal
useful provider.

**Available now:**

- **github** — built-in, nothing to install
- **gitlab** — [`rootle-gitlab`](https://github.com/rootledev/rootle-gitlab):
  `rootle provider install gitlab`, set `GITLAB_TOKEN`, done —
  30 seconds. Nested groups, code search with real line numbers,
  advisory cache budget. The reference out-of-tree provider.

- **bitbucket** — [`rootle-bitbucket`](https://github.com/rootledev/rootle-bitbucket):
  `rootle provider install bitbucket`, set `BITBUCKET_USERNAME` +
  `BITBUCKET_TOKEN` (app password) or a lone bearer token. First
  consumer of the protocol's `file_search` split — Bitbucket Cloud has
  no code-search API, so file find walks the commit-pinned tree while
  grep answers honestly.

The manager downloads the checksum-verified release binary for your
platform (the mandatory `.sha256` sidecar — a mismatch aborts the
install), tracks updates with `rootle provider update` / `upgrade`, and
`provider use` writes the config for you. Manual routes stay supported:
`cargo install`, prebuilt tarballs, plain-HTTP artifact URLs, and
`--path` for config-managed deployments.

![how rootle talks to backends: one seam, github in-tree, anything else as an NDJSON-RPC stdio child](architecture.svg)

## Point rootle at your backend

```toml
# ~/.config/rootle/config.toml
[provider]
kind = "stdio"
command = ["python3", "/path/to/fs_provider.py", "/path/to/code"]
```

Misconfiguration never blocks startup — a failed spawn or bad handshake
falls back to GitHub with a warning on the status line.

Try it against a directory of local repos with the reference adapter:

```
python3 examples/providers/fs_provider.py ~/code   # serves ~/code/* under "local"
```

## The shape of a provider

One JSON message per line on stdin/stdout. An `initialize` handshake,
then calls like `repo/tree` and `repo/blob`:

```
→ {"jsonrpc":"2.0","id":1,"method":"repo/tree","params":{"repo":"local/alpha"}}
← {"jsonrpc":"2.0","id":1,"result":{"entries":[…],"truncated":false,"branch":"main"}}

`search/code` streams (v1.3): rootle sends `"partial": true` and your
adapter may emit `$/partial` notifications carrying batches of items —
results render in the TUI as they arrive. The final reply is then
metadata-only (`items: []` + `truncated`). The reference adapter
streams per repo; the deadline is per-inactivity while you stream.

## Process lifecycle — what rootle assumes about your adapter

Your process is owned by rootle: it is killed on exit, and if it dies
mid-session (crash, OOM, network partition) rootle **respawns it with
bounded backoff and re-runs the handshake** — an unbounded number of
times per session. That self-healing works for you only if the adapter
is built for it:

- **Startup must be cheap and idempotent.** `initialize` runs once per
  generation; a new generation appears after every death.
- **State belongs on disk, not in memory.** Every respawn starts from
  scratch — cache by the protocol's content ids (they're immutable and
  content-keyed) under `~/.cache/rootle/providers/<name>/`.
- **Fetch credentials lazily** (first use, not at spawn) and cache them
  outside the process. Re-running an auth handshake on every respawn
  turns a network blip into a credential problem.
- Requests may be in flight **concurrently**, and replies may arrive
  out of order — ids route them. Each call has a read deadline
  (`timeout_ms`); during a respawn, a call may additionally wait one
  backoff interval plus a handshake round trip.

The [full spec](https://github.com/rootledev/rootle/blob/main/doc/provider-protocol.md)
carries the normative wording, error kinds, and the advisory-cancel
notification.

## Building one

- **Full wire spec** — every method, error kinds, cancellation:
  [doc/provider-protocol.md](https://github.com/rootledev/rootle/blob/main/doc/provider-protocol.md)
- **Reference adapter** (documentation-by-example):
  [examples/providers/fs_provider.py](https://github.com/rootledev/rootle/blob/main/examples/providers/fs_provider.py)
- **Scaffolding skill** — capability questionnaire + adapter skeleton:
  [skills/rootle-provider](https://github.com/rootledev/rootle/tree/main/skills/rootle-provider)
- **Conformance gate** — the canonical numbered suite every adapter
  runs in CI (rootle, gitlab, and bitbucket all do):
  [forge-conformance](https://github.com/rootledev/forge-conformance)

The e2e suite drives the full TUI through this protocol against the
reference adapter — offline proof of the whole path.
