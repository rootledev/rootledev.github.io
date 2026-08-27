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
