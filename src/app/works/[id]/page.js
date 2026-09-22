import Link from "next/link";
import { notFound } from "next/navigation";
import { createClient } from "@supabase/supabase-js";
import { ChevronLeft, ChevronRight } from "lucide-react";
import ChapterJump from "./ChapterJump";
import PassageList from "./PassageList";
import Breadcrumb from "@/components/Breadcrumb";
import BackToTop from "@/components/BackToTop";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

async function getWorkMeta(id) {
  const { data: work, error } = await supabase
    .from("works")
    .select(`
      id,
      title,
      volume_number,
      original_language,
      authors ( name, slug )
    `)
    .eq("id", id)
    .single();

  if (error || !work) return null;

  return { ...work, author: work.authors };
}

// Groups contiguous chunks that share a citation into "chapters."
// Only pulls citation + chunk_index — cheap even for a 300-chunk work.
async function getChapterIndex(workId) {
  const { data, error } = await supabase
    .from("passages")
    .select("citation, chunk_index")
    .eq("work_id", workId)
    .order("chunk_index");

  if (error || !data) return [];

  const chapters = [];
  for (const row of data) {
    const prev = chapters[chapters.length - 1];
    if (!prev || prev.citation !== row.citation) {
      chapters.push({ citation: row.citation, startIndex: row.chunk_index });
    }
  }
  return chapters;
}

async function getChapterPassages(workId, startIndex, endIndex) {
  let query = supabase
    .from("passages")
    .select("id, chunk_index, citation, chunk_text")
    .eq("work_id", workId)
    .gte("chunk_index", startIndex)
    .order("chunk_index");

  if (endIndex !== null) {
    query = query.lt("chunk_index", endIndex);
  }

  const { data, error } = await query;
  if (error) console.error("Error fetching chapter passages:", error);
  return data ?? [];
}

// Given a target chunk_index, find which chapter's range contains it.
// Returns a 1-based page number.
function findChapterForChunk(chapters, targetChunk) {
  let page = 1;
  for (let i = 0; i < chapters.length; i++) {
    if (chapters[i].startIndex <= targetChunk) {
      page = i + 1;
    } else {
      break;
    }
  }
  return page;
}

export default async function WorkPage({ params, searchParams }) {
  const { id } = await params;
  const { chapter, chunk } = await searchParams;

  const work = await getWorkMeta(id);
  if (!work) notFound();

  const chapters = await getChapterIndex(id);
  const totalChapters = chapters.length;

  if (totalChapters === 0) {
    return (
      <main className="af-root">
        <div className="px-8 md:px-16 py-16 max-w-3xl mx-auto">
          <WorkHeader work={work} />
          <p className="af-text-parchment-dim">
            No passages indexed yet for this work.
          </p>
        </div>
      </main>
    );
  }

  // A ?chunk= param (from semantic search) takes priority over ?chapter=
  // (from manual prev/next or the dropdown) — it lands on whichever
  // chapter actually contains that chunk.
  const targetChunk = chunk !== undefined ? parseInt(chunk, 10) : null;

  let currentPage;
  if (Number.isInteger(targetChunk)) {
    currentPage = findChapterForChunk(chapters, targetChunk);
  } else {
    const requested = parseInt(chapter, 10);
    currentPage = Number.isInteger(requested)
      ? Math.min(Math.max(requested, 1), totalChapters)
      : 1;
  }

  const currentIndex = currentPage - 1;
  const current = chapters[currentIndex];
  const next = chapters[currentIndex + 1];
  const passages = await getChapterPassages(
    id,
    current.startIndex,
    next ? next.startIndex : null
  );

  const prevHref = currentPage > 1 ? `/works/${id}?chapter=${currentPage - 1}` : null;
  const nextHref =
    currentPage < totalChapters ? `/works/${id}?chapter=${currentPage + 1}` : null;

  return (
    <main className="af-root">
      <div className="px-8 md:px-16 py-16 max-w-3xl mx-auto">
        <WorkHeader work={work} />

        <div className="af-rule mb-6" />

        <div className="af-chapter-nav">
          <NavButton href={prevHref} direction="prev" />

          <div className="af-mono af-text-gold text-xs text-center">
            Chapter {currentPage} of {totalChapters}
            {current.citation && (
              <div className="af-text-parchment-dim mt-1 normal-case">
                {current.citation}
              </div>
            )}
          </div>

          <NavButton href={nextHref} direction="next" />
        </div>

        <ChapterJump workId={id} chapters={chapters} currentPage={currentPage} />

        <div className="af-scroll mt-8">
          <PassageList passages={passages} highlightChunk={targetChunk} />
        </div>

              <div className="af-chapter-nav mt-8">
        <NavButton href={prevHref} direction="prev" />
        <div />
        <NavButton href={nextHref} direction="next" />
      </div>
      <BackToTop />
    </div>
  </main>
  );
}

function WorkHeader({ work }) {
  return (
    <>
      <Breadcrumb
        items={[
          { label: "Home", href: "/" },
          { label: work.author.name, href: `/fathers/${work.author.slug}` },
          { label: work.title },
        ]}
      />

      <h1 className="af-display af-text-parchment text-4xl italic mb-2">
        {work.title}
      </h1>

      <div className="af-mono af-text-gold text-xs mb-10">
        {[
          work.author?.name,
          work.volume_number ? `Vol. ${work.volume_number}` : null,
          work.original_language,
        ]
          .filter(Boolean)
          .join(" · ")}
      </div>
    </>
  );
}

function NavButton({ href, direction }) {
  const disabled = !href;
  const Icon = direction === "prev" ? ChevronLeft : ChevronRight;
  const label = direction === "prev" ? "Prev" : "Next";

  const content = (
    <span className="af-btn af-chapter-btn inline-flex items-center gap-1">
      {direction === "prev" && <Icon size={14} />}
      {label}
      {direction === "next" && <Icon size={14} />}
    </span>
  );

  if (disabled) {
    return <span className="af-chapter-btn-disabled">{content}</span>;
  }

  return <Link href={href}>{content}</Link>;
}