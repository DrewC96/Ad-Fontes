import Link from "next/link";
import { notFound } from "next/navigation";
import { createClient } from "@supabase/supabase-js";
import { ChevronLeft } from "lucide-react";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

async function getFatherWithWorks(slug) {
  const { data: author, error: authorError } = await supabase
    .from("authors")
    .select(`
      id,
      name,
      slug,
      birth_year,
      death_year,
      region,
      bio,
      eras ( name )
    `)
    .eq("slug", slug)
    .single();

  if (authorError || !author) {
    return null;
  }

  const { data: works, error: worksError } = await supabase
    .from("works")
    .select("id, title, volume_number, original_language")
    .eq("author_id", author.id)
    .order("title");

  if (worksError) {
    console.error("Error fetching works:", worksError);
  }

  return {
    ...author,
    era: author.eras?.name ?? "Unknown",
    works: works ?? [],
  };
}

export default async function FatherPage({ params }) {
  // Next.js 16: params is async now
  const { slug } = await params;
  const father = await getFatherWithWorks(slug);

  if (!father) {
    notFound();
  }

  const meta = [
    father.region,
    father.birth_year || father.death_year
      ? `${father.birth_year ?? "?"}–${father.death_year ?? "?"}`
      : null,
  ]
    .filter(Boolean)
    .join(" · ");

  return (
    <main className="af-root px-8 md:px-16 py-16 max-w-4xl mx-auto">
      <Link
        href="/"
        className="af-mono text-xs"
        style={{
          color: "var(--gold)",
          display: "inline-flex",
          alignItems: "center",
          gap: "4px",
          marginBottom: "32px",
        }}
      >
        <ChevronLeft size={14} /> Back to all Fathers
      </Link>

      <h1
        className="af-display text-4xl italic mb-2"
        style={{ color: "var(--parchment)" }}
      >
        {father.name}
      </h1>

      <div
        className="af-mono text-xs mb-10"
        style={{ color: "var(--gold)" }}
      >
        {father.era}
        {meta ? ` · ${meta}` : ""}
      </div>

      {father.bio && (
        <p
          className="text-lg leading-relaxed mb-10 max-w-2xl"
          style={{ color: "var(--parchment)" }}
        >
          {father.bio}
        </p>
      )}

      <div className="af-rule mb-8" />

      <div
        className="af-mono text-xs mb-5"
        style={{ color: "var(--gold)" }}
      >
        Works ({father.works.length})
      </div>

      {father.works.length === 0 ? (
        <p style={{ color: "var(--parchment-dim)" }}>
          No works indexed yet for this Father.
        </p>
      ) : (
        <div
          className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-4"
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(4, 1fr)",
            gap: "16px",
          }}
        >
          {father.works.map((work) => (
            <div
              key={work.id}
              className="af-fragment"
              style={{ padding: "18px 20px" }}
            >
              <div
                className="af-display italic"
                style={{ color: "#2a1810", lineHeight: 1.3 }}
              >
                {work.title}
              </div>

              {(work.volume_number || work.original_language) && (
                <div
                  className="text-sm mt-2"
                  style={{ color: "#6b4a3a" }}
                >
                  {[
                    work.volume_number ? `Vol. ${work.volume_number}` : null,
                    work.original_language,
                  ]
                    .filter(Boolean)
                    .join(" · ")}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </main>
  );
}