const SEARCH_PATH = "/search";

/** Validate `from` and turn it into a breadcrumb item, or null. */
export function parseSearchTrail(from) {
  if (typeof from !== "string") return null;
  let url;
  try {
    url = new URL(from, "http://local");
  } catch {
    return null;
  }
  // Rejects absolute URLs, //host, and anything not on the search route
  if (url.origin !== "http://local" || url.pathname !== SEARCH_PATH) return null;

  const q = url.searchParams.get("q")?.trim();
  const short = q && q.length > 32 ? q.slice(0, 31) + "…" : q;
  return {
    label: short ? `Search: “${short}”` : "Search results",
    href: url.pathname + url.search,
  };
}

/** Append a validated search URL to a link as ?from=... */
export function withFrom(href, from) {
  if (!parseSearchTrail(from)) return href;
  const [path, query = ""] = href.split("?");
  const params = new URLSearchParams(query);
  params.set("from", from);
  return `${path}?${params}`;
}