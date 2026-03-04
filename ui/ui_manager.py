"""
UI管理器
"""
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import pygame

from .font_manager import get_font


class UIState(Enum):
    MAIN_MENU = "main_menu"
    CHARACTER_SELECT = "character_select"
    CHARACTER_CREATE = "character_create"
    GAME = "game"
    INVENTORY = "inventory"
    CHARACTER_PANEL = "character_panel"
    SKILL_TREE = "skill_tree"
    SETTINGS = "settings"
    PAUSE = "pause"
    DIALOGUE = "dialogue"
    VENDOR = "vendor"
    CRAFTING = "crafting"


class UIManager:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        self.current_state = UIState.MAIN_MENU
        self.previous_state: Optional[UIState] = None
        
        self.elements: Dict[str, Any] = {}
        self.containers: Dict[str, Any] = {}
        
        self.focused_element: Optional[str] = None
        self.hovered_element: Optional[str] = None
        
        self.fonts: Dict[str, pygame.font.Font] = {}
        self._load_fonts()
        
        self.callbacks: Dict[str, Callable] = {}
        
        self.tooltip_text: Optional[str] = None
        self.tooltip_position: tuple = (0, 0)
        
        self.notifications: List[Dict[str, Any]] = []
        self.notification_duration = 3.0
    
    def _load_fonts(self):
        """使用字体管理器加载字体"""
        sizes = [12, 14, 16, 18, 20, 24, 28, 32, 36, 48, 64]
        
        for size in sizes:
            self.fonts[f"{size}"] = get_font(size)
    
    def get_font(self, size: int) -> pygame.font.Font:
        return self.fonts.get(f"{size}", get_font(16))
    
    def register_element(self, element_id: str, element: Any):
        self.elements[element_id] = element
    
    def unregister_element(self, element_id: str):
        if element_id in self.elements:
            del self.elements[element_id]
    
    def get_element(self, element_id: str) -> Optional[Any]:
        return self.elements.get(element_id)
    
    def change_state(self, new_state: UIState):
        self.previous_state = self.current_state
        self.current_state = new_state
    
    def previous_menu(self):
        if self.previous_state:
            self.change_state(self.previous_state)
    
    def register_callback(self, event_name: str, callback: Callable):
        self.callbacks[event_name] = callback
    
    def trigger_callback(self, event_name: str, *args, **kwargs):
        if event_name in self.callbacks:
            self.callbacks[event_name](*args, **kwargs)
    
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEMOTION:
            self._handle_mouse_motion(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event.pos, event.button)
        elif event.type == pygame.KEYDOWN:
            self._handle_key_press(event.key, event.unicode)
    
    def _handle_mouse_motion(self, pos: tuple):
        self.hovered_element = None
        
        for element_id, element in self.elements.items():
            if hasattr(element, 'contains_point') and element.contains_point(pos):
                self.hovered_element = element_id
                if hasattr(element, 'on_hover'):
                    element.on_hover(pos)
                break
    
    def _handle_mouse_click(self, pos: tuple, button: int):
        if button == 1:
            for element_id, element in self.elements.items():
                if hasattr(element, 'contains_point') and element.contains_point(pos):
                    if hasattr(element, 'on_click'):
                        element.on_click(pos)
                    self.focused_element = element_id
                    break
    
    def _handle_key_press(self, key: int, unicode: str):
        if self.focused_element and self.focused_element in self.elements:
            element = self.elements[self.focused_element]
            if hasattr(element, 'on_key_press'):
                element.on_key_press(key, unicode)
    
    def show_tooltip(self, text: str, position: tuple):
        self.tooltip_text = text
        self.tooltip_position = position
    
    def hide_tooltip(self):
        self.tooltip_text = None
    
    def add_notification(self, text: str, color: tuple = (255, 255, 255), 
                         duration: float = None):
        self.notifications.append({
            "text": text,
            "color": color,
            "duration": duration or self.notification_duration,
            "start_time": pygame.time.get_ticks() / 1000
        })
    
    def update(self, delta_time: float):
        current_time = pygame.time.get_ticks() / 1000
        
        self.notifications = [
            n for n in self.notifications
            if current_time - n["start_time"] < n["duration"]
        ]
        
        for element in self.elements.values():
            if hasattr(element, 'update'):
                element.update(delta_time)
    
    def render(self):
        for element in self.elements.values():
            if hasattr(element, 'visible') and not element.visible:
                continue
            
            if hasattr(element, 'render'):
                element.render(self.screen)
        
        self._render_tooltip()
        self._render_notifications()
    
    def _render_tooltip(self):
        if not self.tooltip_text:
            return
        
        font = self.get_font(14)
        lines = self.tooltip_text.split('\n')
        
        max_width = max(font.size(line)[0] for line in lines)
        total_height = sum(font.size(line)[1] for line in lines) + 10
        
        x, y = self.tooltip_position
        x = min(x, self.screen_width - max_width - 20)
        y = min(y, self.screen_height - total_height - 10)
        
        tooltip_surface = pygame.Surface((max_width + 20, total_height), pygame.SRCALPHA)
        tooltip_surface.fill((30, 30, 30, 230))
        
        pygame.draw.rect(tooltip_surface, (100, 100, 100), 
                         (0, 0, max_width + 20, total_height), 1)
        
        for i, line in enumerate(lines):
            text_surface = font.render(line, True, (255, 255, 255))
            tooltip_surface.blit(text_surface, (10, 5 + i * font.get_linesize()))
        
        self.screen.blit(tooltip_surface, (x, y))
    
    def _render_notifications(self):
        font = self.get_font(18)
        y_offset = 100
        
        for notification in self.notifications:
            alpha = 255
            current_time = pygame.time.get_ticks() / 1000
            elapsed = current_time - notification["start_time"]
            
            if elapsed > notification["duration"] - 0.5:
                alpha = int(255 * (notification["duration"] - elapsed) / 0.5)
            
            text_surface = font.render(notification["text"], True, notification["color"])
            text_surface.set_alpha(alpha)
            
            x = (self.screen_width - text_surface.get_width()) // 2
            self.screen.blit(text_surface, (x, y_offset))
            
            y_offset += text_surface.get_height() + 10
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        
        for element in self.elements.values():
            if hasattr(element, 'on_resize'):
                element.on_resize(width, height)
