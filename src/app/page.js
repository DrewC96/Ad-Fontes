import HomeClient from "./HomeClient";
import { createClient } from "@supabase/supabase-js";

const supabase = createClient(
  process.env.NEXT_PUBLIC_SUPABASE_URL,
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
);

async function getFathers() {
  const { data, error } = await supabase
    .from("authors")
    .select(`
      name,
      slug,
      birth_year,
      death_year,
      eras ( name ),
      works ( count )
    `)
    .order("name");

  if (error) {
    console.error("Error fetching fathers:", error);
    return [];
  }

  return data.map((row) => ({
   name: row.name,
   slug: row.slug,
   era: row.eras?.name ?? "Unknown",
   works: row.works?.[0]?.count ?? 0,
   }));
}

export default async function Page() {
  const fathers = await getFathers();
  return <HomeClient fathers={fathers} />;
}