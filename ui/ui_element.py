"""
UI基础元素
"""
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
import pygame

from .font_manager import get_font


@dataclass
class UIElement:
    id: str
    x: int
    y: int
    width: int
    height: int
    
    visible: bool = True
    enabled: bool = True
    
    background_color: Tuple[int, int, int] = (40, 40, 40)
    border_color: Tuple[int, int, int] = (80, 80, 80)
    border_width: int = 1
    
    hover_color: Optional[Tuple[int, int, int]] = None
    click_color: Optional[Tuple[int, int, int]] = None
    
    _is_hovered: bool = field(default=False, repr=False)
    _is_clicked: bool = field(default=False, repr=False)
    
    def contains_point(self, pos: Tuple[int, int]) -> bool:
        return (self.x <= pos[0] <= self.x + self.width and
                self.y <= pos[1] <= self.y + self.height)
    
    def on_hover(self, pos: Tuple[int, int]):
        self._is_hovered = True
    
    def on_click(self, pos: Tuple[int, int]):
        self._is_clicked = True
    
    def on_key_press(self, key: int, unicode: str):
        pass
    
    def update(self, delta_time: float):
        self._is_hovered = False
        self._is_clicked = False
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        color = self.background_color
        if self._is_hovered and self.hover_color:
            color = self.hover_color
        if self._is_clicked and self.click_color:
            color = self.click_color
        
        pygame.draw.rect(surface, color, 
                         (self.x, self.y, self.width, self.height))
        
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color,
                             (self.x, self.y, self.width, self.height),
                             self.border_width)
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def set_size(self, width: int, height: int):
        self.width = width
        self.height = height
    
    def center_on_screen(self, screen_width: int, screen_height: int):
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2


class UILabel(UIElement):
    def __init__(self, id: str, x: int, y: int, text: str = "",
                 font_size: int = 16, text_color: Tuple[int, int, int] = (255, 255, 255),
                 **kwargs):
        super().__init__(id, x, y, 0, 0, **kwargs)
        
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        
        self.font = get_font(font_size)
        self._update_size()
        
        self.background_color = (0, 0, 0, 0)
        self.border_width = 0
    
    def _update_size(self):
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            self.width = text_surface.get_width()
            self.height = text_surface.get_height()
    
    def set_text(self, text: str):
        self.text = text
        self._update_size()
    
    def render(self, surface: pygame.Surface):
        if not self.visible or not self.text:
            return
        
        text_surface = self.font.render(self.text, True, self.text_color)
        surface.blit(text_surface, (self.x, self.y))


class UIButton(UIElement):
    def __init__(self, id: str, x: int, y: int, width: int, height: int,
                 text: str = "", font_size: int = 16,
                 text_color: Tuple[int, int, int] = (255, 255, 255),
                 on_click_callback: Callable = None,
                 **kwargs):
        super().__init__(id, x, y, width, height, **kwargs)
        
        self.text = text
        self.font_size = font_size
        self.text_color = text_color
        
        self.font = get_font(font_size)
        self.on_click_callback = on_click_callback
        
        self.background_color = (60, 60, 60)
        self.hover_color = (80, 80, 80)
        self.click_color = (100, 100, 100)
        self.border_color = (120, 120, 120)
    
    def on_click(self, pos: Tuple[int, int]):
        super().on_click(pos)
        if self.on_click_callback:
            self.on_click_callback(self)
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        super().render(surface)
        
        if self.text:
            text_surface = self.font.render(self.text, True, self.text_color)
            text_x = self.x + (self.width - text_surface.get_width()) // 2
            text_y = self.y + (self.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))


