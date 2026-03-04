"""
物品掉落系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import math

from entities.items import Item, ItemFactory, ItemRarity, Gem, Rune
from entities.items.gem import GemType, GemQuality
from entities.items.rune import RuneType


class DropSource(Enum):
    MONSTER = "monster"
    CHEST = "chest"
    BREAKABLE = "breakable"
    BOSS = "boss"
    ELITE = "elite"
    VENDOR = "vendor"
    QUEST = "quest"


@dataclass
class LootTable:
    id: str
    name: str
    
    item_weights: Dict[str, float] = field(default_factory=dict)
    gold_min: int = 0
    gold_max: int = 0
    gold_chance: float = 1.0
    
    gem_chance: float = 0.0
    gem_quality_weights: Dict[int, float] = field(default_factory=dict)
    
    rune_chance: float = 0.0
    rune_level_range: Tuple[int, int] = (1, 10)
    
    guaranteed_drops: List[str] = field(default_factory=list)
    
    magic_find_bonus: float = 0.0
    
    def roll_drop(self, magic_find: float = 0.0) -> List[Dict[str, Any]]:
        drops = []
        
        for item_id in self.guaranteed_drops:
            drops.append({"type": "item", "id": item_id})
        
        effective_magic_find = magic_find + self.magic_find_bonus
        
        if random.random() < self.gold_chance:
            gold = random.randint(self.gold_min, self.gold_max)
            gold = int(gold * (1 + effective_magic_find * 0.01))
            if gold > 0:
                drops.append({"type": "gold", "amount": gold})
        
        for item_id, weight in self.item_weights.items():
            adjusted_weight = weight * (1 + effective_magic_find * 0.01)
            if random.random() < adjusted_weight:
                drops.append({"type": "item", "id": item_id})
        
        if random.random() < self.gem_chance * (1 + effective_magic_find * 0.005):
            quality = self._roll_gem_quality()
            gem_type = random.choice(list(GemType))
            drops.append({"type": "gem", "gem_type": gem_type, "quality": quality})
        
        if random.random() < self.rune_chance * (1 + effective_magic_find * 0.005):
            rune_level = random.randint(self.rune_level_range[0], self.rune_level_range[1])
            rune_type = RuneType(rune_level)
            drops.append({"type": "rune", "rune_type": rune_type})
        
        return drops
    
    def _roll_gem_quality(self) -> GemQuality:
        if not self.gem_quality_weights:
            return GemQuality.STANDARD
        
        total = sum(self.gem_quality_weights.values())
        roll = random.random() * total
        
        cumulative = 0
        for quality, weight in self.gem_quality_weights.items():
            cumulative += weight
            if roll <= cumulative:
                return GemQuality(quality)
        
        return GemQuality.STANDARD


@dataclass
class DroppedItem:
    item: Any
    position: Tuple[float, float]
    velocity: Tuple[float, float] = (0, 0)
    
    lifetime: float = 300.0
    age: float = 0.0
    
    is_gold: bool = False
    gold_amount: int = 0
    
    magnet_range: float = 3.0
    pickup_range: float = 0.5
    
    is_being_collected: bool = False
    
    def update(self, delta_time: float, player_pos: Tuple[float, float] = None) -> bool:
        self.age += delta_time
        
        if self.age >= self.lifetime:
            return False
        
        self.position = (
            self.position[0] + self.velocity[0] * delta_time,
            self.position[1] + self.velocity[1] * delta_time
        )
        
        self.velocity = (
            self.velocity[0] * 0.95,
            self.velocity[1] * 0.95
        )
        
        if player_pos:
            dx = player_pos[0] - self.position[0]
            dy = player_pos[1] - self.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= self.magnet_range:
                self.is_being_collected = True
                speed = 10.0
                self.position = (
                    self.position[0] + (dx / distance) * speed * delta_time,
                    self.position[1] + (dy / distance) * speed * delta_time
                )
            
            if distance <= self.pickup_range:
                return True
        
        return False
    
    def can_pickup(self, player_pos: Tuple[float, float]) -> bool:
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        return distance <= self.pickup_range


class LootManager:
    def __init__(self):
        self.loot_tables: Dict[str, LootTable] = {}
        self.dropped_items: List[DroppedItem] = []
        
        self._create_default_loot_tables()
    
    def _create_default_loot_tables(self):
        self.loot_tables["normal_monster"] = LootTable(
            id="normal_monster",
            name="普通怪物",
            gold_min=1,
            gold_max=10,
            gold_chance=0.8,
            gem_chance=0.01,
            gem_quality_weights={1: 50, 2: 30, 3: 15, 4: 4, 5: 1},
            rune_chance=0.005,
            rune_level_range=(1, 10)
        )
        
        self.loot_tables["elite_monster"] = LootTable(
            id="elite_monster",
            name="精英怪物",
            gold_min=20,
            gold_max=100,
            gold_chance=1.0,
            item_weights={"sword_1h": 0.1, "helmet_light": 0.1, "ring": 0.15},
            gem_chance=0.1,
            gem_quality_weights={2: 40, 3: 35, 4: 20, 5: 4, 6: 1},
            rune_chance=0.05,
            rune_level_range=(5, 20)
        )
        
        self.loot_tables["boss"] = LootTable(
            id="boss",
            name="首领",
            gold_min=100,
            gold_max=500,
            gold_chance=1.0,
            item_weights={
                "sword_1h": 0.3, "axe_1h": 0.3, "staff": 0.3,
                "chest_heavy": 0.25, "chest_light": 0.25,
                "ring": 0.5, "amulet": 0.3
            },
            gem_chance=0.5,
            gem_quality_weights={3: 30, 4: 35, 5: 25, 6: 8, 7: 2},
            rune_chance=0.3,
            rune_level_range=(15, 33)
        )
        
        self.loot_tables["chest_normal"] = LootTable(
            id="chest_normal",
            name="普通宝箱",
            gold_min=10,
            gold_max=50,
            gold_chance=0.9,
            item_weights={"sword_1h": 0.1, "dagger": 0.1, "helmet_light": 0.1},
            gem_chance=0.05,
            rune_chance=0.02,
            rune_level_range=(1, 15)
        )
        
        self.loot_tables["chest_rare"] = LootTable(
            id="chest_rare",
            name="稀有宝箱",
            gold_min=50,
            gold_max=200,
            gold_chance=1.0,
            item_weights={
                "sword_1h": 0.2, "axe_1h": 0.2, "staff": 0.2,
                "chest_heavy": 0.15, "chest_light": 0.15,
                "ring": 0.3, "amulet": 0.2
            },
            gem_chance=0.2,
            gem_quality_weights={3: 40, 4: 35, 5: 20, 6: 4, 7: 1},
            rune_chance=0.1,
            rune_level_range=(10, 25)
        )
    
    def generate_loot(self, source: DropSource, level: int, 
                       position: Tuple[float, float],
                       magic_find: float = 0.0) -> List[DroppedItem]:
        table_id = self._get_table_id_for_source(source)
        table = self.loot_tables.get(table_id)
        
        if not table:
            return []
        
        drops = table.roll_drop(magic_find)
        dropped_items = []
        
        for drop in drops:
            item = self._create_drop_item(drop, level)
            if item:
                dropped_item = DroppedItem(
                    item=item,
                    position=position,
                    velocity=self._calculate_drop_velocity(),
                    is_gold=drop["type"] == "gold",
                    gold_amount=drop.get("amount", 0)
                )
                dropped_items.append(dropped_item)
        
        return dropped_items
    
    def _get_table_id_for_source(self, source: DropSource) -> str:
        mapping = {
            DropSource.MONSTER: "normal_monster",
            DropSource.ELITE: "elite_monster",
            DropSource.BOSS: "boss",
            DropSource.CHEST: "chest_normal",
            DropSource.BREAKABLE: "normal_monster",
        }
        return mapping.get(source, "normal_monster")
    
    def _create_drop_item(self, drop: Dict[str, Any], level: int) -> Any:
        drop_type = drop.get("type")
        
        if drop_type == "gold":
            return None
        
        if drop_type == "item":
            item_id = drop.get("id")
            rarity = self._roll_item_rarity()
            return ItemFactory.create_item(item_id, level, rarity)
        
        if drop_type == "gem":
            gem_type = drop.get("gem_type")
            quality = drop.get("quality")
            return Gem(gem_type, quality)
        
        if drop_type == "rune":
            rune_type = drop.get("rune_type")
            return Rune(rune_type)
        
        return None
    
    def _roll_item_rarity(self) -> ItemRarity:
        weights = [70, 20, 7, 2, 1, 0]
        roll = random.random() * 100
        cumulative = 0
        
        for i, weight in enumerate(weights):
            cumulative += weight
            if roll < cumulative:
                return ItemRarity(i)
        
        return ItemRarity.COMMON
    
    def _calculate_drop_velocity(self) -> Tuple[float, float]:
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 5)
        
        return (math.cos(angle) * speed, math.sin(angle) * speed)
    
    def add_dropped_items(self, items: List[DroppedItem]):
        self.dropped_items.extend(items)
    
    def update(self, delta_time: float, player_pos: Tuple[float, float] = None) -> List[DroppedItem]:
        collected = []
        
        for dropped in self.dropped_items[:]:
            if dropped.update(delta_time, player_pos):
                collected.append(dropped)
                self.dropped_items.remove(dropped)
        
        return collected
    
    def get_dropped_items(self) -> List[DroppedItem]:
        return self.dropped_items
    
    def get_items_near_position(self, position: Tuple[float, float], 
                                  range_limit: float) -> List[DroppedItem]:
        nearby = []
        
        for dropped in self.dropped_items:
            dx = position[0] - dropped.position[0]
            dy = position[1] - dropped.position[1]
            distance = math.sqrt(dx * dx + dy * dy)
            
            if distance <= range_limit:
                nearby.append(dropped)
        
        return nearby
    
    def clear(self):
        self.dropped_items.clear()
    
    def register_loot_table(self, table: LootTable):
        self.loot_tables[table.id] = table
