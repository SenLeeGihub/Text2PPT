import argparse
from pathlib import Path
from typing import Optional
from pptx import Presentation
from config import AppConfig
from llm_router import choose_and_structure
from generator.ppt_builder import load_theme, new_presentation
from generator.layouts import timeline as L_timeline
from generator.layouts import summary as L_summary
from generator.layouts import image_headline as L_img
from generator.layouts import news_report as L_news

LAYOUT_IMPL = {
    "timeline": L_timeline.render,
    "summary": L_summary.render,
    "image_headline": L_img.render,
    "news_report": L_news.render,   # 新增
}

def run(news_text: str, model: str, out_file: str, layout: Optional[str]):
    routed = choose_and_structure(news_text, model=model, forced_layout=layout)  # LLM selects layout + structures JSON
    theme = load_theme()
    prs = new_presentation(theme)

    if routed.layout not in LAYOUT_IMPL:
        raise SystemExit(f"未实现布局: {routed.layout}")

    # 渲染
    LAYOUT_IMPL[routed.layout](prs, routed)

    prs.save(out_file)
    print(f"✅ 已生成: {out_file}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--news_file", type=str, default="examples/sample_news.txt")
    ap.add_argument("--model", type=str, default=AppConfig.model)
    ap.add_argument("--layout", type=str, choices=sorted(LAYOUT_IMPL.keys()), default=None, help="Force a specific layout; leave empty to let AI decide")
    ap.add_argument("--out", type=str, default=AppConfig.out_file)
    args = ap.parse_args()

    text = Path(args.news_file).read_text(encoding="utf-8")
    run(text, args.model, args.out, args.layout)

