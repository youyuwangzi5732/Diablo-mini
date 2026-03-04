"""
任务追踪UI
"""
from typing import Dict, List, Optional, Any
import pygame

from .ui_manager import UIManager
from .ui_theme import draw_panel, font as ui_font, line_height, ui, PALETTE


class QuestTrackerUI:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = True
        
        self.base_panel_width = 300
        self.base_panel_height = 250
        self.panel_width = self.base_panel_width
        self.panel_height = self.base_panel_height
        
        self.tracked_quests: List[Dict[str, Any]] = []
        self.max_tracked = 5
        
        self.expanded = True
    
    def set_quests(self, quests: List[Dict[str, Any]]):
        self.tracked_quests = quests[:self.max_tracked]
    
    def add_quest(self, quest: Dict[str, Any]):
        if len(self.tracked_quests) < self.max_tracked:
            self.tracked_quests.append(quest)
    
    def remove_quest(self, quest_id: str):
        self.tracked_quests = [q for q in self.tracked_quests if q.get("id") != quest_id]
    
    def toggle(self):
        self.visible = not self.visible
    
    def toggle_expand(self):
        self.expanded = not self.expanded
    
    def get_position(self) -> tuple:
        # 放置在右上角，避免与HUD重叠
        return (self.screen_width - self.panel_width - 10, 10)
    
    def update(self, delta_time: float):
        pass

    def _apply_ui_scale(self):
        self.panel_width = ui(self.base_panel_width)
        self.panel_height = ui(self.base_panel_height)
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        self._apply_ui_scale()
        
        x, y = self.get_position()
        
        if self.expanded:
            self._render_expanded(surface, x, y)
        else:
            self._render_collapsed(surface, x, y)
    
    def _render_collapsed(self, surface: pygame.Surface, x: int, y: int):
        font = ui_font("body", bold=True)
        
        quest_count = len(self.tracked_quests)
        text = font.render(f"任务 ({quest_count})", True, (200, 180, 100))
        
        bg_surface = pygame.Surface((ui(150), ui(34)), pygame.SRCALPHA)
        pygame.draw.rect(bg_surface, PALETTE["panel_bg"], (0, 0, ui(150), ui(34)), border_radius=ui(10))
        pygame.draw.rect(bg_surface, PALETTE["panel_border"], (0, 0, ui(150), ui(34)), width=1, border_radius=ui(10))
        
        bg_surface.blit(text, (ui(10), ui(7)))
        surface.blit(bg_surface, (x, y))
    
    def _render_expanded(self, surface: pygame.Surface, x: int, y: int):
        panel_height = 40 + len(self.tracked_quests) * 60
        
        panel_surface = pygame.Surface(
            (self.panel_width, panel_height),
            pygame.SRCALPHA
        )
        draw_panel(panel_surface, self.panel_width, panel_height, "任务追踪")
        
        self._render_header(panel_surface)
        self._render_quests(panel_surface)
        
        surface.blit(panel_surface, (x, y))
    
    def _render_header(self, surface: pygame.Surface):
        font = ui_font("section", bold=True)
        
        title = font.render("任务追踪", True, PALETTE["title_text"][:3])
        surface.blit(title, (ui(12), ui(8)))
    
    def _render_quests(self, surface: pygame.Surface):
        font_name = ui_font("body", bold=True)
        font_obj = ui_font("small")
        
        start_y = ui(56)
        
        for i, quest in enumerate(self.tracked_quests):
            y = start_y + i * ui(62)
            
            quest_name = quest.get("name", "未知任务")
            quest_type = quest.get("quest_type", "main")
            
            type_colors = {
                "main": (255, 200, 50),
                "side": (100, 200, 255),
                "event": (255, 100, 255),
            }
            
            color = type_colors.get(quest_type, (200, 200, 200))
            
            name_text = font_name.render(quest_name, True, color)
            surface.blit(name_text, (10, y))
            
            objectives = quest.get("objectives", [])
            for j, obj in enumerate(objectives[:3]):
                if not obj.get("completed", False):
                    obj_text = obj.get("description", "")
                    current = obj.get("current", 0)
                    required = obj.get("required", 1)
                    
                    if required > 1:
                        obj_text = f"{obj_text} ({current}/{required})"
                    
                    text = font_obj.render(f"  • {obj_text}", True, (180, 180, 180))
                    surface.blit(text, (ui(10), y + ui(20) + j * line_height("small")))
    
    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        
        x, y = self.get_position()
        
        if self.expanded:
            if x <= pos[0] <= x + self.panel_width and y <= pos[1] <= y + 30:
                self.toggle_expand()
                return True
        else:
            if x <= pos[0] <= x + 120 and y <= pos[1] <= y + 30:
                self.toggle_expand()
                return True
        
        return False
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height


