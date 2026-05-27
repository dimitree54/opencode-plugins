---
name: notes-structure
description: "Use it when you need to add some files/notes to the user's personal database. Or if you are editing the database. Here you will find info about the database structure and how to maintain it."
---


## Notes structure
When writing a note, you need to place this note into the appropriate structure. The basic format is a .md file, but we will also 
use a folder hierarchy to conveniently organize the notes, and you should be the one to think through this structure.

What could the structure options be? This could be a folder hierarchy, and for some notes, it might be convenient to 
combine them into a single .md file.

This structure, this organization, will and can change dynamically. That is, if a note is currently placed in some 
folder or simply saved, then later, when new notes are added, it is necessary to re-evaluate this organization to see 
if it might be convenient to change the structure. For example, maybe a new note brings together some other notes well. 
Or maybe some notes were previously grouped together, but now with the addition of a new note, a new structure or 
substructure emerges. Or perhaps it would be more convenient to combine things into a single .md file. This kind of 
optimal and convenient structure also needs to be considered with each new note added, but at the same time, 
you shouldn't over-engineer it, so the structure doesn’t change every single time—a trade-off is needed between having 
an optimal structure and maintaining consistency and stability.

## Recording a note
The note should be written in the original language, on which it was sent (English or Russian) unless the note contains 
other instructions on this matter.

The idea is that these notes can be of very different nature, and your task is not only to save the note as it is, but 
to format it in a structured, visually appealing way. That is, present it nicely, but don't go overboard—don't deviate 
too much from what was actually said in the note, don't make things up. At the same time, format it so that it's 
suitable for saving, so it looks good overall. Maybe polish some things here and there. But it's important that the 
original meaning and intent isn't lost, and maybe even the lack of structure that's inherent to it is preserved.

Notes will be in text format, plus there may also be additional resources such as images. When adding a note, it might 
be given in a rather general form — for example, just the title of a movie — and your task is to turn it into some kind 
of full-fledged note, but not too wordy, just to the point. So, if it is not clear from the note what the note is 
actually about, you can ask a clarifying question. But if, in principle, it’s clear from the note what it is and what 
the intention is, then you don’t need to ask such questions. You should also mention to the user the destination, where
you decided to place this note — that is, into which cell, folder, or how the organization will be changed when adding 
this note.

If the content really belongs to a structured collection with its own update workflow, do not force it into an ordinary standalone note. 
Use the dedicated collection skill instead. For tracked TV series with watch progress and release checks, use `tv-series-tracking`.

## Resources
All resources that are loaded along with the note or instead of the note must be saved in their original form along 
with the .md note and used as a link or as an image, if it is an image, in the .md file. There is no need to describe 
in detail or list everything depicted—in other words, this resource itself serves as the note. 
It is necessary to describe in detail what is presented in the resource only if there are specific instructions to do so. 
That is, the note should be as brief as possible, providing only a general description of the resource without any details.

### Image handling

When saving images attached to notes, compress them by default to reduce storage usage, unless the user explicitly says the image should not be compressed or that the original file must be preserved without changes.

Use one practical default preset:

- Resize the image so the longest side is at most `1280` px.
- Do not upscale smaller images.
- Save with good visual quality suitable for viewing inside notes.
- Preserve the original file format whenever possible: JPEG stays JPEG, PNG stays PNG, WebP stays WebP, and so on.

The goal is not archival quality, but a lightweight visual reference that remains clear enough to recognize the content.
Use exceptions only when the original file quality, exact pixels, metadata, or lossless preservation is clearly important.

Available tools for image work:

- `ImageMagick` as the main default toolkit.
- `magick` and `identify` for conversion, resize, compression, and metadata inspection.
- `jpegoptim` for additional JPEG optimization.
- `optipng` and `pngquant` for PNG optimization.
- `ffmpeg` as a universal fallback for resize, conversion, animated formats, and frame extraction.
- `webp` tools: `cwebp`, `dwebp`, `gif2webp`.
- `libheif-examples` tools: `heif-convert`, `heif-info` for HEIC and HEIF images.
- Python fallback: `Pillow` and `pillow-heif` when CLI tools are unavailable or custom processing is needed.

Prefer CLI tools first. Use `ImageMagick` as the default choice when it is available. Use format-specific optimizers 
like `jpegoptim`, `optipng`, and `pngquant` as a second pass when they meaningfully reduce file size.

The `inbox` folder should remain only a temporary buffer for incoming files. When a resource has already been saved into
the permanent notes structure and linked or embedded into the appropriate `.md` note, it should no longer be kept in
`inbox`. Remove files from `inbox` after they have been successfully processed, and when possible, also remove any empty
subfolders left behind.

## Tags
For each note, tags should also be created in the form of a header in the .md file. The format of the header with tags 
should be like obsidian-friendly properties. These tags need to be concise and logical, and the set of tags can also be 
dynamic depending on the content. Some tags may be added to old notes if new tags are introduced into the system. 
Similarly, some tags may be removed if they become outdated.

The format of tags is in English and, if there are several words, they are separated by an underscore.


## Table of contents
There should also be a "TOC.md" file in the documents folder. This file should contain a table of contents, that is, the 
entire hierarchy present in the "documents" folder. Correspondingly, the hierarchy should be listed along with any 
necessary comments about particular folders, such as what a given folder is intended to contain. This file can be used 
by you yourself to navigate the hierarchy more effectively and, for example, to find a suitable place to add notes. 
Likewise, it can also serve as a clear overview of the hierarchy for users. Therefore, this file should be updated after 
each addition of a note or any changes to the folder structure.

This Table of Contents file should also contain a list of all the tags used in the system and should also be updated if 
necessary.

If the current notes tree, tags, or `TOC.md` may have drifted after manual edits, deletions, renames, or moves, use 
`system-inconsistencies-revision` before making broader structural changes.

If the tag list in `TOC.md` becomes long or hard to scan, use `toc-tag-grouping` to organize it into meaningful groups.

When adding new tags during normal note creation or editing, place them into the most appropriate existing group in 
`TOC.md` when possible. If no good group exists, create a new one instead of extending an unstructured flat list.

If `TOC.md` becomes too long, too flat, or too verbose for everyday navigation, use `toc-navigation-structure` to make 
it more hierarchical, linked, and concise.
