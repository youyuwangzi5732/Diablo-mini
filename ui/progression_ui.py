from typing import Dict, Any, List, Optional
import pygame

from .ui_manager import UIManager
from .ui_theme import draw_panel, font as ui_font, line_height, ui, PALETTE


class ProgressionUI:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        self.visible = False
        self.base_panel_width = 760
        self.base_panel_height = 520
        self.panel_width = self.base_panel_width
        self.panel_height = self.base_panel_height
        self.chapter_history: List[Dict[str, Any]] = []
        self.ending_history: List[Dict[str, Any]] = []
        self.achievements: Dict[str, Dict[str, Any]] = {}
        self.story_flags: Dict[str, str] = {}

    def toggle(self):
        self.visible = not self.visible

    def hide(self):
        self.visible = False

    def set_data(
        self,
        chapter_history: List[Dict[str, Any]],
        ending_history: List[Dict[str, Any]],
        achievements: Dict[str, Dict[str, Any]],
        story_flags: Dict[str, str]
    ):
        self.chapter_history = chapter_history
        self.ending_history = ending_history
        self.achievements = achievements
        self.story_flags = story_flags

    def get_panel_position(self) -> tuple:
        x = (self.screen_width - self.panel_width) // 2
        y = (self.screen_height - self.panel_height) // 2
        return (x, y)

    def _apply_ui_scale(self):
        self.panel_width = ui(self.base_panel_width)
        self.panel_height = ui(self.base_panel_height)

    def update(self, delta_time: float):
        pass

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        self._apply_ui_scale()

        panel_x, panel_y = self.get_panel_position()
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        draw_panel(panel_surface, self.panel_width, self.panel_height, "主线回顾与成就", "圆角一体化面板")

        self._render_title(panel_surface)
        self._render_chapters(panel_surface)
        self._render_endings(panel_surface)
        self._render_achievements(panel_surface)
        self._render_footer(panel_surface)

        surface.blit(panel_surface, (panel_x, panel_y))

    def _render_title(self, surface: pygame.Surface):
        sub_font = ui_font("small")
        alignment = self.story_flags.get("faction_alignment", "未选择")
        surface.blit(sub_font.render(f"当前阵营取向: {alignment}", True, PALETTE["muted_text"][:3]), (ui(20), ui(48)))

    def _render_chapters(self, surface: pygame.Surface):
        title_font = ui_font("section", bold=True)
        text_font = ui_font("small")
        surface.blit(title_font.render("章节回顾", True, (180, 210, 255)), (ui(20), ui(82)))

        y = ui(112)
        for chapter in self.chapter_history[-9:]:
            chapter_name = chapter.get("name", "未知章节")
            summary = chapter.get("summary", "")
            line = f"{chapter_name}: {summary}"
            surface.blit(text_font.render(line[:58], True, (220, 220, 220)), (ui(24), y))
            y += line_height("small")

    def _render_achievements(self, surface: pygame.Surface):
        title_font = ui_font("section", bold=True)
        text_font = ui_font("small")
        surface.blit(title_font.render("长线成就", True, (255, 200, 160)), (ui(390), ui(250)))

        unlocked = [a for a in self.achievements.values() if a.get("unlocked")]
        locked = [a for a in self.achievements.values() if not a.get("unlocked")]

        y = ui(280)
        for ach in unlocked[:8]:
            surface.blit(text_font.render(f"✓ {ach.get('name', '')}", True, (120, 240, 140)), (ui(394), y))
            y += line_height("small")
        for ach in locked[:6]:
            surface.blit(text_font.render(f"□ {ach.get('name', '')}", True, (170, 170, 170)), (ui(394), y))
            y += line_height("small")

    def _render_endings(self, surface: pygame.Surface):
        title_font = ui_font("section", bold=True)
        text_font = ui_font("small")
        surface.blit(title_font.render("章节收官结局回看", True, (200, 230, 255)), (ui(390), ui(82)))
        y = ui(112)
        for ending in self.ending_history[-6:]:
            chapter = ending.get("chapter_name", "章节")
            quest_name = ending.get("quest_name", "任务")
            outcome = ending.get("outcome_label", "默认")
            summary = ending.get("summary", "")
            surface.blit(text_font.render(f"{chapter} | {quest_name}", True, (230, 230, 230)), (ui(394), y))
            y += line_height("small")
            surface.blit(text_font.render(f"结局: {outcome}", True, (160, 220, 255)), (ui(398), y))
            y += line_height("small")
            surface.blit(text_font.render(summary[:24], True, (190, 190, 200)), (ui(398), y))
            y += line_height("small") + ui(6)

    def _render_footer(self, surface: pygame.Surface):
        font = ui_font("small")
        unlocked_count = len([a for a in self.achievements.values() if a.get("unlocked")])
        total_count = len(self.achievements)
        surface.blit(font.render(f"成就进度: {unlocked_count}/{total_count}", True, (210, 210, 230)), (ui(20), self.panel_height - ui(34)))
        surface.blit(font.render("按 L 关闭", True, (180, 180, 180)), (self.panel_width - ui(110), self.panel_height - ui(34)))

    def handle_key(self, key: int):
        if not self.visible:
            return
        if key in [pygame.K_ESCAPE, pygame.K_l]:
            self.hide()

    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        return True

    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
