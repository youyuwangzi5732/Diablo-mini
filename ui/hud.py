"""
HUD系统 - 游戏内抬头显示（商业化级别）
"""
from typing import Dict, List, Optional, Any
import pygame
import math

from .ui_element import UIElement, UILabel, UIProgressBar, UIButton
from .ui_manager import UIManager
from .font_manager import get_font


class SkillCooldownData:
    """技能冷却数据"""
    def __init__(self):
        self.remaining: float = 0.0
        self.total: float = 0.0
        self.skill_id: Optional[str] = None
        self.skill_name: str = ""
        self.skill_icon: str = ""
        self.mana_cost: int = 0
        self.is_ready: bool = True


class SkillSlotRenderer:
    """技能槽渲染器"""
    
    def __init__(self, x: int, y: int, size: int = 50):
        self.x = x
        self.y = y
        self.size = size
        self.cooldown_data = SkillCooldownData()
        self.is_hovered = False
        self.key_binding: Optional[int] = None
    
    def set_cooldown(self, remaining: float, total: float):
        self.cooldown_data.remaining = remaining
        self.cooldown_data.total = total
        self.cooldown_data.is_ready = remaining <= 0
    
    def set_skill(self, skill_id: str, name: str, mana_cost: int = 0):
        self.cooldown_data.skill_id = skill_id
        self.cooldown_data.skill_name = name
        self.cooldown_data.mana_cost = mana_cost
    
    def update(self, delta_time: float):
        if self.cooldown_data.remaining > 0:
            self.cooldown_data.remaining -= delta_time
            if self.cooldown_data.remaining < 0:
                self.cooldown_data.remaining = 0
            self.cooldown_data.is_ready = self.cooldown_data.remaining <= 0
    
    def render(self, surface: pygame.Surface):
        # 绘制技能槽背景
        bg_color = (30, 30, 35)
        border_color = (80, 80, 90)
        
        if self.is_hovered:
            border_color = (150, 150, 180)
        
        if not self.cooldown_data.is_ready:
            bg_color = (20, 20, 25)
            border_color = (60, 60, 70)
        
        pygame.draw.rect(surface, bg_color, (self.x, self.y, self.size, self.size))
        pygame.draw.rect(surface, border_color, (self.x, self.y, self.size, self.size), 2)
        
        # 绘制技能图标/名称
        if self.cooldown_data.skill_name:
            font = get_font(14)
            name_initial = self.cooldown_data.skill_name[:2]
            text_color = (200, 200, 200) if self.cooldown_data.is_ready else (100, 100, 100)
            text = font.render(name_initial, True, text_color)
            text_x = self.x + (self.size - text.get_width()) // 2
            text_y = self.y + (self.size - text.get_height()) // 2 - 5
            surface.blit(text, (text_x, text_y))
        
        # 绘制冷却遮罩
        if not self.cooldown_data.is_ready and self.cooldown_data.total > 0:
            self._render_cooldown_overlay(surface)
        
        # 绘制按键绑定
        if self.key_binding is not None:
            key_font = get_font(10)
            key_text = key_font.render(str(self.key_binding), True, (150, 150, 150))
            surface.blit(key_text, (self.x + 3, self.y + self.size - 12))
        
        # 绘制法力消耗
        if self.cooldown_data.mana_cost > 0 and self.cooldown_data.is_ready:
            mana_font = get_font(9)
            mana_text = mana_font.render(str(self.cooldown_data.mana_cost), True, (100, 150, 255))
            surface.blit(mana_text, (self.x + self.size - 15, self.y + 3))
    
    def _render_cooldown_overlay(self, surface: pygame.Surface):
        """渲染冷却遮罩"""
        if self.cooldown_data.total <= 0:
            return
        
        progress = self.cooldown_data.remaining / self.cooldown_data.total
        
        # 绘制扇形冷却效果
        center_x = self.x + self.size // 2
        center_y = self.y + self.size // 2
        radius = self.size // 2 - 2
        
        # 创建冷却遮罩表面
        overlay = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        
        # 绘制半透明遮罩
        overlay.fill((0, 0, 0, 150))
        
        # 计算扇形角度
        start_angle = -math.pi / 2  # 从顶部开始
        sweep_angle = progress * 2 * math.pi
        
        # 绘制扇形（已冷却部分为透明）
        if progress < 1.0:
            points = [(self.size // 2, self.size // 2)]
            for i in range(int(sweep_angle * 20) + 1):
                angle = start_angle + sweep_angle * i / max(1, int(sweep_angle * 20))
                px = self.size // 2 + int(radius * math.cos(angle))
                py = self.size // 2 + int(radius * math.sin(angle))
                points.append((px, py))
            
            if len(points) > 2:
                pygame.draw.polygon(overlay, (0, 0, 0, 0), points)
        
        surface.blit(overlay, (self.x, self.y))
        
        # 绘制冷却时间文本
        if self.cooldown_data.remaining > 0:
            font = get_font(16)
            cd_text = f"{self.cooldown_data.remaining:.1f}"
            text = font.render(cd_text, True, (255, 255, 255))
            text_x = self.x + (self.size - text.get_width()) // 2
            text_y = self.y + (self.size - text.get_height()) // 2 + 5
            surface.blit(text, (text_x, text_y))
    
    def render_tooltip(self, surface: pygame.Surface, mouse_pos: tuple):
        """渲染技能提示框"""
        if not self.is_hovered or not self.cooldown_data.skill_name:
            return
        
        tooltip_width = 200
        tooltip_height = 80
        
        # 计算提示框位置
        tooltip_x = mouse_pos[0] + 15
        tooltip_y = mouse_pos[1] + 15
        
        # 避免超出屏幕
        if tooltip_x + tooltip_width > surface.get_width():
            tooltip_x = mouse_pos[0] - tooltip_width - 15
        if tooltip_y + tooltip_height > surface.get_height():
            tooltip_y = mouse_pos[1] - tooltip_height - 15
        
        # 绘制提示框背景
        tooltip_surface = pygame.Surface((tooltip_width, tooltip_height), pygame.SRCALPHA)
        pygame.draw.rect(tooltip_surface, (20, 20, 25, 230), (0, 0, tooltip_width, tooltip_height))
        pygame.draw.rect(tooltip_surface, (100, 100, 120), (0, 0, tooltip_width, tooltip_height), 1)
        
        # 技能名称
        font = get_font(14)
        name_text = font.render(self.cooldown_data.skill_name, True, (255, 220, 100))
        tooltip_surface.blit(name_text, (10, 10))
        
        # 冷却时间
        small_font = get_font(12)
        if self.cooldown_data.is_ready:
            cd_text = small_font.render("就绪", True, (100, 255, 100))
        else:
            cd_text = small_font.render(f"冷却: {self.cooldown_data.remaining:.1f}秒", True, (255, 150, 100))
        tooltip_surface.blit(cd_text, (10, 35))
        
        # 法力消耗
        if self.cooldown_data.mana_cost > 0:
            mana_text = small_font.render(f"法力消耗: {self.cooldown_data.mana_cost}", True, (100, 150, 255))
            tooltip_surface.blit(mana_text, (10, 55))
        
        surface.blit(tooltip_surface, (tooltip_x, tooltip_y))


class HUD:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.skill_slots: List[SkillSlotRenderer] = []
        self.quick_potions = [None] * 4
        
        self.minimap_size = 150
        self.show_minimap = True
        
        self.elements: Dict[str, UIElement] = {}
        self._create_elements()
        
        # 屏幕震动效果
        self.screen_shake_intensity = 0.0
        self.screen_shake_duration = 0.0
        self.shake_offset = (0, 0)
    
    def _create_elements(self):
        bar_width = 300
        bar_height = 20
        margin = 20
        
        self.elements["health_bar"] = UIProgressBar(
            id="health_bar",
            x=margin,
            y=self.screen_height - bar_height - margin - 30,
            width=bar_width,
            height=bar_height,
            bar_color=(200, 50, 50),
            background_color=(60, 20, 20)
        )
        
        self.elements["mana_bar"] = UIProgressBar(
            id="mana_bar",
            x=margin,
            y=self.screen_height - bar_height - margin,
            width=bar_width,
            height=bar_height,
            bar_color=(50, 100, 200),
            background_color=(20, 30, 60)
        )
        
        self.elements["experience_bar"] = UIProgressBar(
            id="experience_bar",
            x=margin,
            y=self.screen_height - 10,
            width=bar_width,
            height=5,
            bar_color=(100, 200, 100),
            background_color=(30, 60, 30),
            show_text=False
        )
        
        self.elements["level_label"] = UILabel(
            id="level_label",
            x=margin + bar_width + 10,
            y=self.screen_height - bar_height - margin - 30,
            text="Lv.1",
            font_size=16,
            text_color=(255, 220, 100)
        )
        
        self.elements["health_text"] = UILabel(
            id="health_text",
            x=margin + bar_width + 10,
            y=self.screen_height - bar_height - margin - 10,
            text="100/100",
            font_size=12,
            text_color=(200, 50, 50)
        )
        
        # 创建技能槽渲染器
        skill_bar_width = 60 * 6 + 10
        skill_bar_x = (self.screen_width - skill_bar_width) // 2
        skill_bar_y = self.screen_height - 70
        
        for i in range(6):
            slot = SkillSlotRenderer(
                x=skill_bar_x + i * 60 + 5,
                y=skill_bar_y,
                size=50
            )
            slot.key_binding = i + 1
            self.skill_slots.append(slot)
        
        self.elements["minimap_border"] = UIElement(
            id="minimap_border",
            x=self.screen_width - self.minimap_size - 10,
            y=10,
            width=self.minimap_size,
            height=self.minimap_size,
            background_color=(30, 30, 30, 150),
            border_color=(100, 100, 100)
        )
        
        self.elements["gold_label"] = UILabel(
            id="gold_label",
            x=self.screen_width - 160,
            y=self.screen_height - 30,
            text="金币: 0",
            font_size=14,
            text_color=(255, 215, 0)
        )
    
    def update_character(self, character: Any):
        if hasattr(character, 'current_health') and hasattr(character, 'get_max_health'):
            health_bar = self.elements.get("health_bar")
            if health_bar:
                health_bar.value = character.current_health
                health_bar.max_value = character.get_max_health()
            
            health_text = self.elements.get("health_text")
            if health_text:
                health_text.set_text(
                    f"{int(character.current_health)}/{int(character.get_max_health())}"
                )
        
        if hasattr(character, 'current_resource') and hasattr(character, 'get_max_resource'):
            mana_bar = self.elements.get("mana_bar")
            if mana_bar:
                mana_bar.value = character.current_resource
                mana_bar.max_value = character.get_max_resource()
        
        if hasattr(character, 'level'):
            level_label = self.elements.get("level_label")
            if level_label:
                level_label.set_text(f"Lv.{character.level}")
        
        if hasattr(character, 'gold'):
            gold_label = self.elements.get("gold_label")
            if gold_label:
                gold_label.set_text(f"金币: {character.gold}")
    
    def update_skill_bar(self, skills: List[Dict[str, Any]]):
        for i, skill in enumerate(skills):
            if i >= len(self.skill_slots):
                break
            
            if skill:
                self.skill_slots[i].set_skill(
                    skill.get("id", ""),
                    skill.get("name", ""),
                    skill.get("mana_cost", 0)
                )
    
    def set_skill_cooldown(self, slot_index: int, remaining: float, total: float):
        if 0 <= slot_index < len(self.skill_slots):
            self.skill_slots[slot_index].set_cooldown(remaining, total)
    
    def trigger_screen_shake(self, intensity: float, duration: float):
        """触发屏幕震动"""
        self.screen_shake_intensity = intensity
        self.screen_shake_duration = duration
    
    def toggle_minimap(self):
        self.show_minimap = not self.show_minimap
        minimap = self.elements.get("minimap_border")
        if minimap:
            minimap.visible = self.show_minimap
    
    def update(self, delta_time: float):
        for element in self.elements.values():
            if hasattr(element, 'update'):
                element.update(delta_time)
        
        # 更新技能槽
        for slot in self.skill_slots:
            slot.update(delta_time)
        
        # 更新屏幕震动
        if self.screen_shake_duration > 0:
            self.screen_shake_duration -= delta_time
            import random
            self.shake_offset = (
                random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity)),
                random.randint(-int(self.screen_shake_intensity), int(self.screen_shake_intensity))
            )
        else:
            self.shake_offset = (0, 0)
            self.screen_shake_intensity = 0
    
    def handle_mouse_motion(self, pos: tuple):
        """处理鼠标移动"""
        for slot in self.skill_slots:
            slot.is_hovered = (
                slot.x <= pos[0] <= slot.x + slot.size and
                slot.y <= pos[1] <= slot.y + slot.size
            )
    
    def render(self, surface: pygame.Surface):
        for element in self.elements.values():
            if hasattr(element, 'visible') and not element.visible:
                continue
            
            if hasattr(element, 'render'):
                element.render(surface)
        
        # 渲染技能槽
        mouse_pos = pygame.mouse.get_pos()
        for slot in self.skill_slots:
            slot.render(surface)
            slot.render_tooltip(surface, mouse_pos)
        
        self._render_minimap(surface)
    
    def _render_minimap(self, surface: pygame.Surface):
        if not self.show_minimap:
            return
        
        minimap = self.elements.get("minimap_border")
        if not minimap:
            return
        
        minimap_surface = pygame.Surface(
            (self.minimap_size - 4, self.minimap_size - 4),
            pygame.SRCALPHA
        )
        minimap_surface.fill((20, 20, 20, 200))
        
        center_x = self.minimap_size // 2
        center_y = self.minimap_size // 2
        
        pygame.draw.circle(minimap_surface, (100, 200, 100), (center_x, center_y), 3)
        
        surface.blit(minimap_surface, (minimap.x + 2, minimap.y + 2))
    
    def render_area_name(self, surface: pygame.Surface, area_name: str, is_safe_zone: bool = False):
        """渲染当前区域名称"""
        font = get_font(24)
        
        # 区域名称
        name_text = font.render(area_name, True, (255, 220, 100))
        
        # 安全区标识
        if is_safe_zone:
            safe_font = get_font(14)
            safe_text = safe_font.render("[安全区]", True, (100, 255, 100))
            
            # 计算总宽度
            total_width = name_text.get_width() + safe_text.get_width() + 10
            x = (surface.get_width() - total_width) // 2
            y = 60
            
            # 绘制背景
            bg_padding = 8
            bg_rect = (x - bg_padding, y - bg_padding,
                      total_width + bg_padding * 2,
                      max(name_text.get_height(), safe_text.get_height()) + bg_padding * 2)
            pygame.draw.rect(surface, (20, 20, 20, 180), bg_rect)
            pygame.draw.rect(surface, (100, 100, 100), bg_rect, 1)
            
            surface.blit(name_text, (x, y))
            surface.blit(safe_text, (x + name_text.get_width() + 10, y + 5))
        else:
            x = (surface.get_width() - name_text.get_width()) // 2
            y = 60
            
            # 绘制背景
            bg_padding = 8
            bg_rect = (x - bg_padding, y - bg_padding,
                      name_text.get_width() + bg_padding * 2,
                      name_text.get_height() + bg_padding * 2)
            pygame.draw.rect(surface, (20, 20, 20, 180), bg_rect)
            pygame.draw.rect(surface, (100, 100, 100), bg_rect, 1)
            
            surface.blit(name_text, (x, y))
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
        
        bar_width = 300
        bar_height = 20
        margin = 20
        
        health_bar = self.elements.get("health_bar")
        if health_bar:
            health_bar.y = height - bar_height - margin - 30
        
        mana_bar = self.elements.get("mana_bar")
        if mana_bar:
            mana_bar.y = height - bar_height - margin
        
        exp_bar = self.elements.get("experience_bar")
        if exp_bar:
            exp_bar.y = height - 10
        
        skill_bar_width = 60 * 6 + 10
        skill_bar_x = (width - skill_bar_width) // 2
        skill_bar_y = height - 70
        
        for i in range(6):
            skill_slot = self.elements.get(f"skill_slot_{i}")
            if skill_slot:
                skill_slot.x = skill_bar_x + i * 60 + 5
                skill_slot.y = skill_bar_y
        
        minimap = self.elements.get("minimap_border")
        if minimap:
            minimap.x = width - self.minimap_size - 10
        
        gold_label = self.elements.get("gold_label")
        if gold_label:
            gold_label.x = width - 160
            gold_label.y = height - 30
