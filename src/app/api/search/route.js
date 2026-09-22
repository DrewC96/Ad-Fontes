import { NextResponse } from "next/server";
import { searchPassages } from "../../../lib/search";

export async function POST(request) {
  try {
    const { query } = await request.json();

    if (!query || typeof query !== "string" || !query.trim()) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    const results = await searchPassages(query, { rawMatchCount: 25 });

    return NextResponse.json({ results });
  } catch (err) {
    console.error("Search API error:", err);
    return NextResponse.json({ error: "Something went wrong" }, { status: 500 });
  }
}
