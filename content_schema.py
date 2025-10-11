from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class Reference(BaseModel):
    label: str
    url: Optional[str] = None

    @field_validator("label")
    @classmethod
    def _label_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("reference.label must be a non-empty string")
        return value.strip()

    @field_validator("url")
    @classmethod
    def _trim_url(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None


class Summary(BaseModel):
    label: str
    bullets: List[str]

    @field_validator("label")
    @classmethod
    def _label_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("summary.label must be a non-empty string")
        return value.strip()

    @field_validator("bullets")
    @classmethod
    def _validate_bullets(cls, bullets: List[str]) -> List[str]:
        cleaned = [b.strip() for b in bullets if b and b.strip()]
        if not (3 <= len(cleaned) <= 6):
            raise ValueError("summary.bullets must contain between 3 and 6 non-empty entries")
        return cleaned


class Section(BaseModel):
    subtitle_bold: str
    bullets: List[str]

    @field_validator("subtitle_bold")
    @classmethod
    def _subtitle_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("section.subtitle_bold must be a non-empty string")
        return value.strip()

    @field_validator("bullets")
    @classmethod
    def _section_bullets(cls, bullets: List[str]) -> List[str]:
        cleaned = [b.strip() for b in bullets if b and b.strip()]
        if len(cleaned) < 3:
            raise ValueError("section.bullets should contain at least three items")
        return cleaned[:6]


class Column(BaseModel):
    title: str
    sections: List[Section]

    @field_validator("title")
    @classmethod
    def _title_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("column.title must be a non-empty string")
        return value.strip()

    @field_validator("sections")
    @classmethod
    def _min_sections(cls, sections: List[Section]) -> List[Section]:
        if len(sections) < 2:
            raise ValueError("each column must include at least two sections")
        return sections


class NewsReportSlide(BaseModel):
    header_title: str
    brand_tag: Optional[str] = None
    summary: Summary
    left: Column
    right: Column
    references: Optional[List[Reference]] = None

    @field_validator("header_title")
    @classmethod
    def _header_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("header_title must be a non-empty string")
        return value.strip()


class TimelineEvent(BaseModel):
    date: str = Field(..., description="Time label displayed on the fishbone spine")
    headline: str
    detail: Optional[str] = None

    @field_validator("date")
    @classmethod
    def _date_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("timeline event date must be provided")
        return value.strip()

    @field_validator("headline")
    @classmethod
    def _headline_not_empty(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("timeline event headline must be a non-empty string")
        return value.strip()

    @field_validator("detail")
    @classmethod
    def _detail_trim(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        return trimmed or None


class TimelineAnalysis(BaseModel):
    table_headers: Optional[List[str]] = None
    table_rows: Optional[List[List[str]]] = None
    key_points: Optional[List[str]] = None

    @field_validator("table_headers")
    @classmethod
    def _clean_headers(cls, headers: Optional[List[str]]) -> Optional[List[str]]:
        if not headers:
            return None
        cleaned = [h.strip() for h in headers if h and h.strip()]
        return cleaned[:4] or None

    @field_validator("table_rows")
    @classmethod
    def _clean_rows(cls, rows: Optional[List[List[str]]]) -> Optional[List[List[str]]]:
        if not rows:
            return None
        cleaned: list[list[str]] = []
        for row in rows:
            if not isinstance(row, list):
                continue
            cells = [str(c).strip() for c in row]
            if any(cells):
                cleaned.append(cells)
        return cleaned[:6] or None

    @field_validator("key_points")
    @classmethod
    def _clean_points(cls, points: Optional[List[str]]) -> Optional[List[str]]:
        if not points:
            return None
        cleaned = [p.strip() for p in points if p and p.strip()]
        return cleaned[:6] or None

    @model_validator(mode="after")
    def _align_rows(self) -> "TimelineAnalysis":
        headers = self.table_headers or []
        width = len(headers) if headers else 0
        if self.table_rows:
            aligned: list[list[str]] = []
            for row in self.table_rows:
                if width:
                    padded = row + [""] * max(0, width - len(row))
                    aligned.append(padded[:width])
                else:
                    aligned.append(row)
            self.table_rows = aligned
        return self


class TimelineSlide(BaseModel):
    title: Optional[str] = None
    header_title: Optional[str] = None
    heading: Optional[str] = None
    events: List[TimelineEvent]
    analysis: Optional[TimelineAnalysis] = None

    @field_validator("events")
    @classmethod
    def _event_count(cls, events: List[TimelineEvent]) -> List[TimelineEvent]:
        if not (3 <= len(events) <= 8):
            raise ValueError("timeline slides require between 3 and 8 events")
        return events


class RoutedNewsReport(BaseModel):
    layout: str
    slides: List[NewsReportSlide]

    @field_validator("layout")
    @classmethod
    def _layout_match(cls, value: str) -> str:
        if value != "news_report":
            raise ValueError("RoutedNewsReport expects layout='news_report'")
        return value


class RoutedTimeline(BaseModel):
    layout: str
    slides: List[TimelineSlide]

    @field_validator("layout")
    @classmethod
    def _layout_match(cls, value: str) -> str:
        if value != "timeline":
            raise ValueError("RoutedTimeline expects layout='timeline'")
        return value
