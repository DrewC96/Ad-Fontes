import { createClient } from "@supabase/supabase-js";
import { GoogleGenAI } from "@google/genai";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

const GEMINI_EMBEDDING_MODEL = "gemini-embedding-001";
const OUTPUT_DIMENSIONALITY = 768;

// Passages from the same work whose chunk_index falls within this many
// chunks of an already-kept result are treated as the same underlying
// passage. Tuned against Confessions IX, where one continuous meditation
// on Monica spanned chunks 241 and 253-256 — a 15-chunk range collapsed
// to one result with this window.
const DEDUPE_WINDOW = 5;

export async function embedQuery(query) {
  const embedResponse = await ai.models.embedContent({
    model: GEMINI_EMBEDDING_MODEL,
    contents: query,
    config: {
      taskType: "RETRIEVAL_QUERY",
      outputDimensionality: OUTPUT_DIMENSIONALITY,
    },
  });

  return embedResponse.embeddings[0].values;
}

// Results must already be sorted by similarity descending (match_passages
// returns them that way), so the first result encountered in each
// neighborhood is the strongest one, and later, weaker duplicates from
// the same work are dropped.
export function dedupeResults(results, windowSize = DEDUPE_WINDOW) {
  const kept = [];

  for (const result of results) {
    const isDuplicate = kept.some(
      (existing) =>
        existing.work_id === result.work_id &&
        Math.abs(existing.chunk_index - result.chunk_index) <= windowSize
    );

    if (!isDuplicate) {
      kept.push(result);
    }
  }

  return kept;
}

// rawMatchCount is deliberately larger than what callers actually show —
// dedup can collapse several raw hits into one, so we over-fetch to make
// sure there's still a full page of distinct results left afterward.
export async function searchPassages(query, { rawMatchCount = 25 } = {}) {
  const queryEmbedding = await embedQuery(query);

  const { data, error } = await supabase.rpc("match_passages", {
    query_embedding: queryEmbedding,
    match_count: rawMatchCount,
  });

  if (error) {
    throw new Error(`match_passages error: ${error.message}`);
  }

  return dedupeResults(data ?? []);
}
