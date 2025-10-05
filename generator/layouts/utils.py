from pptx.dml.color import RGBColor

def ensure_bg(slide, theme):
    # 简单填充纯色背景（如需背景图，可在这里实现）
    fill = slide.background.fill
    fill.solid()
    fill.fore_color.rgb = theme.colors["bg"]
