/**
 * nikdumroese-mcp — remote MCP server on Cloudflare Workers.
 * Streamable HTTP transport (JSON-RPC 2.0 over POST). No dependencies.
 * Mirrors server.py so local (stdio) and remote (HTTP) behave the same.
 */

const SITE = "https://nikdumroese.com";
const VERSION = "1.0.0";
const DEFAULT_PROTOCOL = "2025-06-18";

const ABOUT =
  "Nik (Niklaas) Dumroese builds and ships agentic go-to-market systems: multi-agent infrastructure, growth engineering, and the GTM data underneath. From a tiny town in Idaho, now building in Germany. He started in performance marketing for the measurability and worked his way to performance of GTM. Through-line: don't take a reported number on faith — build the system that produces an honest one.";
const AVAILABILITY =
  "Open to new work from September 2026. Focus: agentic GTM systems, growth engineering, GTM data.";
const CONTACT = {
  email: "hello@nikdumroese.com",
  site: "https://nikdumroese.com",
  linkedin: "https://linkedin.com/in/nikdumroese",
  github: "https://github.com/nikdumroese",
};

const PROJECTS = [
  { id: "gtm-engine", name: "A proactive GTM engine, built end-to-end", summary: "Turned a 100% inbound motion into a signal-driven outbound engine.", scope: "Signal pipeline -> enrichment -> ICP + signal scoring -> branched outreach -> eval loop", stack: "Python, dbt, Clay, LLM copy layer, CRM automation, GitHub/PyPI/Docker APIs", outcome: "Shipped as a live app + runnable scoring model. Every number from a real public API. ~14x directional year-one ROI; <5% of sends need human review." },
  { id: "agentic", name: "Production multi-agent marketing system", summary: "24/7 agentic infrastructure for a 30+ person marketing team.", scope: "Orchestrator agents coordinating subagents; content, reporting, data refresh, knowledge upkeep", stack: "Claude / Claude Code, MCP (Canva, Linear, Miro), RAG, vector search, evals", outcome: "Self-improving loops, RAG memory over a ~1,000-doc vector-indexed wiki, eval frameworks with regression tracking. Ran without manual triggers." },
  { id: "incrementality", name: "Incrementality testing framework", summary: "From-scratch causal measurement so spend followed proven lift.", scope: "Lift experiments separating causal impact from correlation", stack: "Python, ads-platform APIs, SQL, geo-experiments", outcome: "~15% CAC improvement; set the experimentation culture behind later agent-driven testing." },
  { id: "data-infra", name: "GTM data infrastructure & conversion tracking", summary: "The clean data foundation the agentic layer runs on.", scope: "CDP ownership, server-side events, lifecycle tracking", stack: "Segment CDP, CAPI, GTM, lifecycle-stage events, GDPR-compliant pipelines", outcome: "~7% CVR improvement, 2M EUR+ ARR uplift contribution, ~10% more open pipeline." },
];

const REPOS = [
  { name: "plain-language-skill", desc: "Agent skill for ISO 24495 plain-language writing.", url: "https://github.com/nikdumroese/plain-language-skill" },
  { name: "audit-swarm", desc: "Multi-agent swarm to audit code, verify research, or stress-test a plan.", url: "https://github.com/nikdumroese/audit-swarm" },
  { name: "crm-refine", desc: "Streaming CRM dedupe and field standardisation, dependency-free.", url: "https://github.com/nikdumroese/crm-refine" },
  { name: "knowledge-base-ops", desc: "Token-efficient persistent knowledge base for LLMs over large corpora.", url: "https://github.com/nikdumroese/knowledge-base-ops" },
  { name: "context-engineering", desc: "Patterns for token-efficient CLAUDE.md files and layered agent context.", url: "https://github.com/nikdumroese/context-engineering" },
  { name: "agent-skills", desc: "Harness-agnostic collection of skills, commands, and eval patterns.", url: "https://github.com/nikdumroese/agent-skills" },
  { name: "minto-pyramid", desc: "Restructure and pressure-test writing with the Pyramid Principle.", url: "https://github.com/nikdumroese/minto-pyramid" },
];

const TOOLS = [
  { name: "about", description: "Who is Nik Dumroese — background and how he works.", inputSchema: { type: "object", properties: {} } },
  { name: "availability", description: "Is Nik available for work, and for what.", inputSchema: { type: "object", properties: {} } },
  { name: "list_projects", description: "List Nik's selected work (case studies) with one-line summaries.", inputSchema: { type: "object", properties: {} } },
  { name: "get_project", description: "Full detail of one project: scope, stack, and outcome.", inputSchema: { type: "object", properties: { id: { type: "string", enum: PROJECTS.map((p) => p.id) } }, required: ["id"] } },
  { name: "list_open_source", description: "Nik's open-source tools and agent skills.", inputSchema: { type: "object", properties: {} } },
  { name: "contact", description: "How to reach Nik.", inputSchema: { type: "object", properties: {} } },
  { name: "search", description: "Keyword search across the live site content (Home, About, CV).", inputSchema: { type: "object", properties: { query: { type: "string", description: "Words or phrase to find." } }, required: ["query"] } },
];

