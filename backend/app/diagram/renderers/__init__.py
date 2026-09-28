from .html import HTMLRenderer
from .png import PNGRenderer
from .svg import SVGRenderer


RENDERERS = {
    "svg": SVGRenderer,
    "html": HTMLRenderer,
    "png": PNGRenderer,
}


def get_renderer(name: str):
    renderer_class = RENDERERS.get(
        name.lower().strip()
    )

    if renderer_class is None:
        raise ValueError(
            f"Unknown renderer: {name}"
        )

    return renderer_class()


__all__ = [
    "SVGRenderer",
    "HTMLRenderer",
    "PNGRenderer",
    "RENDERERS",
    "get_renderer",
]