"use client";

import { useEffect, useRef } from "react";

export default function PassageList({ passages, highlightChunk }) {
  const highlightRef = useRef(null);

  useEffect(() => {
    if (highlightRef.current) {
      highlightRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [highlightChunk]);

  return (
    <>
      {passages.map((passage) => {
        const isHighlighted = passage.chunk_index === highlightChunk;
        return (
          <p
            key={passage.id}
            ref={isHighlighted ? highlightRef : null}
            className={`leading-relaxed mb-6 last:mb-0 ${
              isHighlighted ? "af-passage-highlight" : ""
            }`}
          >
            {passage.chunk_text}
          </p>
        );
      })}
    </>
  );
}