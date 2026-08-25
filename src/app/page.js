// custom bookshelf with cross and bible on top and then 5 shelves for each era. books for each fatehr in each era. when you click on a book, it opens a modal with the works of that father. each work is a link to the source. the modal has a search bar to search within the works of that father. the modal has a close button. the modal has a next and previous button to navigate between fathers. the modal has a filter to filter by era. the modal has a sort by dropdown to sort by name or number of works. the modal has a pagination to navigate between pages of works. the modal has a copy button to copy the works to clipboard. 

"use client";

import React, { useState } from "react";
import {
  Search,
  BookOpen,
  ScrollText,
  Sparkles,
  ChevronRight,
} from "lucide-react";

import { createClient } from '@supabase/supabase-js'

const supabase = createClient('https://unfztmjqxjxguyrvnicm.supabase.co', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVuZnp0bWpxeGp4Z3V5cnZuaWNtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODYzODA1MDgsImV4cCI6MjEwMTk1NjUwOH0.xbgTehhR6qW1aXOMChq7ITvbhbEhhJxz4fQWt9MWmBk')

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
  const [activeEra, setActiveEra] = useState(null);

  const shownFathers = activeEra
    ? FATHERS.filter((father) => father.era === activeEra)
    : FATHERS;

  return (
    <main className="af-root">

      {/* Landing Page */}
      <div className="px-8 md:px-16 py-16 max-w-4xl mx-auto">

        {/* Small heading */}
        <div
          className="af-mono text-xs mb-8"
          style={{ color: "var(--gold)" }}
        >
          ANF / NPNF · 38 VOLUMES · RETRIEVAL ONLY
        </div>

        {/* Title + Search */}
        <div className="mb-6 flex items-center justify-between flex-wrap gap-6">

          <div>
            <span className="af-dropcap">A</span>

            <h1 className="af-display text-5xl md:text-6xl italic font-semibold leading-tight">
              d Fontes
            </h1>
          </div>

          <button type="button" className="af-header-search">
            <Search size={14} color="var(--gold)" />

            <span>
              Search the Fathers…
            </span>
          </button>

        </div>

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