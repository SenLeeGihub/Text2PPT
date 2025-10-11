Layout: timeline
Choose this layout for stories driven by a chronological sequence or milestones. The slide renders as a horizontal fishbone: a central spine with milestone diamonds, alternating callouts above and below, plus an analysis band beneath the spine.

Slide requirements:
- Provide 4-8 `events`, ordered from earliest to latest.
- Each event object must include:
  - `date`: 具体到日的时间标签（例如："2024-09-12"），并且不同事件的日期不能相同。
  - `headline`: 1 short sentence (<= 80 characters) describing the milestone.
  - Optional `detail`: supporting context (<= 120 characters).
- Add an `analysis` object with:
  - `table_headers`: 2-4 short column headers for the follow-up analysis table.
  - `table_rows`: 2-4 rows (each a list) whose cell count matches `table_headers`.
  - `key_points`: 3-6 concise core conclusions  shown to the right of the table.
- Optional slide-level keys `title`, `header_title`, or `heading` can override the default slide title.

Writing hints:
- Focus on causality or progression between events to keep the fishbone narrative clear.
- Keep the table factual—use metrics, stakeholders, or actions to explain the timeline’s implications.
- Express key conclusions as action-oriented statements; avoid speculation.
- Return all text in Chinese.
