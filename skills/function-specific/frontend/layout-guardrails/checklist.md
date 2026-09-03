# Layout Guardrails — PR Checklist

1. [ ] **Scope declared** — element annotated with `data-scope="…"` or `data-z-layer="…"`.
2. [ ] **Z-index cap respected** — ≤ scope cap table in `strategies.md`.
3. [ ] **Parent overflow** — immediate ancestor `overflow` verified not to clip floating child.
4. [ ] **Portal restack** — after teleport, child re-opens own stacking-context / `overflow-visible`.
5. [ ] **Edge flip** — dropdown auto-flips or scrolls into view at viewport boundary.
