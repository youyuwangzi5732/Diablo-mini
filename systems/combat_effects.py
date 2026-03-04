"""
战斗特效系统 - 商业化级别的打击感效果
"""
import pygame
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import math
import random


class EffectType(Enum):
    HIT = "hit"
    CRITICAL = "critical"
    BLOCK = "block"
    DODGE = "dodge"
    DEATH = "death"
    SKILL = "skill"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    color: Tuple[int, int, int]
    size: float
    life: float
    max_life: float
    gravity: float = 0.0
    friction: float = 0.98
    alpha: int = 255
    
    def update(self, delta_time: float) -> bool:
        self.life -= delta_time
        if self.life <= 0:
            return False
        
        self.vy += self.gravity * delta_time
        self.vx *= self.friction
        self.vy *= self.friction
        
        self.x += self.vx * delta_time * 60
        self.y += self.vy * delta_time * 60
        
        # 淡出效果
        life_ratio = self.life / self.max_life
        self.alpha = int(255 * life_ratio)
        self.size *= 0.99
        
        return True
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        screen_x = int(self.x - camera_offset[0])
        screen_y = int(self.y - camera_offset[1])
        
        if self.size < 1:
            return
        
        particle_surface = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        color_with_alpha = (*self.color, self.alpha)
        pygame.draw.circle(particle_surface, color_with_alpha, 
                          (int(self.size), int(self.size)), int(self.size))
        surface.blit(particle_surface, (screen_x - int(self.size), screen_y - int(self.size)))


@dataclass
class HitEffect:
    """打击特效"""
    x: float
    y: float
    effect_type: EffectType
    particles: List[Particle] = field(default_factory=list)
    duration: float = 0.5
    elapsed: float = 0.0
    flash_intensity: float = 0.0
    shake_intensity: float = 0.0
    
    def update(self, delta_time: float) -> bool:
        self.elapsed += delta_time
        
        # 更新粒子
        self.particles = [p for p in self.particles if p.update(delta_time)]
        
        return self.elapsed < self.duration or len(self.particles) > 0
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        for particle in self.particles:
            particle.render(surface, camera_offset)


