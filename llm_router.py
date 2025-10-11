import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from openai import OpenAI
from pydantic import ValidationError

from content_schema import RoutedNewsReport, RoutedTimeline

HERE = Path(__file__).parent
PROMPT_DIR = HERE / "templates" / "prompts"


@dataclass
class RoutedContent:
    layout: str
    slides: List[dict]


def _read_prompt(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8").strip()


def build_system_prompt(enabled_layouts: List[str]) -> str:
    base_prompt = _read_prompt(PROMPT_DIR / "base.md")
    if not base_prompt:
        raise FileNotFoundError(f"Missing base prompt file at {PROMPT_DIR / 'base.md'}")

    sections = [base_prompt]
    for layout in enabled_layouts:
        section = _read_prompt(PROMPT_DIR / f"{layout}.md")
        if section:
            sections.append(section)
    return "\n\n".join(part for part in sections if part)


def load_layouts() -> Dict[str, Any]:
    with open(HERE / "templates" / "layouts.yaml", "r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


LAYOUT_VALIDATORS = {
    "news_report": RoutedNewsReport,
    "timeline": RoutedTimeline,
}


def _fill_bullets(source, minimum: int, placeholder: str) -> List[str]:
    cleaned = [str(item).strip() for item in (source or []) if str(item).strip()]
    if not cleaned:
        cleaned = [placeholder]
    cleaned = cleaned[:6]
    while len(cleaned) < minimum:
        cleaned.append(cleaned[-1])
    return cleaned


def _coerce_news_report_payload(data: dict) -> dict:
    slides = data.get("slides")
    if not isinstance(slides, list):
        return data
    placeholder = "待补充"
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        summary = slide.get("summary") or {}
        summary_bullets = _fill_bullets(summary.get("bullets"), 3, placeholder)
        summary["bullets"] = summary_bullets
        slide["summary"] = summary
        for side, label in (("left", "左列"), ("right", "右列")):
            column = slide.get(side) or {}
            sections = [sec for sec in (column.get("sections") or []) if isinstance(sec, dict)]
            while len(sections) < 2:
                sections.append({
                    "subtitle_bold": f"{label}补充{len(sections) + 1}",
                    "bullets": summary_bullets[:3],
                })
            for idx, section in enumerate(sections):
                section["bullets"] = _fill_bullets(section.get("bullets"), 3, placeholder)
                if not section.get("subtitle_bold"):
                    section["subtitle_bold"] = f"{label}要点{idx + 1}"
            column["sections"] = sections[:6]
            if not column.get("title"):
                column["title"] = f"{label}要点"
            slide[side] = column
    return data


def _coerce_timeline_payload(data: dict) -> dict:
    slides = data.get("slides")
    if not isinstance(slides, list):
        return data
    for slide in slides:
        if not isinstance(slide, dict):
            continue
        events = [ev for ev in (slide.get("events") or []) if isinstance(ev, dict)]
        if not events:
            continue
        for idx, event in enumerate(events, start=1):
            date_raw = str(event.get("date", "")).strip()
            if not date_raw:
                event["date"] = f"日期缺失-事件{idx}"
            else:
                event["date"] = date_raw
            headline_raw = str(event.get("headline", "")).strip()
            if not headline_raw:
                event["headline"] = f"事件{idx}"
            else:
                event["headline"] = headline_raw
            detail_raw = event.get("detail")
            if detail_raw is not None:
                trimmed = str(detail_raw).strip()
                event["detail"] = trimmed or None
        slide["events"] = events[:8]
    return data


def choose_and_structure(news_text: str, model: str = "o4-mini", forced_layout: Optional[str] = None) -> RoutedContent:
    layouts_cfg = load_layouts()
    available_layouts = layouts_cfg.get("layouts", {})

    if forced_layout:
        if forced_layout not in available_layouts:
            raise ValueError(f"Unknown layout '{forced_layout}' requested via --layout")
        enabled_layouts = [forced_layout]
    else:
        enabled_layouts = [name for name, cfg in available_layouts.items() if cfg.get("enabled", False)]
        if not enabled_layouts:
            raise ValueError("No layouts are enabled in templates/layouts.yaml")

    system_prompt = build_system_prompt(enabled_layouts)

    client = OpenAI()
    user_prompt = (
        "可选布局: "
        + ", ".join(enabled_layouts)
        + "\n请阅读以下新闻并返回 JSON:\n\"\"\""
        + news_text.strip()
        + "\"\"\""
    )

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_output = response.output_text

    try:
        data = json.loads(raw_output)
    except json.JSONDecodeError as exc:
        snippet = raw_output[:300].replace("\n", " ")
        raise ValueError(f"AI response is not valid JSON: {exc}. Snippet: {snippet}...") from exc

    layout = data.get("layout")
    if not isinstance(layout, str) or not layout:
        raise ValueError("AI response must include a non-empty 'layout' field")

    if forced_layout and layout != forced_layout:
        raise ValueError(f"AI response layout '{layout}' did not match forced layout '{forced_layout}'")

    if layout == "news_report":
        data = _coerce_news_report_payload(data)
    elif layout == "timeline":
        data = _coerce_timeline_payload(data)

    slides_payload = data.get("slides")
    if not isinstance(slides_payload, list):
        raise ValueError("AI response must include a 'slides' array")

    validator = LAYOUT_VALIDATORS.get(layout)
    if validator:
        try:
            validated = validator(**data)
        except ValidationError as exc:
            raise ValueError(f"AI JSON failed validation for layout '{layout}': {exc}") from exc
        slides = [slide.model_dump(mode="python") for slide in validated.slides]
    else:
        slides = slides_payload

    return RoutedContent(layout=layout, slides=slides)
