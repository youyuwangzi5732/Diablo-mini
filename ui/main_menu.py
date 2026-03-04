"""
主菜单界面
"""
from typing import Dict, List, Optional, Any, Callable
import pygame

from .ui_element import UIElement, UIButton, UILabel, UIPanel
from .ui_manager import UIManager, UIState
from .font_manager import get_font


class MainMenu:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        # 先初始化颜色等属性
        self.background_color = (20, 15, 10)
        self.title_color = (200, 150, 50)
        
        self.elements: Dict[str, UIElement] = {}
        self._create_elements()
        
        self.selected_character_index = 0
        self.characters: List[Dict[str, Any]] = []
    
    def _create_elements(self):
        title_font = get_font(64)
        title_width = title_font.size("暗黑迷你")[0]
        
        self.elements["title"] = UILabel(
            id="title",
            x=(self.screen_width - title_width) // 2,
            y=100,
            text="暗黑迷你",
            font_size=64,
            text_color=self.title_color
        )
        
        self.elements["subtitle"] = UILabel(
            id="subtitle",
            x=self.screen_width // 2 - 80,
            y=180,
            text="Diablo Mini",
            font_size=24,
            text_color=(150, 120, 80)
        )
        
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        button_start_y = 300
        button_spacing = 70
        
        self.elements["btn_new_game"] = UIButton(
            id="btn_new_game",
            x=button_x,
            y=button_start_y,
            width=button_width,
            height=button_height,
            text="创建角色",
            font_size=20,
            on_click_callback=self._on_new_game
        )
        
        self.elements["btn_continue"] = UIButton(
            id="btn_continue",
            x=button_x,
            y=button_start_y + button_spacing,
            width=button_width,
            height=button_height,
            text="继续游戏",
            font_size=20,
            on_click_callback=self._on_continue
        )
        
        self.elements["btn_settings"] = UIButton(
            id="btn_settings",
            x=button_x,
            y=button_start_y + button_spacing * 2,
            width=button_width,
            height=button_height,
            text="设置",
            font_size=20,
            on_click_callback=self._on_settings
        )
        
        self.elements["btn_quit"] = UIButton(
            id="btn_quit",
            x=button_x,
            y=button_start_y + button_spacing * 3,
            width=button_width,
            height=button_height,
            text="退出游戏",
            font_size=20,
            on_click_callback=self._on_quit
        )
        
        self.elements["version"] = UILabel(
            id="version",
            x=10,
            y=self.screen_height - 30,
            text="Version 1.0.0",
            font_size=12,
            text_color=(100, 100, 100)
        )
    
    def _on_new_game(self, button: UIButton):
        self.ui_manager.change_state(UIState.CHARACTER_CREATE)
        self.ui_manager.trigger_callback("new_game")
    
    def _on_continue(self, button: UIButton):
        self.ui_manager.change_state(UIState.CHARACTER_SELECT)
        self.ui_manager.trigger_callback("continue_game")
    
    def _on_settings(self, button: UIButton):
        self.ui_manager.change_state(UIState.SETTINGS)
        self.ui_manager.trigger_callback("open_settings")
    
    def _on_quit(self, button: UIButton):
        self.ui_manager.trigger_callback("quit_game")
    
    def update(self, delta_time: float):
        for element in self.elements.values():
            if hasattr(element, 'update'):
                element.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        surface.fill(self.background_color)
        
        self._render_background(surface)
        
        for element in self.elements.values():
            if hasattr(element, 'render'):
                element.render(surface)
    
    def _render_background(self, surface: pygame.Surface):
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        for i in range(5):
            radius = 100 + i * 50
            alpha = 30 - i * 5
            color = (50 + i * 10, 30 + i * 5, 20 + i * 3)
            
            circle_surface = pygame.Surface(
                (radius * 2, radius * 2),
                pygame.SRCALPHA
            )
            pygame.draw.circle(
                circle_surface,
                (*color, alpha),
                (radius, radius),
                radius
            )
            surface.blit(
                circle_surface,
                (center_x - radius, center_y - radius)
            )
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        
        title_font = get_font(64)
        title_width = title_font.size("暗黑迷你")[0]
        
        title = self.elements.get("title")
        if title:
            title.x = (width - title_width) // 2
        
        subtitle = self.elements.get("subtitle")
        if subtitle:
            subtitle.x = width // 2 - 80
        
        button_width = 200
        button_x = (width - button_width) // 2
        button_start_y = 300
        button_spacing = 70
        
        for i, btn_id in enumerate(["btn_new_game", "btn_continue", "btn_settings", "btn_quit"]):
            btn = self.elements.get(btn_id)
            if btn:
                btn.x = button_x
                btn.y = button_start_y + i * button_spacing
        
        version = self.elements.get("version")
        if version:
            version.y = height - 30


