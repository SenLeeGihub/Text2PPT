Layout: news_report
Use this layout when the story needs an executive summary plus two detailed columns of supporting sections.

Slide requirements:
- `header_title`: concise headline for the slide.Must be conclusive.
- `summary.label`: label for the red ribbon on the left (1–4 characters recommended).
- `summary.bullets`: 3–6 key takeaways. Keep each bullet under 90 characters.
- `left` and `right` columns must each contain:
  - `title`: short column heading.
  - `sections`: at least 2-3 sections. Each section needs a `subtitle_bold` string and 2–5 `bullets` with 2 sentence.
- Optional `references`: list of `{ "label": str, "url": str | null }` for sources.

Writing hints:
- Bold-facing is applied automatically before the first colon (`:`) in bullets, so include colons for label/value bullets when helpful.
- Balance content between columns; avoid duplicating the same idea in multiple bullets.
- summary.bullets 必须使用“主题：解释”的结构，例如：
  - 行动目的：出于国家安全考量，加拿大政府要求海康威视退出市场。
  - 市场影响：关闭业务加剧西方对中国科技企业的限制趋势。
  - 外交影响：此举可能对中加技术和贸易关系造成紧张。
