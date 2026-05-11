# Requirements Checklist

Use this checklist after reading and decomposing the user's source material. Present recommendations first, then ask the user to confirm or modify them. Do not proceed to final prompt documents until the user confirms.

When the user writes in Chinese, present this confirmation set in Chinese.

## Bundled Confirmation Template

```markdown
I have analyzed the source material and recommend the following PPT requirements. Please confirm, or edit any item directly:

1. Canvas format: 16:9 landscape / 4:3 / vertical / other
2. Page count range: recommended X-Y pages; any hard page count or defense duration
3. Scenario: project proposal defense / academic defense / business roadshow / work report / other
4. Target audience: leaders and decision makers / expert reviewers / investors / technical team / mixed audience
5. Narrative arc: for example "background and pain point -> core concepts -> solution architecture -> tasks and metrics -> proof and foundation -> value and recommendation"
6. Style objective: academic and rigorous / technology-government / consulting report / brand launch / clean business / other
7. Color scheme: main color, secondary color, accent color; whether to follow a reference master
8. Typography plan: Chinese and English font preferences; title/body hierarchy
9. Icon approach: line icons / solid icons / system UI icons / minimal icons
10. Image approach: AI-generated visuals / data charts / real photos / abstract backgrounds / mixed
11. PPT master or reference: whether the user will upload a PPT master, brand guide, or existing deck
12. Speech script: total speaking duration, speaker identity, tone, and whether to output per-slide script, full continuous script, or both
13. Output format: PPTX, two prompt documents, per-slide images, speech script, and whether speaker notes are needed
14. Editability: image-only slides / image background plus editable text / mostly native editable PPT
15. Safety boundary: any confidential, sensitive, forbidden, or abstract-only content
```

## Recommendation Rules

- Infer sensible defaults from the source. Do not ask the user to fill a blank form.
- If source content is dense or technical, recommend fewer words per slide and more visual decomposition.
- If the user gives a PPT master/template, prioritize its canvas ratio, typography, title treatment, color system, divider style, and footer/page-number behavior.
- For project defense decks, prefer a leadership-friendly arc: why it matters, what it is, what will be built, what indicators prove it, why the team can deliver, and what value or decision is requested.
- For sensitive defense or security content, recommend abstract system diagrams, dashboards, maps, sensor icons, warning markers, and silhouettes rather than realistic equipment details.
- For speech scripts, recommend a realistic duration based on page count. As a default, use 45-90 seconds per content-heavy slide and 15-30 seconds for cover,目录, transition, and ending slides.
