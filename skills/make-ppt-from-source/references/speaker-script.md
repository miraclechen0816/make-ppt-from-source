# Speaker Script Specification

Generate the speech script after the final PPT/PPTX has been assembled. The script must be grounded in both the final PPT and the original data source.

## Inputs

Use these inputs in priority order:

1. Final PPT/PPTX slide order and slide titles.
2. Deck-level prompt document, especially page objectives, body copy, visual suggestions, and speaker-script points.
3. Rendered slide images, when available, to understand what the audience will see.
4. Original source data, to recover accurate logic, evidence, definitions, and numbers.
5. User-confirmed audience, duration, tone, and safety boundaries.

## Output Files

Save Markdown by default:

- `presentation_speech_script.md`

When the user wants Chinese filenames, use:

- `PPT配套演讲稿.md`

Export to DOCX when requested.

## Recommended Structure

```markdown
# [PPT topic] presentation speech script

## 1. Speaking Setup

- Scenario:
- Audience:
- Recommended duration:
- Speaker tone:
- Core message:

## 2. Full Continuous Script

[A complete, natural spoken script from opening to closing. Include section transitions.]

## 3. Slide-By-Slide Script

### Slide 1: [title]

- Suggested time: [seconds/minutes]
- Speaking objective: [one sentence]
- Script:
  [Natural spoken text. Do not merely read the slide.]
- Transition:
  [One or two sentences leading to the next slide.]

## 4. Key Q&A Preparation

- Likely question:
  Recommended answer:
```

## Writing Rules

- Match the user's language.
- Do not copy slide bullets mechanically. Explain why each slide matters.
- Keep a spoken, confident, and concise style suitable for the audience.
- Restore context that was simplified on the PPT, but do not overload the script with every source detail.
- Use exact numbers, project names, and technical terms only when they appear in the source or final PPT.
- Flag unclear or missing data instead of inventing it.
- For leadership or review settings, emphasize decision logic: necessity, feasibility, value, risk control, and implementation path.
- For technical expert settings, add more mechanism, indicator, method, and evidence explanation.
- For sensitive content, keep wording abstract and aligned with the PPT's safety boundary.

## Timing Rules

- If the user gives a target duration, distribute time across slides and keep the script within that target.
- If no target duration is provided, estimate duration from page count and scenario.
- Use 15-30 seconds for cover,目录, transition, and ending slides.
- Use 45-90 seconds for content-heavy slides.
- For long decks, group adjacent pages into sections in the full continuous script while still preserving slide-by-slide notes.
