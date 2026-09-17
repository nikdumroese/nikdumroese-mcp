# nikdumroese-mcp — CLAUDE.md

Dependency-free MCP server exposing nikdumroese.com as agent tools (`about`,
`availability`, `list_projects`, `get_project`, `list_open_source`, `contact`, `search`)
plus two resources (`nik://site`, `nik://map`). See `README.md` for the tool table, run
instructions, and Claude Desktop config.

## Two parallel implementations — keep in sync
- `server.py` — stdlib-only Python, JSON-RPC 2.0 over stdio (local/Claude Desktop).
- `worker.js` — Cloudflare Worker, same tools over Streamable HTTP (`mcp.nikdumroese.com`, `wrangler.toml`).
- Both hardcode the **same static data** independently: `ABOUT`, `AVAILABILITY`, `CONTACT`,
  `PROJECTS`, `REPOS` (`server.py:20-81`, `worker.js:11-38`). There is no shared source file —
  editing one without the other silently desyncs the two transports. Any content change
  (positioning, project list, contact info) must be applied to both.
- Only `search` and the two resources fetch live content from nikdumroese.com
  (`server.py:84` `fetch()`, hits `/llms-full.txt` / `/llms.txt`) — those stay current automatically.
  Everything else (`about`, `availability`, `list_projects`, `get_project`, `list_open_source`) is
  a static snapshot and drifts from the real site (`../nikdumroese-com/`) unless updated by hand.

## Rules
- No dependencies. Don't add a `pip install` or npm package to either implementation —
  the whole point is dependency-free/single-file.
- Keep `PROJECTS`/`REPOS` entries consistent with `../nikdumroese-com/llms.txt` and
  `../nikdumroese-com/index.html` when either changes — check both when touching site copy.
- `wrangler.toml` custom-domain `routes` block is commented out by default; don't uncomment/deploy
  without confirming intent (it's a live production route).

## Verification
No test suite. After changing tool logic or data:
- Python: `printf '...' | python3 server.py` per the "Quick manual test" in `README.md`.
- Worker: `npx wrangler dev` locally, or `curl` the deployed URL per `README.md`'s example.
