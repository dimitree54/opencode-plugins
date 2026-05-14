---
name: toc-tag-grouping
description: Use when the user asks to restructure, group, clean up, or improve tag presentation in TOC.md, especially when a flat tag list has become hard to navigate.
---

# TOC Tag Grouping

Use this skill to make the tag section in `TOC.md` more structured and easier to scan.

## Goal

Represent tags in `TOC.md` not only as a flat list, but as meaningful groups when good natural groupings exist.

The purpose is faster orientation: the user should be able to understand what kinds of notes already exist in the system 
without reading one long undifferentiated tag list.

## Principles

- Group tags by meaning, not just alphabetically.
- Use natural categories such as genres, countries, note formats, health topics, or other recurring conceptual families.
- Show the result hierarchically.
- Leave tags ungrouped when there is no clear good category for them.
- Prefer clarity over taxonomy perfection.
- When a new tag is added to the system, place it into an existing logical group when possible. If no good group exists, 
create a new one instead of appending the tag into an unstructured flat list.

## Relationship To Note Structure

- Tag groups may partially reflect the folder structure, but they do not need to mirror it exactly.
- Some tags are cross-category and should remain grouped by meaning rather than by folder.
- Do not force tags into the folder hierarchy if that makes the tag view less useful.

## What To Look For

When revising the tag section in `TOC.md`, check for:

1. Long flat tag lists that are hard to scan.
2. Obvious families of tags that can be grouped together.
3. Mixed tag types in a single undifferentiated list.
4. Tags that belong to cross-cutting concepts rather than one folder.
5. Tags that do not fit any good group and should remain standalone.

## Suggested Group Types

Use only the groups that are actually justified by the current note system. Common examples:

- Genres
- Countries
- Formats
- Health topics
- People
- Places
- Status or workflow
- Media types
- Themes

Group names should stay short and obvious.

## Workflow

1. Read the current tag section in `TOC.md`.
2. Review the tags currently used across notes.
3. Identify natural families of tags.
4. Rewrite the tag section in a hierarchical grouped form.
5. Leave truly uncategorizable tags in an ungrouped section.
6. Keep the final structure easy to scan and maintain.

When new tags appear during normal note updates, do not wait for a separate regrouping request. Add each new tag 
directly into the most appropriate existing group, or create a new group if that is the clearest fit. Full regrouping 
is only needed when the current structure has become noisy or confusing.

## Editing Rules

- Do not invent abstract grouping systems that the user will not understand later.
- Do not over-group sparse tags when a simple list is clearer.
- Do not create many one-item groups unless they are genuinely useful.
- Keep stable groups stable across revisions when possible.
- Prefer semantic grouping over mechanical grouping.

## When To Ask The User

Ask a short clarifying question if:

- Two different grouping strategies both look reasonable.
- A tag could belong to multiple groups and the better presentation is unclear.
- The user may want a domain-specific taxonomy that is not obvious from the current notes.

## Expected Outcome

After running this skill, the tag section in `TOC.md` should be:

- easier to scan
- meaningfully grouped where appropriate
- still simple to maintain
- tolerant of tags that do not fit any strong category

## Response Style

When reporting results, mention:

- whether the tag section in `TOC.md` was regrouped
- what main groups were introduced
- whether any tags were left ungrouped by design
