---
name: toc-navigation-structure
description: Use when the user asks to restructure TOC.md for better navigation, hierarchy, links, or brevity, especially when the TOC has become long, flat, or overloaded with per-note summaries.
---

# TOC Navigation Structure

Use this skill to make `TOC.md` easier to navigate as the note system grows.

## Goal

Turn `TOC.md` into a clear navigational map of the note system rather than a long descriptive catalog.

The focus is fast movement through the structure:

- show the hierarchy clearly
- link to notes and important aggregating files
- keep details brief
- avoid clutter from unnecessary per-note summaries

## Principles

- Prefer a tree-like or otherwise clearly hierarchical structure.
- Use hyperlinks in `TOC.md` consistently, not optionally.
- Link only to real notes or files, not to directories. In Obsidian, a wikilink such as `[[Folder]]` points to a note, 
not a folder, and can create an unwanted empty note when clicked.
- Show folders and categories as plain text headings or list labels unless there is an actual category/index note to link.
- Category pages, important aggregating files, and individual note pages should be linked so the user can jump directly 
to them.
- Optimize for navigation, not exhaustive description.
- Keep note entries brief: usually just the title or link target is enough.
- Short comments are useful for categories or folders, but not for every ordinary note.
- Preserve a balance between overview and brevity.

## What To Include

Usually include:

- the folder and subfolder hierarchy
- plain text folder and subfolder labels
- hyperlinks for category-level files, aggregating files, and ordinary notes that appear in the navigation tree
- links to important category-level files
- links to aggregating files such as tables, indexes, dashboards, or overview pages
- links to ordinary notes when they belong in the visible navigation tree

## What To Avoid

- Do not add short summaries for every ordinary note.
- Do not repeat note content that is already clear from the title.
- Do not turn `TOC.md` into a full catalog of descriptions.
- Do not flatten the structure into one long list when the hierarchy is meaningful.
- Do not create Obsidian wikilinks whose target is only a folder path.

## Category vs Note Detail

- Folders or categories may have short explanatory text if it helps navigation.
- Folders should usually be plain text. If a category has a real overview/index note, link to that note rather than to 
the directory itself.
- Important aggregating files may also have a short explanation.
- Ordinary standalone notes should usually appear as just a title or link, without extra summary.

## Relationship To Structure

- The `TOC.md` hierarchy should broadly reflect the real note tree.
- It does not need to reproduce every filesystem detail mechanically if that harms readability.
- The point is navigability, not literal low-level mirroring.

## Workflow

1. Read the current `TOC.md`.
2. Inspect the actual note and folder hierarchy.
3. Identify where the current `TOC.md` is too flat, too verbose, or hard to navigate.
4. Rewrite the structure into a clearer hierarchical form.
5. Replace note and file entries with links so the user can navigate directly from `TOC.md`.
6. Remove unnecessary per-note summaries.
7. Keep short descriptions only where they help orient the user at the category level.

## Editing Rules

- Prefer simple, stable hierarchy over decorative formatting.
- Do not over-explain ordinary notes.
- Keep the structure scannable.
- Use links consistently and by default for notes and files.
- Keep folder-only entries non-clickable unless they point to a real index or category note.
- If a note is only useful through an aggregating file, the aggregating file may deserve more prominence than the 
individual note.

## When To Ask The User

Ask a short clarifying question if:

- There are two plausible navigation structures with different tradeoffs.
- It is unclear whether a file should be treated as an ordinary note or as a category-level navigation asset.
- The current filesystem hierarchy is itself confusing enough that larger restructuring may be better than only 
rewriting `TOC.md`.

## Expected Outcome

After running this skill, `TOC.md` should be:

- easier to scan
- easier to click through
- more hierarchical
- less verbose
- better suited for day-to-day navigation

## Response Style

When reporting results, mention:

- whether `TOC.md` was made more hierarchical
- whether links were added or normalized
- whether unnecessary note summaries were removed
- any remaining structural ambiguity
