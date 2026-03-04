"""
地下城系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class DungeonType(Enum):
    RANDOM = "random"
    RIFT = "rift"
    GREATER_RIFT = "greater_rift"
    STORY = "story"
    EVENT = "event"


@dataclass
class DungeonRoom:
    id: str
    x: int
    y: int
    width: int
    height: int
    
    room_type: str = "normal"
    is_explored: bool = False
    
    monsters: List[Dict[str, Any]] = field(default_factory=list)
    objects: List[Dict[str, Any]] = field(default_factory=list)
    
    connections: List[str] = field(default_factory=list)
    
    def get_center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def contains_point(self, x: int, y: int) -> bool:
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + self.height)


@dataclass
class DungeonLevel:
    level: int
    rooms: Dict[str, DungeonRoom] = field(default_factory=dict)
    
    entrance: Optional[Tuple[int, int]] = None
    exit: Optional[Tuple[int, int]] = None
    
    monster_level: int = 1
    monster_density: float = 1.0


class Dungeon:
    def __init__(self, dungeon_id: str, name: str, 
                 dungeon_type: DungeonType = DungeonType.RANDOM,
                 max_levels: int = 5):
        self.id = dungeon_id
        self.name = name
        self.dungeon_type = dungeon_type
        self.max_levels = max_levels
        
        self.levels: Dict[int, DungeonLevel] = {}
        self.current_level = 1
        
        self.is_completed = False
        self.completion_time: Optional[float] = None
        
        self.monster_level_base = 1
        self.monster_level_scale = 2
    
    def generate_level(self, level_num: int, width: int = 50, height: int = 50) -> DungeonLevel:
        generator = DungeonGenerator()
        
        level = generator.generate(
            width=width,
            height=height,
            room_count=8 + level_num * 2,
            level_num=level_num
        )
        
        level.level = level_num
        level.monster_level = self.monster_level_base + (level_num - 1) * self.monster_level_scale
        level.monster_density = 1.0 + level_num * 0.1
        
        self.levels[level_num] = level
        return level
    
    def get_current_level_data(self) -> Optional[DungeonLevel]:
        return self.levels.get(self.current_level)
    
    def go_to_next_level(self) -> bool:
        if self.current_level >= self.max_levels:
            self.is_completed = True
            return False
        
        self.current_level += 1
        
        if self.current_level not in self.levels:
            self.generate_level(self.current_level)
        
        return True
    
    def get_room_at(self, x: int, y: int) -> Optional[DungeonRoom]:
        level = self.get_current_level_data()
        if not level:
            return None
        
        for room in level.rooms.values():
            if room.contains_point(x, y):
                return room
        
        return None


class DungeonGenerator:
    def __init__(self):
        self.min_room_size = 5
        self.max_room_size = 12
    
    def generate(self, width: int, height: int, 
                 room_count: int, level_num: int) -> DungeonLevel:
        level = DungeonLevel(level=level_num)
        
        rooms = self._generate_rooms(width, height, room_count)
        
        for i, room_data in enumerate(rooms):
            room = DungeonRoom(
                id=f"room_{i}",
                x=room_data["x"],
                y=room_data["y"],
                width=room_data["width"],
                height=room_data["height"],
                room_type=room_data.get("type", "normal")
            )
            level.rooms[room.id] = room
        
        self._connect_rooms(level)
        
        self._place_monsters(level, level_num)
        
        room_list = list(level.rooms.values())
        if room_list:
            first_room = room_list[0]
            level.entrance = first_room.get_center()
            
            last_room = room_list[-1]
            level.exit = last_room.get_center()
            last_room.room_type = "exit"
        
        return level
    
    def _generate_rooms(self, width: int, height: int, 
                         count: int) -> List[Dict[str, Any]]:
        rooms = []
        attempts = 0
        max_attempts = count * 10
        
        while len(rooms) < count and attempts < max_attempts:
            room_width = random.randint(self.min_room_size, self.max_room_size)
            room_height = random.randint(self.min_room_size, self.max_room_size)
            
            x = random.randint(1, width - room_width - 1)
            y = random.randint(1, height - room_height - 1)
            
            if not self._room_overlaps(rooms, x, y, room_width, room_height):
                rooms.append({
                    "x": x,
                    "y": y,
                    "width": room_width,
                    "height": room_height,
                    "type": self._determine_room_type(len(rooms), count)
                })
            
            attempts += 1
        
        return rooms
    
    def _room_overlaps(self, rooms: List[Dict], x: int, y: int, 
                        width: int, height: int) -> bool:
        for room in rooms:
            if (x < room["x"] + room["width"] + 2 and
                x + width + 2 > room["x"] and
                y < room["y"] + room["height"] + 2 and
                y + height + 2 > room["y"]):
                return True
        return False
    
    def _determine_room_type(self, index: int, total: int) -> str:
        if index == 0:
            return "entrance"
        elif index == total - 1:
            return "boss"
        elif random.random() < 0.1:
            return "treasure"
        elif random.random() < 0.15:
            return "elite"
        else:
            return "normal"
    
    def _connect_rooms(self, level: DungeonLevel):
        rooms = list(level.rooms.values())
        
        for i in range(len(rooms) - 1):
            room1 = rooms[i]
            room2 = rooms[i + 1]
            
            room1.connections.append(room2.id)
            room2.connections.append(room1.id)
        
        for i in range(len(rooms)):
            if random.random() < 0.3:
                j = random.randint(0, len(rooms) - 1)
                if i != j:
                    rooms[i].connections.append(rooms[j].id)
                    rooms[j].connections.append(rooms[i].id)
    
    def _place_monsters(self, level: DungeonLevel, level_num: int):
        for room in level.rooms.values():
            if room.room_type == "entrance":
                continue
            
            monster_count = int(room.width * room.height * level.monster_density * 0.05)
            
            if room.room_type == "elite":
                monster_count = max(1, monster_count // 3)
                for _ in range(monster_count):
                    room.monsters.append({
                        "type": "champion",
                        "level": level.monster_level + 2,
                        "position": self._random_position_in_room(room)
                    })
            
            elif room.room_type == "boss":
                room.monsters.append({
                    "type": "boss",
                    "level": level.monster_level + 5,
                    "position": room.get_center()
                })
            
            else:
                for _ in range(monster_count):
                    room.monsters.append({
                        "type": "normal",
                        "level": level.monster_level,
                        "position": self._random_position_in_room(room)
                    })
    
    def _random_position_in_room(self, room: DungeonRoom) -> Tuple[int, int]:
        return (
            random.randint(room.x + 1, room.x + room.width - 2),
            random.randint(room.y + 1, room.y + room.height - 2)
        )


class RiftDungeon(Dungeon):
    def __init__(self, rift_level: int, is_greater: bool = False):
        dungeon_type = DungeonType.GREATER_RIFT if is_greater else DungeonType.RIFT
        
        super().__init__(
            dungeon_id=f"rift_{rift_level}",
            name=f"{'大' if is_greater else ''}秘境 第{rift_level}层",
            dungeon_type=dungeon_type,
            max_levels=1
        )
        
        self.rift_level = rift_level
        self.is_greater = is_greater
        
        self.progress = 0.0
        self.progress_required = 100.0
        
        self.time_limit = 600.0 if is_greater else None
        self.elapsed_time = 0.0
        
        self.rift_guardian_spawned = False
        self.rift_guardian_defeated = False
    
    def add_progress(self, amount: float):
        self.progress = min(self.progress_required, self.progress + amount)
    
    def is_progress_complete(self) -> bool:
        return self.progress >= self.progress_required
    
    def spawn_rift_guardian(self) -> Dict[str, Any]:
        if self.rift_guardian_spawned:
            return {}
        
        self.rift_guardian_spawned = True
        
        return {
            "type": "boss",
            "level": self.rift_level + 10,
            "name": self._get_guardian_name()
        }
    
    def _get_guardian_name(self) -> str:
        guardians = [
            "贪婪女爵",
            "雷兹艾尔",
            "艾格多",
            "斯库瓦",
            "骨王",
            "瘟疫使者"
        ]
        return random.choice(guardians)
    
    def get_rewards(self) -> Dict[str, Any]:
        if not self.rift_guardian_defeated:
            return {}
        
        base_gold = self.rift_level * 100
        base_exp = self.rift_level * 500
        
        if self.is_greater:
            base_gold *= 2
            base_exp *= 3
        
        return {
            "gold": base_gold,
            "experience": base_exp,
            "legendary_gem_upgrades": 3 if self.is_greater else 0
        }