class QuestLogUI:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = False
        
        self.base_panel_width = 600
        self.base_panel_height = 500
        self.panel_width = self.base_panel_width
        self.panel_height = self.base_panel_height
        
        self.quests: List[Dict[str, Any]] = []
        self.selected_quest: Optional[int] = None
        
        self.current_tab = "active"
        self.scroll_offset = 0
    
    def toggle(self):
        self.visible = not self.visible
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def set_quests(self, quests: List[Dict[str, Any]]):
        self.quests = quests
    
    def get_panel_position(self) -> tuple:
        x = (self.screen_width - self.panel_width) // 2
        y = (self.screen_height - self.panel_height) // 2
        return (x, y)
    
    def update(self, delta_time: float):
        pass

    def _apply_ui_scale(self):
        self.panel_width = ui(self.base_panel_width)
        self.panel_height = ui(self.base_panel_height)
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        self._apply_ui_scale()
        
        panel_x, panel_y = self.get_panel_position()
        
        panel_surface = pygame.Surface(
            (self.panel_width, self.panel_height),
            pygame.SRCALPHA
        )
        draw_panel(panel_surface, self.panel_width, self.panel_height, "任务日志", "分支结局已整合")
        
        self._render_header(panel_surface)
        self._render_tabs(panel_surface)
        self._render_quest_list(panel_surface)
        self._render_quest_details(panel_surface)
        
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def _render_header(self, surface: pygame.Surface):
        font = ui_font("section", bold=True)
        
        title = font.render("任务日志", True, PALETTE["title_text"][:3])
        surface.blit(title, (ui(20), ui(14)))
    
    def _render_tabs(self, surface: pygame.Surface):
        font = get_font(16)
        
        tabs = [
            ("active", "进行中"),
            ("completed", "已完成"),
        ]
        
        x = 20
        for tab_id, tab_name in tabs:
            is_selected = self.current_tab == tab_id
            
            bg_color = (60, 60, 60) if is_selected else (40, 40, 40)
            text_color = (255, 255, 255) if is_selected else (180, 180, 180)
            
            tab_width = 80
            pygame.draw.rect(surface, bg_color, (x, 55, tab_width, 30))
            pygame.draw.rect(surface, (100, 100, 100), (x, 55, tab_width, 30), 1)
            
            text = font.render(tab_name, True, text_color)
            text_x = x + (tab_width - text.get_width()) // 2
            surface.blit(text, (text_x, 62))
            
            x += tab_width + 10
    
    def _render_quest_list(self, surface: pygame.Surface):
        font = get_font(16)
        font_small = get_font(14)
        
        list_x = 10
        list_y = 95
        list_width = 250
        list_height = self.panel_height - 120
        
        pygame.draw.rect(surface, (25, 25, 25), (list_x, list_y, list_width, list_height))
        pygame.draw.rect(surface, (80, 80, 80), (list_x, list_y, list_width, list_height), 1)
        
        filtered_quests = self._get_filtered_quests()
        
        for i, quest in enumerate(filtered_quests[self.scroll_offset:self.scroll_offset + 10]):
            y = list_y + 5 + i * 38
            actual_index = i + self.scroll_offset
            
            is_selected = self.selected_quest == actual_index
            bg_color = (50, 45, 40) if is_selected else (35, 35, 35)
            
            pygame.draw.rect(surface, bg_color, (list_x + 5, y, list_width - 10, 35))
            
            if is_selected:
                pygame.draw.rect(surface, (200, 180, 100), (list_x + 5, y, list_width - 10, 35), 1)
            
            quest_name = quest.get("name", "未知任务")
            quest_type = quest.get("quest_type", "side")
            
            type_colors = {
                "main": (255, 200, 50),
                "side": (100, 200, 255),
                "event": (255, 100, 255),
            }
            
            color = type_colors.get(quest_type, (200, 200, 200))
            
            name_text = font.render(quest_name[:15], True, color)
            surface.blit(name_text, (list_x + 10, y + 3))
            
            level = quest.get("required_level", 1)
            level_text = font_small.render(f"Lv.{level}", True, (150, 150, 150))
            surface.blit(level_text, (list_x + 10, y + 20))
    
    def _render_quest_details(self, surface: pygame.Surface):
        if self.selected_quest is None:
            return
        
        filtered_quests = self._get_filtered_quests()
        if self.selected_quest >= len(filtered_quests):
            return
        
        quest = filtered_quests[self.selected_quest]
        
        detail_x = 270
        detail_y = 95
        detail_width = self.panel_width - 280
        detail_height = self.panel_height - 120
        
        pygame.draw.rect(surface, (25, 25, 25), (detail_x, detail_y, detail_width, detail_height))
        pygame.draw.rect(surface, (80, 80, 80), (detail_x, detail_y, detail_width, detail_height), 1)
        
        font_title = get_font(20)
        font_text = get_font(16)
        font_small = get_font(14)
        
        quest_name = quest.get("name", "未知任务")
        name_text = font_title.render(quest_name, True, (255, 220, 100))
        surface.blit(name_text, (detail_x + 10, detail_y + 10))
        
        description = quest.get("description", "")
        self._render_wrapped_text(surface, description, font_text, 
                                   detail_x + 10, detail_y + 40, detail_width - 20)
        
        obj_y = detail_y + 120
        obj_title = font_text.render("目标:", True, (200, 180, 100))
        surface.blit(obj_title, (detail_x + 10, obj_y))
        
        objectives = quest.get("objectives", [])
        for i, obj in enumerate(objectives):
            y = obj_y + 25 + i * 22
            
            completed = obj.get("completed", False)
            check = "[X]" if completed else "[ ]"
            color = (100, 255, 100) if completed else (200, 200, 200)
            
            obj_text = obj.get("description", "")
            current = obj.get("current", 0)
            required = obj.get("required", 1)
            
            if required > 1:
                obj_text = f"{obj_text} ({current}/{required})"
            
            text = font_small.render(f"{check} {obj_text}", True, color)
            surface.blit(text, (detail_x + 15, y))

        ending_summary = quest.get("ending_summary", "")
        if ending_summary:
            ending_title_y = obj_y + 25 + len(objectives) * 22 + 6
            ending_title = font_text.render("结局:", True, (180, 220, 255))
            surface.blit(ending_title, (detail_x + 10, ending_title_y))
            self._render_wrapped_text(
                surface,
                ending_summary,
                font_small,
                detail_x + 15,
                ending_title_y + 22,
                detail_width - 28
            )
        
        rewards = quest.get("rewards", {})
        if rewards:
            reward_y = obj_y + 25 + len(objectives) * 22 + (78 if ending_summary else 20)
            
            reward_title = font_text.render("奖励:", True, (200, 180, 100))
            surface.blit(reward_title, (detail_x + 10, reward_y))
            
            if "experience" in rewards:
                exp_text = font_small.render(f"  经验: {rewards['experience']}", True, (100, 200, 255))
                surface.blit(exp_text, (detail_x + 15, reward_y + 25))
            
            if "gold" in rewards:
                gold_text = font_small.render(f"  金币: {rewards['gold']}", True, (255, 215, 0))
                surface.blit(gold_text, (detail_x + 15, reward_y + 45))
            
            if "items" in rewards:
                items_text = font_small.render(f"  物品: {len(rewards['items'])} 件", True, (200, 150, 100))
                surface.blit(items_text, (detail_x + 15, reward_y + 65))
    
    def _render_wrapped_text(self, surface: pygame.Surface, text: str, font: pygame.font.Font,
                              x: int, y: int, max_width: int):
        if ' ' not in text:
            lines = []
            current_line = ""
            for char in text:
                test_line = current_line + char
                if font.size(test_line)[0] < max_width:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = char
            if current_line:
                lines.append(current_line)
            for i, line in enumerate(lines[:5]):
                text_surface = font.render(line, True, (200, 200, 200))
                surface.blit(text_surface, (x, y + i * 18))
            return

        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word + " "
        
        if current_line:
            lines.append(current_line)
        
        for i, line in enumerate(lines[:5]):
            text_surface = font.render(line, True, (200, 200, 200))
            surface.blit(text_surface, (x, y + i * 18))
    
    def _get_filtered_quests(self) -> List[Dict[str, Any]]:
        if self.current_tab == "active":
            return [q for q in self.quests if not q.get("completed", False)]
        else:
            return [q for q in self.quests if q.get("completed", False)]
    
    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        
        panel_x, panel_y = self.get_panel_position()
        local_pos = (pos[0] - panel_x, pos[1] - panel_y)
        
        x = 20
        for tab_id in ["active", "completed"]:
            if x <= local_pos[0] <= x + 80 and 55 <= local_pos[1] <= 85:
                self.current_tab = tab_id
                self.selected_quest = None
                self.scroll_offset = 0
                return True
            x += 90
        
        list_x = 10
        list_y = 95
        list_width = 250
        
        if list_x <= local_pos[0] <= list_x + list_width and list_y <= local_pos[1] <= list_y + 380:
            relative_y = local_pos[1] - list_y - 5
            item_index = relative_y // 38 + self.scroll_offset
            
            filtered_quests = self._get_filtered_quests()
            if 0 <= item_index < len(filtered_quests):
                self.selected_quest = item_index
            return True
        
        return True
    
    def handle_key(self, key: int):
        if not self.visible:
            return
        
        if key == pygame.K_ESCAPE:
            self.hide()
        elif key == pygame.K_UP:
            if self.selected_quest and self.selected_quest > 0:
                self.selected_quest -= 1
        elif key == pygame.K_DOWN:
            filtered = self._get_filtered_quests()
            if self.selected_quest is not None and self.selected_quest < len(filtered) - 1:
                self.selected_quest += 1
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
