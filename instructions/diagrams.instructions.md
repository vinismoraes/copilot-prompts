---
applyTo: "**"
description: Use Mermaid syntax for all diagrams and flowcharts
---

# Diagrams

- Always use **Mermaid** syntax when creating diagrams, flowcharts, or sequence diagrams
- Prefer `sequenceDiagram` for API/service flows and `flowchart` for decision trees

## Label formatting

- Keep labels **short** — max ~5 words per line
- **Never** use `\n` inside node labels — Mermaid renders it inconsistently
- If a label needs two lines, split into a main label and a note, or use `<br/>` inside quotes: `["Line one<br/>Line two"]`
- Avoid long descriptions in nodes — move detail to notes or surrounding text

## Layout

- Use `flowchart TD` (top-down) by default; use `LR` (left-right) only for simple linear flows
- Declare all nodes first, then edges — keeps the source readable
- Avoid more than 6-8 nodes per diagram; split complex flows into multiple diagrams
- Don't nest subgraphs more than one level deep
