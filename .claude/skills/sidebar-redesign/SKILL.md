---
name: sidebar-redesign
description: Redesign this Vue 3 app's UI into a modern SaaS-style interface — a left vertical navigation sidebar instead of the top nav bar, a consistent spacing/design-token system, and an overall more polished, professional look. Use when asked to redesign the UI, modernize the look, add a sidebar nav, convert the top nav to a sidebar, or give the app a more "SaaS" feel.
---

# Sidebar Redesign

Turns this app's current top-nav layout into a modern SaaS-style shell: a fixed left sidebar for
navigation, a consistent spacing/color/typography token system, and small polish fixes across
existing views. This is a **visual-layer refactor** — data fetching, routes, filters, i18n keys,
and business logic must come out unchanged. Follow the four phases below in order. Do not skip
Phase 2's approval step — this touches nearly every view in the app and should not start writing
code before the user has seen and confirmed the plan.

## Phase 1 — Audit the current UI

Launch an `Explore` agent (or do it directly if the app is small) to build a full picture before
proposing anything:

- The root layout component (usually `App.vue` or equivalent) — current nav markup, its global
  `<style>` block, and every class it defines that other views rely on (`.card`, `.stat-card`,
  `.badge`, `.page-header`, table styles, buttons, etc.).
- Every view/page component and the router config — full list of routes and nav items, so the
  sidebar has 1:1 parity with what the top nav currently exposes.
- Any existing design-token usage (CSS custom properties, a shared `variables.css`, hardcoded hex
  values scattered across scoped styles) — most of this codebase's demo/workshop apps have no
  token layer yet, so expect to find raw hex/rem values repeated per-component instead.
- The project's `CLAUDE.md` (root and any nested ones) for a documented design system — color
  palette, status colors, "no emojis in UI" rules, or other constraints already agreed. Treat
  anything documented there as a hard constraint, not a suggestion to override.
- Any modal/detail-panel components and how they're styled, since a sidebar layout changes
  available horizontal space and modals may need adjustment.

Report back (to yourself, feeding Phase 2): current nav item list, current global style
primitives and where they live, current color/spacing values in use, and anything already
consistent that should be preserved rather than reinvented.

## Phase 2 — Propose the redesign plan and get approval

Do not write any code in this phase. Produce a concrete plan covering:

1. **Sidebar structure**: fixed left column (~240–260px), logo/brand at top, vertical nav items
   below (icon + label), active-route highlight (accent background or left border accent, not
   just a color change), hover state, full-viewport height, independent scroll from the main
   content area. Main content area gets consistent outer padding and a max-width if the app
   doesn't already constrain one.
2. **Design tokens**: introduce CSS custom properties for spacing (a small scale — e.g.
   `4/8/12/16/24/32/48px` — replacing ad hoc rem values found in Phase 1), color (reuse the
   existing palette from `CLAUDE.md`/global styles rather than inventing a new one — extend it
   with a sidebar background/border/active-state token if needed), radius, and shadow. These
   tokens go in one place (the root layout component's global style block, or a new
   `variables.css` if the app's build supports importing plain CSS) so every view inherits them
   instead of repeating literals.
3. **Component polish**: which existing global primitives (cards, tables, badges, buttons,
   stat-cards) get updated to consume the new tokens, and what specifically looks inconsistent
   today (mismatched paddings, inconsistent border-radius, inconsistent font sizes) that this
   pass will fix.
4. **Responsive behavior**: what happens below a reasonable breakpoint — collapse to icon-only,
   an overlay/hamburger toggle, or (for an internal demo app) an explicit decision to not support
   narrow viewports. Pick one and say so; don't leave it implicit.
5. **Explicitly out of scope**: no route changes, no new pages, no changed data-fetching, no
   changed filter/composable behavior, no i18n key renames (existing `t('nav.x')` keys move to
   the sidebar markup as-is), no changes to modal component internals beyond width/spacing if the
   new content area is narrower.

Use `AskUserQuestion` for any real open call in the plan (icon set or none, collapsible sidebar
or fixed, whether to keep the top bar for search/profile/language-switcher controls above the
content area vs. folding them into the sidebar). Then present the full plan in the chat and wait
for explicit user confirmation before moving to Phase 3. If the user pushes back on any part,
revise and re-confirm rather than proceeding on a partial yes.

## Phase 3 — Execute

This modifies `.vue` files, which this project's `CLAUDE.md` mandates delegating: **you must use
the `vue-expert` subagent for this phase, not edit `.vue` files directly.** Give it one
consolidated task rather than fragmenting into many small ones, since the changes are
interdependent (sidebar layout, tokens, and per-view polish all touch the same shared styles):

- Convert the root layout's top nav into a left sidebar component (extract to its own
  `Sidebar.vue` if the nav markup is nontrivial, or restructure the existing root component if
  it's simple) per the approved plan — full nav-item parity with the current routes, preserving
  every existing `t('nav.x')` i18n call.
- Introduce the token layer, then sweep the global style block and each view's scoped styles for
  hardcoded spacing/color/radius values that should now reference tokens — prioritize the shared
  primitives (`.card`, `.stat-card`, `.badge`, tables, buttons) since fixing those once fixes
  every view that uses them.
- Adjust the main content wrapper to sit beside the sidebar with consistent padding.
- Leave every `<script>` block's logic untouched unless a prop/emit needs to move because markup
  was extracted into a new component — flag any such case explicitly rather than doing it
  silently.
- Preserve `client/CLAUDE.md`'s Composition API conventions and this app's existing
  loading/error-state patterns exactly as they are; this is a styling and layout pass, not a
  rewrite.

## Phase 4 — Verify

1. Run the frontend's production build (`npm run build`) and confirm it's clean.
2. If Playwright MCP tools are available, load the app in a browser, walk every nav item, and
   confirm: the sidebar renders, active-state highlighting works per route, no layout overflow at
   the app's normal viewport width, and (if the app has an i18n switcher) the sidebar renders
   correctly in every locale with no untranslated strings. If Playwright isn't available, start
   both dev servers, open the app with `open`, and say so explicitly rather than claiming a
   visual check that didn't happen.
3. Run a `code-reviewer` pass on the diff — this is a wide-reaching style refactor, worth a
   second look for accidentally-broken class references or orphaned CSS.
4. Report back concisely: what changed, which files, and any deviations made from the approved
   plan and why.
