# Your forge (build a provider)

Any system rootle can't reach in-tree wraps as a **child process
speaking NDJSON-RPC 2.0 over stdio** — the LSP model. Write the
adapter in anything that speaks JSON on pipes; rootle owns the process
lifecycle (spawn, kill, bounded-backoff respawn) and the protocol
handles the rest.

## The shape

```sh
rootle config  # ~/.config/rootle/config.toml
```

```toml
[provider]
kind = "stdio"
command = ["python3", "/path/to/your_provider.py"]
# name = "shortname"   # modeline chip label (defaults to the handshake name)
# icon = "github"      # builtin icon name, or a single glyph
```

The reference adapter — `fs_provider.py`, ~200 lines of Python serving
a local directory of repos — is the worked example:

```python
def handle(root: str, method: str, params: dict) -> dict:
    if method == "initialize":
        return {
            "protocol": 1,
            "name": "fs",
            "icon": "folder",
            "capabilities": {"orgs": True, "code_search": True},
        }
    if method == "repo/tree":
        return {
            "entries": walk_tree(root, params["repo"]),
            "truncated": False,
            "branch": "main",
        }
    ...
```

Four methods make a minimal useful provider: `repo/tree`,
`repo/blob`, `search/repos`, and the handshake itself. Everything else
(`org/repos`, `org/url`, `repo/web_url`, `repo/clone_url`,
`search/code`) layers on top.

## The contract highlights

- **Content ids, not shas**: every `sha` is an opaque id that MUST
  change when content changes — the cache is content-keyed and
  immutable; trees and blobs are never invalidated, only evicted.
- **Restart obligations**: rootle kills and respawns the child an
  unbounded number of times. Startup must be cheap and idempotent;
  read credentials lazily on first use, never at spawn.
- **Streaming (v1.3)**: answer `search/code` requests carrying
  `"partial": true` with `$/partial` notifications — results render in
  the TUI as they arrive. The final reply is metadata-only.
- **Capability splits**: declare what you have — `orgs`,
  `code_search`, `file_search` (Bitbucket Cloud is the example:
  filename search yes, content search no).
- **Honest errors**: `data.kind` taxonomy — `auth`,
  `rate_limited` (+ `retry_after_s`), `not_found`, `network`,
  `timeout`, `provider`. Unknown kinds degrade to a toast, never a
  crash.

## The spec and the gate

The normative wire format lives in
[`doc/provider-protocol.md`](https://github.com/rootledev/rootle/blob/main/doc/provider-protocol.md)
(v1.4). The [scaffolding
skill](https://github.com/rootledev/rootle/tree/main/skills/rootle-provider)
walks you through the capability questionnaire, and the canonical
[forge-conformance](https://github.com/rootledev/forge-conformance)
suite is the integration gate — every protocol gotcha as a numbered,
citable case (FC-001..080) against a deterministic fixture. It is the
same gate rootle-gitlab and rootle-bitbucket run in their own CI.

Real out-of-tree providers to read: [rootle-gitlab](https://github.com/rootledev/rootle-gitlab)
(GitLab REST v4, content-addressed cache, ETag revalidation) and
[rootle-bitbucket](https://github.com/rootledev/rootle-bitbucket)
(Bitbucket REST 2.0, commit-pinned ids, the `file_search` split).
