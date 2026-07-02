# Comprehensive Audit Report — Dan Beattie
**Audit by:** Claude Fable 5 (anthropic/claude-fable-5) via OpenRouter
**Scope:** whoisdanbeattie.com linkinbio page · 72 Hermes skills · config.yaml v30
**Date:** July 2, 2026

---

# AREA 1: WEBSITE CODE QUALITY AUDIT

## Summary
The page is structurally sound for a linkinbio, but it has two broken ticket links, a fragile hotlinked album art dependency, no SEO/social metadata strategy visible, and several accessibility gaps in the carousel and mobile nav. As a musician landing page, the biggest missed opportunity is structured data for tour dates (Google event rich results) and Open Graph tags (this URL gets shared on social constantly — that's its entire job).

---

**[WEBSITE] [Priority: High] [Effort: Small]**
**What:** Fix the two dead ticket buttons — Bathurst (Jul 17) and Tweed (Sep 5) render `tickets()` with no `href`.
**Why:** A ticket button that goes nowhere is directly lost revenue and erodes trust in every other button on the page. Users won't distinguish "not on sale yet" from "broken site."
**How:** Either:
1. If tickets aren't on sale yet, change the button state explicitly:
```html
<span class="ticket-btn ticket-btn--pending" aria-disabled="true">On Sale Soon</span>
```
2. If they are on sale, add the Bandsintown URLs. Add a build-time check so an entry without a URL can never render as a live-looking button again.

---

**[WEBSITE] [Priority: High] [Effort: Small]**
**What:** Stop hotlinking album art from the Spotify CDN (`i.scdn.co/...`).
**Why:** Spotify CDN URLs are not stable contracts — they rotate on re-ingestion, artwork updates, or CDN policy changes. When it breaks, the centerpiece of your Music section is a broken image on your highest-traffic page.
**How:** Download the image, optimize it, and serve locally alongside your other assets:
```bash
curl -o images/album-art.jpg "https://i.scdn.co/image/<hash>"
cwebp -q 82 images/album-art.jpg -o images/album-art.webp
```
```html
<picture>
  <source srcset="images/album-art.webp" type="image/webp">
  <img src="images/album-art.jpg" alt="Call You A Country Boy — Album Cover" width="600" height="600" loading="lazy">
</picture>
```

---

**[WEBSITE] [Priority: High] [Effort: Small]**
**What:** Add Open Graph, Twitter Card, canonical, and description meta tags to `<head>`.
**Why:** This is a linkinbio page — its primary distribution channel is being pasted into Instagram, TikTok, and X. Without OG tags, shares render as a bare URL with no image. That's a large, free CTR loss on every share.
**How:**
```html
<meta name="description" content="Dan Beattie — official links: tour dates Jul–Sep 2026, new album out Sep 18, music on all platforms.">
<link rel="canonical" href="https://whoisdanbeattie.com/">
<meta property="og:title" content="Dan Beattie — Music, Tour Dates & Links">
<meta property="og:description" content="New album Sep 18, 2026. Tour dates, tickets, and streaming links.">
<meta property="og:image" content="https://whoisdanbeattie.com/images/og-card.jpg">
<meta property="og:url" content="https://whoisdanbeattie.com/">
<meta property="og:type" content="website">
<meta name="twitter:card" content="summary_large_image">
```
Create a dedicated 1200×630 `og-card.jpg` — don't reuse a hero slide with faces at the edges that get cropped.

---

**[WEBSITE] [Priority: High] [Effort: Medium]**
**What:** Add schema.org `MusicGroup` + `MusicEvent` JSON-LD for the 9 tour dates and the Sep 18 album release.
**Why:** Google shows tour dates directly in search results (event rich results) for artists with valid `MusicEvent` markup. It's the single highest-ROI SEO change available to this page.
**How:** Add before `</body>`:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "MusicGroup",
  "name": "Dan Beattie",
  "url": "https://whoisdanbeattie.com",
  "sameAs": [
    "https://instagram.com/whoisdanbeattie",
    "https://tiktok.com/@whoisdanbeattie",
    "https://x.com/whoisdanbeattie"
  ],
  "event": [
    {
      "@type": "MusicEvent",
      "name": "18th Annual Hollywood Jamboree",
      "startDate": "2026-07-02",
      "location": { "@type": "Place", "name": "Hollywood Jamboree", "address": "Belleville, ON" },
      "offers": { "@type": "Offer", "url": "BANDSINTOWN_URL", "availability": "https://schema.org/InStock" }
    }
    // ... remaining 8 dates
  ]
}
</script>
```

---

**[WEBSITE] [Priority: Medium] [Effort: Medium]**
**What:** Move tour dates out of hardcoded HTML into a single JSON data structure rendered by JS (or a tiny build step).
**Why:** Nine dates hardcoded in markup is how the two missing-href bugs happened. Tour data changes constantly and one source of truth also feeds the JSON-LD above.
**How:**
```js
const TOUR = [
  { date: "2026-07-17", city: "Bathurst", venue: "...", tickets: null },
  { date: "2026-09-05", city: "Tweed", venue: "...", tickets: null },
  // ...
];
```

---

**[WEBSITE] [Priority: Medium] [Effort: Small]**
**What:** Fix countdown timer timezone parsing and add a post-release "Out Now" state for Sep 18, 2026.
**Why:** `new Date("2026-09-18")` parses as UTC midnight — fans in different timezones see the countdown hit zero at different (wrong) moments. On Sep 19, naive countdowns display negative numbers and sit broken.
**How:**
```js
const RELEASE = new Date("2026-09-18T00:00:00-04:00"); // pin explicit timezone
function tick() {
  const diff = RELEASE - Date.now();
  if (diff <= 0) {
    countdownEl.innerHTML = '<a class="out-now" href="SPOTIFY_URL">OUT NOW — LISTEN</a>';
    clearInterval(timer);
    return;
  }
  // render d/h/m/s
}
```

---

**[WEBSITE] [Priority: Medium] [Effort: Small]**
**What:** Carousel accessibility and lifecycle fixes: pause on hover/focus, respect `prefers-reduced-motion`, pause on hidden tab, add `aria` roles, keyboard support.
**Why:** Auto-advancing content every 5s violates WCAG 2.2.2 (Pause, Stop, Hide) without a pause mechanism. `setInterval` also keeps firing in background tabs.
**How:**
```js
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
let timer = reduced ? null : setInterval(next, 5000);
document.addEventListener('visibilitychange', () =>
  document.hidden ? clearInterval(timer) : (timer = reduced ? null : setInterval(next, 5000)));
