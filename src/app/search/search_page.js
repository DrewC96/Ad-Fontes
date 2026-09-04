"use client";

import { Suspense, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Search, ArrowLeft } from "lucide-react";
import Link from "next/link";

function SearchInner() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get("q") || "";

  const [query, setQuery] = useState(initialQuery);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searched, setSearched] = useState(false);

  async function runSearch(q) {
    if (!q.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: q }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || "Search failed");
      setResults(data.results || []);
      setSearched(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (initialQuery) runSearch(initialQuery);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleSubmit(e) {
    e.preventDefault();
    runSearch(query);
  }

  return (
    <main className="af-root">
      <div className="px-8 md:px-16 py-16 max-w-3xl mx-auto">

        <Link
          href="/"
          className="af-mono text-xs inline-flex items-center gap-2 mb-10"
          style={{ color: "var(--gold)" }}
        >
          <ArrowLeft size={12} />
          Back to Ad Fontes
        </Link>

        <form
          onSubmit={handleSubmit}
          className="af-header-search mb-10"
          style={{ maxWidth: "100%", cursor: "text" }}
        >
          <Search size={14} color="var(--gold)" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask a question of the Fathers…"
            style={{
              background: "transparent",
              border: "none",
              outline: "none",
              color: "var(--parchment)",
              fontFamily: "'Crimson Pro', serif",
              fontStyle: "italic",
              fontSize: "14px",
              width: "100%",
            }}
          />
        </form>

        {loading && (
          <p className="af-mono text-xs" style={{ color: "var(--parchment-dim)" }}>
            Searching the corpus…
          </p>
        )}

        {error && (
          <p className="af-mono text-xs" style={{ color: "var(--oxblood-bright)" }}>
            {error}
          </p>
        )}

        {!loading && searched && results.length === 0 && !error && (
          <p style={{ color: "var(--parchment-dim)" }}>
            No passages found. Try rephrasing your question.
          </p>
        )}

        {results.length > 0 && (
          <div className="af-mono text-xs mb-6" style={{ color: "var(--gold)" }}>
            {results.length} PASSAGES FOUND
          </div>
        )}

        {results.map((r) => (
          <div key={r.passage_id} className="af-fragment">

            <div
              className="af-mono text-[10px] mb-3 flex items-center justify-between flex-wrap gap-2"
              style={{ color: "var(--scroll-ink)", opacity: 0.65 }}
            >
              <span>{r.author_name} · {r.work_title}</span>
              <span>{r.citation}</span>
            </div>

            <p
              className="leading-relaxed mb-3"
              style={{ fontFamily: "'Crimson Pro', serif", fontSize: "16px" }}
            >
              {r.chunk_text}
            </p>

            <div className="flex items-center justify-between">
              <span
                className="af-mono text-[10px]"
                style={{ color: "var(--scroll-ink)", opacity: 0.5 }}
              >
                {r.era_name}
              </span>
            </div>

          </div>
        ))}

      </div>
    </main>
  );
}

// useSearchParams requires a Suspense boundary in the App Router
export default function SearchPage() {
  return (
    <Suspense fallback={null}>
      <SearchInner />
    </Suspense>
  );
}
