"use client";

import { useEffect, useRef } from "react";

export default function PassageList({ passages, highlightChunk }) {
  const highlightRef = useRef(null);

  useEffect(() => {
    if (highlightRef.current) {
      const reduceMotion = window.matchMedia(
        "(prefers-reduced-motion: reduce)"
      ).matches;
      highlightRef.current.scrollIntoView({
        behavior: reduceMotion ? "auto" : "smooth",
        block: "center",
      });
    }
  }, [highlightChunk]);

  return (
    <>
      {passages.map((passage) => {
        if (passage.chunk_index === highlightChunk) {
          return (
            <div
              key={passage.id}
              ref={highlightRef}
              className="af-passage-highlight"
            >
              <span className="af-mono af-passage-match-label">
                Matched passage
              </span>
              <p className="leading-relaxed">{passage.chunk_text}</p>
            </div>
          );
        }
        return (
          <p key={passage.id} className="leading-relaxed mb-6 last:mb-0">
            {passage.chunk_text}
          </p>
        );
      })}
    </>
  );
}