class CombatEffectsManager:
    """战斗特效管理器"""
    
    EFFECT_CONFIGS = {
        EffectType.HIT: {
            "particle_count": 8,
            "particle_colors": [(255, 200, 100), (255, 150, 50), (255, 100, 50)],
            "particle_speed": 5.0,
            "particle_size": 4.0,
            "particle_life": 0.3,
            "shake_intensity": 3.0,
            "shake_duration": 0.1,
            "flash_intensity": 0.2,
        },
        EffectType.CRITICAL: {
            "particle_count": 20,
            "particle_colors": [(255, 255, 100), (255, 200, 50), (255, 150, 0)],
            "particle_speed": 8.0,
            "particle_size": 6.0,
            "particle_life": 0.5,
            "shake_intensity": 8.0,
            "shake_duration": 0.2,
            "flash_intensity": 0.4,
        },
        EffectType.BLOCK: {
            "particle_count": 5,
            "particle_colors": [(150, 150, 200), (100, 100, 150)],
            "particle_speed": 3.0,
            "particle_size": 3.0,
            "particle_life": 0.2,
            "shake_intensity": 1.0,
            "shake_duration": 0.05,
            "flash_intensity": 0.1,
        },
        EffectType.DODGE: {
            "particle_count": 3,
            "particle_colors": [(100, 200, 100), (50, 150, 50)],
            "particle_speed": 2.0,
            "particle_size": 2.0,
            "particle_life": 0.2,
            "shake_intensity": 0.0,
            "shake_duration": 0.0,
            "flash_intensity": 0.0,
        },
        EffectType.DEATH: {
            "particle_count": 30,
            "particle_colors": [(255, 50, 50), (200, 0, 0), (150, 0, 0)],
            "particle_speed": 6.0,
            "particle_size": 5.0,
            "particle_life": 1.0,
            "shake_intensity": 10.0,
            "shake_duration": 0.3,
            "flash_intensity": 0.5,
        },
        EffectType.SKILL: {
            "particle_count": 15,
            "particle_colors": [(100, 150, 255), (150, 100, 255), (200, 150, 255)],
            "particle_speed": 6.0,
            "particle_size": 5.0,
            "particle_life": 0.4,
            "shake_intensity": 5.0,
            "shake_duration": 0.15,
            "flash_intensity": 0.3,
        },
        EffectType.HEAL: {
            "particle_count": 10,
            "particle_colors": [(100, 255, 100), (50, 200, 50), (150, 255, 150)],
            "particle_speed": 3.0,
            "particle_size": 4.0,
            "particle_life": 0.6,
            "shake_intensity": 0.0,
            "shake_duration": 0.0,
            "flash_intensity": 0.0,
        },
    }
    
    def __init__(self):
        self.effects: List[HitEffect] = []
        self.screen_shake = (0.0, 0.0)
        self.shake_duration = 0.0
        self.flash_alpha = 0.0
        self.flash_color = (255, 255, 255)
        
        # 伤害数字
        self.damage_numbers: List[Dict] = []
    
    def create_hit_effect(self, x: float, y: float, effect_type: EffectType,
                          direction: Tuple[float, float] = (0, -1)):
        """创建打击特效"""
        config = self.EFFECT_CONFIGS.get(effect_type, self.EFFECT_CONFIGS[EffectType.HIT])
        
        effect = HitEffect(
            x=x,
            y=y,
            effect_type=effect_type,
            duration=config["particle_life"] + 0.2,
            shake_intensity=config["shake_intensity"],
            flash_intensity=config["flash_intensity"]
        )
        
        # 创建粒子
        for _ in range(config["particle_count"]):
            angle = random.uniform(0, math.pi * 2)
            speed = config["particle_speed"] * random.uniform(0.5, 1.5)
            
            # 添加方向偏移
            angle += math.atan2(direction[1], direction[0]) + random.uniform(-0.5, 0.5)
            
            particle = Particle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-10, 10),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=random.choice(config["particle_colors"]),
                size=config["particle_size"] * random.uniform(0.5, 1.5),
                life=config["particle_life"] * random.uniform(0.5, 1.0),
                max_life=config["particle_life"],
                gravity=2.0 if effect_type in [EffectType.HIT, EffectType.CRITICAL, EffectType.DEATH] else 0.0
            )
            effect.particles.append(particle)
        
        self.effects.append(effect)
        
        # 触发屏幕震动
        if config["shake_intensity"] > 0:
            self.trigger_screen_shake(config["shake_intensity"], config["shake_duration"])
        
        # 触发闪光
        if config["flash_intensity"] > 0:
            self.trigger_flash(config["flash_intensity"])
    
    def create_damage_number(self, x: float, y: float, damage: int, 
                              is_crit: bool = False, is_heal: bool = False):
        """创建伤害数字"""
        self.damage_numbers.append({
            "x": x,
            "y": y,
            "damage": damage,
            "is_crit": is_crit,
            "is_heal": is_heal,
            "life": 1.5,
            "max_life": 1.5,
            "offset_y": 0,
            "vy": -50 if not is_heal else -30,
        })
    
    def trigger_screen_shake(self, intensity: float, duration: float):
        """触发屏幕震动"""
        self.shake_duration = max(self.shake_duration, duration)
        self.screen_shake = (
            random.uniform(-intensity, intensity),
            random.uniform(-intensity, intensity)
        )
    
    def trigger_flash(self, intensity: float, color: Tuple[int, int, int] = (255, 255, 255)):
        """触发屏幕闪光"""
        self.flash_alpha = int(255 * intensity)
        self.flash_color = color
    
    def update(self, delta_time: float):
        # 更新特效
        self.effects = [e for e in self.effects if e.update(delta_time)]
        
        # 更新屏幕震动
        if self.shake_duration > 0:
            self.shake_duration -= delta_time
            if self.shake_duration <= 0:
                self.screen_shake = (0, 0)
        
        # 更新闪光
        if self.flash_alpha > 0:
            self.flash_alpha = max(0, self.flash_alpha - int(500 * delta_time))
        
        # 更新伤害数字
        for dn in self.damage_numbers[:]:
            dn["life"] -= delta_time
            dn["offset_y"] += dn["vy"] * delta_time
            dn["vy"] *= 0.95  # 减速
            
            if dn["life"] <= 0:
                self.damage_numbers.remove(dn)
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float] = (0, 0)):
        # 渲染特效
        for effect in self.effects:
            effect.render(surface, camera_offset)
        
        # 渲染伤害数字
        for dn in self.damage_numbers:
            screen_x = int(dn["x"] - camera_offset[0])
            screen_y = int(dn["y"] - camera_offset[1] + dn["offset_y"])
            
            # 选择颜色和字体
            if dn["is_heal"]:
                color = (100, 255, 100)
                font_size = 16
            elif dn["is_crit"]:
                color = (255, 200, 50)
                font_size = 24
            else:
                color = (255, 255, 255)
                font_size = 18
            
            from ui.font_manager import get_font
            font = get_font(font_size)
            
            # 格式化数字
            if dn["is_heal"]:
                text = f"+{dn['damage']}"
            else:
                text = str(dn["damage"])
            
            # 淡出效果
            alpha = int(255 * (dn["life"] / dn["max_life"]))
            
            # 创建带透明度的文字
            text_surface = font.render(text, True, color)
            text_surface.set_alpha(alpha)
            
            # 绘制阴影
            shadow_surface = font.render(text, True, (0, 0, 0))
            shadow_surface.set_alpha(alpha // 2)
            surface.blit(shadow_surface, (screen_x - text_surface.get_width() // 2 + 1, 
                                          screen_y + 1))
            
            surface.blit(text_surface, (screen_x - text_surface.get_width() // 2, screen_y))
        
        # 渲染屏幕闪光
        if self.flash_alpha > 0:
            flash_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            flash_surface.fill((*self.flash_color, self.flash_alpha))
            surface.blit(flash_surface, (0, 0))
    
    def get_shake_offset(self) -> Tuple[int, int]:
        """获取当前震动偏移"""
        return (int(self.screen_shake[0]), int(self.screen_shake[1]))


class SkillEffectFactory:
    """技能特效工厂"""
    
    @staticmethod
    def create_melee_slash(x: float, y: float, direction: float) -> List[Particle]:
        """创建近战斩击特效"""
        particles = []
        
        for i in range(12):
            angle = direction + random.uniform(-0.5, 0.5)
            speed = random.uniform(3, 8)
            
            particle = Particle(
                x=x + random.uniform(-20, 20),
                y=y + random.uniform(-20, 20),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=random.choice([(255, 255, 255), (200, 200, 255), (150, 150, 200)]),
                size=random.uniform(2, 5),
                life=random.uniform(0.2, 0.4),
                max_life=0.4,
                gravity=0.5
            )
            particles.append(particle)
        
        return particles
    
    @staticmethod
    def create_fire_explosion(x: float, y: float, radius: float = 50) -> List[Particle]:
        """创建火焰爆炸特效"""
        particles = []
        
        for i in range(25):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 6)
            
            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed - 2,
                color=random.choice([(255, 100, 0), (255, 200, 0), (255, 150, 50)]),
                size=random.uniform(3, 8),
                life=random.uniform(0.3, 0.6),
                max_life=0.6,
                gravity=-0.5
            )
            particles.append(particle)
        
        return particles
    
    @staticmethod
    def create_ice_shatter(x: float, y: float) -> List[Particle]:
        """创建冰霜破碎特效"""
        particles = []
        
        for i in range(15):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(2, 5)
            
            particle = Particle(
                x=x + random.uniform(-10, 10),
                y=y + random.uniform(-10, 10),
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=random.choice([(150, 200, 255), (200, 230, 255), (100, 150, 255)]),
                size=random.uniform(2, 6),
                life=random.uniform(0.3, 0.5),
                max_life=0.5,
                gravity=1.0
            )
            particles.append(particle)
        
        return particles
    
    @staticmethod
    def create_lightning_strike(x: float, y: float) -> List[Particle]:
        """创建闪电打击特效"""
        particles = []
        
        for i in range(20):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(4, 10)
            
            particle = Particle(
                x=x,
                y=y,
                vx=math.cos(angle) * speed,
                vy=math.sin(angle) * speed,
                color=random.choice([(200, 200, 255), (150, 150, 255), (255, 255, 255)]),
                size=random.uniform(1, 4),
                life=random.uniform(0.1, 0.3),
                max_life=0.3,
                gravity=0.0
            )
            particles.append(particle)
        
        return particles
