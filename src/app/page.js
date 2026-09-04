"use client";

import React, { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import {
  Search,
  BookOpen,
  ScrollText,
  Sparkles,
  ChevronRight,
} from "lucide-react";

import { createClient } from '@supabase/supabase-js'

const supabase = createClient(process.env.NEXT_PUBLIC_SUPABASE_URL, process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY)

async function getFathers() {
  const { data, error } = await supabase
    .from('authors')
    .select(`
      name,
      slug,
      birth_year,
      death_year,
      eras ( name ),
      works ( count )
    `)
    .order('name')

  if (error) {
    console.error('Error fetching fathers:', error)
    return []
  }

  return data.map((row) => ({
    name: row.name,
    era: row.eras?.name ?? 'Unknown',
    works: row.works?.[0]?.count ?? 0,
  }))
}

const FATHERS = await getFathers();

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

export default function Home() {
  const router = useRouter();
  const [activeEra, setActiveEra] = useState(null);
  const [heroQuery, setHeroQuery] = useState("");

  const shownFathers = activeEra
    ? FATHERS.filter((father) => father.era === activeEra)
    : FATHERS;

  const handleHeroSearch = (e) => {
    e.preventDefault();
    if (!heroQuery.trim()) return;
    router.push(`/search?q=${encodeURIComponent(heroQuery.trim())}`);
  };

  return (
    <main className="af-root">

      {/* Hero */}
      <div className="relative left-1/2 right-1/2 -mx-[50vw] w-screen h-[52vh] min-h-[360px] max-h-[640px] overflow-hidden">

        <div
          className="absolute inset-0 motion-safe:md:bg-fixed"
          style={{ position: "absolute", inset: 0 }}
        >
          <Image
            src="/images/hero-library.jpg"
            alt="A candlelit study lined with old books, a fire in the hearth"
            fill
            priority
            sizes="100vw"
            className="object-cover"
            style={{ objectFit: "cover" }}
          />
        </div>

        {/* Oxblood gradient so the title below stays readable */}
        <div
          className="absolute inset-0"
          style={{
            background:
              "linear-gradient(to bottom, rgba(20,8,8,0.15) 0%, rgba(20,8,8,0.55) 65%, var(--oxblood, #2a0d0d) 100%)",
          }}
        />

        {/* Overlay content — sits above the image + gradient in stacking order */}
        <div className="absolute inset-0 flex flex-col items-center justify-center text-center px-8">

          <div
            className="af-mono text-xs mb-3"
            style={{ color: "var(--gold)" }}
          >
            ANF / NPNF · 38 VOLUMES · RETRIEVAL ONLY
          </div>

          <h1
            className="af-display text-4xl md:text-6xl italic font-semibold leading-tight mb-6"
            style={{ color: "var(--parchment)" }}
          >
            Ad Fontes
          </h1>

          <form
            onSubmit={handleHeroSearch}
            className="flex items-center gap-2 w-full max-w-md"
            style={{
              background: "rgba(0, 0, 0, 0.35)",
              border: "1px solid var(--gold)",
              padding: "10px 16px",
              backdropFilter: "blur(2px)",
            }}
          >
            <Search size={16} color="var(--gold)" />

            <input
              type="text"
              value={heroQuery}
              onChange={(e) => setHeroQuery(e.target.value)}
              placeholder="Ask the Fathers a question…"
              className="af-mono flex-1 bg-transparent outline-none text-sm italic"
              style={{ color: "var(--parchment)" }}
            />
          </form>

        </div>

        {/* Scroll down prompt */}
        <div className="af-scroll-cue absolute bottom-8 left-1/2 -translate-x-1/2">
          <span className="label">Scroll</span>
          <div className="line" />
        </div>

      </div>

      {/* Landing Page */}
      <div className="px-8 md:px-16 py-16 max-w-4xl mx-auto">

        {/* Description */}
        <p
          className="text-lg leading-relaxed mb-8 max-w-2xl"
          style={{ color: "var(--parchment)" }}
        >
          Ask a question in plain language. Read what the early Church
          Fathers actually wrote in answer — never a generated summary,
          only the passage itself, cited and linked to its source.
        </p>

        {/* Try Asking */}
        <div className="flex items-center gap-2 mb-3">
          <Sparkles size={13} color="var(--gold)" />

          <span
            className="af-mono text-xs"
            style={{ color: "var(--gold)" }}
          >
            Try asking
          </span>
        </div>

        <div className="flex flex-wrap gap-2 mb-14">
          {QUICK_QUESTIONS.map((question) => (
            <button
              type="button"
              key={question}
              className="af-chip"
              onClick={() =>
                router.push(`/search?q=${encodeURIComponent(question)}`)
              }
            >
              {question}
            </button>
          ))}
        </div>

        {/* Browse by Era */}
        <div
          className="af-mono text-xs mb-5"
          style={{ color: "var(--gold)" }}
        >
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
                <div
                  className="af-era-track"
                  style={{ flex: 0.4 }}
                />
              )}

            </React.Fragment>
          ))}

        </div>

        <div className="af-rule my-10" />

        {/* Fathers */}
        <div className="flex items-center justify-between mb-5">

          <span
            className="af-mono text-xs"
            style={{ color: "var(--gold)" }}
          >
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
        <div className="grid grid-cols-1 md:grid-cols-3 gap-2">

          <div className="af-feature-row">

            <ScrollText
              size={16}
              color="var(--gold)"
            />

            <div>

              <div
                className="af-display text-base italic"
                style={{ color: "var(--gold-bright)" }}
              >
                Pure retrieval
              </div>

              <div
                className="text-sm"
                style={{ color: "var(--parchment-dim)" }}
              >
                No generated answers, ever.
              </div>

            </div>

          </div>

          <div className="af-feature-row">

            <BookOpen
              size={16}
              color="var(--gold)"
            />

            <div>

              <div
                className="af-display text-base italic"
                style={{ color: "var(--gold-bright)" }}
              >
                Tradition-grouped
              </div>

              <div
                className="text-sm"
                style={{ color: "var(--parchment-dim)" }}
              >
                Orthodox and Catholic, side by side.
              </div>

            </div>

          </div>

          <div className="af-feature-row">

            <Search
              size={16}
              color="var(--gold)"
            />

            <div>

              <div
                className="af-display text-base italic"
                style={{ color: "var(--gold-bright)" }}
              >
                Semantic search
              </div>

              <div
                className="text-sm"
                style={{ color: "var(--parchment-dim)" }}
              >
                Matching by meaning, not keyword.
              </div>

            </div>

          </div>

        </div>

      </div>

      {/* Footer */}
      <div className="af-rule mt-16" />

      <div
        className="af-mono text-[10px] text-center py-6"
        style={{
          color: "var(--parchment-dim)",
        }}
      >
        AD FONTES — PRIMARY SOURCE INDEX
      </div>

    </main>
  );
}