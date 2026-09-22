import Link from "next/link";
import { createClient } from "@supabase/supabase-js";
import { Search } from "lucide-react";
import { searchPassages } from "../../lib/search";
import Breadcrumb from "@/components/Breadcrumb";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

async function getWorkMetaMap(workIds) {
  if (workIds.length === 0) return {};

  const { data, error } = await supabase
    .from("works")
    .select("id, title, authors ( name, slug )")
    .in("id", workIds);

  if (error || !data) return {};

  return Object.fromEntries(
    data.map((w) => [w.id, { title: w.title, author: w.authors }])
  );
}

export default async function SearchPage({ searchParams }) {
  const { q } = await searchParams;
  const query = (q ?? "").trim();

  if (!query) {
    return (
      <main className="af-root">
        <div className="px-8 md:px-16 py-16 max-w-3xl mx-auto">
          <Breadcrumb
            items={[{ label: "Home", href: "/" }, { label: "Search" }]}
          />
          <p className="af-text-parchment-dim">No search query provided.</p>
        </div>
      </main>
    );
  }

  let results = [];
  let searchFailed = false;

  try {
    const raw = await searchPassages(query, { rawMatchCount: 25 });
    results = raw.slice(0, 8);
  } catch (err) {
    console.error("Search page error:", err);
    searchFailed = true;
  }

  const workIds = [...new Set(results.map((r) => r.work_id))];
  const workMeta = await getWorkMetaMap(workIds);

  return (
    <main className="af-root">
      <div className="px-8 md:px-16 py-16 max-w-3xl mx-auto">
        <Breadcrumb
          items={[
            { label: "Home", href: "/" },
            { label: `Search: "${query}"` },
          ]}
        />

        <div className="flex items-center gap-2 mb-2">
          <Search size={16} color="var(--gold)" />
          <span className="af-mono af-text-gold text-xs">Results for</span>
        </div>

        <h1 className="af-display af-text-parchment text-3xl italic mb-10">
          &ldquo;{query}&rdquo;
        </h1>

        {searchFailed && (
          <p className="af-search-error af-mono text-sm">
            Search failed. Try again in a moment.
          </p>
        )}

        {!searchFailed && results.length === 0 && (
          <p className="af-text-parchment-dim">
            No matching passage found — try rephrasing your question.
          </p>
        )}

        <div className="flex flex-col gap-4">
          {results.map((result) => {
            const meta = workMeta[result.work_id];
            return (
              <Link
                key={result.id}
                href={`/works/${result.work_id}?chunk=${result.chunk_index}`}
                className="af-fragment af-fragment-interactive"
              >
                <div className="af-mono af-text-gold text-xs mb-2">
                  {meta?.author?.name ?? "Unknown Father"}
                  {meta?.title ? ` · ${meta.title}` : ""}
                </div>

                {result.citation && (
                  <div className="af-display af-text-ink italic text-sm mb-2 opacity-80">
                    {result.citation}
                  </div>
                )}

                <p className="af-text-ink leading-relaxed line-clamp-4">
                  {result.chunk_text}
                </p>
              </Link>
            );
          })}
        </div>
      </div>
    </main>
  );
}