from pydantic import BaseModel, Field
from typing import List, Optional

class TimelineEvent(BaseModel):
    date: str = Field(..., description="YYYY-MM-DD 或简要日期")
    headline: str
    detail: Optional[str] = None

class SummarySlide(BaseModel):
    title: str
    bullets: List[str]

class ImageHeadlineSlide(BaseModel):
    title: str
    hero_image: Optional[str] = None  # 本地路径或URL（本地优先）
    caption: Optional[str] = None

class RoutedContent(BaseModel):
    layout: str  # "timeline" | "summary" | "image_headline" | ...
    slides: List[dict]  # 每个布局对应的 schema 字典（见上面）