const RESOURCES = [
  { uri: "nik://site", name: "Full site (markdown)", description: "Every page of nikdumroese.com as clean markdown.", mimeType: "text/markdown" },
  { uri: "nik://map", name: "Site map for LLMs", description: "The llms.txt summary of the site.", mimeType: "text/markdown" },
];

async function fetchText(path) {
  try {
    const r = await fetch(SITE + path, { headers: { "User-Agent": "nikdumroese-mcp/1.0" } });
    return r.ok ? await r.text() : null;
  } catch {
    return null;
  }
}

async function callTool(name, args) {
  args = args || {};
  switch (name) {
    case "about": return ABOUT;
    case "availability": return AVAILABILITY;
    case "list_projects": return PROJECTS.map((p) => `- ${p.id}: ${p.name} — ${p.summary}`).join("\n");
    case "get_project": {
      const p = PROJECTS.find((x) => x.id === args.id);
      if (!p) return `Unknown project '${args.id}'. Try one of: ${PROJECTS.map((x) => x.id).join(", ")}.`;
      return `${p.name}\n\nScope: ${p.scope}\nStack: ${p.stack}\n\nOutcome: ${p.outcome}`;
    }
    case "list_open_source": return REPOS.map((r) => `- ${r.name}: ${r.desc} (${r.url})`).join("\n");
    case "contact": return Object.entries(CONTACT).map(([k, v]) => `${k}: ${v}`).join("\n");
    case "search": {
      const q = (args.query || "").trim();
      if (!q) return "Provide a query.";
      const doc = (await fetchText("/llms-full.txt")) || "";
      if (!doc) return "Could not fetch site content right now.";
      const hits = [];
      const ql = q.toLowerCase();
      for (const line of doc.split("\n")) {
        if (line.trim() && line.toLowerCase().includes(ql)) hits.push(line.trim());
        if (hits.length >= 8) break;
      }
      return hits.length ? `Matches for '${q}':\n\n` + hits.map((h) => `- ${h}`).join("\n") : `No matches for '${q}'.`;
    }
    default: throw new Error(`Unknown tool: ${name}`);
  }
}

async function readResource(uri) {
  if (uri === "nik://site") return (await fetchText("/llms-full.txt")) || "(offline)";
  if (uri === "nik://map") return (await fetchText("/llms.txt")) || "(offline)";
  return `Unknown resource: ${uri}`;
}

async function handleRpc(msg) {
  const { method, id, params } = msg;
  const ok = (result) => ({ jsonrpc: "2.0", id, result });
  switch (method) {
    case "initialize":
      return ok({
        protocolVersion: (params && params.protocolVersion) || DEFAULT_PROTOCOL,
        capabilities: { tools: {}, resources: {} },
        serverInfo: { name: "nikdumroese-mcp", version: VERSION },
        instructions: "Query Nik Dumroese's site: about, availability, list_projects, get_project, list_open_source, contact, search.",
      });
    case "tools/list": return ok({ tools: TOOLS });
    case "tools/call":
      try {
        const text = await callTool(params.name, params.arguments);
        return ok({ content: [{ type: "text", text }] });
      } catch (e) {
        return ok({ content: [{ type: "text", text: `error: ${e.message}` }], isError: true });
      }
    case "resources/list": return ok({ resources: RESOURCES });
    case "resources/read":
      return ok({ contents: [{ uri: params.uri, mimeType: "text/markdown", text: await readResource(params.uri) }] });
    case "ping": return ok({});
    case "prompts/list": return ok({ prompts: [] });
    case "resources/templates/list": return ok({ resourceTemplates: [] });
    default:
      if (id === undefined || id === null) return null; // notification
      return { jsonrpc: "2.0", id, error: { code: -32601, message: `method not found: ${method}` } };
  }
}

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Mcp-Session-Id, Mcp-Protocol-Version",
};

export default {
  async fetch(request) {
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });

    if (request.method === "GET") {
      return new Response(
        JSON.stringify({ name: "nikdumroese-mcp", version: VERSION, transport: "streamable-http", note: "POST JSON-RPC 2.0 here. See github.com/nikdumroese/nikdumroese-mcp" }, null, 2),
        { headers: { "Content-Type": "application/json", ...CORS } }
      );
    }

    if (request.method === "POST") {
      let body;
      try { body = await request.json(); } catch { return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "parse error" } }); }
      if (Array.isArray(body)) {
        const out = (await Promise.all(body.map(handleRpc))).filter(Boolean);
        return json(out);
      }
      const res = await handleRpc(body);
      return res ? json(res) : new Response(null, { status: 202, headers: CORS });
    }

    return new Response("Method not allowed", { status: 405, headers: CORS });
  },
};

function json(obj) {
  return new Response(JSON.stringify(obj), { headers: { "Content-Type": "application/json", ...CORS } });
}
