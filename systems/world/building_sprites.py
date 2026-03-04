"""
建筑贴图系统 - 支持美术资源替换的建筑渲染
"""
import pygame
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import math


class BuildingStyle(Enum):
    MEDIEVAL = "medieval"
    GOTHIC = "gothic"
    RUSTIC = "rustic"
    MAGICAL = "magical"


@dataclass
class BuildingSprite:
    building_id: str
    base_surface: Optional[pygame.Surface] = None
    roof_surface: Optional[pygame.Surface] = None
    door_surface: Optional[pygame.Surface] = None
    window_surface: Optional[pygame.Surface] = None
    decoration_surfaces: List[pygame.Surface] = None
    
    def __post_init__(self):
        if self.decoration_surfaces is None:
            self.decoration_surfaces = []


class BuildingSpriteRenderer:
    """建筑精灵渲染器 - 支持美术资源替换"""
    
    BUILDING_TEMPLATES = {
        "tavern": {
            "style": BuildingStyle.RUSTIC,
            "features": ["sign", "chimney", "windows"],
            "colors": {
                "wall": (139, 90, 43),
                "roof": (120, 60, 30),
                "trim": (100, 70, 40),
                "door": (80, 50, 30)
            }
        },
        "blacksmith": {
            "style": BuildingStyle.MEDIEVAL,
            "features": ["anvil", "forge", "chimney"],
            "colors": {
                "wall": (80, 80, 85),
                "roof": (60, 60, 65),
                "trim": (100, 100, 105),
                "door": (50, 50, 55)
            }
        },
        "merchant": {
            "style": BuildingStyle.MEDIEVAL,
            "features": ["awning", "display", "sign"],
            "colors": {
                "wall": (100, 120, 100),
                "roof": (80, 100, 80),
                "trim": (120, 140, 120),
                "door": (70, 90, 70)
            }
        },
        "healer": {
            "style": BuildingStyle.GOTHIC,
            "features": ["stained_glass", "herb_rack", "cross"],
            "colors": {
                "wall": (200, 200, 220),
                "roof": (150, 150, 170),
                "trim": (180, 180, 200),
                "door": (120, 120, 140)
            }
        },
        "stash": {
            "style": BuildingStyle.MEDIEVAL,
            "features": ["lock", "bars", "reinforced_door"],
            "colors": {
                "wall": (150, 130, 100),
                "roof": (130, 110, 80),
                "trim": (170, 150, 120),
                "door": (100, 80, 60)
            }
        },
        "waypoint": {
            "style": BuildingStyle.MAGICAL,
            "features": ["rune_circle", "floating_crystals", "glow"],
            "colors": {
                "base": (100, 100, 150),
                "rune": (150, 150, 255),
                "crystal": (200, 200, 255),
                "glow": (100, 100, 255)
            }
        },
        "trainer": {
            "style": BuildingStyle.MEDIEVAL,
            "features": ["weapon_rack", "target", "training_dummy"],
            "colors": {
                "wall": (180, 150, 100),
                "roof": (150, 120, 70),
                "trim": (200, 170, 120),
                "door": (120, 90, 60)
            }
        },
        "jeweler": {
            "style": BuildingStyle.MAGICAL,
            "features": ["gem_display", "magnifier", "crystals"],
            "colors": {
                "wall": (150, 120, 180),
                "roof": (130, 100, 160),
                "trim": (170, 140, 200),
                "door": (110, 80, 140)
            }
        },
        "quest_hall": {
            "style": BuildingStyle.GOTHIC,
            "features": ["banner", "notice_board", "statue"],
            "colors": {
                "wall": (180, 170, 140),
                "roof": (150, 140, 110),
                "trim": (200, 190, 160),
                "door": (130, 120, 90)
            }
        }
    }
    
    def __init__(self):
        self._sprite_cache: Dict[str, BuildingSprite] = {}
        self._animation_time = 0.0
        self._generate_all_sprites()
    
    def _generate_all_sprites(self):
        """生成所有建筑精灵"""
        for building_id in self.BUILDING_TEMPLATES:
            self._sprite_cache[building_id] = self._generate_building_sprite(building_id)
    
    def _generate_building_sprite(self, building_id: str) -> BuildingSprite:
        """生成单个建筑精灵"""
        template = self.BUILDING_TEMPLATES.get(building_id)
        if not template:
            return BuildingSprite(building_id)
        
        colors = template["colors"]
        style = template["style"]
        
        sprite = BuildingSprite(building_id)
        
        # 根据建筑类型生成不同大小的表面
        size_map = {
            "tavern": (320, 192),
            "blacksmith": (256, 192),
            "merchant": (192, 128),
            "healer": (192, 128),
            "stash": (192, 128),
            "waypoint": (128, 128),
            "trainer": (256, 256),
            "jeweler": (192, 128),
            "quest_hall": (256, 192)
        }
        
        width, height = size_map.get(building_id, (192, 128))
        
        # 生成建筑主体
        sprite.base_surface = self._draw_building_base(width, height, colors, style, building_id)
        
        return sprite
    
    def _draw_building_base(self, width: int, height: int, 
                            colors: Dict[str, Tuple[int, int, int]],
                            style: BuildingStyle, building_id: str) -> pygame.Surface:
        """绘制建筑主体"""
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        wall_color = colors.get("wall", colors.get("base", (100, 80, 60)))
        roof_color = colors.get("roof", (80, 60, 40))
        trim_color = colors.get("trim", (120, 100, 80))
        door_color = colors.get("door", (60, 40, 20))
        
        # 墙体
        wall_height = int(height * 0.7)
        pygame.draw.rect(surface, wall_color, (0, height - wall_height, width, wall_height))
        
        # 墙体纹理
        self._add_wall_texture(surface, 0, height - wall_height, width, wall_height, wall_color)
        
        # 屋顶
        roof_height = int(height * 0.35)
        if building_id == "waypoint":
            # 传送点特殊处理 - 圆形基座
            pygame.draw.ellipse(surface, wall_color, 
                              (width//4, height - wall_height, width//2, wall_height))
        else:
            # 普通屋顶
            roof_points = [
                (0, height - wall_height),
                (width // 2, height - wall_height - roof_height),
                (width, height - wall_height)
            ]
            pygame.draw.polygon(surface, roof_color, roof_points)
            
            # 屋顶纹理
            self._add_roof_texture(surface, roof_points, roof_color)
        
        # 门
        door_width = width // 4
        door_height = int(wall_height * 0.6)
        door_x = (width - door_width) // 2
        door_y = height - door_height
        
        if building_id != "waypoint":
            pygame.draw.rect(surface, door_color, (door_x, door_y, door_width, door_height))
            pygame.draw.rect(surface, tuple(max(0, c - 20) for c in door_color), 
                           (door_x, door_y, door_width, door_height), 2)
            # 门把手
            pygame.draw.circle(surface, (200, 180, 100), 
                             (door_x + door_width - 8, door_y + door_height // 2), 3)
        
        # 窗户
        if building_id not in ["waypoint", "stash"]:
            window_size = min(width // 6, height // 8)
            window_y = height - wall_height + wall_height // 4
            
            # 左窗
            self._draw_window(surface, width // 6, window_y, window_size, building_id)
            # 右窗
            self._draw_window(surface, width - width // 6 - window_size, window_y, 
                            window_size, building_id)
        
        # 建筑特色装饰
        self._add_building_features(surface, building_id, width, height, colors)
        
        # 边框
        pygame.draw.rect(surface, trim_color, 
                        (0, height - wall_height, width, wall_height), 2)
        
        return surface
    
    def _add_wall_texture(self, surface: pygame.Surface, x: int, y: int,
                          width: int, height: int, base_color: Tuple[int, int, int]):
        """添加墙体纹理"""
        import random
        random.seed(x + y)
        
        # 砖石纹理
        brick_height = height // 4
        for row in range(4):
            offset = (row % 2) * (width // 8)
            for col in range(-1, width // 16 + 2):
                bx = x + col * 16 + offset
                by = y + row * brick_height
                
                color_var = random.randint(-10, 10)
                brick_color = tuple(max(0, min(255, c + color_var)) for c in base_color)
                
                pygame.draw.rect(surface, brick_color, (bx, by, 15, brick_height - 1))
    
    def _add_roof_texture(self, surface: pygame.Surface, 
                          roof_points: List[Tuple[int, int]],
                          base_color: Tuple[int, int, int]):
        """添加屋顶纹理"""
        # 简单的瓦片线条
        for i in range(5):
            y_offset = i * 8
            alpha = 150 - i * 20
            line_color = tuple(max(0, c - 20) for c in base_color)
            
            # 计算线条位置
            progress = i / 5
            left_x = roof_points[0][0] + (roof_points[1][0] - roof_points[0][0]) * progress
            right_x = roof_points[2][0] + (roof_points[1][0] - roof_points[2][0]) * progress
            y = roof_points[0][1] + y_offset
            
            pygame.draw.line(surface, line_color, (left_x, y), (right_x, y), 1)
    
    def _draw_window(self, surface: pygame.Surface, x: int, y: int, 
                     size: int, building_id: str):
        """绘制窗户"""
        # 窗框
        frame_color = (80, 60, 40)
        pygame.draw.rect(surface, frame_color, (x, y, size, size))
        
        # 窗玻璃
        if building_id == "healer":
            # 彩色玻璃
            glass_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
            for i, color in enumerate(glass_colors):
                pygame.draw.rect(surface, color, 
                               (x + i * size // 3 + 1, y + 1, size // 3 - 2, size - 2))
        else:
            # 普通玻璃
            glass_color = (200, 220, 240)
            pygame.draw.rect(surface, glass_color, (x + 2, y + 2, size - 4, size - 4))
            
            # 窗格
            pygame.draw.line(surface, frame_color, (x + size // 2, y), (x + size // 2, y + size), 1)
            pygame.draw.line(surface, frame_color, (x, y + size // 2), (x + size, y + size // 2), 1)
    
    def _add_building_features(self, surface: pygame.Surface, building_id: str,
                                width: int, height: int, 
                                colors: Dict[str, Tuple[int, int, int]]):
        """添加建筑特色装饰"""
        if building_id == "blacksmith":
            # 烟囱
            chimney_x = width - 40
            chimney_y = 10
            pygame.draw.rect(surface, (60, 60, 60), (chimney_x, chimney_y, 20, 40))
            # 烟雾效果
            for i in range(3):
                smoke_y = chimney_y - 10 - i * 8
                alpha = 100 - i * 30
                smoke_surface = pygame.Surface((15, 15), pygame.SRCALPHA)
                pygame.draw.circle(smoke_surface, (150, 150, 150, alpha), (7, 7), 7)
                surface.blit(smoke_surface, (chimney_x + 2, smoke_y))
        
        elif building_id == "merchant":
            # 招牌
            sign_width = width // 2
            sign_x = (width - sign_width) // 2
            sign_y = height // 3
            pygame.draw.rect(surface, (150, 120, 80), (sign_x, sign_y, sign_width, 20))
            pygame.draw.rect(surface, (100, 70, 40), (sign_x, sign_y, sign_width, 20), 2)
        
        elif building_id == "waypoint":
            # 传送点符文圆环
            center_x = width // 2
            center_y = height // 2
            
            # 外圈
            pygame.draw.circle(surface, colors.get("rune", (150, 150, 255)), 
                             (center_x, center_y), 40, 3)
            # 内圈
            pygame.draw.circle(surface, colors.get("rune", (150, 150, 255)), 
                             (center_x, center_y), 25, 2)
            
            # 符文标记
            for i in range(8):
                angle = i * math.pi / 4
                rx = center_x + int(32 * math.cos(angle))
                ry = center_y + int(32 * math.sin(angle))
                pygame.draw.circle(surface, (200, 200, 255), (rx, ry), 3)
        
        elif building_id == "jeweler":
            # 宝石展示
            gem_positions = [(20, height // 2), (width - 30, height // 2)]
            gem_colors = [(255, 50, 50), (50, 255, 50), (50, 50, 255)]
            for i, (gx, gy) in enumerate(gem_positions):
                color = gem_colors[i % len(gem_colors)]
                # 宝石形状
                points = [
                    (gx, gy - 8),
                    (gx + 6, gy),
                    (gx, gy + 8),
                    (gx - 6, gy)
                ]
                pygame.draw.polygon(surface, color, points)
                pygame.draw.polygon(surface, (255, 255, 255), points, 1)
        
        elif building_id == "quest_hall":
            # 旗帜
            banner_x = 10
            banner_y = height // 4
            pygame.draw.rect(surface, (150, 50, 50), (banner_x, banner_y, 15, 40))
            pygame.draw.polygon(surface, (180, 60, 60), [
                (banner_x + 15, banner_y + 5),
                (banner_x + 40, banner_y + 15),
                (banner_x + 15, banner_y + 25)
            ])
    
    def render_building(self, surface: pygame.Surface, building_id: str,
                        x: int, y: int, scale: float = 1.0):
        """渲染建筑"""
        sprite = self._sprite_cache.get(building_id)
        if not sprite or not sprite.base_surface:
            return
        
        # 应用缩放
        if scale != 1.0:
            scaled_width = int(sprite.base_surface.get_width() * scale)
            scaled_height = int(sprite.base_surface.get_height() * scale)
            scaled_surface = pygame.transform.scale(sprite.base_surface, 
                                                    (scaled_width, scaled_height))
        else:
            scaled_surface = sprite.base_surface
        
        surface.blit(scaled_surface, (x, y - scaled_surface.get_height()))
    
    def render_building_animated(self, surface: pygame.Surface, building_id: str,
                                  x: int, y: int, scale: float = 1.0):
        """渲染带动画的建筑"""
        # 基础渲染
        self.render_building(surface, building_id, x, y, scale)
        
        # 添加动态效果
        if building_id == "waypoint":
            self._render_waypoint_animation(surface, x, y, scale)
        elif building_id == "blacksmith":
            self._render_blacksmith_animation(surface, x, y, scale)
    
    def _render_waypoint_animation(self, surface: pygame.Surface, 
                                    x: int, y: int, scale: float):
        """传送点动画"""
        center_x = x + int(64 * scale)
        center_y = y - int(64 * scale)
        
        # 旋转光环
        for i in range(4):
            angle = self._animation_time * 2 + i * math.pi / 2
            px = center_x + int(30 * scale * math.cos(angle))
            py = center_y + int(30 * scale * math.sin(angle))
            
            glow_surface = pygame.Surface((10, 10), pygame.SRCALPHA)
            alpha = int(150 + 100 * math.sin(self._animation_time * 3 + i))
            pygame.draw.circle(glow_surface, (150, 150, 255, alpha), (5, 5), 5)
            surface.blit(glow_surface, (px - 5, py - 5))
    
    def _render_blacksmith_animation(self, surface: pygame.Surface,
                                      x: int, y: int, scale: float):
        """铁匠铺火花动画"""
        import random
        
        if random.random() < 0.1:  # 10%概率产生火花
            spark_x = x + int(random.randint(150, 200) * scale)
            spark_y = y - int(random.randint(50, 100) * scale)
            
            for _ in range(3):
                spark_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(spark_surface, (255, 200, 100, 200), (2, 2), 2)
                surface.blit(spark_surface, 
                           (spark_x + random.randint(-10, 10), 
                            spark_y + random.randint(-10, 10)))
    
    def update(self, delta_time: float):
        """更新动画"""
        self._animation_time += delta_time
    
    def get_building_size(self, building_id: str) -> Tuple[int, int]:
        """获取建筑尺寸"""
        sprite = self._sprite_cache.get(building_id)
        if sprite and sprite.base_surface:
            return (sprite.base_surface.get_width(), sprite.base_surface.get_height())
        return (192, 128)
