from dataclasses import dataclass

@dataclass
class AppConfig:
    model: str = "o4-mini"         # 或其它可用模型
    out_file: str = "out.pptx"     # 输出文件名
