---
name: tv-series-tracking
description: Use when the user wants to save, update, review, or check TV series as a standalone Markdown tracker, especially for watch progress, released seasons, and newly released seasons found via internet search.
---

# TV Series Tracking

Use this skill when the user wants to track TV series as a structured collection rather than as ordinary standalone notes.

This includes cases like:

- saving a new series to watch later
- saving a series the user is already watching or has watched
- updating which season the user has watched up to
- checking whether new seasons have been released
- refreshing stored release information from the internet

## Goal

Maintain the user's TV series collection as a compact database-like Markdown table in the current workspace.

The collection should support both:

- personal watch progress
- external release tracking

## Storage Model

Keep one central collection file as a structured Markdown table.

Default file: `series-tracker.md` in the current workspace root.

If the workspace already contains an obvious TV tracker file, use it instead of creating a duplicate. Prefer a stable descriptive filename such as `series-tracker.md` or `tracked-tv-series.md`.

Do not store tracked TV series as random separate notes by default. Use the table as the compact tracking layer.

Separate per-series notes are allowed when a series needs a short description, personal notes, source notes, ambiguity, or richer context than should live inside the table. Put those files in a local `series/` folder and link them from the `Title` column when useful.

If the tracking file does not exist yet, create it during the first add operation.

If `TOC.md` exists in the workspace, use it for navigation and keep it consistent with tracker file changes according to the workspace's existing TOC rules.

If the workspace has dedicated instructions for maintaining `TOC.md`, follow those instructions instead of inventing new TOC rules in this skill.

## First-Time Setup

When the user adds the first tracked TV series and no collection file exists yet:

1. Create `series-tracker.md` in the current workspace root unless the user asks for another location.
2. Add a short title and, if useful, one brief sentence explaining the purpose of the table.
3. Initialize the table with the chosen column layout.
4. Add the first series row immediately.
5. Update `TOC.md` if it exists.

## Preferred Table Shape

Use a compact schema that is easy to maintain in Markdown while still supporting update checks.

Preferred columns:

- `Title`
- `User status`
- `Watched up to`
- `Latest released`
- `Next release`
- `Series status`
- `Years`
- `Last checked`

This schema is recommended, not rigid. Keep the same overall ideas, but adapt the exact columns if the collection needs a slightly different shape in practice.

## Example Table Template

Use a structure like this when creating the collection note for the first time:

```md
# TV Series Tracker

Tracked TV series with watch progress and release updates.

| Title | User status | Watched up to | Latest released | Next release | Series status | Years | Last checked |
| --- | --- | --- | --- | --- | --- | --- | --- |
| The Simpsons | watching | S35 | S36 | S37, date unknown | ongoing | 1989- | 2026-05-27 |
| Friends | completed | S10 | S10 | - | ended | 1994-2004 | 2026-05-27 |
| Stranger Things | planned | none | S5 | - | ongoing | 2016- | 2026-05-27 |
```

Use `-` or another single consistent empty marker where a value is currently unknown or not applicable.

## Column Meaning

- `Title`: canonical series title, optionally linked to a per-series note.
- `User status`: for example `planned`, `watching`, `completed`, `paused`, or `dropped`.
- `Watched up to`: the last season the user has watched. If none, store an explicit empty-state value such as `none` or `0`, and use it consistently within the table.
- `Latest released`: the latest released season currently available.
- `Next release`: upcoming season and date in one compact field when known, for example `S5, 2026-10-12` or `S5, date unknown`.
- `Series status`: for example `ongoing` or `ended`.
- `Years`: compact production span such as `2019-` or `1994-2004`.
- `Last checked`: when the release information was last reviewed.

Longer notes, short descriptions, and richer commentary should usually live in a separate per-series note rather than in the table itself.

## Adding A Series

When the user asks to save or add a TV series:

1. Find or create the central TV series tracking file.
2. Search the internet for the canonical title and current release information if the user did not provide enough data.
3. Detect duplicates using the corrected canonical title, not only the raw user wording.
4. Ask which season the user has watched up to if that is not already clear.
5. If the user has not watched any season, store the chosen default empty-state value consistently.
6. Add the series as a new table row.
7. Update `TOC.md` if it exists and the tracker file, `series/` folder, or a per-series note is new or moved.

Use the title language that the user naturally uses for that series. If the user refers to the series as `Друзья`, store `Друзья`; if they refer to it as `Friends`, store `Friends`. Use canonical naming within that language rather than forcibly switching to English.

## Updating Progress

When the user says they watched a season, update at least:

- `Watched up to`
- `User status` when the status clearly changes

If the series has a separate note, update that note when the user provides information that belongs there rather than in the tracking table.

Do not re-fetch all metadata from the internet for a simple progress update unless the user also asked for a release check.

## Checking For Release Updates

When the user asks to check whether new seasons have come out:

1. Review the tracked TV series table.
2. Search the internet for current release information for relevant series.
3. Compare stored values against current information.
4. Update changed fields such as `Latest released`, `Next release`, `Series status`, `Years`, and `Last checked` when needed.
5. If the series has a separate note and important factual context changed, update that note too.
6. Summarize which series changed and what changed.

Typical examples:

- a new season was released
- an upcoming season now has a date
- a series changed from ongoing to ended
- a previously announced next season was cancelled or removed from official plans

## Internet Lookup Rules

- When adding a series, use the internet to fill missing factual metadata.
- When checking updates, use the internet as the source for current release status.
- Prefer recent and reliable sources.
- If sources conflict, prefer the most authoritative and current information. If the ambiguity is worth preserving, put it in the separate per-series note rather than bloating the table.
- Preserve the user's preferred title language in the stored table entry.

## Data Quality Rules

- Prefer canonical titles over user nicknames, but preserve recognizable naming.
- Prefer canonical naming within the language the user naturally uses for that series.
- Keep the table compact and readable.
- Do not create too many columns: the table should remain readable.
- Use consistent season notation across rows.
- Keep dates in a consistent format when known.
- Avoid long descriptions inside the tracking table.
- Put series descriptions and extended notes into separate per-series notes when they are useful.

## When To Ask The User

Ask a short clarifying question if:

- multiple series match the user's title
- it is unclear which adaptation or regional version they mean
- watched progress is required but missing
- the table already contains a near-duplicate that may or may not be the same series

## Recommended Defaults

- If the user only says they want to watch a series later, set `User status` to `planned`.
- If the user is actively watching it, use `watching`.
- If the user says they finished all currently available seasons but the series is not over, keep `User status` meaningful for the user's workflow and rely on `Watched up to` plus `Latest released` to show that they are caught up.
- Use a single consistent empty-state value for "watched nothing yet" across the table.

## Response Style

When reporting results, mention:

- where the tracking file lives
- whether a separate per-series note was created or updated
- whether a series was added, updated, or refreshed
- what internet-derived fields were filled or changed
- any ambiguity that still needs user input
