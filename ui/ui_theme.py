from typing import Dict, Tuple
import pygame

from .font_manager import get_font


_ui_scale = 1.0


PALETTE: Dict[str, Tuple[int, int, int, int]] = {
    "panel_bg": (20, 24, 34, 228),
    "panel_border": (110, 144, 196, 230),
    "title_bg": (38, 56, 86, 240),
    "title_text": (232, 240, 255, 255),
    "body_text": (210, 218, 232, 255),
    "muted_text": (164, 176, 196, 255),
    "accent": (132, 198, 255, 255),
    "success": (120, 220, 160, 255),
    "warning": (255, 210, 126, 255),
}


FONT_BASE = {
    "title": 24,
    "section": 18,
    "body": 15,
    "small": 13,
}


LINE_HEIGHT = {
    "title": 1.35,
    "section": 1.45,
    "body": 1.52,
    "small": 1.5,
}


def set_ui_scale(scale: float):
    global _ui_scale
    _ui_scale = max(0.75, min(1.6, float(scale)))


def get_ui_scale() -> float:
    return _ui_scale


def ui(value: float) -> int:
    return max(1, int(round(value * _ui_scale)))


def font(role: str, bold: bool = False) -> pygame.font.Font:
    size = FONT_BASE.get(role, FONT_BASE["body"])
    return get_font(ui(size), bold=bold)


def line_height(role: str) -> int:
    ratio = LINE_HEIGHT.get(role, 1.5)
    return max(1, int(font(role).get_height() * ratio))


def draw_panel(surface: pygame.Surface, width: int, height: int, title: str, subtitle: str = "") -> pygame.Rect:
    radius = ui(14)
    pygame.draw.rect(surface, PALETTE["panel_bg"], (0, 0, width, height), border_radius=radius)
    pygame.draw.rect(surface, PALETTE["panel_border"], (0, 0, width, height), width=ui(2), border_radius=radius)
    title_h = ui(46)
    pygame.draw.rect(
        surface,
        PALETTE["title_bg"],
        (0, 0, width, title_h),
        border_top_left_radius=radius,
        border_top_right_radius=radius
    )
    title_font = font("title", bold=True)
    title_text = title_font.render(title, True, PALETTE["title_text"][:3])
    surface.blit(title_text, (ui(16), ui(10)))
    if subtitle:
        sub_font = font("small")
        sub_text = sub_font.render(subtitle, True, PALETTE["muted_text"][:3])
        surface.blit(sub_text, (ui(18), ui(10) + title_text.get_height()))
    pygame.draw.line(surface, PALETTE["panel_border"][:3], (ui(12), title_h), (width - ui(12), title_h), 1)
    return pygame.Rect(ui(12), title_h + ui(8), width - ui(24), height - title_h - ui(18))
