---
name: make-ppt-from-source
description: Create a complete PPT production workflow from user-provided data sources for project defense, proposal defense, roadshow, reporting, academic defense, or other structured presentation tasks. Use when the user asks to upload or provide PPT source data, analyze and decompose the material, confirm PPT requirements and optional reference master/template, generate a full deck-planning prompt document plus per-slide AI image prompts, call an AI image model such as image2 to render slides page by page, assemble the rendered images into a PPT/PPTX file, and generate a matching presentation speech script from the final PPT and original data source.
---

# Make PPT From Source

## Overview

Use this skill to turn source materials into a complete image-based PPT deck workflow. Match the user's language in all user-facing outputs. For Chinese users, write the prompt documents and final status in Chinese.

The required outputs are:

1. A deck-level prompt document modeled after a complete project-defense PPT prompt.
2. A per-slide AI drawing prompt document modeled after a page-by-page image prompt guide.
3. One rendered 16:9 image per slide, generated sequentially with `image2` or the available equivalent image-generation tool.
4. A PPT/PPTX assembled from the rendered slide images, using a reference master/template when the user provides one.
5. A matching presentation speech script generated from the final PPT and original source data.

## Workflow

### 1. Collect Source Data

If the user has not provided source material, stop and ask them to upload it. Accept DOCX, PDF, PPTX, Markdown, text, spreadsheets, images, URLs, or pasted notes.

When files are provided:

- Extract the text and tables into a working Markdown source.
- Preserve document titles, headings, tables, metrics, formulas, definitions, project names, stakeholder names, and source filenames.
- Treat user-provided PPT/PPTX files as either source content or a visual/master reference; ask which role they should play if unclear.
- For sensitive or defense-related content, keep visuals abstract and system-oriented. Do not create realistic weapon details, attack scenes, classified deployment diagrams, or operational instructions.

### 2. Analyze And Decompose

Read the source before asking detailed questions. Produce a concise internal decomposition:

- Topic and project name.
- Presentation scenario and likely audience.
- Core problem, value proposition, evidence, solution, tasks, indicators, team/foundation, budget/benefit, and next-step recommendation.
- Candidate narrative arc.
- Candidate page count and page groups.
- Visual risks: dense tables, sensitive content, ambiguous claims, missing data, or pages needing charts.

### 3. Confirm Requirements

Read `references/requirements-checklist.md`, then present one bundled recommendation set to the user and wait for explicit confirmation or edits before writing the final prompt documents.

Always include the `ppt-master`-style core confirmations:

- Canvas format.
- Page count range.
- Target audience.
- Style objective.
- Color scheme.
- Icon usage approach.
- Typography plan.
- Image usage approach.

Also ask whether the user has a PPT master/template/reference deck to upload. If a template is provided, use it as the visual style and layout reference unless the user says it is source content only.

### 4. Generate The Two Prompt Documents

Read `references/prompt-documents.md`.

Create a project working folder and save both documents there, preferably as Markdown first:

- `ppt_complete_prompt.md`
- `per_slide_image_prompts.md`

Use Chinese filenames too when the user explicitly wants the output filenames to mirror Chinese reference documents. Export to DOCX when the user asks for Word files or when the workflow expects DOCX deliverables.

The deck-level prompt document must include:

- Usage notes.
- A directly reusable total prompt.
- Overall structure and narrative thread.
- A page-by-page plan where every page includes: page number and title, page objective, slide body copy, visual presentation suggestion, and speaker-script points.

The per-slide AI drawing prompt document must include:

- Unified drawing specification.
- Universal negative prompt.
- For every slide: slide title, AI drawing prompt, image keywords, and negative prompt.

### 5. Generate Slide Images

Use the confirmed prompt documents as the only source of slide image generation instructions.

- Generate images sequentially by slide number.
- Use `image2` when available. If the session exposes only another image-generation tool, use the closest available equivalent and state the substitution.
- Use 16:9 landscape output, preferably 3840x2160 or 1920x1080.
- Keep text sparse in generated images. Use large labels, diagrams, charts, dashboards, matrices, flow diagrams, maps, and abstract system visuals.
- Save files with stable names such as `slide_001.png`, `slide_002.png`, etc.
- After each image, check whether the rendered page follows the prompt, is legible, and is safe. Regenerate or adjust the prompt when necessary.

### 6. Assemble The PPT

Create a PPT/PPTX using one full-slide image per page.

- If the user provided a reference PPT master/template, preserve its slide size, theme, and master style when possible, then place each generated image full-bleed on a blank layout.
- If no template is provided, create a 16:9 deck.
- Maintain the same slide order and titles as the two prompt documents.
- Add speaker notes from the deck-level prompt document when the available PPT tooling supports notes.
- If the user asks for editable text, create editable title/body overlays or switch to a native-PPT/SVG workflow instead of image-only slides.

### 7. Generate The Speech Script

Read `references/speaker-script.md`.

Generate the speech script after the PPT/PPTX exists, not before. Use the final PPT slide order, the deck-level page plan, the rendered slide images when available, and the original data source.

The script must:

- Match the confirmed audience, scenario, tone, and time limit.
- Follow the final slide order exactly.
- Explain what the audience sees on each slide, but not merely read the slide text.
- Restore important source-data logic that may have been compressed on the visual slide.
- Include transitions between sections and slides.
- Highlight decision points, risks, quantitative indicators, and conclusions.
- Keep sensitive content at the same abstraction level used in the PPT.

Save the script as `presentation_speech_script.md` by default. Export to DOCX when the user asks for Word output.

### 8. Final QA

Before returning the deck, check:

- Slide count matches the prompt documents.
- All images are present and ordered correctly.
- No slide is blank, distorted, cropped incorrectly, or visibly low-resolution.
- Important text is legible and not overcrowded.
- The template/master style, if provided, is reflected.
- The speech script matches the final PPT slide count and sequence.
- The speech script is grounded in the original data source and does not invent claims.
- Sensitive content is represented abstractly and safely.
- Output files are clearly named and located in the project folder.

## Output To User

Return the PPT/PPTX path, the two prompt document paths, the slide image folder, and the speech-script path. Briefly summarize page count, style, speaking duration, and any substitutions or unresolved limitations, such as missing notes support or unavailable `image2`.
