from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from .utils import ensure_bg
from ..ppt_builder import load_theme

def render(prs, routed_content):
    theme = load_theme()
    for slide_spec in routed_content.slides:
        slide = prs.slides.add_slide(prs.slide_layouts[6])
        ensure_bg(slide, theme)

        # 标题
        title = "事件时间线"
        from ..ppt_builder import add_title
        add_title(prs, theme, title)

        # 在当前最后一页拿到 slide
        slide = prs.slides[-1]

        # 画时间轴：简单水平线 + 若干节点
        left = Inches(1); right = Inches(11) - Inches(1)
        mid_y = Inches(4)
        line = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.RECTANGLE, left, mid_y, right-left, Inches(0.05))
        line.fill.solid(); line.fill.fore_color.rgb = theme.colors["sub"]; line.line.fill.background()

        events = slide_spec["events"]
        n = max(1, len(events))
        span = (right - left) / n
        for i, ev in enumerate(events):
            cx = left + span*i + span/2
            # 节点
            dot = slide.shapes.add_shape(MSO_AUTO_SHAPE_TYPE.OVAL, cx - Inches(0.08), mid_y - Inches(0.08), Inches(0.16), Inches(0.16))
            dot.fill.solid(); dot.fill.fore_color.rgb = theme.colors["accent"]; dot.line.fill.background()
            # 文本
            tb = slide.shapes.add_textbox(cx - Inches(1.2), mid_y - Inches(1.2), Inches(2.4), Inches(1.1))
            p0 = tb.text_frame.paragraphs[0]; p0.text = ev["date"]; p0.font.size = Pt(theme.sizes["body_pt"]); p0.font.color.rgb = theme.colors["sub"]; p0.alignment = PP_ALIGN.CENTER
            p = tb.text_frame.add_paragraph(); p.text = ev["headline"]; p.font.size = Pt(theme.sizes["h2_pt"]); p.font.name = theme.fonts["body"]; p.font.color.rgb = theme.colors["text"]; p.alignment = PP_ALIGN.CENTER
            if ev.get("detail"):
                p2 = tb.text_frame.add_paragraph(); p2.text = ev["detail"]; p2.font.size = Pt(theme.sizes["body_pt"]); p2.font.color.rgb = theme.colors["sub"]; p2.alignment = PP_ALIGN.CENTER
