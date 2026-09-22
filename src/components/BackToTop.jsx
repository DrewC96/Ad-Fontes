"use client";

import { useEffect, useState } from "react";

/**
 * Fixed, top-center "back to top" cue styled after the hero SCROLL
 * indicator: small uppercase label + a thin vertical line with a
 * traveling highlight. Fades in once the user has scrolled past
 * `threshold` px. The highlight travels upward (vs. the hero's
 * downward travel) to signal direction.
 */
export default function BackToTop({ threshold = 600 }) {
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    function onScroll() {
      setVisible(window.scrollY > threshold);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [threshold]);

  function scrollToTop() {
    const prefersReducedMotion = window.matchMedia(
      "(prefers-reduced-motion: reduce)"
    ).matches;
    window.scrollTo({
      top: 0,
      behavior: prefersReducedMotion ? "auto" : "smooth",
    });
  }

  return (
    <button
      type="button"
      onClick={scrollToTop}
      className={`af-back-to-top ${visible ? "af-back-to-top-visible" : ""}`}
      aria-label="Back to top"
      tabIndex={visible ? 0 : -1}
    >
      <span className="af-back-to-top-label">Top</span>
      <span className="af-back-to-top-line" aria-hidden="true" />
    </button>
  );
}