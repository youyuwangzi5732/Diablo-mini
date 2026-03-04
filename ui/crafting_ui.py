from typing import Any, List, Dict
import pygame

from .ui_manager import UIManager
from .ui_theme import draw_panel, font as ui_font, line_height, ui, PALETTE


class CraftingUI:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        self.visible = False
        self.base_panel_width = 560
        self.base_panel_height = 320
        self.panel_width = self.base_panel_width
        self.panel_height = self.base_panel_height
        self.mode = "craft"
        self.npc: Any = None
        self.actions: List[Dict[str, str]] = []

    def _apply_ui_scale(self):
        self.panel_width = ui(self.base_panel_width)
        self.panel_height = ui(self.base_panel_height)

    def show(self, npc: Any, mode: str):
        self.npc = npc
        self.mode = mode
        self.actions = self._build_actions(mode)
        self.visible = True

    def hide(self):
        self.visible = False

    def _build_actions(self, mode: str) -> List[Dict[str, str]]:
        if mode == "gem_combine":
            return [{"id": "gem_combine", "name": "合成宝石", "desc": "消耗金币与材料合成更高品质宝石"}]
        if mode == "socket":
            return [{"id": "socket", "name": "装备开孔", "desc": "为武器添加额外孔位（需要符文）"}]
        return [{"id": "craft", "name": "升格/重铸", "desc": "优先执行升格配方，不满足则回退淬炼"}]

    def _get_panel_position(self):
        return ((self.screen_width - self.panel_width) // 2, (self.screen_height - self.panel_height) // 2)

    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        self._apply_ui_scale()
        x, y = self._get_panel_position()
        panel = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        draw_panel(panel, self.panel_width, self.panel_height, "工匠台", "圆角一体化锻造面板")
        body_font = ui_font("body", bold=True)
        small_font = ui_font("small")
        line_y = ui(68)
        for idx, action in enumerate(self.actions):
            rect = pygame.Rect(ui(20), line_y + idx * ui(74), self.panel_width - ui(40), ui(64))
            pygame.draw.rect(panel, (36, 46, 64), rect, border_radius=ui(10))
            pygame.draw.rect(panel, PALETTE["panel_border"][:3], rect, width=1, border_radius=ui(10))
            panel.blit(body_font.render(f"[{idx + 1}] {action['name']}", True, PALETTE["accent"][:3]), (rect.x + ui(12), rect.y + ui(10)))
            panel.blit(small_font.render(action["desc"], True, PALETTE["muted_text"][:3]), (rect.x + ui(14), rect.y + ui(34)))
        footer = small_font.render("按 Enter 执行  Esc 关闭", True, PALETTE["body_text"][:3])
        panel.blit(footer, (ui(20), self.panel_height - ui(30)))
        surface.blit(panel, (x, y))

    def handle_key(self, key: int) -> bool:
        if not self.visible:
            return False
        if key == pygame.K_ESCAPE:
            self.hide()
            return True
        if key in [pygame.K_RETURN, pygame.K_1]:
            self.execute_primary_action()
            return True
        return True

    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        x, y = self._get_panel_position()
        local = (pos[0] - x, pos[1] - y)
        rect = pygame.Rect(ui(20), ui(68), self.panel_width - ui(40), ui(64))
        if rect.collidepoint(local):
            self.execute_primary_action()
            return True
        return True

    def execute_primary_action(self):
        if not self.actions:
            return
        action = self.actions[0]["id"]
        self.ui_manager.trigger_callback("craft_action", self.npc, action)
        self.hide()

    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
