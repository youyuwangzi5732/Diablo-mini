"""
主城渲染系统 - 渲染主城建筑、NPC、传送点等
"""
import pygame
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class BuildingType(Enum):
    TAVERN = "tavern"
    BLACKSMITH = "blacksmith"
    MERCHANT = "merchant"
    HEALER = "healer"
    STASH = "stash"
    WAYPOINT = "waypoint"
    TRAINER = "trainer"
    JEWELER = "jeweler"
    QUEST_HALL = "quest_hall"


@dataclass
class Building:
    id: str
    name: str
    building_type: BuildingType
    position: Tuple[int, int]
    size: Tuple[int, int] = (4, 3)  # 建筑占地大小（格子）
    color: Tuple[int, int, int] = (100, 80, 60)
    icon: str = ""


class TownRenderer:
    """主城渲染器"""
    
    BUILDING_COLORS = {
        BuildingType.TAVERN: (139, 90, 43),      # 棕色 - 酒馆
        BuildingType.BLACKSMITH: (80, 80, 80),   # 灰色 - 铁匠铺
        BuildingType.MERCHANT: (100, 150, 100),  # 绿色 - 商店
        BuildingType.HEALER: (200, 200, 255),    # 淡蓝 - 治疗所
        BuildingType.STASH: (150, 120, 80),      # 土黄 - 仓库
        BuildingType.WAYPOINT: (100, 100, 255),  # 蓝色 - 传送点
        BuildingType.TRAINER: (200, 150, 50),    # 金色 - 训练场
        BuildingType.JEWELER: (150, 100, 200),   # 紫色 - 珠宝店
        BuildingType.QUEST_HALL: (200, 180, 100), # 金黄 - 任务大厅
    }
    
    BUILDING_NAMES = {
        BuildingType.TAVERN: "冒险者酒馆",
        BuildingType.BLACKSMITH: "铁匠铺",
        BuildingType.MERCHANT: "杂货店",
        BuildingType.HEALER: "治疗所",
        BuildingType.STASH: "私人仓库",
        BuildingType.WAYPOINT: "传送点",
        BuildingType.TRAINER: "训练场",
        BuildingType.JEWELER: "珠宝店",
        BuildingType.QUEST_HALL: "镇政厅",
    }
    
    def __init__(self):
        self.buildings: Dict[str, Building] = {}
        self._create_town_buildings()
        
        # 字体缓存
        self._font_small = None
        self._font_medium = None
    
    def _get_font(self, size: int):
        """获取字体"""
        from ui.font_manager import get_font
        return get_font(size)
    
    def _create_town_buildings(self):
        """创建主城建筑布局"""
        # 主城建筑布局 - 围绕中心广场
        building_configs = [
            ("merchant_shop", BuildingType.MERCHANT, (15, 15), (3, 2)),
            ("blacksmith_shop", BuildingType.BLACKSMITH, (35, 18), (4, 3)),
            ("jeweler_shop", BuildingType.JEWELER, (22, 32), (3, 2)),
            ("quest_hall", BuildingType.QUEST_HALL, (12, 28), (4, 3)),
            ("healer_house", BuildingType.HEALER, (8, 18), (3, 2)),
            ("stash_house", BuildingType.STASH, (38, 32), (3, 2)),
            ("waypoint_shrine", BuildingType.WAYPOINT, (25, 8), (2, 2)),
            ("trainer_ground", BuildingType.TRAINER, (42, 25), (4, 4)),
            ("tavern_main", BuildingType.TAVERN, (18, 38), (5, 3)),
        ]
        
        for building_id, btype, pos, size in building_configs:
            building = Building(
                id=building_id,
                name=self.BUILDING_NAMES.get(btype, "建筑"),
                building_type=btype,
                position=pos,
                size=size,
                color=self.BUILDING_COLORS.get(btype, (100, 80, 60))
            )
            self.buildings[building_id] = building
    
    def render(self, surface: pygame.Surface, camera_offset: Tuple[float, float], 
               area_type: str = "town"):
        """渲染主城"""
        if area_type != "town":
            return
            
        cam_x, cam_y = camera_offset
        tile_size = 64
        
        # 渲染建筑
        for building in self.buildings.values():
            self._render_building(surface, building, cam_x, cam_y, tile_size)
        
        # 渲染中心广场标记
        self._render_town_center(surface, cam_x, cam_y, tile_size)
    
    def _render_building(self, surface: pygame.Surface, building: Building,
                         cam_x: float, cam_y: float, tile_size: int):
        """渲染单个建筑"""
        # 计算屏幕位置
        screen_x = int(building.position[0] * tile_size - cam_x)
        screen_y = int(building.position[1] * tile_size - cam_y)
        
        width = building.size[0] * tile_size
        height = building.size[1] * tile_size
        
        # 检查是否在屏幕范围内
        if screen_x + width < 0 or screen_x > surface.get_width():
            return
        if screen_y + height < 0 or screen_y > surface.get_height():
            return
        
        # 绘制建筑主体
        pygame.draw.rect(surface, building.color, 
                        (screen_x, screen_y, width, height))
        
        # 绘制建筑边框
        border_color = tuple(min(255, c + 30) for c in building.color)
        pygame.draw.rect(surface, border_color, 
                        (screen_x, screen_y, width, height), 2)
        
        # 绘制屋顶（三角形）
        roof_height = tile_size // 2
        roof_points = [
            (screen_x, screen_y),
            (screen_x + width // 2, screen_y - roof_height),
            (screen_x + width, screen_y)
        ]
        roof_color = tuple(max(0, c - 20) for c in building.color)
        pygame.draw.polygon(surface, roof_color, roof_points)
        pygame.draw.polygon(surface, border_color, roof_points, 2)
        
        # 绘制门
        door_width = tile_size // 2
        door_height = tile_size
        door_x = screen_x + (width - door_width) // 2
        door_y = screen_y + height - door_height
        pygame.draw.rect(surface, (60, 40, 30), 
                        (door_x, door_y, door_width, door_height))
        
        # 绘制窗户
        window_size = tile_size // 3
        window_y = screen_y + tile_size // 2
        for i in range(1, building.size[0]):
            window_x = screen_x + i * tile_size - window_size // 2
            pygame.draw.rect(surface, (200, 200, 150), 
                           (window_x, window_y, window_size, window_size))
            pygame.draw.rect(surface, (100, 100, 80), 
                           (window_x, window_y, window_size, window_size), 1)
        
        # 绘制建筑名称
        if self._font_small is None:
            self._font_small = self._get_font(12)
        
        name_text = self._font_small.render(building.name, True, (255, 255, 255))
        name_x = screen_x + (width - name_text.get_width()) // 2
        name_y = screen_y - roof_height - 15
        
        # 文字背景
        bg_padding = 4
        bg_rect = (name_x - bg_padding, name_y - bg_padding,
                   name_text.get_width() + bg_padding * 2, 
                   name_text.get_height() + bg_padding * 2)
        pygame.draw.rect(surface, (30, 30, 30, 180), bg_rect)
        
        surface.blit(name_text, (name_x, name_y))
    
    def _render_town_center(self, surface: pygame.Surface, 
                           cam_x: float, cam_y: float, tile_size: int):
        """渲染中心广场"""
        center_x = 25 * tile_size - cam_x
        center_y = 25 * tile_size - cam_y
        radius = 3 * tile_size
        
        # 绘制广场地面（圆形区域）
        pygame.draw.circle(surface, (80, 75, 70), 
                          (int(center_x), int(center_y)), radius)
        pygame.draw.circle(surface, (100, 95, 90), 
                          (int(center_x), int(center_y)), radius, 3)
        
        # 绘制中心喷泉/纪念碑
        pygame.draw.circle(surface, (150, 140, 130), 
                          (int(center_x), int(center_y)), tile_size)
        pygame.draw.circle(surface, (200, 190, 180), 
                          (int(center_x), int(center_y)), tile_size, 2)
    
    def get_building_at(self, position: Tuple[float, float], 
                        range_limit: float = 2.0) -> Optional[Building]:
        """获取指定位置附近的建筑"""
        for building in self.buildings.values():
            # 计算建筑中心
            center_x = building.position[0] + building.size[0] / 2
            center_y = building.position[1] + building.size[1] / 2
            
            dx = position[0] - center_x
            dy = position[1] - center_y
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= range_limit:
                return building
        
        return None
    
    def render_minimap(self, surface: pygame.Surface, 
                      camera_offset: Tuple[float, float] = (0, 0)):
        """在小地图上渲染建筑标记"""
        scale = 0.2  # 小地图缩放比例
        offset_x = surface.get_width() - 150 + 10
        offset_y = 10
        
        for building in self.buildings.values():
            map_x = int(offset_x + building.position[0] * 64 * scale)
            map_y = int(offset_y + building.position[1] * 64 * scale)
            
            # 建筑在小地图上的标记
            size = max(3, int(min(building.size) * 64 * scale))
            pygame.draw.rect(surface, building.color, 
                           (map_x - size//2, map_y - size//2, size, size))
