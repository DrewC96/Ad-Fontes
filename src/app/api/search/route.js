import { NextResponse } from "next/server";
import { createClient } from "@supabase/supabase-js";
import { GoogleGenAI } from "@google/genai";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

const ai = new GoogleGenAI({ apiKey: process.env.GEMINI_API_KEY });

export async function POST(request) {
  try {
    const { query } = await request.json();

    if (!query || typeof query !== "string" || !query.trim()) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    // RETRIEVAL_QUERY (not RETRIEVAL_DOCUMENT, which is what the ingestion
    // pipeline used) - Gemini's embedding model treats these differently
    // for better retrieval quality when a short question is being matched
    // against longer indexed passages.
    const embedResponse = await ai.models.embedContent({
      model: "gemini-embedding-001",
      contents: query,
      config: {
        taskType: "RETRIEVAL_QUERY",
        outputDimensionality: 768,
      },
    });

    const queryEmbedding = embedResponse.embeddings[0].values;

    const { data, error } = await supabase.rpc("search_passages", {
      query_embedding: queryEmbedding,
      match_count: 10,
    });

    if (error) {
      console.error("Supabase search error:", error);
      return NextResponse.json({ error: "Search failed" }, { status: 500 });
    }

    return NextResponse.json({ results: data });
  } catch (err) {
    console.error("Search API error:", err);
    return NextResponse.json({ error: "Something went wrong" }, { status: 500 });
  }
}
