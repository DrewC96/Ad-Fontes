import Link from "next/link";
import { parseSearchTrail } from "@/lib/trail";

/**
 * Breadcrumb trail: Home > [Search] > Author > Work.
 * Follows site structure, plus a search crumb after Home when the user
 * arrived from a search (a validated `from` URL is passed in).
 *
 * items: [{ label, href }] — omit href on the last item (current page).
 * from:  optional search URL to show as a crumb.
 */
export default function Breadcrumb({ items, from }) {
  const trail = parseSearchTrail(from);
  const all = trail ? [items[0], trail, ...items.slice(1)] : items;

  return (
    <nav aria-label="Breadcrumb" className="af-breadcrumb">
      <ol className="af-breadcrumb-list">
        {all.map((item, i) => {
          const isLast = i === all.length - 1;
          return (
            <li key={i} className="af-breadcrumb-item">
              {isLast || !item.href ? (
                <span
                  className="af-breadcrumb-current"
                  title={item.label}
                  aria-current="page"
                >
                  {item.label}
                </span>
              ) : (
                <Link href={item.href} className="af-breadcrumb-link">
                  {item.label}
                </Link>
              )}
              {!isLast && (
                <span className="af-breadcrumb-sep" aria-hidden="true">
                  &rsaquo;
                </span>
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}