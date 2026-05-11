# Prompt Document Specifications

Generate two prompt documents after the user confirms requirements. Match the user's language. For Chinese users, use Chinese section titles and Chinese body text.

## Document 1: Deck-Level Complete Prompt

Use this structure:

```markdown
# [PPT topic] complete prompt

Based on the user's uploaded data source; constrained by the confirmed PPT requirements and any reference master.

## 1. Usage Notes

- Document role: This is not the final PPT. It is a complete prompt that can be copied into a PPT-generation AI, given to a PPT planner, or used by the next production step.
- Content source: Use only the uploaded data source for content. Use any reference master only for visual style, layout, and expression standards.
- Defense audience: [target audience]
- Hard constraints: [page count, duration, canvas, style, safety boundary, required coverage]

## 2. Directly Reusable Total Prompt

Act as a "[scenario] PPT planning expert, [domain] expression editor, and [technical/industry advisor when useful]". Based on the content of "[source name]", generate a PPT content plan suitable for [defense/report/roadshow].

Strictly follow this logic: "[narrative arc]".

Do not write the PPT like an essay or paper. Use short phrases, visual structure, and concise bullets. Split complex tables across pages or convert them into matrices, flowcharts, indicator cards, or architecture diagrams.

Every page must output: page number and title, page objective, slide body copy, visual presentation suggestion, and speaker-script points.

Overall style: [style, colors, typography hierarchy, chart density, master requirements]

## 3. Overall Structure And Narrative Thread

- Layer 1: [why it is needed]
- Layer 2: [what the system/solution is]
- Layer 3: [what it can do or how it works]
- Layer 4: [why it can be delivered or what evidence supports it]
- Layer 5: [value, decision request, or implementation path]

## 4. Page-By-Page PPT Prompt Body

### Page 1: [title]

Page objective: [one sentence]

Slide body copy:

- [short bullet 1]
- [short bullet 2]
- [short bullet 3]

Visual presentation suggestion: [recommended graphic, composition, chart, image, whitespace, and emphasis]

Speaker-script points: [natural presenter notes]
```

Repeat the page block for every slide.

The `speaker-script points` field is not the final speech script. It is a compact planning field that will later be expanded after the final PPT exists.

## Document 2: Per-Slide AI Drawing Prompts

Use this structure:

```markdown
# Per-slide AI drawing prompts

For generating PPT diagrams, backgrounds, and infographics for [PPT topic].

## 1. Unified Drawing Specification

- Canvas: 16:9 landscape PPT, preferably 3840x2160 or 1920x1080.
- Style: [confirmed style]; main color [main color], secondary color [secondary color], accent color [accent color].
- Typography: clear sans-serif style; strong title hierarchy; enough whitespace.
- Visual principle: avoid long paragraphs; express ideas through architecture diagrams, flowcharts, matrices, indicator cards, map grids, system UI, data charts, and abstract scenes.
- Safety expression: [abstract-expression rules for sensitive content; if none, say there are no special limits but still avoid misleading or dangerous visuals.]
- Universal negative prompt: no dense tiny text, no messy layout, no low resolution, no excessive glow, no unrelated elements, [project-specific negatives].

## Page 1: [title]

AI drawing prompt:
[Full natural-language prompt. Include canvas, style, theme, core visual, points to express, composition requirements, and text-density requirements.]

Image keywords: [keyword 1], [keyword 2], [keyword 3], [keyword 4]

Negative prompt: [page-specific negatives; inherit the universal negative prompt]
```

Repeat the page block for every slide.

## Quality Rules

- Each page prompt must be self-contained. Do not require the image model to remember previous pages.
- Keep generated-slide text minimal. The PPT can carry precise text later; image generation should carry layout, diagrams, background, and large labels.
- For chart pages, specify chart type, axis meaning, key values, and desired visual hierarchy.
- For cover pages, make the project name the first-viewport signal.
- For summary or ending pages, use closure diagrams such as value loops, roadmaps, decision requests, or implementation paths.
- Avoid generic stock-photo wording. Describe the actual system, scene, product, dataset, or argument.