class CharacterSelectMenu:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.elements: Dict[str, UIElement] = {}
        self._create_elements()
        
        self.characters: List[Dict[str, Any]] = []
        self.selected_index = 0
    
    def _create_elements(self):
        self.elements["title"] = UILabel(
            id="title",
            x=self.screen_width // 2 - 80,
            y=50,
            text="选择角色",
            font_size=36,
            text_color=(200, 150, 50)
        )
        
        self.elements["btn_back"] = UIButton(
            id="btn_back",
            x=50,
            y=self.screen_height - 70,
            width=120,
            height=40,
            text="返回",
            font_size=16,
            on_click_callback=self._on_back
        )
        
        self.elements["btn_play"] = UIButton(
            id="btn_play",
            x=self.screen_width - 170,
            y=self.screen_height - 70,
            width=120,
            height=40,
            text="开始游戏",
            font_size=16,
            on_click_callback=self._on_play
        )
    
    def _on_back(self, button: UIButton):
        self.ui_manager.change_state(UIState.MAIN_MENU)
    
    def _on_play(self, button: UIButton):
        if self.characters:
            self.ui_manager.trigger_callback("start_game", self.characters[self.selected_index])
    
    def set_characters(self, characters: List[Dict[str, Any]]):
        self.characters = characters
        self.selected_index = 0
    
    def update(self, delta_time: float):
        for element in self.elements.values():
            if hasattr(element, 'update'):
                element.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        surface.fill((20, 15, 10))
        
        for element in self.elements.values():
            if hasattr(element, 'render'):
                element.render(surface)
        
        self._render_character_list(surface)
    
    def _render_character_list(self, surface: pygame.Surface):
        if not self.characters:
            font = get_font(24)
            text = font.render("没有找到角色存档", True, (150, 150, 150))
            x = (self.screen_width - text.get_width()) // 2
            y = self.screen_height // 2
            surface.blit(text, (x, y))
            return
        
        font = get_font(20)
        start_y = 120
        card_height = 80
        card_width = 400
        card_x = (self.screen_width - card_width) // 2
        
        for i, char in enumerate(self.characters):
            y = start_y + i * (card_height + 10)
            
            bg_color = (60, 50, 40) if i == self.selected_index else (40, 35, 30)
            border_color = (200, 150, 50) if i == self.selected_index else (80, 70, 60)
            
            pygame.draw.rect(surface, bg_color, (card_x, y, card_width, card_height))
            pygame.draw.rect(surface, border_color, (card_x, y, card_width, card_height), 2)
            
            name_text = font.render(char.get("name", "未命名"), True, (255, 255, 255))
            surface.blit(name_text, (card_x + 20, y + 15))
            
            class_text = font.render(
                f"{char.get('class_id', '未知')} Lv.{char.get('level', 1)}",
                True, (180, 180, 180)
            )
            surface.blit(class_text, (card_x + 20, y + 45))
    
    def handle_click(self, pos: tuple):
        start_y = 120
        card_height = 80
        card_width = 400
        card_x = (self.screen_width - card_width) // 2
        
        for i in range(len(self.characters)):
            y = start_y + i * (card_height + 10)
            if (card_x <= pos[0] <= card_x + card_width and
                y <= pos[1] <= y + card_height):
                self.selected_index = i
                return
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        
        title = self.elements.get("title")
        if title:
            title.x = width // 2 - 80
        
        btn_back = self.elements.get("btn_back")
        if btn_back:
            btn_back.y = height - 70
        
        btn_play = self.elements.get("btn_play")
        if btn_play:
            btn_play.x = width - 170
            btn_play.y = height - 70


