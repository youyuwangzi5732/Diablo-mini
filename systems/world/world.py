"""
世界系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class AreaType(Enum):
    TOWN = "town"
    WILDERNESS = "wilderness"
    DUNGEON = "dungeon"
    FOREST = "forest"
    DESERT = "desert"
    SNOW = "snow"
    SWAMP = "swamp"
    MOUNTAIN = "mountain"
    UNDERGROUND = "underground"
    HELL = "hell"


@dataclass
class AreaConnection:
    target_area_id: str
    position: Tuple[int, int]
    bidirectional: bool = True
    required_level: int = 1
    required_quest: Optional[str] = None


@dataclass
class Area:
    id: str
    name: str
    area_type: AreaType
    level_range: Tuple[int, int] = (1, 10)
    
    width: int = 100
    height: int = 100
    
    connections: List[AreaConnection] = field(default_factory=list)
    
    monster_spawns: List[Dict[str, Any]] = field(default_factory=list)
    npc_spawns: List[Dict[str, Any]] = field(default_factory=list)
    object_spawns: List[Dict[str, Any]] = field(default_factory=list)
    
    ambient_color: Tuple[int, int, int] = (255, 255, 255)
    music_track: str = ""
    
    is_safe_zone: bool = False
    is_dungeon: bool = False
    is_rift: bool = False
    
    description: str = ""
    
    def get_random_spawn_point(self) -> Tuple[float, float]:
        return (
            random.uniform(5, self.width - 5),
            random.uniform(5, self.height - 5)
        )
    
    def get_connection_at(self, position: Tuple[float, float], 
                           radius: float = 2.0) -> Optional[AreaConnection]:
        for conn in self.connections:
            dx = conn.position[0] - position[0]
            dy = conn.position[1] - position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= radius:
                return conn
        
        return None


class World:
    def __init__(self):
        self.areas: Dict[str, Area] = {}
        self.current_area_id: Optional[str] = None
        
        self._create_default_areas()
    
    def _create_default_areas(self):
        town = Area(
            id="tristram",
            name="新崔斯特姆",
            area_type=AreaType.TOWN,
            level_range=(1, 70),
            width=50,
            height=50,
            is_safe_zone=True,
            npc_spawns=[
                {"npc_id": "merchant", "position": (20, 15)},
                {"npc_id": "blacksmith", "position": (30, 20)},
                {"npc_id": "jeweler", "position": (25, 30)},
                {"npc_id": "quest_giver", "position": (15, 25)},
            ]
        )
        
        forest = Area(
            id="weald",
            name="腐化林地",
            area_type=AreaType.FOREST,
            level_range=(1, 15),
            width=200,
            height=200,
            monster_spawns=[
                {"monster_id": "zombie", "count": 20, "level": 3},
                {"monster_id": "skeleton", "count": 15, "level": 5},
                {"monster_id": "fallen", "count": 25, "level": 2},
            ],
            connections=[
                AreaConnection("tristram", (5, 100)),
                AreaConnection("cathedral", (195, 100)),
            ]
        )
        
        cathedral = Area(
            id="cathedral",
            name="大教堂",
            area_type=AreaType.DUNGEON,
            level_range=(5, 20),
            width=150,
            height=150,
            is_dungeon=True,
            monster_spawns=[
                {"monster_id": "skeleton", "count": 30, "level": 8},
                {"monster_id": "ghost", "count": 15, "level": 10},
                {"monster_id": "skeleton_archer", "count": 10, "level": 9},
            ],
            connections=[
                AreaConnection("weald", (5, 75)),
                AreaConnection("crypts", (145, 75)),
            ]
        )
        
        desert = Area(
            id="desert",
            name="卡尔蒂姆沙漠",
            area_type=AreaType.DESERT,
            level_range=(15, 30),
            width=250,
            height=250,
            monster_spawns=[
                {"monster_id": "demon", "count": 20, "level": 18},
                {"monster_id": "fallen", "count": 30, "level": 15},
            ],
            connections=[
                AreaConnection("tristram", (125, 5)),
            ]
        )
        
        snow = Area(
            id="snow",
            name="亚瑞特山脉",
            area_type=AreaType.SNOW,
            level_range=(30, 45),
            width=200,
            height=200,
            monster_spawns=[
                {"monster_id": "demon", "count": 25, "level": 35},
            ],
            connections=[
                AreaConnection("tristram", (100, 5)),
            ]
        )
        
        hell = Area(
            id="hell",
            name="地狱",
            area_type=AreaType.HELL,
            level_range=(50, 70),
            width=300,
            height=300,
            monster_spawns=[
                {"monster_id": "demon", "count": 50, "level": 55},
            ],
            connections=[
                AreaConnection("tristram", (150, 5)),
            ]
        )
        
        self.areas[town.id] = town
        self.areas[forest.id] = forest
        self.areas[cathedral.id] = cathedral
        self.areas[desert.id] = desert
        self.areas[snow.id] = snow
        self.areas[hell.id] = hell
        
        self._load_extended_areas()
        
        self.current_area_id = town.id
    
    def _load_extended_areas(self):
        try:
            from .area_extensions import create_extended_areas
            extended = create_extended_areas()
            for area_id, area in extended.items():
                if area_id not in self.areas:
                    self.areas[area_id] = area
        except ImportError:
            pass
    
    def get_current_area(self) -> Optional[Area]:
        return self.areas.get(self.current_area_id)
    
    def change_area(self, area_id: str) -> bool:
        if area_id not in self.areas:
            return False
        
        self.current_area_id = area_id
        return True
    
    def get_area(self, area_id: str) -> Optional[Area]:
        return self.areas.get(area_id)
    
    def get_connected_areas(self, area_id: str) -> List[str]:
        area = self.areas.get(area_id)
        if not area:
            return []
        
        return [conn.target_area_id for conn in area.connections]
    
    def get_areas_by_level(self, level: int) -> List[Area]:
        return [
            area for area in self.areas.values()
            if area.level_range[0] <= level <= area.level_range[1]
        ]
    
    def get_areas_by_type(self, area_type: AreaType) -> List[Area]:
        return [
            area for area in self.areas.values()
            if area.area_type == area_type
        ]
