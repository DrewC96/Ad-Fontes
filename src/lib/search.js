import { createClient } from "@supabase/supabase-js";
import { GoogleGenAI } from "@google/genai";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

const GEMINI_EMBEDDING_MODEL = "gemini-embedding-001";
const OUTPUT_DIMENSIONALITY = 768;

// Longer queries are truncated before embedding so nobody can burn quota
// by submitting huge strings.
const MAX_QUERY_LENGTH = 300;

// Passages from the same work whose chunk_index falls within this many
// chunks of an already-kept result are treated as the same underlying
// passage. Tuned against Confessions IX, where one continuous meditation
// on Monica spanned chunks 241 and 253-256 — a 15-chunk range collapsed
// to one result with this window.
const DEDUPE_WINDOW = 5;

// Thrown when Gemini returns HTTP 429 so the UI can show a "busy" message
// instead of a generic failure.
export class SearchRateLimitError extends Error {
  constructor() {
    super("Embedding rate limit reached");
    this.name = "SearchRateLimitError";
  }
}

// Created on first use so a missing key gives a clear error at search time
// instead of breaking module import.
let aiClient = null;
function getAi() {
  if (!process.env.GEMINI_API_KEY) {
    throw new Error(
      "Missing GEMINI_API_KEY. Copy .env.example to .env.local and add your key."
    );
  }
  aiClient ??= new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });
  return aiClient;
}

// Small in-memory LRU cache of query embeddings. Best-effort only: each
// serverless instance has its own copy, but repeated searches (refreshes,
// shared links) usually land on a warm instance and skip the Gemini call.
const EMBEDDING_CACHE_MAX = 200;
const embeddingCache = new Map();

export async function embedQuery(query) {
  const text = (query ?? "").trim().slice(0, MAX_QUERY_LENGTH);
  if (!text) {
    throw new Error("Empty search query");
  }

  const cached = embeddingCache.get(text);
  if (cached) {
    // Re-insert to mark as most recently used.
    embeddingCache.delete(text);
    embeddingCache.set(text, cached);
    return cached;
  }

  let values;
  try {
    const embedResponse = await getAi().models.embedContent({
      model: GEMINI_EMBEDDING_MODEL,
      contents: text,
      config: {
        taskType: "RETRIEVAL_QUERY",
        outputDimensionality: OUTPUT_DIMENSIONALITY,
      },
    });
    values = embedResponse.embeddings[0].values;
  } catch (err) {
    if (err?.status === 429) {
      throw new SearchRateLimitError();
    }
    throw err;
  }

  embeddingCache.set(text, values);
  if (embeddingCache.size > EMBEDDING_CACHE_MAX) {
    // Map iterates in insertion order, so the first key is the oldest.
    embeddingCache.delete(embeddingCache.keys().next().value);
  }

  return values;
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