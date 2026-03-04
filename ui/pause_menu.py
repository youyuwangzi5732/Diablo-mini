"""
暂停菜单和设置界面
"""
from typing import Dict, List, Optional, Any, Callable
import pygame

from .font_manager import get_font
from .ui_element import UIElement, UIButton, UILabel, UIPanel, UIProgressBar
from .ui_manager import UIManager, UIState


class PauseMenu:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = False
        
        self.panel_width = 400
        self.panel_height = 450
        
        self.elements: Dict[str, UIElement] = {}
        self._create_elements()
        
        self.background_overlay = None
    
    def _create_elements(self):
        title_x = (self.screen_width - 100) // 2
        self.elements["title"] = UILabel(
            id="title",
            x=title_x,
            y=100,
            text="游戏暂停",
            font_size=36,
            text_color=(200, 180, 100)
        )
        
        button_width = 200
        button_height = 50
        button_x = (self.screen_width - button_width) // 2
        button_start_y = 200
        button_spacing = 70
        
        self.elements["btn_resume"] = UIButton(
            id="btn_resume",
            x=button_x,
            y=button_start_y,
            width=button_width,
            height=button_height,
            text="继续游戏",
            font_size=20,
            on_click_callback=self._on_resume
        )
        
        self.elements["btn_settings"] = UIButton(
            id="btn_settings",
            x=button_x,
            y=button_start_y + button_spacing,
            width=button_width,
            height=button_height,
            text="设置",
            font_size=20,
            on_click_callback=self._on_settings
        )
        
        self.elements["btn_main_menu"] = UIButton(
            id="btn_main_menu",
            x=button_x,
            y=button_start_y + button_spacing * 2,
            width=button_width,
            height=button_height,
            text="返回主菜单",
            font_size=20,
            on_click_callback=self._on_main_menu
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
    
    def _on_resume(self, button: UIButton):
        self.ui_manager.trigger_callback("resume_game")
    
    def _on_settings(self, button: UIButton):
        self.ui_manager.trigger_callback("open_settings")
    
    def _on_main_menu(self, button: UIButton):
        self.ui_manager.trigger_callback("return_to_main_menu")
    
    def _on_quit(self, button: UIButton):
        self.ui_manager.trigger_callback("quit_game")
    
    def toggle(self):
        self.visible = not self.visible
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def update(self, delta_time: float):
        for element in self.elements.values():
            if hasattr(element, 'update'):
                element.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        for element in self.elements.values():
            if hasattr(element, 'render'):
                element.render(surface)
    
    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        
        for element in self.elements.values():
            if hasattr(element, 'contains_point') and element.contains_point(pos):
                if hasattr(element, 'on_click'):
                    element.on_click(pos)
                return True
        
        return True
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        
        title = self.elements.get("title")
        if title:
            title.x = (width - 100) // 2
        
        button_width = 200
        button_x = (width - button_width) // 2
        button_start_y = 200
        button_spacing = 70
        
        for i, btn_id in enumerate(["btn_resume", "btn_settings", "btn_main_menu", "btn_quit"]):
            btn = self.elements.get(btn_id)
            if btn:
                btn.x = button_x
                btn.y = button_start_y + i * button_spacing


class SettingsMenu:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = False
        
        self.panel_width = 500
        self.panel_height = 600
        
        self.settings = {
            "master_volume": 100,
            "music_volume": 80,
            "sfx_volume": 100,
            "voice_volume": 100,
            "fullscreen": False,
            "vsync": True,
            "ui_scale": 1.0,
            "show_damage_numbers": True,
            "show_health_bars": True,
            "auto_pickup_gold": True,
            "auto_pickup_gems": False,
        }
        
        self.elements: Dict[str, UIElement] = {}
        self.sliders: Dict[str, Any] = {}
        self._create_elements()
    
    def _create_elements(self):
        self.elements = {}
        self.sliders = {}
        
        self.elements["title"] = UILabel(
            id="title",
            x=200,
            y=20,
            text="设置",
            font_size=28,
            text_color=(200, 180, 100)
        )
        
        self.elements["audio_label"] = UILabel(
            id="audio_label",
            x=20,
            y=70,
            text="音频设置",
            font_size=20,
            text_color=(180, 160, 100)
        )
        
        slider_start_y = 110
        slider_spacing = 50
        
        volume_settings = [
            ("master_volume", "主音量"),
            ("music_volume", "音乐音量"),
            ("sfx_volume", "音效音量"),
            ("voice_volume", "语音音量"),
        ]
        
        for i, (setting_id, label) in enumerate(volume_settings):
            y = slider_start_y + i * slider_spacing
            self._create_slider(20, y, setting_id, label)
        
        self.elements["video_label"] = UILabel(
            id="video_label",
            x=20,
            y=330,
            text="视频设置",
            font_size=20,
            text_color=(180, 160, 100)
        )
        
        toggle_start_y = 370
        toggle_spacing = 40
        
        toggle_settings = [
            ("fullscreen", "全屏模式"),
            ("vsync", "垂直同步"),
            ("show_damage_numbers", "显示伤害数字"),
            ("show_health_bars", "显示血条"),
        ]
        
        for i, (setting_id, label) in enumerate(toggle_settings):
            y = toggle_start_y + i * toggle_spacing
            self._create_toggle(20, y, setting_id, label)

        scale_y = 530
        self.elements["label_ui_scale"] = UILabel(
            id="label_ui_scale",
            x=20,
            y=scale_y,
            text="界面比例",
            font_size=16,
            text_color=(200, 200, 200)
        )
        self.elements["value_ui_scale"] = UIButton(
            id="value_ui_scale",
            x=300,
            y=scale_y - 6,
            width=120,
            height=30,
            text=f"{int(self.settings.get('ui_scale', 1.0) * 100)}%",
            font_size=14,
            on_click_callback=self._cycle_ui_scale
        )
        
        self.elements["btn_back"] = UIButton(
            id="btn_back",
            x=200,
            y=self.panel_height - 36,
            width=100,
            height=28,
            text="返回",
            font_size=18,
            on_click_callback=self._on_back
        )
    
    def _create_slider(self, x: int, y: int, setting_id: str, label: str):
        label_element = UILabel(
            id=f"label_{setting_id}",
            x=x,
            y=y,
            text=label,
            font_size=16,
            text_color=(200, 200, 200)
        )
        self.elements[f"label_{setting_id}"] = label_element
        
        value = self.settings.get(setting_id, 50)
        value_element = UILabel(
            id=f"value_{setting_id}",
            x=x + 350,
            y=y,
            text=f"{value}%",
            font_size=16,
            text_color=(255, 255, 255)
        )
        self.elements[f"value_{setting_id}"] = value_element
        
        self.sliders[setting_id] = {
            "x": x,
            "y": y + 25,
            "width": 350,
            "height": 10,
            "value": value,
            "dragging": False
        }
    
    def _create_toggle(self, x: int, y: int, setting_id: str, label: str):
        label_element = UILabel(
            id=f"label_{setting_id}",
            x=x,
            y=y,
            text=label,
            font_size=16,
            text_color=(200, 200, 200)
        )
        self.elements[f"label_{setting_id}"] = label_element
        
        value = self.settings.get(setting_id, False)
        toggle_element = UIButton(
            id=f"toggle_{setting_id}",
            x=x + 350,
            y=y - 5,
            width=60,
            height=30,
            text="开" if value else "关",
            font_size=14,
            on_click_callback=lambda b, s=setting_id: self._toggle_setting(s)
        )
        self.elements[f"toggle_{setting_id}"] = toggle_element
    
    def _toggle_setting(self, setting_id: str):
        self.settings[setting_id] = not self.settings[setting_id]
        
        toggle = self.elements.get(f"toggle_{setting_id}")
        if toggle:
            toggle.text = "开" if self.settings[setting_id] else "关"
        
        self.ui_manager.trigger_callback("setting_changed", setting_id, self.settings[setting_id])

    def _cycle_ui_scale(self, button: UIButton):
        options = [0.85, 1.0, 1.15, 1.3]
        current = float(self.settings.get("ui_scale", 1.0))
        nearest = min(range(len(options)), key=lambda i: abs(options[i] - current))
        next_index = (nearest + 1) % len(options)
        value = options[next_index]
        self.settings["ui_scale"] = value
        button.text = f"{int(value * 100)}%"
        self.ui_manager.trigger_callback("setting_changed", "ui_scale", value)
    
    def _on_back(self, button: UIButton):
        self.ui_manager.trigger_callback("close_settings")
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def toggle(self):
        self.visible = not self.visible
    
    def get_settings(self) -> Dict[str, Any]:
        return self.settings.copy()
    
    def load_settings(self, settings: Dict[str, Any]):
        self.settings.update(settings)
        self._update_ui_from_settings()
    
    def _update_ui_from_settings(self):
        for setting_id, value in self.settings.items():
            if setting_id in self.sliders:
                self.sliders[setting_id]["value"] = value
                value_label = self.elements.get(f"value_{setting_id}")
                if value_label:
                    value_label.set_text(f"{value}%")
            
            toggle = self.elements.get(f"toggle_{setting_id}")
            if toggle:
                toggle.text = "开" if value else "关"
        scale_button = self.elements.get("value_ui_scale")
        if scale_button:
            scale_button.text = f"{int(float(self.settings.get('ui_scale', 1.0)) * 100)}%"
    
    def update(self, delta_time: float):
        for element in self.elements.values():
            if hasattr(element, 'update'):
                element.update(delta_time)
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        panel_x = (self.screen_width - self.panel_width) // 2
        panel_y = (self.screen_height - self.panel_height) // 2
        
        panel_surface = pygame.Surface(
            (self.panel_width, self.panel_height),
            pygame.SRCALPHA
        )
        panel_surface.fill((30, 30, 30, 240))
        pygame.draw.rect(panel_surface, (100, 100, 100),
                         (0, 0, self.panel_width, self.panel_height), 2)
        
        for element in self.elements.values():
            if hasattr(element, 'render'):
                element.render(panel_surface)
        
        for setting_id, slider in self.sliders.items():
            self._render_slider(panel_surface, slider)
        
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def _render_slider(self, surface: pygame.Surface, slider: Dict[str, Any]):
        x, y = slider["x"], slider["y"]
        width, height = slider["width"], slider["height"]
        value = slider["value"]
        
        pygame.draw.rect(surface, (50, 50, 50), (x, y, width, height))
        
        fill_width = int(width * value / 100)
        if fill_width > 0:
            pygame.draw.rect(surface, (100, 150, 200), (x, y, fill_width, height))
        
        pygame.draw.rect(surface, (100, 100, 100), (x, y, width, height), 1)
        
        handle_x = x + fill_width
        pygame.draw.circle(surface, (200, 200, 200), (handle_x, y + height // 2), 8)
    
    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        
        panel_x = (self.screen_width - self.panel_width) // 2
        panel_y = (self.screen_height - self.panel_height) // 2
        local_pos = (pos[0] - panel_x, pos[1] - panel_y)
        
        for setting_id, slider in self.sliders.items():
            slider_rect = pygame.Rect(
                slider["x"], slider["y"],
                slider["width"], slider["height"] + 20
            )
            if slider_rect.collidepoint(local_pos):
                self._update_slider_value(setting_id, local_pos[0])
                return True
        
        for element in self.elements.values():
            if hasattr(element, 'contains_point'):
                adjusted_pos = (pos[0] - panel_x, pos[1] - panel_y)
                if element.contains_point(adjusted_pos):
                    if hasattr(element, 'on_click'):
                        element.on_click(adjusted_pos)
                    return True
        
        return True
    
    def _update_slider_value(self, setting_id: str, click_x: int):
        slider = self.sliders.get(setting_id)
        if not slider:
            return
        
        relative_x = click_x - slider["x"]
        value = max(0, min(100, int(relative_x / slider["width"] * 100)))
        
        slider["value"] = value
        self.settings[setting_id] = value
        
        value_label = self.elements.get(f"value_{setting_id}")
        if value_label:
            value_label.set_text(f"{value}%")
        
        self.ui_manager.trigger_callback("setting_changed", setting_id, value)
    
    def handle_motion(self, pos: tuple):
        if not self.visible:
            return
        
        for setting_id, slider in self.sliders.items():
            if slider["dragging"]:
                panel_x = (self.screen_width - self.panel_width) // 2
                local_x = pos[0] - panel_x
                self._update_slider_value(setting_id, local_x)
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        self._create_elements()
        self._update_ui_from_settings()
