#!/usr/bin/env python3
"""
nikdumroese-mcp — a tiny, dependency-free MCP server for nikdumroese.com.

Proof of concept: an AI agent can connect over the Model Context Protocol and
query the site — who Nik is, what he's built, whether he's available, and how to
reach him. Stdlib only. No pip install. Newline-delimited JSON-RPC 2.0 over stdio.

Run:   python3 server.py
Wire into Claude Desktop / any MCP client — see README.md.
"""
import sys
import json
import urllib.request

SITE = "https://nikdumroese.com"
DEFAULT_PROTOCOL = "2025-06-18"
VERSION = "1.0.0"

ABOUT = (
    "Nik (Niklaas) Dumroese is a marketing AI engineer. He builds the measurement "
    "models, data pipelines and agents that marketing and GTM teams run on. From a "
    "small town in Idaho, now based in Germany. He started in performance marketing "
    "because it could be measured, and moved into building GTM systems. Across his "
    "work, he builds the system that produces a number he can check instead of "
    "trusting a reported one."
)

AVAILABILITY = "Available immediately. Open to marketing AI engineering roles; also growth engineering and GTM data work."

CONTACT = {
    "email": "hello@nikdumroese.com",
    "site": "https://nikdumroese.com",
    "linkedin": "https://linkedin.com/in/nikdumroese",
    "github": "https://github.com/nikdumroese",
}

PROJECTS = [
    {
        "id": "gtm-engine",
        "name": "A proactive GTM engine, built end-to-end",
        "summary": "Turned a 100% inbound motion into a signal-driven outbound engine.",
        "scope": "Signal pipeline -> enrichment -> ICP + signal scoring -> branched outreach -> eval loop",
        "stack": "Python, dbt, Clay, LLM copy layer, CRM automation, GitHub/PyPI/Docker APIs",
        "outcome": "Shipped as a live app + runnable scoring model. Every number from a real public API. ~14x modelled year-one ROI; <5% of sends need human review.",
    },
    {
        "id": "agentic",
        "name": "Production multi-agent marketing system",
        "summary": "24/7 agentic infrastructure for a 30+ person marketing team.",
        "scope": "Orchestrator agents coordinating subagents; content, reporting, data refresh, knowledge upkeep",
        "stack": "Claude / Claude Code, MCP (Canva, Linear, Miro), RAG, vector search, evals",
        "outcome": "Self-improving loops, RAG memory over a ~1,000-doc vector-indexed wiki, eval frameworks with regression tracking. Ran without manual triggers.",
    },
    {
        "id": "agent-swarm",
        "name": "Decentralized multi-agent swarm, no orchestrator",
        "summary": "Tests whether agents can coordinate with no single agent or human ever picking the next move.",
        "scope": "Holacracy-inspired framework, no central orchestrator, reusable across use cases",
        "stack": "LangGraph (StateGraph, Send fan-out), Claude Code CLI (headless), JSON Schema, Python",
        "outcome": "Independent roles coordinate via file-based mailboxes; a proposal integrates only once every other role has had a turn to object, computed from an append-only audit log, never decided by an LLM or human. Applied to a real live job search with a dedicated fact-checking role enforcing a hard no-fabrication rule; found 3 real permission-model bugs via direct CLI testing.",
    },
    {
        "id": "incrementality",
        "name": "Incrementality testing framework",
        "summary": "From-scratch causal measurement so spend followed proven lift.",
        "scope": "Lift experiments separating causal impact from correlation",
        "stack": "Python, ads-platform APIs, SQL, geo-experiments",
        "outcome": "~15% CAC improvement.",
    },
    {
        "id": "data-infra",
        "name": "GTM data infrastructure & conversion tracking",
        "summary": "The clean data foundation the agentic layer runs on.",
        "scope": "CDP ownership, server-side events, lifecycle tracking",
        "stack": "Segment CDP, CAPI, GTM, lifecycle-stage events, GDPR-compliant pipelines",
        "outcome": "~7% CVR improvement, 2M EUR+ ARR uplift contribution, ~10% more open pipeline.",
    },
]

REPOS = [
    {"name": "plain-language-skill", "desc": "Agent skill for ISO 24495 plain-language writing.", "url": "https://github.com/nikdumroese/plain-language-skill"},
    {"name": "audit-swarm", "desc": "Multi-agent swarm to audit code, verify research, or stress-test a plan.", "url": "https://github.com/nikdumroese/audit-swarm"},
    {"name": "crm-refine", "desc": "Streaming CRM dedupe and field standardisation, dependency-free.", "url": "https://github.com/nikdumroese/crm-refine"},
    {"name": "knowledge-base-ops", "desc": "Token-efficient persistent knowledge base for LLMs over large corpora.", "url": "https://github.com/nikdumroese/knowledge-base-ops"},
    {"name": "context-engineering", "desc": "Patterns for token-efficient CLAUDE.md files and layered agent context.", "url": "https://github.com/nikdumroese/context-engineering"},
    {"name": "agent-skills", "desc": "Harness-agnostic collection of skills, commands, and eval patterns.", "url": "https://github.com/nikdumroese/agent-skills"},
    {"name": "minto-pyramid", "desc": "Restructure and pressure-test writing with the Pyramid Principle.", "url": "https://github.com/nikdumroese/minto-pyramid"},
]


