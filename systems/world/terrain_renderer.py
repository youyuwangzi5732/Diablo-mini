"""
增强地形渲染系统 - 商业化级别的地图渲染
"""
import pygame
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import random
import math


class TerrainType(Enum):
    STONE = "stone"
    GRASS = "grass"
    DIRT = "dirt"
    SAND = "sand"
    SNOW = "snow"
    LAVA = "lava"
    WATER = "water"
    WOOD = "wood"


@dataclass
class TerrainTile:
    terrain_type: TerrainType
    base_color: Tuple[int, int, int]
    variation: int = 0
    decoration: str = ""


class TerrainRenderer:
    """增强地形渲染器"""
    
    TERRAIN_CONFIGS = {
        TerrainType.STONE: {
            "base_colors": [(70, 70, 75), (65, 65, 70), (75, 75, 80)],
            "patterns": ["cobble", "smooth", "cracked"],
            "decorations": ["moss", "crack", "none"]
        },
        TerrainType.GRASS: {
            "base_colors": [(40, 80, 35), (35, 75, 30), (45, 85, 40)],
            "patterns": ["wild", "trimmed", "patchy"],
            "decorations": ["flower", "rock", "bush", "none"]
        },
        TerrainType.DIRT: {
            "base_colors": [(90, 70, 50), (85, 65, 45), (95, 75, 55)],
            "patterns": ["rough", "packed", "muddy"],
            "decorations": ["pebble", "root", "none"]
        },
        TerrainType.SAND: {
            "base_colors": [(180, 160, 120), (175, 155, 115), (185, 165, 125)],
            "patterns": ["dunes", "flat", "rippled"],
            "decorations": ["shell", "bone", "none"]
        },
        TerrainType.SNOW: {
            "base_colors": [(230, 235, 240), (225, 230, 235), (235, 240, 245)],
            "patterns": ["fresh", "packed", "icy"],
            "decorations": ["footprint", "ice_crystal", "none"]
        },
        TerrainType.LAVA: {
            "base_colors": [(180, 60, 20), (200, 80, 30), (160, 50, 15)],
            "patterns": ["flowing", "crusted", "bubbling"],
            "decorations": ["ember", "smoke", "none"]
        },
        TerrainType.WATER: {
            "base_colors": [(30, 80, 140), (25, 75, 135), (35, 85, 145)],
            "patterns": ["calm", "rippled", "waves"],
            "decorations": ["foam", "reflection", "none"]
        },
        TerrainType.WOOD: {
            "base_colors": [(120, 80, 50), (115, 75, 45), (125, 85, 55)],
            "patterns": ["planks", "boards", "parquet"],
            "decorations": ["knot", "grain", "none"]
        },
    }
    
    AREA_TERRAIN_MAP = {
        "town": TerrainType.STONE,
        "forest": TerrainType.GRASS,
        "dungeon": TerrainType.STONE,
        "desert": TerrainType.SAND,
        "snow": TerrainType.SNOW,
        "hell": TerrainType.LAVA,
    }
    
    def __init__(self):
        self._tile_cache: Dict[str, pygame.Surface] = {}
        self._animation_time = 0.0
        self._random_seed = 42
    
    def _get_tile_key(self, terrain_type: TerrainType, x: int, y: int) -> str:
        """获取瓦片缓存键"""
        return f"{terrain_type.value}_{x}_{y}"
    
    def render_tile(self, surface: pygame.Surface, x: int, y: int, 
                    terrain_type: TerrainType, tile_size: int = 64,
                    camera_offset: Tuple[float, float] = (0, 0)):
        """渲染单个地形瓦片"""
        # 计算屏幕位置
        screen_x = x * tile_size - int(camera_offset[0])
        screen_y = y * tile_size - int(camera_offset[1])
        
        # 检查是否在屏幕范围内
        if (screen_x + tile_size < 0 or screen_x > surface.get_width() or
            screen_y + tile_size < 0 or screen_y > surface.get_height()):
            return
        
        # 获取地形配置
        config = self.TERRAIN_CONFIGS.get(terrain_type)
        if not config:
            pygame.draw.rect(surface, (50, 50, 50), (screen_x, screen_y, tile_size, tile_size))
            return
        
        # 使用确定性随机选择颜色变体
        random.seed(x * 1000 + y + self._random_seed)
        base_color = random.choice(config["base_colors"])
        
        # 绘制基础颜色
        pygame.draw.rect(surface, base_color, (screen_x, screen_y, tile_size, tile_size))
        
        # 添加纹理变化
        self._add_texture_variation(surface, screen_x, screen_y, tile_size, base_color, terrain_type)
        
        # 添加边缘过渡
        self._add_edge_detail(surface, screen_x, screen_y, tile_size, base_color)
        
        # 添加装饰物
        decoration = random.choice(config["decorations"])
        if decoration != "none":
            self._add_decoration(surface, screen_x, screen_y, tile_size, decoration, terrain_type)
    
    def _add_texture_variation(self, surface: pygame.Surface, x: int, y: int, 
                                size: int, base_color: Tuple[int, int, int],
                                terrain_type: TerrainType):
        """添加纹理变化"""
        random.seed(x * 100 + y)
        
        # 添加随机噪点
        for _ in range(15):
            px = x + random.randint(0, size - 1)
            py = y + random.randint(0, size - 1)
            
            # 颜色偏移
            offset = random.randint(-15, 15)
            color = tuple(max(0, min(255, c + offset)) for c in base_color)
            
            pygame.draw.circle(surface, color, (px, py), random.randint(1, 3))
        
        # 添加格子纹理（针对石板、木板等）
        if terrain_type in [TerrainType.STONE, TerrainType.WOOD]:
            # 绘制格子线
            line_color = tuple(max(0, c - 20) for c in base_color)
            pygame.draw.line(surface, line_color, (x, y), (x + size, y), 1)
            pygame.draw.line(surface, line_color, (x, y), (x, y + size), 1)
            
            # 添加格子内部阴影
            inner_color = tuple(max(0, c - 10) for c in base_color)
            pygame.draw.line(surface, inner_color, (x + 2, y + 2), (x + size - 2, y + 2), 1)
            pygame.draw.line(surface, inner_color, (x + 2, y + 2), (x + 2, y + size - 2), 1)
    
    def _add_edge_detail(self, surface: pygame.Surface, x: int, y: int,
                          size: int, base_color: Tuple[int, int, int]):
        """添加边缘细节"""
        # 边缘阴影
        shadow_color = tuple(max(0, c - 25) for c in base_color)
        pygame.draw.line(surface, shadow_color, (x, y + size - 1), (x + size, y + size - 1), 2)
        pygame.draw.line(surface, shadow_color, (x + size - 1, y), (x + size - 1, y + size), 2)
        
        # 边缘高光
        highlight_color = tuple(min(255, c + 15) for c in base_color)
        pygame.draw.line(surface, highlight_color, (x, y), (x + size, y), 1)
        pygame.draw.line(surface, highlight_color, (x, y), (x, y + size), 1)
    
    def _add_decoration(self, surface: pygame.Surface, x: int, y: int,
                        size: int, decoration: str, terrain_type: TerrainType):
        """添加装饰物"""
        center_x = x + size // 2
        center_y = y + size // 2
        
        if decoration == "moss":
            # 苔藓
            moss_color = (50, 100, 40)
            for i in range(3):
                mx = x + random.randint(5, size - 10)
                my = y + random.randint(5, size - 10)
                pygame.draw.circle(surface, moss_color, (mx, my), random.randint(2, 4))
        
        elif decoration == "flower":
            # 花朵
            flower_colors = [(255, 100, 100), (255, 200, 100), (200, 100, 255)]
            for i in range(2):
                fx = x + random.randint(10, size - 10)
                fy = y + random.randint(10, size - 10)
                color = random.choice(flower_colors)
                pygame.draw.circle(surface, color, (fx, fy), 3)
                pygame.draw.circle(surface, (255, 255, 100), (fx, fy), 1)
        
        elif decoration == "pebble":
            # 小石子
            pebble_color = (120, 110, 100)
            for i in range(3):
                px = x + random.randint(5, size - 5)
                py = y + random.randint(5, size - 5)
                pygame.draw.ellipse(surface, pebble_color, 
                                   (px - 2, py - 1, 4, 2))
        
        elif decoration == "shell":
            # 贝壳
            shell_color = (255, 240, 220)
            sx = x + random.randint(10, size - 10)
            sy = y + random.randint(10, size - 10)
            pygame.draw.arc(surface, shell_color, (sx - 4, sy - 4, 8, 8), 0, 3.14, 2)
        
        elif decoration == "ember":
            # 余烬（动态效果）
            glow = int(128 + 127 * math.sin(self._animation_time * 3))
            ember_color = (255, glow // 2, 0)
            ex = x + random.randint(10, size - 10)
            ey = y + random.randint(10, size - 10)
            pygame.draw.circle(surface, ember_color, (ex, ey), 2)
        
        elif decoration == "foam":
            # 水泡
            foam_color = (200, 220, 255)
            for i in range(2):
                fx = x + random.randint(5, size - 5)
                fy = y + random.randint(5, size - 5)
                pygame.draw.circle(surface, foam_color, (fx, fy), 2)
    
    def render_area(self, surface: pygame.Surface, area_type: str,
                    camera_offset: Tuple[float, float], area_width: int, area_height: int,
                    tile_size: int = 64):
        """渲染整个区域"""
        terrain_type = self.AREA_TERRAIN_MAP.get(area_type, TerrainType.DIRT)
        
        # 计算可见范围
        start_x = max(0, int(camera_offset[0] // tile_size) - 1)
        start_y = max(0, int(camera_offset[1] // tile_size) - 1)
        end_x = min(area_width, start_x + surface.get_width() // tile_size + 3)
        end_y = min(area_height, start_y + surface.get_height() // tile_size + 3)
        
        # 渲染瓦片
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                self.render_tile(surface, x, y, terrain_type, tile_size, camera_offset)
    
    def update(self, delta_time: float):
        """更新动画状态"""
        self._animation_time += delta_time
    
    def render_town_ground(self, surface: pygame.Surface, camera_offset: Tuple[float, float],
                           area_width: int, area_height: int, tile_size: int = 64):
        """渲染主城地面（特殊处理）"""
        # 主城使用石板地面
        start_x = max(0, int(camera_offset[0] // tile_size) - 1)
        start_y = max(0, int(camera_offset[1] // tile_size) - 1)
        end_x = min(area_width, start_x + surface.get_width() // tile_size + 3)
        end_y = min(area_height, start_y + surface.get_height() // tile_size + 3)
        
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                screen_x = x * tile_size - int(camera_offset[0])
                screen_y = y * tile_size - int(camera_offset[1])
                
                # 主城石板颜色（更温暖的色调）
                random.seed(x * 1000 + y + self._random_seed)
                base_colors = [(85, 75, 65), (80, 70, 60), (90, 80, 70)]
                base_color = random.choice(base_colors)
                
                pygame.draw.rect(surface, base_color, 
                               (screen_x, screen_y, tile_size, tile_size))
                
                # 添加石板纹理
                self._add_stone_floor_pattern(surface, screen_x, screen_y, tile_size, base_color)
    
    def _add_stone_floor_pattern(self, surface: pygame.Surface, x: int, y: int,
                                  size: int, base_color: Tuple[int, int, int]):
        """添加石板地面图案"""
        # 石板缝隙
        gap_color = (40, 35, 30)
        pygame.draw.rect(surface, gap_color, (x, y, size, size), 1)
        
        # 内部纹理
        random.seed(x * 100 + y)
        for _ in range(8):
            px = x + random.randint(5, size - 5)
            py = y + random.randint(5, size - 5)
            offset = random.randint(-8, 8)
            color = tuple(max(0, min(255, c + offset)) for c in base_color)
            pygame.draw.circle(surface, color, (px, py), random.randint(1, 2))
        
        # 边角阴影
        shadow = tuple(max(0, c - 15) for c in base_color)
        pygame.draw.line(surface, shadow, (x + 2, y + size - 3), (x + size - 2, y + size - 3), 1)
        pygame.draw.line(surface, shadow, (x + size - 3, y + 2), (x + size - 3, y + size - 2), 1)


class EnvironmentEffects:
    """环境特效系统"""
    
    def __init__(self):
        self.particles: List[Dict] = []
        self._animation_time = 0.0
    
    def add_ambient_particles(self, area_type: str, count: int = 50):
        """添加环境粒子"""
        particle_configs = {
            "forest": {"type": "leaf", "color": (100, 150, 50), "speed": 0.5},
            "snow": {"type": "snowflake", "color": (255, 255, 255), "speed": 0.3},
            "desert": {"type": "sand", "color": (200, 180, 140), "speed": 1.0},
            "hell": {"type": "ember", "color": (255, 100, 50), "speed": 0.8},
        }
        
        config = particle_configs.get(area_type)
        if not config:
            return
        
        for _ in range(count):
            self.particles.append({
                "x": random.randint(0, 1920),
                "y": random.randint(-100, 1080),
                "speed": config["speed"] * random.uniform(0.5, 1.5),
                "size": random.randint(2, 5),
                "color": config["color"],
                "alpha": random.randint(100, 200),
                "type": config["type"]
            })
    
    def update(self, delta_time: float):
        """更新粒子"""
        self._animation_time += delta_time
        
        for particle in self.particles:
            particle["y"] += particle["speed"] * 60 * delta_time
            particle["x"] += math.sin(self._animation_time + particle["y"] * 0.01) * 0.5
            
            # 重置超出屏幕的粒子
            if particle["y"] > 1100:
                particle["y"] = -10
                particle["x"] = random.randint(0, 1920)
    
    def render(self, surface: pygame.Surface):
        """渲染粒子"""
        for particle in self.particles:
            color = (*particle["color"], particle["alpha"])
            particle_surface = pygame.Surface((particle["size"] * 2, particle["size"] * 2), 
                                              pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (particle["size"], particle["size"]), particle["size"])
            surface.blit(particle_surface, (int(particle["x"]), int(particle["y"])))
