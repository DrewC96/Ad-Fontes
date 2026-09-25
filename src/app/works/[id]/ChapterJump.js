"use client";

import { useRouter } from "next/navigation";
import { ChevronDown } from "lucide-react";

export default function ChapterJump({ workId, chapters, currentPage }) {
  const router = useRouter();

  return (
    <div className="af-chapter-select-wrap">
      <select
        className="af-chapter-select"
        value={currentPage}
        onChange={(e) => router.push(`/works/${workId}?chapter=${e.target.value}`)}
      >
        {chapters.map((chapter, index) => (
          <option key={index} value={index + 1}>
            {index + 1}. {chapter.citation || `Chunk ${chapter.startIndex}`}
          </option>
        ))}
      </select>
      <ChevronDown size={14} className="af-chapter-select-icon" aria-hidden="true" />
    </div>
  );
}