class UIPanel(UIElement):
    def __init__(self, id: str, x: int, y: int, width: int, height: int,
                 title: str = "", **kwargs):
        super().__init__(id, x, y, width, height, **kwargs)
        
        self.title = title
        self.title_font = get_font(18)
        
        self.children: List[UIElement] = []
        
        self.background_color = (30, 30, 30, 200)
        self.border_color = (100, 100, 100)
        self.title_color = (200, 180, 100)
        
        self.draggable = False
        self._dragging = False
        self._drag_offset = (0, 0)
    
    def add_child(self, element: UIElement):
        self.children.append(element)
    
    def remove_child(self, element_id: str):
        self.children = [c for c in self.children if c.id != element_id]
    
    def on_click(self, pos: Tuple[int, int]):
        super().on_click(pos)
        
        for child in self.children:
            if child.contains_point(pos):
                child.on_click(pos)
                return
    
    def on_hover(self, pos: Tuple[int, int]):
        super().on_hover(pos)
        
        for child in self.children:
            if child.contains_point(pos):
                child.on_hover(pos)
                return
    
    def update(self, delta_time: float):
        super().update(delta_time)
        for child in self.children:
            child.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        panel_surface.fill(self.background_color)
        
        pygame.draw.rect(panel_surface, self.border_color,
                         (0, 0, self.width, self.height), 2)
        
        if self.title:
            title_surface = self.title_font.render(self.title, True, self.title_color)
            panel_surface.blit(title_surface, (10, 5))
            
            pygame.draw.line(panel_surface, self.border_color,
                             (0, 30), (self.width, 30), 1)
        
        for child in self.children:
            child.render(panel_surface)
        
        surface.blit(panel_surface, (self.x, self.y))


class UIContainer(UIElement):
    def __init__(self, id: str, x: int, y: int, width: int, height: int, **kwargs):
        super().__init__(id, x, y, width, height, **kwargs)
        
        self.children: Dict[str, UIElement] = {}
        self.layout = "vertical"
        self.spacing = 5
        self.padding = 10
    
    def add_element(self, element: UIElement):
        self.children[element.id] = element
        self._update_layout()
    
    def remove_element(self, element_id: str):
        if element_id in self.children:
            del self.children[element_id]
            self._update_layout()
    
    def _update_layout(self):
        if self.layout == "vertical":
            current_y = self.y + self.padding
            for element in self.children.values():
                element.x = self.x + self.padding
                element.y = current_y
                current_y += element.height + self.spacing
        
        elif self.layout == "horizontal":
            current_x = self.x + self.padding
            for element in self.children.values():
                element.x = current_x
                element.y = self.y + self.padding
                current_x += element.width + self.spacing
    
    def update(self, delta_time: float):
        super().update(delta_time)
        for child in self.children.values():
            child.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        super().render(surface)
        
        for child in self.children.values():
            child.render(surface)
    
    def on_resize(self, width: int, height: int):
        self._update_layout()


class UIImage(UIElement):
    def __init__(self, id: str, x: int, y: int, image: pygame.Surface = None, **kwargs):
        if image:
            width = image.get_width()
            height = image.get_height()
        else:
            width = kwargs.pop('width', 100)
            height = kwargs.pop('height', 100)
        
        super().__init__(id, x, y, width, height, **kwargs)
        
        self.image = image
        self.border_width = 0
    
    def set_image(self, image: pygame.Surface):
        self.image = image
        self.width = image.get_width()
        self.height = image.get_height()
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        if self.image:
            surface.blit(self.image, (self.x, self.y))
        else:
            super().render(surface)


class UIProgressBar(UIElement):
    def __init__(self, id: str, x: int, y: int, width: int, height: int,
                 value: float = 0, max_value: float = 100,
                 bar_color: Tuple[int, int, int] = (0, 200, 0),
                 background_color: Tuple[int, int, int] = (40, 40, 40),
                 show_text: bool = True, **kwargs):
        super().__init__(id, x, y, width, height, **kwargs)
        
        self.value = value
        self.max_value = max_value
        self.bar_color = bar_color
        self.show_text = show_text
        
        self.background_color = background_color
        self.border_width = 1
    
    def set_value(self, value: float):
        self.value = max(0, min(value, self.max_value))
    
    def get_percentage(self) -> float:
        if self.max_value <= 0:
            return 0
        return self.value / self.max_value
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        pygame.draw.rect(surface, self.background_color,
                         (self.x, self.y, self.width, self.height))
        
        bar_width = int(self.width * self.get_percentage())
        if bar_width > 0:
            pygame.draw.rect(surface, self.bar_color,
                             (self.x, self.y, bar_width, self.height))
        
        if self.border_width > 0:
            pygame.draw.rect(surface, self.border_color,
                             (self.x, self.y, self.width, self.height),
                             self.border_width)
        
        if self.show_text:
            font = get_font(12)
            text = f"{int(self.value)}/{int(self.max_value)}"
            text_surface = font.render(text, True, (255, 255, 255))
            text_x = self.x + (self.width - text_surface.get_width()) // 2
            text_y = self.y + (self.height - text_surface.get_height()) // 2
            surface.blit(text_surface, (text_x, text_y))