def fetch(path, timeout=6):
    try:
        req = urllib.request.Request(SITE + path, headers={"User-Agent": "nikdumroese-mcp/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception:
        return None


TOOLS = [
    {"name": "about", "description": "Who is Nik Dumroese — background and how he works.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "availability", "description": "Is Nik available for work, and for what.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "list_projects", "description": "List Nik's selected work (case studies) with one-line summaries.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "get_project", "description": "Full detail of one project: scope, stack, and outcome.",
     "inputSchema": {"type": "object",
                     "properties": {"id": {"type": "string", "enum": [p["id"] for p in PROJECTS]}},
                     "required": ["id"]}},
    {"name": "list_open_source", "description": "Nik's open-source tools and agent skills.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "contact", "description": "How to reach Nik.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "search", "description": "Keyword search across the live site content (Home, About, CV).",
     "inputSchema": {"type": "object",
                     "properties": {"query": {"type": "string", "description": "Words or phrase to find."}},
                     "required": ["query"]}},
]


def tool_about(_):
    return ABOUT


def tool_availability(_):
    return AVAILABILITY


def tool_list_projects(_):
    return "\n".join(f"- {p['id']}: {p['name']} — {p['summary']}" for p in PROJECTS)


def tool_get_project(args):
    pid = (args or {}).get("id")
    p = next((x for x in PROJECTS if x["id"] == pid), None)
    if not p:
        ids = ", ".join(x["id"] for x in PROJECTS)
        return f"Unknown project '{pid}'. Try one of: {ids}."
    return (f"{p['name']}\n\nScope: {p['scope']}\nStack: {p['stack']}\n\nOutcome: {p['outcome']}")


def tool_list_open_source(_):
    return "\n".join(f"- {r['name']}: {r['desc']} ({r['url']})" for r in REPOS)


def tool_contact(_):
    return "\n".join(f"{k}: {v}" for k, v in CONTACT.items())


def tool_search(args):
    q = ((args or {}).get("query") or "").strip()
    if not q:
        return "Provide a query."
    doc = fetch("/llms-full.txt") or ""
    if not doc:
        return "Could not fetch site content right now."
    hits = []
    ql = q.lower()
    for para in doc.split("\n"):
        if ql in para.lower() and para.strip():
            hits.append(para.strip())
        if len(hits) >= 8:
            break
    if not hits:
        return f"No matches for '{q}'. The site covers agentic GTM systems, projects, open source, and contact."
    return f"Matches for '{q}':\n\n" + "\n".join(f"- {h}" for h in hits)


DISPATCH = {
    "about": tool_about,
    "availability": tool_availability,
    "list_projects": tool_list_projects,
    "get_project": tool_get_project,
    "list_open_source": tool_list_open_source,
    "contact": tool_contact,
    "search": tool_search,
}

RESOURCES = [
    {"uri": "nik://site", "name": "Full site (markdown)", "description": "Every page of nikdumroese.com as clean markdown.", "mimeType": "text/markdown"},
    {"uri": "nik://map", "name": "Site map for LLMs", "description": "The llms.txt summary of the site.", "mimeType": "text/markdown"},
]


def read_resource(uri):
    if uri == "nik://site":
        return fetch("/llms-full.txt") or "(offline)"
    if uri == "nik://map":
        return fetch("/llms.txt") or "(offline)"
    return f"Unknown resource: {uri}"


def send(obj):
    sys.stdout.write(json.dumps(obj) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except json.JSONDecodeError:
            continue
        method = msg.get("method")
        mid = msg.get("id")

        if method == "initialize":
            proto = (msg.get("params") or {}).get("protocolVersion", DEFAULT_PROTOCOL)
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "protocolVersion": proto,
                "capabilities": {"tools": {}, "resources": {}},
                "serverInfo": {"name": "nikdumroese-mcp", "version": VERSION},
                "instructions": "Query Nik Dumroese's site: about, availability, list_projects, get_project, list_open_source, contact, search.",
            }})
        elif method == "tools/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
        elif method == "tools/call":
            params = msg.get("params") or {}
            name = params.get("name")
            fn = DISPATCH.get(name)
            if not fn:
                send({"jsonrpc": "2.0", "id": mid, "result": {
                    "content": [{"type": "text", "text": f"Unknown tool: {name}"}], "isError": True}})
            else:
                try:
                    text = fn(params.get("arguments") or {})
                    send({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": text}]}})
                except Exception as e:  # noqa: BLE001
                    send({"jsonrpc": "2.0", "id": mid, "result": {
                        "content": [{"type": "text", "text": f"error: {e}"}], "isError": True}})
        elif method == "resources/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"resources": RESOURCES}})
        elif method == "resources/read":
            uri = (msg.get("params") or {}).get("uri")
            send({"jsonrpc": "2.0", "id": mid, "result": {
                "contents": [{"uri": uri, "mimeType": "text/markdown", "text": read_resource(uri)}]}})
        elif method == "ping":
            send({"jsonrpc": "2.0", "id": mid, "result": {}})
        elif method in ("prompts/list",):
            send({"jsonrpc": "2.0", "id": mid, "result": {"prompts": []}})
        elif method == "resources/templates/list":
            send({"jsonrpc": "2.0", "id": mid, "result": {"resourceTemplates": []}})
        elif method and method.startswith("notifications/"):
            pass  # notifications get no response
        else:
            if mid is not None:
                send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": f"method not found: {method}"}})


if __name__ == "__main__":
    try:
        main()
    except (BrokenPipeError, KeyboardInterrupt):
        pass