carousel.addEventListener('mouseenter', () => clearInterval(timer));
carousel.addEventListener('focusin',  () => clearInterval(timer));
```
Dots should be `<button>` elements with `aria-label="Go to slide 2"` and `aria-current` on the active one.

---

**[WEBSITE] [Priority: Medium] [Effort: Small]**
**What:** Hamburger menu accessibility: `aria-expanded`, `aria-controls`, Escape-to-close, focus management.
**Why:** Screen reader and keyboard users currently have no way to know the menu state or dismiss it.
**How:**
```html
<button class="hamburger" aria-expanded="false" aria-controls="mobile-menu" aria-label="Menu">
```
Toggle `aria-expanded` in JS; on open, move focus to first link; on Escape or link click, close and return focus.

---

**[WEBSITE] [Priority: Medium] [Effort: Medium]**
**What:** Image performance pass: explicit `width`/`height` on all `<img>`, `loading="lazy"` on below-fold images, `fetchpriority="high"` + `<link rel="preload">` on the first hero slide, WebP with `srcset` responsive sizes.
**Why:** Full-screen hero image is your LCP element. Missing dimensions cause CLS. Unoptimized JPGs on mobile burn data.
**How:**
```html
<link rel="preload" as="image" href="images/img_5-1200.webp" fetchpriority="high">
<img src="images/img_5-1200.webp" srcset="..." sizes="100vw" width="2000" height="1125" alt="Dan Beattie" fetchpriority="high">
```

---

**[WEBSITE] [Priority: Medium] [Effort: Small]**
**What:** Add `rel="noopener noreferrer"` to all `target="_blank"` links.
**How:** One-line grep audit: `grep -rn 'target="_blank"' index.html | grep -v noopener`. Fix all hits.

---

**[WEBSITE] [Priority: Medium] [Effort: Small]**
**What:** Deduplicate social link data — same 4–6 URLs appear in three places (sidebar, mobile bar, connect pills).
**Why:** When Dan's handle changes, someone will update two of three locations. Same class of bug as the ticket hrefs.
**How:** Define once in JS, render three times from a `SOCIALS` array.

---

**[WEBSITE] [Priority: Low] [Effort: Small]**
**What:** Add favicon set, `apple-touch-icon`, `theme-color`, and `site.webmanifest`.
**Why:** Missing favicons look unfinished in browser tabs and bookmarks.
**How:** Generate via realfavicongenerator.net from album art or logo.

---

**[WEBSITE] [Priority: Low] [Effort: Small]**
**What:** Add privacy-friendly analytics (Plausible, GoatCounter, or Cloudflare Web Analytics).
**Why:** Zero visibility into which streaming button fans click, which tour dates get ticket clicks, or where traffic comes from.
**How:** One script tag; add custom events on streaming buttons and ticket links.

---

**[WEBSITE] [Priority: Low] [Effort: Small]**
**What:** Domain/hosting hygiene: enforce HTTPS redirect, `www` → apex canonical redirect, basic security headers, dynamic footer copyright.
**Why:** Split traffic between `www` and apex dilutes SEO; stale "© 2026" in mid-2027 signals abandonment.
**How:** 301 redirect `www` → apex; add `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`; use JS for dynamic year.

---

# AREA 2: HERMES SKILLS AUDIT

## Summary
72 skills is a heavy inventory with meaningful overlap in four clusters (humanizers, musician landing pages, design mockups, AI music). Every skill description occupies context in routing decisions, so redundancy isn't just clutter — it degrades skill selection accuracy and burns tokens on every turn. There are also six uncategorized skills and several gaps that matter specifically for a musician/CEO operating profile.

## 2.1 Redundancies & Consolidations

**[SKILLS] [Priority: High] [Effort: Small]**
**What:** Merge `humanizer` and `content-humanizer` into a single skill.
**Why:** They serve the same purpose — stripping AI-writing tells from output text. Having both means Claude has to disambiguate at invocation time, they can drift apart, and they double the token cost when both descriptions load into context.
**How:** Diff the two SKILL.md files. Keep the more comprehensive rule set, fold in unique rules from the other, delete the loser.

---

**[SKILLS] [Priority: High] [Effort: Medium]**
**What:** Consolidate the `musician-website` / `personal-landing-page` / `claude-design` triangle.
**Why:** All three contain overlapping guidance on layout, typography, color, and responsive patterns. When a website task comes in, it's ambiguous which skill fires.
**How:** `claude-design` becomes the canonical design-system skill (tokens, typography, spacing); `musician-website` and `personal-landing-page` keep only domain-specific deltas with an explicit "defer to claude-design" line.

---

**[SKILLS] [Priority: Medium] [Effort: Small]**
**What:** Deduplicate writing-adjacent cluster (summarization, rewriting, tone-adjustment skills).
**Why:** Multiple skills touch "take this text and transform it" — collectively they fragment what should be one coherent style system.
**How:** Audit every skill whose core verb is a text transformation. Merge into one `text-transforms` skill, or rewrite descriptions for mutually exclusive triggers.

---

**[SKILLS] [Priority: Medium] [Effort: Small]**
**What:** Resolve overlap between document-format skills (PDF/DOCX/XLSX/PPTX handling).
**Why:** More than one skill may claim file-conversion territory. Format skills are also most likely to contain stale library instructions.
**How:** One skill per file format, hard boundaries, smoke test for each.

---

## 2.2 Gaps — Missing Skills

**[SKILLS] [Priority: High] [Effort: Small]**
**What:** Add a `deploy-and-verify` skill covering the website's actual deployment pipeline.
**Why:** Area 1 identified ~15 website fixes. Without a skill encoding how this specific site deploys (host, build step, DNS, cache invalidation), every fix session re-derives the pipeline from scratch.
**How:** Write a short SKILL.md documenting: repo location, build command, deploy target, verify procedure, rollback.

---

**[SKILLS] [Priority: High] [Effort: Small]**
**What:** Add a `qa-checklist` / pre-publish verification skill.
**Why:** Many Area 1 issues (broken ticket buttons, hotlinked images, missing rel attributes) are exactly the class of bug a systematic pre-publish check catches.
**How:** Concrete checklist: all links return 200, all images self-hosted, OG/JSON-LD validate, a11y quick pass, mobile viewport.

---

**[SKILLS] [Priority: Medium] [Effort: Small]**
**What:** Add an `image-pipeline` skill (optimization, formats, hosting).
**Why:** The hotlinked album art and LCP findings both trace back to no defined image workflow.
**How:** Encode: always self-host, convert to WebP/AVIF, target dimensions per slot, compression targets, exact commands.

---

**[SKILLS] [Priority: Medium] [Effort: Small]**
**What:** Add a `release-announcement` skill for the musician context.
**Why:** Nothing encodes the repeatable workflow of "new single/tour date drops → update site, JSON-LD, streaming links, socials."
**How:** Step-by-step runbook per event type (release, tour date, cancellation), cross-referencing deploy and QA skills.

---

**[SKILLS] [Priority: Low] [Effort: Small]**
**What:** Add an `analytics-review` skill.
**Why:** Without a companion skill, analytics data will be collected and never read.
**How:** Dashboard location, 4-5 key metrics, template for monthly summary.

---

## 2.3 Improvement Opportunities

**[SKILLS] [Priority: High] [Effort: Medium]**
**What:** Rewrite weak `description` frontmatter across the collection.
**Why:** The description is the only part Claude sees before deciding to load it. Vague descriptions cause both false negatives and false positives. Highest-ROI improvement for a 72-skill collection.
**How:** Each description should answer: what it does, when to trigger it, when not to. Pattern: "Use when [concrete trigger]. Covers X, Y, Z. Do not use for [adjacent case]."

---

**[SKILLS] [Priority: Medium] [Effort: Medium]**
**What:** Split oversized SKILL.md files using progressive disclosure (references/ and scripts/).
**Why:** Any skill over ~300 lines burns context on every invocation, even for simple sub-tasks.
**How:** Keep core workflow in SKILL.md; move reference tables and extended examples to `references/*.md`; move deterministic operations to `scripts/`.

---

**[SKILLS] [Priority: Medium] [Effort: Small]**
**What:** Convert deterministic instructions into scripts.
**Why:** Anywhere a skill says "run these 6 commands in order," a script is faster, cheaper, and can't be paraphrased incorrectly.
**How:** Audit for step sequences with no decision points. Extract to `scripts/`, replace prose with "Run `scripts/name.sh`; interpret output."

---

**[SKILLS] [Priority: Medium] [Effort: Small]**
**What:** Standardize naming and structure conventions across all skills.
**Why:** Mixed conventions (e.g. `humanizer` vs `content-humanizer`) make gaps/overlaps harder to spot.
**How:** Kebab-case, consistent section order: Purpose → When to use → Workflow → Rules → References.

---

**[SKILLS] [Priority: Low] [Effort: Small]**
**What:** Add worked before/after examples to rules-heavy skills.
**Why:** Skills that only state rules perform noticeably worse than ones with concrete input→output examples.
**How:** One compact example per skill, under ~30 lines.

---

**[SKILLS] [Priority: Low] [Effort: Small]**
**What:** Prune dead and speculative skills down to 45–55 active.
**Why:** Each unused skill still costs description tokens and selection ambiguity forever.
**How:** Flag skills untouched by recent work. Move candidates to an `archive/` directory.

---

# AREA 3: CONFIGURATION OPTIMIZATION

**[CONFIG] [Priority: High] [Effort: Small]**
**What:** Slim and de-duplicate global instructions (platform_hints / CLAUDE.md layer).
**Why:** Global instructions load into every conversation. Rules that only apply to specific tasks belong in skills, not globals. Duplicating wastes tokens and creates conflicting versions.
**How:** Audit line by line. Keep only: identity/context, universal behavioral rules, pointers to the skill collection. Target under ~150 lines.

---

**[CONFIG] [Priority: High] [Effort: Small]**
**What:** Tighten tool permissions and the allow/deny lists.
**Why:** Overly broad permissions create risk; overly narrow ones create constant approval friction.
**How:** Auto-allow safe high-frequency operations (read, grep, git status/diff, site build); require confirmation for deploys, deletions, credential access; deny `rm -rf`, pushing to main without review, editing `.env`.

---

**[CONFIG] [Priority: Medium] [Effort: Small]**
**What:** Right-size model selection per task type.
**Why:** DeepSeek-Chat for everything wastes cost/latency on link-checking but may be underpowered for design work.
**How:** Set default to mid-tier model. Document which task classes warrant escalation (architecture, refactors, creative) and which can drop down (mechanical edits, checklists).

---

**[CONFIG] [Priority: Medium] [Effort: Small]**
**What:** Add hooks for automatic post-edit verification.
**Why:** Several Area 1 bugs (broken links, malformed markup) would be caught mechanically. Hooks make verification free.
**How:** Post-edit hook runs HTML validator + link checker when website files change.

---

**[CONFIG] [Priority: Medium] [Effort: Small]**
**What:** Secrets and credentials hygiene — API key in config.yaml.
**Why:** The `config.yaml` contains `api_key: sk-6b9...ed96` in plaintext at line 5. This should be an env var reference only.
**How:** Remove the API key value from config.yaml. Use `api_key_env: DEEPSEEK_API_KEY` instead (or however Hermes supports env-var references). Scan git history for leaked keys. Add `.env` to `.gitignore`.

---

**[CONFIG] [Priority: Low] [Effort: Small]**
**What:** Enable checkpoints with retention (`checkpoints.enabled: true`).
**Why:** Currently disabled. Without checkpoints, undoing a bad automation run or recovering from a broken config edit requires manual restore.
**How:** Set `enabled: true`, `retention_days: 7`, `max_snapshots: 20`.

---

**[CONFIG] [Priority: Low] [Effort: Small]**
**What:** Establish memory/context conventions for long-running work.
**Why:** Multi-session projects lose state between conversations.
**How:** Maintain a single `STATUS.md` with current priorities, decisions, blockers. Add one line to globals instructing Claude to read it at session start.

---

**[CONFIG] [Priority: Low] [Effort: Small]**
**What:** Version-control the entire configuration (skills, config.yaml, global instructions).
**Why:** Without git, a bad consolidation is unrecoverable and there's no way to see what changed.
**How:** Put everything under a single git repo. Commit before starting consolidation. Tag a `pre-audit` baseline.

---

## CONCLUSION

**The shape of the findings:** The website (Area 1) has a handful of genuinely urgent, revenue-touching bugs — broken ticket buttons above all — surrounded by standard hardening work. The skills collection (Area 2) is broad but unmanaged: its problems are duplication, vague triggers, and missing skills for the workflows that actually recur (deploy, QA, releases). The configuration (Area 3) mostly needs tightening, not rebuilding.

**Recommended execution sequence:**

1. **This week (quick wins, ~all Small effort):** Fix ticket buttons, self-host album art, add OG tags. Merge the humanizer pair. Version-control the config and tag a baseline. Remove API key from config.yaml.
2. **Next 2 weeks:** Ship the `deploy-and-verify` and `qa-checklist` skills (they make every subsequent website fix faster and safer), then work through the remaining Area 1 items using them. Rewrite skill descriptions across the collection.
3. **Ongoing:** The design-skill consolidation, progressive-disclosure splits, archive pruning, and the analytics loop. None are urgent; all compound.

**One number to watch:** active skill count. If it's back near 72 in three months with the same overlap patterns, add a rule: *before creating a skill, search the collection for overlap and either extend or consolidate.*

**Overall:** nothing here is structurally broken. It's a maintenance debt problem, and roughly 70% of the total value is captured by the High-priority/Small-effort items alone.

---

*— Report generated by Claude Fable 5 (anthropic/claude-fable-5) via OpenRouter*