class CharacterCreateMenu:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.elements: Dict[str, UIElement] = {}
        self._create_elements()
        
        self.selected_class = "barbarian"
        self.character_name = ""
        self.name_input_focused = False
        self.name_input_rect = (self.screen_width // 2 - 50, 120, 200, 30)
        
        self.class_info = {
            "barbarian": {"name": "野蛮人", "color": (200, 100, 100), "desc": "近战物理输出"},
            "monk": {"name": "武僧", "color": (200, 200, 100), "desc": "敏捷连击战士"},
            "wizard": {"name": "魔法师", "color": (100, 150, 200), "desc": "远程魔法输出"},
            "demon_hunter": {"name": "猎魔人", "color": (100, 200, 150), "desc": "远程物理输出"},
            "necromancer": {"name": "死灵法师", "color": (150, 100, 200), "desc": "召唤与诅咒"},
            "druid": {"name": "德鲁伊", "color": (100, 200, 100), "desc": "变形与自然"},
            "assassin": {"name": "刺客", "color": (200, 150, 200), "desc": "暗影与陷阱"},
            "crusader": {"name": "圣教军", "color": (220, 200, 100), "desc": "神圣骑士"}
        }
    
    def _create_elements(self):
        self.elements["title"] = UILabel(
            id="title",
            x=self.screen_width // 2 - 80,
            y=50,
            text="创建角色",
            font_size=36,
            text_color=(200, 150, 50)
        )
        
        self.elements["name_label"] = UILabel(
            id="name_label",
            x=self.screen_width // 2 - 150,
            y=120,
            text="角色名称:",
            font_size=18,
            text_color=(200, 200, 200)
        )
        
        self.elements["btn_back"] = UIButton(
            id="btn_back",
            x=50,
            y=self.screen_height - 70,
            width=120,
            height=40,
            text="返回",
            font_size=16,
            on_click_callback=self._on_back
        )
        
        self.elements["btn_create"] = UIButton(
            id="btn_create",
            x=self.screen_width - 170,
            y=self.screen_height - 70,
            width=120,
            height=40,
            text="创建",
            font_size=16,
            on_click_callback=self._on_create
        )
    
    def _on_back(self, button: UIButton):
        self.ui_manager.change_state(UIState.MAIN_MENU)
    
    def _on_create(self, button: UIButton):
        print(f"[DEBUG] _on_create called: name='{self.character_name}', class='{self.selected_class}'")
        if self.character_name and self.selected_class:
            print(f"[DEBUG] Triggering callback...")
            self.ui_manager.trigger_callback(
                "create_character",
                name=self.character_name,
                class_id=self.selected_class
            )
        else:
            print(f"[DEBUG] Missing: name={bool(self.character_name)}, class={bool(self.selected_class)}")
    
    def select_class(self, class_id: str):
        self.selected_class = class_id
    
    def set_name(self, name: str):
        self.character_name = name
    
    def update(self, delta_time: float):
        for element in self.elements.values():
            if hasattr(element, 'update'):
                element.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        surface.fill((20, 15, 10))
        
        for element in self.elements.values():
            if hasattr(element, 'render'):
                element.render(surface)
        
        self._render_class_selection(surface)
        self._render_name_input(surface)
    
    def _render_class_selection(self, surface: pygame.Surface):
        font = get_font(16)
        
        start_x = self.screen_width // 2 - 200
        start_y = 180
        card_width = 100
        card_height = 120
        spacing = 10
        
        classes = list(self.class_info.keys())
        
        for i, class_id in enumerate(classes):
            row = i // 4
            col = i % 4
            
            x = start_x + col * (card_width + spacing)
            y = start_y + row * (card_height + spacing)
            
            info = self.class_info[class_id]
            is_selected = class_id == self.selected_class
            
            bg_color = (60, 50, 40) if is_selected else (40, 35, 30)
            border_color = info["color"] if is_selected else (80, 70, 60)
            
            pygame.draw.rect(surface, bg_color, (x, y, card_width, card_height))
            pygame.draw.rect(surface, border_color, (x, y, card_width, card_height), 2)
            
            name_text = font.render(info["name"], True, info["color"])
            name_x = x + (card_width - name_text.get_width()) // 2
            surface.blit(name_text, (name_x, y + 30))
            
            desc_text = font.render(info["desc"], True, (150, 150, 150))
            desc_x = x + (card_width - desc_text.get_width()) // 2
            surface.blit(desc_text, (desc_x, y + 60))
    
    def _render_name_input(self, surface: pygame.Surface):
        font = get_font(20)
        
        input_x, input_y, input_width, input_height = self.name_input_rect
        
        # 根据聚焦状态显示不同边框颜色
        border_color = (200, 150, 50) if self.name_input_focused else (100, 100, 100)
        bg_color = (60, 60, 60) if self.name_input_focused else (50, 50, 50)
        
        pygame.draw.rect(surface, bg_color, 
                         (input_x, input_y, input_width, input_height))
        pygame.draw.rect(surface, border_color, 
                         (input_x, input_y, input_width, input_height), 2)
        
        # 显示输入的文本
        display_text = self.character_name
        if self.name_input_focused and (pygame.time.get_ticks() // 500) % 2 == 0:
            display_text += "|"  # 光标闪烁效果
        
        name_text = font.render(display_text, True, (255, 255, 255))
        surface.blit(name_text, (input_x + 5, input_y + 5))
    
    def handle_click(self, pos: tuple):
        # 首先检查按钮点击
        for element in self.elements.values():
            if hasattr(element, 'contains_point') and element.contains_point(pos):
                if hasattr(element, 'on_click'):
                    element.on_click(pos)
                self.name_input_focused = False  # 点击按钮时取消输入框聚焦
                return
        
        # 检查文本输入框点击
        input_x, input_y, input_width, input_height = self.name_input_rect
        if input_x <= pos[0] <= input_x + input_width and input_y <= pos[1] <= input_y + input_height:
            self.name_input_focused = True
            return
        else:
            self.name_input_focused = False
        
        # 然后检查职业选择卡片
        start_x = self.screen_width // 2 - 200
        start_y = 180
        card_width = 100
        card_height = 120
        spacing = 10
        
        classes = list(self.class_info.keys())
        
        for i, class_id in enumerate(classes):
            row = i // 4
            col = i % 4
            
            x = start_x + col * (card_width + spacing)
            y = start_y + row * (card_height + spacing)
            
            if x <= pos[0] <= x + card_width and y <= pos[1] <= y + card_height:
                self.selected_class = class_id
                return
    
    def handle_key(self, key: int, unicode: str):
        # 只有在输入框聚焦时才处理键盘输入
        if not self.name_input_focused:
            return
        
        if key == pygame.K_BACKSPACE:
            self.character_name = self.character_name[:-1]
        elif key == pygame.K_RETURN:
            self.name_input_focused = False
            if self.character_name and self.selected_class:
                self._on_create(None)
        elif key == pygame.K_ESCAPE:
            self.name_input_focused = False
        elif len(self.character_name) < 16 and unicode.isprintable():
            self.character_name += unicode
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        
        title = self.elements.get("title")
        if title:
            title.x = width // 2 - 80
        
        name_label = self.elements.get("name_label")
        if name_label:
            name_label.x = width // 2 - 150
        
        btn_back = self.elements.get("btn_back")
        if btn_back:
            btn_back.y = height - 70
        
        btn_create = self.elements.get("btn_create")
        if btn_create:
            btn_create.x = width - 170
            btn_create.y = height - 70
