"""
怪物系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random
import math


class MonsterType(Enum):
    NORMAL = "normal"
    CHAMPION = "champion"
    RARE = "rare"
    UNIQUE = "unique"
    BOSS = "boss"


class MonsterBehavior(Enum):
    AGGRESSIVE = "aggressive"
    DEFENSIVE = "defensive"
    PASSIVE = "passive"
    PATROL = "patrol"
    FLEE = "flee"


@dataclass
class MonsterStats:
    health: float = 100
    damage_min: float = 10
    damage_max: float = 20
    armor: float = 10
    movement_speed: float = 1.0
    attack_speed: float = 1.0
    attack_range: float = 1.5
    aggro_range: float = 10.0
    
    fire_resist: float = 0
    cold_resist: float = 0
    lightning_resist: float = 0
    poison_resist: float = 0
    
    experience: int = 10
    gold_min: int = 1
    gold_max: int = 10


@dataclass
class MonsterAffix:
    id: str
    name: str
    description: str
    effects: Dict[str, float] = field(default_factory=dict)


class Monster:
    def __init__(self, monster_id: str, name: str, level: int, 
                 monster_type: MonsterType = MonsterType.NORMAL):
        self.id = monster_id
        self.name = name
        self.level = level
        self.monster_type = monster_type
        
        self.stats = MonsterStats()
        self.current_health = self.stats.health
        self.is_alive = True
        
        self.position: Tuple[float, float] = (0.0, 0.0)
        self.velocity: Tuple[float, float] = (0.0, 0.0)
        self.facing: Tuple[float, float] = (1.0, 0.0)
        
        self.affixes: List[MonsterAffix] = []
        self.behavior = MonsterBehavior.AGGRESSIVE
        
        self.target: Optional[Any] = None
        self.attack_cooldown = 0.0
        self.state = "idle"
        
        self.loot_table: List[Dict[str, Any]] = []
        self.drop_chance = 0.1
        
        self._apply_type_modifiers()
    
    def _apply_type_modifiers(self):
        if self.monster_type == MonsterType.CHAMPION:
            self.stats.health *= 2
            self.stats.damage_min *= 1.3
            self.stats.damage_max *= 1.3
            self.stats.experience *= 2
            self._add_random_affixes(1)
        
        elif self.monster_type == MonsterType.RARE:
            self.stats.health *= 3
            self.stats.damage_min *= 1.5
            self.stats.damage_max *= 1.5
            self.stats.experience *= 3
            self._add_random_affixes(2)
        
        elif self.monster_type == MonsterType.UNIQUE:
            self.stats.health *= 5
            self.stats.damage_min *= 2
            self.stats.damage_max *= 2
            self.stats.experience *= 5
            self._add_random_affixes(3)
        
        elif self.monster_type == MonsterType.BOSS:
            self.stats.health *= 20
            self.stats.damage_min *= 3
            self.stats.damage_max *= 3
            self.stats.experience *= 20
            self._add_random_affixes(4)
        
        self.current_health = self.stats.health
    
    def _add_random_affixes(self, count: int):
        available_affixes = [
            MonsterAffix("vampiric", "吸血", "攻击回复生命", {"life_steal": 20}),
            MonsterAffix("molten", "熔火", "死亡时爆炸", {"death_explosion": 100}),
            MonsterAffix("frozen", "冰冷", "攻击冻结敌人", {"freeze_chance": 30}),
            MonsterAffix("electrified", "带电", "被击中时释放闪电", {"lightning_on_hit": 50}),
            MonsterAffix("plagued", "瘟疫", "留下毒云", {"poison_trail": 100}),
            MonsterAffix("shielding", "护盾", "周期性获得护盾", {"shield": 50}),
            MonsterAffix("teleporter", "传送", "可以传送", {"teleport": 100}),
            MonsterAffix("fast", "快速", "移动速度提高", {"movement_speed": 50}),
            MonsterAffix("jailer", "监禁", "可以禁锢敌人", {"jail_chance": 20}),
            MonsterAffix("wall", "筑墙", "可以召唤墙壁", {"wall_chance": 20}),
        ]
        
        selected = random.sample(available_affixes, min(count, len(available_affixes)))
        
        for affix in selected:
            self.affixes.append(affix)
            for effect, value in affix.effects.items():
                if effect == "movement_speed":
                    self.stats.movement_speed *= (1 + value / 100)
    
    def update(self, delta_time: float, player_pos: Tuple[float, float] = None):
        if not self.is_alive:
            return
        
        self.attack_cooldown = max(0, self.attack_cooldown - delta_time)
        self._update_affix_effects(delta_time)
        
        if player_pos:
            distance = self._distance_to(player_pos)
            
            if distance <= self.stats.aggro_range:
                if self.state == "idle":
                    self._on_aggro()
                self.state = "chase"
                self.target = player_pos
            elif distance > self.stats.aggro_range * 1.5:
                self.state = "idle"
                self.target = None
        
        if self.state == "chase" and self.target:
            self._execute_ai_behavior(delta_time)
    
    def _on_aggro(self):
        for affix in self.affixes:
            if affix.id == "teleporter":
                self._can_teleport = True
    
    def _update_affix_effects(self, delta_time: float):
        for affix in self.affixes:
            if affix.id == "shielding":
                if not hasattr(self, '_shield_timer'):
                    self._shield_timer = 5.0
                    self._shield_active = False
                
                self._shield_timer -= delta_time
                if self._shield_timer <= 0:
                    self._shield_active = not self._shield_active
                    self._shield_timer = 5.0 if self._shield_active else 8.0
            
            elif affix.id == "plagued":
                if not hasattr(self, '_poison_timer'):
                    self._poison_timer = 0
                self._poison_timer += delta_time
                if self._poison_timer >= 1.0:
                    self._poison_timer = 0
                    self._create_poison_pool()
    
    def _execute_ai_behavior(self, delta_time: float):
        if not self.target:
            return
        
        distance = self._distance_to(self.target)
        
        if self.behavior == MonsterBehavior.AGGRESSIVE:
            self._aggressive_behavior(delta_time, distance)
        elif self.behavior == MonsterBehavior.DEFENSIVE:
            self._defensive_behavior(delta_time, distance)
        elif self.behavior == MonsterBehavior.FLEE:
            self._flee_behavior(delta_time, distance)
        elif self.behavior == MonsterBehavior.PATROL:
            self._patrol_behavior(delta_time, distance)
        else:
            self._aggressive_behavior(delta_time, distance)
    
    def _aggressive_behavior(self, delta_time: float, distance: float):
        if distance <= self.stats.attack_range:
            self._try_use_special_ability()
        elif distance > self.stats.attack_range:
            self._move_towards(self.target, delta_time)
            
            if self._can_teleport() and distance > 5:
                self._teleport_to_target()
    
    def _defensive_behavior(self, delta_time: float, distance: float):
        if distance <= self.stats.attack_range * 0.5:
            self._move_away_from_target(delta_time)
        elif distance <= self.stats.attack_range:
            pass
        else:
            self._move_towards(self.target, delta_time * 0.5)
    
    def _flee_behavior(self, delta_time: float, distance: float):
        health_percent = self.current_health / self.stats.health
        
        if health_percent < 0.3:
            self._move_away_from_target(delta_time * 1.5)
        elif distance <= self.stats.attack_range:
            pass
        else:
            self._move_towards(self.target, delta_time * 0.7)
    
    def _patrol_behavior(self, delta_time: float, distance: float):
        if not hasattr(self, '_patrol_target'):
            self._patrol_target = self._get_random_patrol_point()
        
        if distance <= self.stats.aggro_range * 0.5:
            self._move_towards(self.target, delta_time)
        else:
            patrol_dist = self._distance_to(self._patrol_target)
            if patrol_dist < 1.0:
                self._patrol_target = self._get_random_patrol_point()
            else:
                self._move_towards(self._patrol_target, delta_time * 0.3)
    
    def _get_random_patrol_point(self) -> Tuple[float, float]:
        import random
        offset_x = random.uniform(-5, 5)
        offset_y = random.uniform(-5, 5)
        return (
            self.position[0] + offset_x,
            self.position[1] + offset_y
        )
    
    def _move_away_from_target(self, delta_time: float):
        if not self.target:
            return
        
        dx = self.position[0] - self.target[0]
        dy = self.position[1] - self.target[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0.1:
            dx /= distance
            dy /= distance
            
            self.position = (
                self.position[0] + dx * self.stats.movement_speed * delta_time,
                self.position[1] + dy * self.stats.movement_speed * delta_time
            )
    
    def _can_teleport(self) -> bool:
        for affix in self.affixes:
            if affix.id == "teleporter":
                if not hasattr(self, '_teleport_cooldown'):
                    self._teleport_cooldown = 0
                return self._teleport_cooldown <= 0
        return False
    
    def _teleport_to_target(self):
        if not self.target:
            return
        
        dx = self.target[0] - self.position[0]
        dy = self.target[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0:
            dx /= distance
            dy /= distance
            
            teleport_dist = min(distance - 2, 8)
            self.position = (
                self.position[0] + dx * teleport_dist,
                self.position[1] + dy * teleport_dist
            )
            self._teleport_cooldown = 5.0
    
    def _try_use_special_ability(self):
        for affix in self.affixes:
            if affix.id == "jailer":
                if not hasattr(self, '_jail_cooldown'):
                    self._jail_cooldown = 0
                if self._jail_cooldown <= 0:
                    self._use_jail_ability()
                    self._jail_cooldown = 8.0
            
            elif affix.id == "wall":
                if not hasattr(self, '_wall_cooldown'):
                    self._wall_cooldown = 0
                if self._wall_cooldown <= 0:
                    self._use_wall_ability()
                    self._wall_cooldown = 10.0
    
    def _use_jail_ability(self):
        pass
    
    def _use_wall_ability(self):
        pass
    
    def _create_poison_pool(self):
        pass
    
    def _distance_to(self, pos: Tuple[float, float]) -> float:
        dx = pos[0] - self.position[0]
        dy = pos[1] - self.position[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _move_towards(self, target: Tuple[float, float], delta_time: float):
        dx = target[0] - self.position[0]
        dy = target[1] - self.position[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > 0.1:
            dx /= distance
            dy /= distance
            
            self.position = (
                self.position[0] + dx * self.stats.movement_speed * delta_time,
                self.position[1] + dy * self.stats.movement_speed * delta_time
            )
            
            self.facing = (dx, dy)
    
    def can_attack(self, target_pos: Tuple[float, float]) -> bool:
        if self.attack_cooldown > 0:
            return False
        
        distance = self._distance_to(target_pos)
        return distance <= self.stats.attack_range
    
    def attack(self) -> Tuple[float, float, str]:
        self.attack_cooldown = 1.0 / self.stats.attack_speed
        
        damage = random.uniform(self.stats.damage_min, self.stats.damage_max)
        
        return (damage, damage * 1.2, "physical")
    
    def take_damage(self, amount: float) -> float:
        damage_reduction = self.stats.armor / (self.stats.armor + 100)
        actual_damage = amount * (1 - damage_reduction)
        
        self.current_health -= actual_damage
        
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
        
        return actual_damage
    
    def get_loot(self) -> List[Dict[str, Any]]:
        if not self.loot_table:
            return []
        
        loot = []
        
        for item_entry in self.loot_table:
            if random.random() < item_entry.get("chance", 0.1):
                loot.append({
                    "item_id": item_entry["item_id"],
                    "quantity": random.randint(
                        item_entry.get("min_quantity", 1),
                        item_entry.get("max_quantity", 1)
                    )
                })
        
        return loot
    
    def get_experience(self) -> int:
        return self.stats.experience
    
    def get_gold(self) -> int:
        return random.randint(self.stats.gold_min, self.stats.gold_max)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "monster_type": self.monster_type.value,
            "current_health": self.current_health,
            "position": self.position,
            "is_alive": self.is_alive
        }


class MonsterFactory:
    _monster_templates: Dict[str, Dict[str, Any]] = {}
    _initialized = False
    
    @classmethod
    def initialize(cls):
        if cls._initialized:
            return
        
        cls._create_templates()
        cls._initialized = True
    
    @classmethod
    def _create_templates(cls):
        cls._monster_templates = {
            "zombie": {
                "name": "僵尸",
                "base_stats": MonsterStats(
                    health=50,
                    damage_min=5,
                    damage_max=10,
                    armor=5,
                    movement_speed=0.8,
                    experience=5
                )
            },
            "skeleton": {
                "name": "骷髅",
                "base_stats": MonsterStats(
                    health=40,
                    damage_min=8,
                    damage_max=15,
                    armor=3,
                    movement_speed=1.0,
                    experience=6
                )
            },
            "demon": {
                "name": "恶魔",
                "base_stats": MonsterStats(
                    health=80,
                    damage_min=12,
                    damage_max=20,
                    armor=10,
                    movement_speed=1.2,
                    fire_resist=50,
                    experience=15
                )
            },
            "fallen": {
                "name": "堕落者",
                "base_stats": MonsterStats(
                    health=30,
                    damage_min=5,
                    damage_max=10,
                    armor=2,
                    movement_speed=1.5,
                    experience=4
                )
            },
            "skeleton_archer": {
                "name": "骷髅弓箭手",
                "base_stats": MonsterStats(
                    health=35,
                    damage_min=10,
                    damage_max=18,
                    armor=2,
                    movement_speed=0.9,
                    attack_range=10,
                    experience=8
                )
            },
            "ghost": {
                "name": "幽灵",
                "base_stats": MonsterStats(
                    health=60,
                    damage_min=8,
                    damage_max=15,
                    armor=0,
                    movement_speed=1.3,
                    cold_resist=100,
                    experience=10
                )
            },
            "goblin": {
                "name": "哥布林",
                "base_stats": MonsterStats(
                    health=25,
                    damage_min=3,
                    damage_max=8,
                    armor=2,
                    movement_speed=2.0,
                    gold_min=10,
                    gold_max=50,
                    experience=3
                )
            },
            "treasure_goblin": {
                "name": "宝藏哥布林",
                "base_stats": MonsterStats(
                    health=100,
                    damage_min=5,
                    damage_max=10,
                    armor=5,
                    movement_speed=2.5,
                    gold_min=100,
                    gold_max=500,
                    experience=50
                )
            },
            "butcher": {
                "name": "屠夫",
                "base_stats": MonsterStats(
                    health=500,
                    damage_min=30,
                    damage_max=50,
                    armor=20,
                    movement_speed=1.0,
                    experience=200
                )
            },
            "skeleton_king": {
                "name": "骷髅王",
                "base_stats": MonsterStats(
                    health=1000,
                    damage_min=40,
                    damage_max=60,
                    armor=30,
                    movement_speed=0.8,
                    experience=500
                )
            },
        }
    
    @classmethod
    def create_monster(cls, template_id: str, level: int, 
                       monster_type: MonsterType = MonsterType.NORMAL,
                       position: Tuple[float, float] = (0, 0)) -> Optional[Monster]:
        if not cls._initialized:
            cls.initialize()
        
        template = cls._monster_templates.get(template_id)
        if not template:
            return None
        
        monster_id = f"{template_id}_{random.randint(1000, 9999)}"
        monster = Monster(monster_id, template["name"], level, monster_type)
        
        base_stats = template["base_stats"]
        level_mult = 1 + (level - 1) * 0.1
        
        monster.stats = MonsterStats(
            health=base_stats.health * level_mult,
            damage_min=base_stats.damage_min * level_mult,
            damage_max=base_stats.damage_max * level_mult,
            armor=base_stats.armor * level_mult,
            movement_speed=base_stats.movement_speed,
            attack_speed=base_stats.attack_speed,
            attack_range=base_stats.attack_range,
            aggro_range=base_stats.aggro_range,
            fire_resist=base_stats.fire_resist,
            cold_resist=base_stats.cold_resist,
            lightning_resist=base_stats.lightning_resist,
            poison_resist=base_stats.poison_resist,
            experience=int(base_stats.experience * level_mult),
            gold_min=int(base_stats.gold_min * level_mult),
            gold_max=int(base_stats.gold_max * level_mult)
        )
        
        monster.current_health = monster.stats.health
        monster.position = position
        
        return monster
    
    @classmethod
    def get_template_ids(cls) -> List[str]:
        if not cls._initialized:
            cls.initialize()
        return list(cls._monster_templates.keys())
    
    @classmethod
    def create_random_monster(cls, level: int, 
                               monster_type: MonsterType = MonsterType.NORMAL,
                               position: Tuple[float, float] = (0, 0)) -> Monster:
        if not cls._initialized:
            cls.initialize()
        
        template_id = random.choice(list(cls._monster_templates.keys()))
        return cls.create_monster(template_id, level, monster_type, position)
