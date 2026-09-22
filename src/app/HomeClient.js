"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import {
  Search,
  ScrollText,
  Sparkles,
  ChevronRight,
  Loader2,
} from "lucide-react";

const ERAS = [
  "Apostolic",
  "Ante-Nicene",
  "Nicene",
  "Post-Nicene",
  "Byzantine",
];

const QUICK_QUESTIONS = [
  "Did the early church pray for the dead?",
  "What did the Fathers say about icons?",
  "Is baptism necessary for salvation?",
  "How did the Fathers understand apostolic succession?",
];

export default function HomeClient({ fathers }) {
  const router = useRouter();
  const [activeEra, setActiveEra] = useState(null);
  const [heroQuery, setHeroQuery] = useState("");
  const [isSearching, setIsSearching] = useState(false);
  const [searchError, setSearchError] = useState(null);
  const [debugMode, setDebugMode] = useState(false);
  const [debugResults, setDebugResults] = useState(null);

  const shownFathers = activeEra
    ? fathers.filter((father) => father.era === activeEra)
    : fathers;

  // Debug-only: fetches the ranked list and shows it inline with scores,
  // instead of sending the user to the results page.
  const runDebugSearch = async (query) => {
    setIsSearching(true);
    setSearchError(null);
    setDebugResults(null);

    try {
      const res = await fetch("/api/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const data = await res.json();

      if (!res.ok || !data.results?.length) {
        setSearchError("No matching passage found — try rephrasing.");
        return;
      }

      setDebugResults(data.results);
    } catch (err) {
      console.error(err);
      setSearchError("Search failed. Try again.");
    } finally {
      setIsSearching(false);
    }
  };

  const runSearch = (query) => {
    if (debugMode) {
      runDebugSearch(query);
    } else {
      router.push(`/search?q=${encodeURIComponent(query)}`);
    }
  };

  const handleHeroSearch = (e) => {
    e.preventDefault();
    if (!heroQuery.trim() || isSearching) return;
    runSearch(heroQuery.trim());
  };

  return (
    <main className="af-root">

      {/* Hero */}
      <div className="af-hero">

        <div className="absolute inset-0 motion-safe:md:bg-fixed">
          <Image
            src="/images/hero-library.jpg"
            alt="A candlelit study lined with old books, a fire in the hearth"
            fill
            priority
            sizes="100vw"
            className="object-cover"
          />
        </div>

        {/* Oxblood gradient so the title below stays readable */}
        <div className="af-hero-gradient" />

        {/* Overlay content — sits above the image + gradient in stacking order */}
        <div className="af-hero-content">

          <h1 className="af-display af-text-parchment text-4xl md:text-6xl italic font-semibold leading-tight mb-6">
            Ad Fontes
          </h1>

          <form
            onSubmit={handleHeroSearch}
            className="af-hero-search"
          >
            {isSearching ? (
              <Loader2
                size={16}
                color="var(--gold)"
                className="shrink-0 animate-spin"
              />
            ) : (
              <Search size={16} color="var(--gold)" className="shrink-0" />
            )}

            <input
              type="text"
              value={heroQuery}
              onChange={(e) => setHeroQuery(e.target.value)}
              placeholder="Ask the Fathers a question…"
              disabled={isSearching}
              className="af-mono flex-1 bg-transparent outline-none text-sm italic disabled:opacity-60"
            />
          </form>

          {searchError && (
            <div className="af-mono af-search-error text-xs mt-2">
              {searchError}
            </div>
          )}

          {/* Dev-only debug toggle — shows ranked results with similarity
              scores inline instead of going to the results page. Remove
              before Phase 5 polish. */}
          <label className="af-mono af-debug-toggle text-xs mt-3">
            <input
              type="checkbox"
              checked={debugMode}
              onChange={(e) => {
                setDebugMode(e.target.checked);
                setDebugResults(null);
              }}
            />
            Debug: show ranked results
          </label>

          <div className="af-mono af-text-gold text-xs mt-4">
            ANF / NPNF · 38 VOLUMES · RETRIEVAL ONLY
          </div>

        </div>

        {/* Scroll down prompt */}
        <div className="af-scroll-cue absolute bottom-8 left-1/2 -translate-x-1/2">
          <span className="label">Scroll</span>
          <div className="line" />
        </div>

      </div>

      {/* Debug ranked results panel */}
      {debugResults && (
        <div className="px-8 md:px-16 py-10 max-w-4xl mx-auto">
          <div className="af-mono af-text-gold text-xs mb-4">
            Ranked results ({debugResults.length}) — deduped
          </div>

          <div className="flex flex-col gap-3">
            {debugResults.map((result, index) => (
              <Link
                key={result.id}
                href={`/works/${result.work_id}?chunk=${result.chunk_index}`}
                className="af-debug-result"
              >
                <div className="flex items-center justify-between mb-2">
                  <span className="af-mono af-text-gold text-xs">
                    #{index + 1} · work {result.work_id} · chunk{" "}
                    {result.chunk_index}
                  </span>
                  <span className="af-mono af-debug-score">
                    {(result.similarity * 100).toFixed(1)}%
                  </span>
                </div>

                {result.citation && (
                  <div className="af-mono text-xs opacity-70 mb-2">
                    {result.citation}
                  </div>
                )}

                <p className="text-sm leading-relaxed opacity-90">
                  {result.chunk_text}
                </p>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Landing Page */}
      <div className="px-8 md:px-16 py-16 max-w-4xl mx-auto">

        {/* Description */}
        <p className="af-text-parchment text-lg leading-relaxed mb-8 max-w-2xl">
          Ask a question in plain language. Read what the early Church
          Fathers actually wrote in answer — never a generated summary,
          only the passage itself, cited and linked to its source.
        </p>

        {/* Try Asking */}
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={13} color="var(--gold)" />

          <span className="af-mono af-text-gold text-xs">
            Try asking
          </span>
        </div>

        <div className="flex flex-wrap gap-2 mb-14">
          {QUICK_QUESTIONS.map((question) => (
            <button
              type="button"
              key={question}
              className="af-chip"
              disabled={isSearching}
              onClick={() => runSearch(question)}
            >
              {question}
            </button>
          ))}
        </div>

        {/* Browse by Era */}
        <div className="af-mono af-text-gold text-xs mb-5">
          Browse by Era
        </div>

        <div className="af-era-rail mb-2 relative">

          {ERAS.map((era, index) => (
            <React.Fragment key={era}>

              <button
                type="button"
                className={`af-era-stop ${
                  activeEra === era ? "active" : ""
                }`}
                onClick={() =>
                  setActiveEra(
                    activeEra === era ? null : era
                  )
                }
              >
                <div className="dot" />

                <label>{era}</label>
              </button>

              {index < ERAS.length - 1 && (
                <div className="af-era-track" />
              )}

            </React.Fragment>
          ))}

        </div>

        <div className="af-rule my-10" />

        {/* Fathers */}
        <div className="flex items-center justify-between mb-5">

          <span className="af-mono af-text-gold text-xs">
            {activeEra
              ? `${activeEra} Fathers`
              : "All Fathers"}
          </span>

          {activeEra && (
            <button
              type="button"
              className="af-clear-filter"
              onClick={() => setActiveEra(null)}
            >
              clear filter ×
            </button>
          )}

        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mb-14">

          {shownFathers.map((father) => (
            <button
              type="button"
              key={father.name}
              className="af-father-seal-card"
              onClick={() => router.push(`/fathers/${father.slug}`)}
            >

              <div className="af-father-seal">
                {father.name.charAt(0)}
              </div>

              <div className="flex-1 text-left">

                <div className="name">
                  {father.name}
                </div>

                <div className="meta">
                  {father.era} · {father.works} works indexed
                </div>

              </div>

              <ChevronRight
                size={16}
                color="var(--parchment-dim)"
              />

            </button>
          ))}

        </div>

        <div className="af-rule mb-8" />

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">

          <div className="af-feature-row">

            <ScrollText
              size={16}
              color="var(--gold)"
            />

            <div>

              <div className="af-display af-text-gold-bright text-base italic">
                Pure retrieval
              </div>

              <div className="af-text-parchment-dim text-sm">
                No generated answers, ever.
              </div>

            </div>

          </div>

          <div className="af-feature-row">

            <Search
              size={16}
              color="var(--gold)"
            />

            <div>

              <div className="af-display af-text-gold-bright text-base italic">
                Semantic search
              </div>

              <div className="af-text-parchment-dim text-sm">
                Matching by meaning, not keyword.
              </div>

            </div>

          </div>

        </div>

      </div>

      {/* Footer */}
      <div className="af-rule mt-16" />

      <div className="af-mono af-text-parchment-dim text-[10px] text-center py-6">
        AD FONTES — PRIMARY SOURCE INDEX
      </div>

    </main>
  );
}