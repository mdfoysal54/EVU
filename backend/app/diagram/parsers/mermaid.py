from .mermaid_impl import MermaidParser


class SafeMermaidParser:
    @staticmethod
    def parse(source: str):
        return MermaidParser().parse(source)


__all__ = ["MermaidParser", "SafeMermaidParser"]
