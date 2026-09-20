"use client";

import { useRouter } from "next/navigation";

export default function ChapterJump({ workId, chapters, currentPage }) {
  const router = useRouter();

  return (
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
  );
}