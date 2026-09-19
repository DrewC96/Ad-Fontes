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
    <main className="af-root">
      <div className="px-8 md:px-16 py-16 max-w-4xl mx-auto">
        <Link
          href="/"
          className="af-mono af-text-gold text-xs inline-flex items-center gap-1 mb-8"
        >
          <ChevronLeft size={14} /> Back to all Fathers
        </Link>

        <h1 className="af-display af-text-parchment text-4xl italic mb-2">
          {father.name}
        </h1>

        <div className="af-mono af-text-gold text-xs mb-10">
          {father.era}
          {meta ? ` · ${meta}` : ""}
        </div>

        {father.bio && (
          <p className="af-text-parchment text-lg leading-relaxed mb-10 max-w-2xl">
            {father.bio}
          </p>
        )}

        <div className="af-rule mb-8" />

        <div className="af-mono af-text-gold text-xs mb-5">
          Works ({father.works.length})
        </div>

        {father.works.length === 0 ? (
          <p className="af-text-parchment-dim">
            No works indexed yet for this Father.
          </p>
        ) : (
          <div className="af-works-grid">
            {father.works.map((work) => (
              <div key={work.id} className="af-fragment">
                <div className="af-display af-text-ink italic leading-tight">
                  {work.title}
                </div>

                {(work.volume_number || work.original_language) && (
                  <div className="text-sm mt-2 opacity-70 af-text-ink">
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
      </div>
    </main>
  );
}