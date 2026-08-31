# nikdumroese-mcp

A tiny [Model Context Protocol](https://modelcontextprotocol.io) server for **[nikdumroese.com](https://nikdumroese.com)**. It lets an AI agent connect and *query the site as tools* — who Nik is, what he's built, whether he's available, and how to reach him.

Mostly a proof of concept: the site already ships [`/llms.txt`](https://nikdumroese.com/llms.txt) so agents can read it. This takes the idea one step further — the site as a set of callable tools.

**Dependency-free.** Python standard library only. No `pip install`. One file.

## Tools

| Tool | Returns |
|---|---|
| `about` | Background and how Nik works |
| `availability` | Whether he's open to work, and for what |
| `list_projects` | Selected work with one-line summaries |
| `get_project` | Full scope / stack / outcome for one project |
| `list_open_source` | Open-source tools and agent skills |
| `contact` | How to reach him |
| `search` | Keyword search across the live site (Home, About, CV) |

Plus two resources: `nik://site` (full site as markdown) and `nik://map` (the `llms.txt`).

## Run

```bash
python3 server.py
```

It speaks JSON-RPC 2.0 over stdio. Point any MCP client at it.

## Remote (hosted) — no clone needed

There's also a Cloudflare Worker (`worker.js`) exposing the same tools over **Streamable HTTP**, so clients can connect to a URL instead of running the script. Once deployed it lives at:

```
https://mcp.nikdumroese.com
```

Connect from an MCP client that supports HTTP transport (point it at that URL), or poke it by hand:

```bash
curl -s https://mcp.nikdumroese.com -X POST -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"about","arguments":{}}}'
```

### Deploy it yourself

```bash
npx wrangler login          # or: export CLOUDFLARE_API_TOKEN=...
npx wrangler deploy         # ships to *.workers.dev
```

Then attach the custom domain by uncommenting the `routes` block in `wrangler.toml` (the `nikdumroese.com` zone must be on the same Cloudflare account) and running `npx wrangler deploy` again.

### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "nikdumroese": {
      "command": "python3",
      "args": ["/absolute/path/to/nikdumroese-mcp/server.py"]
    }
  }
}
```

Restart Claude Desktop, then ask: *"Is Nik available? What's the GTM engine project?"*

### Quick manual test

```bash
printf '%s\n' \
'{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}}' \
'{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"about","arguments":{}}}' \
| python3 server.py
```

## Why

The site is built to be legible to agents — static HTML, content in the DOM, `llms.txt`, structured data. An MCP server is the logical last step: not just readable, but *queryable*. It's the same thing Nik builds for a living, pointed at himself.

## License

MIT
