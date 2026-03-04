"""
角色面板UI
"""
from typing import Optional, Any
import pygame

from .ui_manager import UIManager
from .ui_theme import draw_panel, font as ui_font, line_height, ui


class CharacterPanel:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = False
        
        self.base_panel_width = 400
        self.base_panel_height = 500
        self.panel_width = self.base_panel_width
        self.panel_height = self.base_panel_height
        
        self.character: Optional[Any] = None
    
    def toggle(self):
        self.visible = not self.visible
    
    def set_character(self, character: Any):
        self.character = character
    
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
        
        panel_surface = pygame.Surface(
            (self.panel_width, self.panel_height),
            pygame.SRCALPHA
        )
        draw_panel(panel_surface, self.panel_width, self.panel_height, "角色", "属性总览")
        
        self._render_header(panel_surface)
        self._render_attributes(panel_surface)
        self._render_derived_stats(panel_surface)
        self._render_resistances(panel_surface)
        
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def _render_header(self, surface: pygame.Surface):
        if not self.character:
            return
        
        font_large = ui_font("section", bold=True)
        font_medium = ui_font("body")
        
        name = getattr(self.character, 'name', '未知')
        name_text = font_large.render(name, True, (255, 220, 100))
        surface.blit(name_text, (ui(20), ui(14)))
        
        class_id = getattr(self.character, 'class_id', 'unknown')
        level = getattr(self.character, 'level', 1)
        class_text = font_medium.render(f"{class_id} Lv.{level}", True, (180, 180, 180))
        surface.blit(class_text, (ui(20), ui(42)))
    
    def _render_attributes(self, surface: pygame.Surface):
        font = ui_font("body")
        title_font = ui_font("section", bold=True)
        
        title = title_font.render("基础属性", True, (200, 180, 100))
        surface.blit(title, (ui(20), ui(82)))
        
        attributes = getattr(self.character, 'attributes', None)
        if not attributes:
            return
        
        from entities.character.attributes import AttributeType
        
        attr_names = {
            AttributeType.STRENGTH: "力量",
            AttributeType.DEXTERITY: "敏捷",
            AttributeType.INTELLIGENCE: "智力",
            AttributeType.VITALITY: "体能"
        }
        
        y = ui(116)
        for attr_type, name in attr_names.items():
            value = attributes.get_total(attr_type)
            base = attributes.get_base(attr_type)
            
            text = font.render(f"{name}: {int(value)}", True, (255, 255, 255))
            surface.blit(text, (30, y))
            
            if value > base:
                bonus_text = font.render(f"(+{int(value - base)})", True, (100, 255, 100))
                surface.blit(bonus_text, (ui(150), y))
            
            y += line_height("body")
    
    def _render_derived_stats(self, surface: pygame.Surface):
        font = ui_font("body")
        title_font = ui_font("section", bold=True)
        
        title = title_font.render("衍生属性", True, (200, 180, 100))
        surface.blit(title, (ui(20), ui(235)))
        
        if not self.character:
            return
        
        stats = [
            ("最大生命", getattr(self.character, 'get_max_health', lambda: 0)()),
            ("最大资源", getattr(self.character, 'get_max_resource', lambda: 0)()),
            ("攻击力", 0),
            ("法术强度", 0),
            ("护甲", 0),
            ("暴击率", "5%"),
            ("暴击伤害", "150%"),
        ]
        
        y = ui(268)
        for stat_name, value in stats:
            if isinstance(value, (int, float)):
                value_str = str(int(value))
            else:
                value_str = str(value)
            
            text = font.render(f"{stat_name}: {value_str}", True, (255, 255, 255))
            surface.blit(text, (ui(30), y))
            y += line_height("small")
    
    def _render_resistances(self, surface: pygame.Surface):
        font = ui_font("small")
        title_font = ui_font("section", bold=True)
        
        title = title_font.render("抗性", True, (200, 180, 100))
        surface.blit(title, (ui(20), ui(422)))
        
        resistances = [
            ("火焰抗性", (255, 100, 100)),
            ("冰冷抗性", (100, 150, 255)),
            ("闪电抗性", (255, 255, 100)),
            ("毒素抗性", (100, 255, 100)),
        ]
        
        y = ui(454)
        x = ui(30)
        col = 0
        
        for res_name, color in resistances:
            text = font.render(f"{res_name}: 0%", True, color)
            surface.blit(text, (x + col * ui(190), y))
            col += 1
            if col >= 2:
                col = 0
                y += line_height("small")
    
    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        
        return True
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
