---
name: send-files-to-user
description: "Use when the assistant needs to send a generated file to the user from a containerized OpenCode session. The delivery mechanism is the mounted outbox directory: create a file in the outbox so the surrounding client can list, download, deliver, and remove it. Covers file naming, size, format, and safety constraints."
---

# Send Files to User

Use this workflow when the user should receive a generated file instead of, or in addition to, a text response.

## Contract

Place the file in the mounted `outbox` directory. The surrounding client lists files from `outbox`, downloads each file, delivers it to the user, and deletes it after a successful download.

Use this path pattern:

```text
<mounted-workspace>/outbox/<safe-filename>
```

If the current workspace is `/workspace`, write files under `/workspace/outbox/`.

## Workflow

1. Create the `outbox` directory if it does not exist.
2. Write the deliverable file directly inside `outbox`.
3. Use a safe filename with no slash, backslash, absolute path, `..`, control characters, or quote characters.
4. Verify the file exists and is a regular file.
5. Mention in the final response that the file was placed in `outbox` for delivery.

## Limits

- Keep each file under 50 MB. The current client refuses larger files even though the low-level outbox endpoint itself has no size limit.
- Prefer much smaller files when possible; large files may be slow or rejected by downstream delivery clients.
- Short Markdown files can be delivered as text by some clients; keep user-readable Markdown under 40 lines when you intend it to appear inline. Longer Markdown should be treated as a document.
- Image files such as `.jpg`, `.jpeg`, `.png`, `.gif`, and `.webp` may be delivered as images.
- Audio files such as `.mp3`, `.ogg`, `.wav`, `.flac`, and `.m4a` may be delivered as audio.
- Other file types are delivered as generic documents.

## Safety

- Do not put secrets, credentials, private keys, tokens, `.env` files, or other sensitive data in `outbox` unless the user explicitly requested that exact content and it is safe to share.
- Do not place directories, symlinks, or nested paths in `outbox`; use regular files only.
- If repository instructions restrict normal work to a content subdirectory, keep source content there. Copy only the final deliverable into `outbox` as the delivery step.
- If a file with the same name already exists, choose a new descriptive name unless replacing it is clearly intended.
- Use clear extensions so the client can choose the best delivery type.

## Examples

Create a report for delivery:

```bash
mkdir -p /workspace/outbox
cp documents/reports/weekly-summary.md /workspace/outbox/weekly-summary.md
```

Create an export directly in outbox:

```bash
mkdir -p /workspace/outbox
your-export-command > /workspace/outbox/notes-export.csv
```

Final response:

```text
Prepared `weekly-summary.md` in `outbox` for delivery.
```
