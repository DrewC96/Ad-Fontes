// components/Breadcrumb.jsx
import Link from "next/link";

/**
 * Hierarchical breadcrumb trail: Home > Author > Work.
 * Always reflects site structure, regardless of how the user
 * actually arrived at the page (search, direct link, etc).
 *
 * items: [{ label, href }] — omit href on the last item (current page).
 */
export default function Breadcrumb({ items }) {
  return (
    <nav aria-label="Breadcrumb" className="af-breadcrumb">
      <ol className="af-breadcrumb-list">
        {items.map((item, i) => {
          const isLast = i === items.length - 1;
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
