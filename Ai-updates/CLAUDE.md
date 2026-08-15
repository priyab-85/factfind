# Morning AI Wire — operating spec

Everything in this directory serves one job: file a daily AI briefing at **07:00 US Eastern**
into a single artifact page that never changes URL.

This file is directory-scoped on purpose. It must never be moved to the repo root — the
rest of this repository is the Advisor AI Fact Finder MVP, and these instructions have
nothing to do with building it.

---

## The page

**Artifact URL:** https://claude.ai/code/artifact/f8c8a99c-d561-4080-a87f-70052a4307ca

**Source of truth:** `Ai-updates/morning-ai-wire.html` in this directory.

Two rules that matter more than anything else below:

1. **Always publish with `url` set to the artifact URL above.** Publishing without it
   creates a *second* artifact at a new address, which silently breaks the pin the user
   set up once and never wants to touch again.
2. **Always edit the committed HTML, never rewrite the page from scratch.** The scheduled
   run starts in a fresh container with no memory of yesterday's design. Regenerating the
   page from the fetched version would let the styling drift a little every morning until
   it looks nothing like edition 001. Pull the file, edit it, publish it, commit it back.

---

## Daily procedure

1. `git pull origin claude/daily-ai-research-summary-2lhv0s` and read
   `Ai-updates/morning-ai-wire.html`.
2. Collect every URL already in that file — today's sections *and* the archive. That set
   is the exclusion list.
3. Search the sources below for genuinely new items dated within roughly the last 7 days.
4. Drop anything whose URL is in the exclusion list. Drop anything you cannot date.
5. Edit the HTML: move yesterday's four sections into the archive as one collapsed
   `<details class="day">` entry with its links intact, drop the oldest archive day if
   there are now more than 14, write today's items into the sections, bump the edition
   number and date in the masthead, update the `.glance` counts and each section's
   `.count`.
6. Publish with `url` set, `favicon: "📡"`, and `label` set to `edition-NNN`.
7. Commit the updated HTML to this branch and push.

If a step fails, still complete the ones that can succeed. A published page with a
committed-but-unpushed file is recoverable; an unpublished page is a missed morning.

---

## Beat

Four categories, in this order on the page:

| Section | Covers |
|---|---|
| Models & agent releases | New models, agent frameworks, SDKs, protocol changes (MCP, Agent Framework, Bedrock) |
| Applied AI in financial services | Wealth and advisor tech, AI in advice and compliance, regulatory movement affecting AI in finance |
| Analyst signal | Gartner and Forrester Hype Cycles, Magic Quadrants, Waves — public pages and abstracts only |
| Worth listening to | New podcast episodes and long-form video, with a line on what's actually covered |

---

## Sources, in priority order

Check tier 1 first. Tiers 2–4 fill gaps and catch what the vendors don't announce loudly.

**Tier 1 — primary vendor & protocol.** Anthropic, OpenAI, Google, Microsoft devblogs,
`blog.modelcontextprotocol.io`. Slower than the trackers, always first-party.

**Tier 2 — advisor & wealthtech trade press.** Kitces, WealthManagement.com, Financial
Planning, Advisor Perspectives, fintech.global. Effectively the only outlets covering the
financial-services beat; without them that section goes empty.

**Tier 3 — model release trackers.** `llmgateway.io/timeline`, `llm-stats.com`.
Comprehensive on what shipped, but secondary — when a tracker is the only source, flag it.

**Tier 4 — engineering press & aggregators.** InfoQ, TechCrunch, Hacker News, arXiv.

`latent.space` is blocked by the network egress proxy. Don't retry it — search for the
episode and link the show index, flagged, or use Apple/Spotify.

---

## Quality bar

Prefer primary, allow flagged secondary. Every item needs a link that resolves.

- `Primary` — the vendor or author themselves.
- `Tracker` / `Archive` / `Show page` — the direct link couldn't be confirmed, so the
  reader is being sent to an index. Say so in the item text too.
- `Paywalled` — abstract is public, document is not.
- `Regulatory` — rule or enforcement change rather than a product launch.

Never invent a headline, a date, a guest name, or a URL. If a podcast guest can't be
confirmed, describe the episode's subject and say the guest wasn't confirmable — that is
a useful item; a fabricated name is a worthless one.

Check dates before including anything. An announcement that resurfaces in trade press
months later is not new — edition 001 nearly ran an Advisor360 launch that was actually
from December 2025.

---

## No repeats

The rolling 14-day archive is the dedup state. It is not decoration and must not be
trimmed for tidiness — dropping it silently re-enables repeats.

A story that genuinely develops (a release candidate going final, a rule taking effect)
may run again, but the item must lead with what changed, not restate the original.

---

## Format of an item

```html
<article class="item">
  <div class="meta">
    <time>Aug 13</time>
    <span class="src">example.com</span>
    <span class="flag">Primary</span>
  </div>
  <h3><a href="https://example.com/post">Headline written as a claim, not a topic</a></h3>
  <p>Two or three sentences on why this matters to a financial-services AI
     engineer, ending with the reason to click or the reason to skip.</p>
</article>
```

Headlines assert something ("the protocol went stateless"), they don't label a subject
("MCP update"). The body earns the click or saves the reader from it.

---

## Quiet days

Target 5–12 items. Drop any category with nothing genuinely new rather than padding it —
a short edition means a slow news day, and the reader has been told that. Never re-report
an archived item to fill space.

If a run finds nothing at all in any category, still publish: update the date and edition
number and state plainly that nothing new cleared the bar. A page that quietly shows
yesterday's date looks broken.

---

## Design

Don't restyle the page. The tokens live in the `<style>` block and cover three theme
states — bare `:root` for light, `prefers-color-scheme: dark` guarded with
`:root:not([data-theme="light"])`, and `:root[data-theme="dark"]`. Any new color must be
added to all three or it will break one theme.

Category hues are set per-section with `style="--hue: var(--c-model)"` and similar. They
encode which beat an item belongs to so the page can be scanned rather than read.
