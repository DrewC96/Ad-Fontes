import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

const GEMINI_EMBEDDING_MODEL = "gemini-embedding-001";
const OUTPUT_DIMENSIONALITY = 768;

export async function POST(request) {
  const { query } = await request.json();

  if (!query || !query.trim()) {
    return Response.json({ error: "Empty query" }, { status: 400 });
  }

  const embedRes = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_EMBEDDING_MODEL}:embedContent?key=${process.env.GEMINI_API_KEY}`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        content: { parts: [{ text: query }] },
        taskType: "RETRIEVAL_QUERY",
        outputDimensionality: OUTPUT_DIMENSIONALITY,
      }),
    }
  );

  if (!embedRes.ok) {
    console.error("Gemini embed error:", await embedRes.text());
    return Response.json({ error: "Embedding failed" }, { status: 502 });
  }

  const embedData = await embedRes.json();
  const queryEmbedding = embedData.embedding?.values;

  if (!queryEmbedding) {
    return Response.json({ error: "No embedding returned" }, { status: 502 });
  }

  const { data, error } = await supabase.rpc("match_passages", {
    query_embedding: queryEmbedding,
    match_count: 5,
  });

  if (error) {
    console.error("Supabase match_passages error:", error);
    return Response.json({ error: "Search failed" }, { status: 500 });
  }

  return Response.json({ results: data ?? [] });
}