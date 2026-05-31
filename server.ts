// Vault AI Backend - Deno Deploy
import { serve } from "https://deno.land/std@0.168.0/http/server.ts";

const cors = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

const sessions = new Map();

serve(async (req) => {
  if (req.method === "OPTIONS") {
    return new Response(null, { headers: cors });
  }

  try {
    const { messages, session_id } = await req.json();
    
    if (!sessions.has(session_id)) {
      sessions.set(session_id, { messages: [], lastActive: Date.now() });
    }
    
    const session = sessions.get(session_id);
    session.lastActive = Date.now();
    session.messages = messages.slice(-10);
    
    const content = messages[messages.length - 1]?.content || "";
    const isUrl = /https?:\/\/[\S]+/i.test(content) || /jpg|jpeg|png|gif|video|mp4|youtu/i.test(content);
    
    let response = isUrl ? await callClaude(content) : await callGemini(content, session.messages);
    
    for (const [k, v] of sessions.entries()) {
      if (Date.now() - v.lastActive > 3600000) sessions.delete(k);
    }
    
    return new Response(
      JSON.stringify({ response }),
      { headers: { ...cors, "Content-Type": "application/json" } }
    );
  } catch {
    return new Response(
      JSON.stringify({ error: "Failed to process request" }),
      { headers: { ...cors, "Content-Type": "application/json" }, status: 500 }
    );
  }
});

async function callClaude(content) {
  const key = Deno.env.get("ANTHROPIC_API_KEY");
  if (!key) return demoResponse(content);
  
  try {
    const response = await fetch("https://api.anthropic.com/v1/messages", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": key,
        "anthropic-version": "2023-06-01",
        "anthropic-dangerous-direct-browser-access": "true"
      },
      body: JSON.stringify({
        model: "claude-3-haiku-20240307",
        max_tokens: 500,
        messages: [{ role: "user", content: "Vault AI here. User shared: " + content }]
      })
    });
    const data = await response.json();
    return data.content?.[0]?.text || demoResponse(content);
  } catch {
    return demoResponse(content);
  }
}

async function callGemini(content, _history) {
  const key = Deno.env.get("GOOGLE_API_KEY");
  if (!key) return demoResponse(content);
  
  try {
    const response = await fetch(
      "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + key,
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          contents: [{ parts: [{ text: "Vault AI for Legacy Vault. User said: " + content }] }],
          generationConfig: { maxOutputTokens: 500 }
        })
      }
    );
    const data = await response.json();
    return data.candidates?.[0]?.content?.parts?.[0]?.text || demoResponse(content);
  } catch {
    return demoResponse(content);
  }
}

function demoResponse(content) {
  const lower = content.toLowerCase();
  
  if (lower.includes("licensing") || lower.includes("music")) {
    return "Modular asset layers handle licensing. Expired music replaced, jerseys as packs, likenesses via overlays.";
  }
  if (lower.includes("pilot") || lower.includes("throwback")) {
    return "48-hour NBA 2K16 Throwback Weekend. Budget under $750K. Target: 15-20% DAU uplift.";
  }
  if (lower.includes("scal") || lower.includes("kubernetes")) {
    return "Kubernetes = automatic scaling. Build once, run anywhere. Each title in isolated container.";
  }
  if (lower.includes("vault") || lower.includes("legacy")) {
    return "Legacy Vault = game-within-a-game. Launch 2K15-2K20 inside modern 2K. No more sunsets!";
  }
  return "I'm Vault AI! Ask about the Legacy Vault campaign.";
}
