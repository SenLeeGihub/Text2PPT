import json
import yaml
from pathlib import Path
from typing import Dict, Any
from openai import OpenAI
from pydantic import BaseModel, Field, ValidationError

HERE = Path(__file__).parent

SYSTEM_PROMPT = """\
你是一名资深幻灯片编辑。给你一条新闻文本，请你：
1) 判断最合适的 PPT 排版（在给定 layouts.yaml 中 enabled=true 的集合内选择）
2) 严格生成 JSON（UTF-8，无注释），字段只用到所选布局定义的 needs
3) 所有文本简洁、适合演示，不能输出解释文字

可选布局：
- news_report: 适合新闻快讯类内容，输出：
    {
        "layout": "news_report",
          "slides": [{
            "header_title": "大标题",
            "summary": {
              "label": "洞察启示",
              "bullets": [
                "2-3条，每条必须是【总结：解释】的格式，例如：\
        - 模型为先的三元飞轮：模型×算力×生态协同，形成持续优势。"
              ]
            },
            "left": {
              "title": "左列主标题",
              "sections": [
                {"subtitle_bold": "小节1", "bullets": ["最多4条，每条两到三句话，要表达清楚观点和依据"]},
                {"subtitle_bold": "小节2", "bullets": ["..."]},
                {"subtitle_bold": "小节3", "bullets": ["..."]}
              ]
            },
            "right": {
              "title": "右列主标题",
              "sections": [
                {"subtitle_bold": "小节A", "bullets": ["最多4条，每条两到三句话，要表达清楚观点和依据"]},
                {"subtitle_bold": "小节B", "bullets": ["..."]},
                {"subtitle_bold": "小节C", "bullets": ["..."]}
              ]
            }
          }]
    }
- timeline: 适合有明确时间顺序的新闻
- summary: 适合要点总结
- image_headline: 适合有大图 + 标题的展示

注意：
- summary.bullets 必须 2–4 条，且每条必须是【总结：解释】的格式。
  - 总结部分简短（3-8个字），后面冒号后的解释可以较长，提供背景、因果、趋势。
  - 例如：
    - 模型为先的三元飞轮：模型（护城河）×算力（放大器）×AI原生硬件/生态（分发与数据回流）联动，形成持续优势。
    - 组织与资本结构为扩张让路：PBC改制+融资+微软分成调整，形成长期弹药，匹配硬件/机器人重资产周期。
- 每个 section.bullets 语言要相对标题长一些，但不要过长，可以包含背景/因果/趋势推演，而不是简短词组。
- subtitle_bold 用于渲染成“□ 【标题】”，保持简洁。
- 新闻文本 → 默认优先 news_report 布局
- 输出必须是 JSON 对象，不要有注释、不要加 Markdown 包裹
"""

# ========== Schema ==========
class Section(BaseModel):
    subtitle_bold: str
    bullets: list[str]

class Column(BaseModel):
    title: str
    sections: list[Section]

class Reference(BaseModel):
    label: str
    url: str | None = None

class Summary(BaseModel):
    label: str
    bullets: list[str]

class Slide(BaseModel):
    header_title: str
    brand_tag: str | None = None
    summary: Summary
    left: Column
    right: Column
    references: list[Reference] | None = None

class RoutedContent(BaseModel):
    layout: str
    slides: list[Slide]

# ========== 加载模板配置 ==========
def load_layouts() -> Dict[str, Any]:
    with open(HERE / "templates" / "layouts.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ========== 主函数 ==========
def choose_and_structure(news_text: str, model: str = "o4-mini") -> RoutedContent:
    layouts_cfg = load_layouts()
    enabled_layouts = [k for k, v in layouts_cfg["layouts"].items() if v.get("enabled", False)]

    client = OpenAI()
    user_prompt = f"""\
可用布局: {', '.join(enabled_layouts)}
原始新闻：
\"\"\"{news_text.strip()}\"\"\""""

    resp = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
    )

    text = resp.output_text
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"AI 输出的不是合法 JSON: {e}\n内容: {text[:300]}...")

    # 校验结构
    try:
        routed = RoutedContent(**data)
    except ValidationError as e:
        raise ValueError(f"生成 JSON 缺字段或格式错误: {e}")

    # 强制检查
    for slide in routed.slides:
        if not (3 <= len(slide.summary.bullets) <= 6):
            raise ValueError("summary.bullets 必须 3-6 条")
        if len(slide.left.sections) < 2 or len(slide.right.sections) < 2:
            raise ValueError("left/right.sections 必须至少 2 组")
        for sec in slide.left.sections + slide.right.sections:
            if not sec.subtitle_bold:
                raise ValueError("每个 section 必须有 subtitle_bold")

    return routed