"""
角色主类
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid
import time

from .attributes import Attributes, AttributeType, AttributeModifier
from .character_class import CharacterClass, ClassFactory, Resource_type
from .paragon import ParagonSystem


@dataclass
class SkillInstance:
    skill_id: str
    level: int = 1
    selected_branch: Optional[str] = None
    cooldown_remaining: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "skill_id": self.skill_id,
            "level": self.level,
            "selected_branch": self.selected_branch,
            "cooldown_remaining": self.cooldown_remaining
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SkillInstance':
        return cls(
            skill_id=data["skill_id"],
            level=data.get("level", 1),
            selected_branch=data.get("selected_branch"),
            cooldown_remaining=data.get("cooldown_remaining", 0.0)
        )


@dataclass
class PassiveInstance:
    passive_id: str
    level: int = 1
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "passive_id": self.passive_id,
            "level": self.level
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PassiveInstance':
        return cls(
            passive_id=data["passive_id"],
            level=data.get("level", 1)
        )


class Character:
    def __init__(self, class_id: str, name: str = ""):
        self.id = str(uuid.uuid4())[:8]
        self.name = name
        self.class_id = class_id
        
        self.character_class = ClassFactory.get_class(class_id)
        if not self.character_class:
            raise ValueError(f"Unknown class: {class_id}")
        
        self.level = 1
        self.experience = 0
        
        self.attributes = Attributes()
        self._initialize_attributes()
        
        self.paragon = ParagonSystem()
        
        self.current_health = self.get_max_health()
        self.current_resource = self.character_class.max_resource
        
        self.skills: Dict[str, SkillInstance] = {}
        self.passives: Dict[str, PassiveInstance] = {}
        self.skill_bar: List[Optional[str]] = [None] * 6
        
        self.equipment: Dict[str, Optional[Any]] = {
            slot: None for slot in [
                "head", "shoulders", "chest", "hands", "waist", "legs", "feet",
                "main_hand", "off_hand", "neck", "ring_left", "ring_right"
            ]
        }
        
        self.inventory: List[Optional[Any]] = [None] * 60
        
        self.gold = 0
        self.play_time = 0.0
        
        self.position = (0.0, 0.0)
        self.facing_direction = (1.0, 0.0)
        
        self.is_alive = True
        self.in_combat = False
        
        self.buffs: List[Dict[str, Any]] = []
        self.debuffs: List[Dict[str, Any]] = []
        
        self._attribute_points = 0
        self._skill_points = 0
    
    def _initialize_attributes(self):
        if self.character_class:
            for attr, value in self.character_class.starting_attributes.items():
                attr_type = getattr(AttributeType, attr.upper(), None)
                if attr_type:
                    self.attributes.set_base(attr_type, value)
    
    def get_max_health(self) -> float:
        derived = self.attributes.calculate_derived_attributes()
        base_health = derived.get(AttributeType.MAX_HEALTH, 100)
        return int(base_health * (1 + self.paragon.get_node_effect("max_health") / 100))
    
    def get_max_resource(self) -> float:
        return self.character_class.max_resource if self.character_class else 100
    
    def get_primary_attribute_value(self) -> float:
        if self.character_class:
            attr_name = self.character_class.primary_attribute.upper()
            attr_type = getattr(AttributeType, attr_name, AttributeType.STRENGTH)
            return self.attributes.get_total(attr_type)
        return 0
    
    def add_experience(self, amount: int) -> bool:
        if self.level >= 70:
            self.paragon.add_experience(amount)
            return False
        
        self.experience += amount
        leveled_up = False
        
        while self.level < 70:
            exp_needed = self.get_experience_for_level(self.level)
            if self.experience >= exp_needed:
                self.experience -= exp_needed
                self.level_up()
                leveled_up = True
            else:
                break
        
        return leveled_up
    
    def get_experience_for_level(self, level: int) -> int:
        return int(100 * (level ** 2.5))
    
    def level_up(self):
        self.level += 1
        self._attribute_points += 5
        self._skill_points += 1
        
        if self.character_class:
            for attr, value in self.character_class.attribute_per_level.items():
                attr_type = getattr(AttributeType, attr.upper(), None)
                if attr_type:
                    self.attributes.add_base(attr_type, value)
        
        self.current_health = self.get_max_health()
        self.current_resource = self.get_max_resource()
    
    def spend_attribute_point(self, attribute: str) -> bool:
        if self._attribute_points <= 0:
            return False
        
        attr_type = getattr(AttributeType, attribute.upper(), None)
        if not attr_type:
            return False
        
        self.attributes.add_base(attr_type, 1)
        self._attribute_points -= 1
        return True
    
    def get_available_attribute_points(self) -> int:
        return self._attribute_points
    
    def get_available_skill_points(self) -> int:
        return self._skill_points
    
    def learn_skill(self, skill_id: str) -> bool:
        if skill_id in self.skills:
            return False
        
        skill_def = None
        for skill in self.character_class.skills:
            if skill.id == skill_id:
                skill_def = skill
                break
        
        if not skill_def:
            return False
        
        if self.level < skill_def.required_level:
            return False
        
        self.skills[skill_id] = SkillInstance(skill_id=skill_id)
        return True
    
    def upgrade_skill(self, skill_id: str) -> bool:
        if skill_id not in self.skills:
            return False
        
        if self._skill_points <= 0:
            return False
        
        skill = self.skills[skill_id]
        skill_def = None
        for s in self.character_class.skills:
            if s.id == skill_id:
                skill_def = s
                break
        
        if skill_def and skill.level >= skill_def.max_level:
            return False
        
        skill.level += 1
        self._skill_points -= 1
        return True
    
    def select_skill_branch(self, skill_id: str, branch_id: str) -> bool:
        if skill_id not in self.skills:
            return False
        
        self.skills[skill_id].selected_branch = branch_id
        return True
    
    def set_skill_bar(self, slot: int, skill_id: Optional[str]) -> bool:
        if slot < 0 or slot >= len(self.skill_bar):
            return False
        
        if skill_id and skill_id not in self.skills:
            return False
        
        self.skill_bar[slot] = skill_id
        return True
    
    def use_skill(self, slot: int) -> bool:
        if slot < 0 or slot >= len(self.skill_bar):
            return False
        
        skill_id = self.skill_bar[slot]
        if not skill_id or skill_id not in self.skills:
            return False
        
        skill = self.skills[skill_id]
        if skill.cooldown_remaining > 0:
            return False
        
        skill_def = None
        for s in self.character_class.skills:
            if s.id == skill_id:
                skill_def = s
                break
        
        if not skill_def:
            return False
        
        if skill_def.resource_cost > self.current_resource:
            return False
        
        self.current_resource -= skill_def.resource_cost
        
        if skill_def.cooldown > 0:
            skill.cooldown_remaining = skill_def.cooldown
        
        return True
    
    def update_cooldowns(self, delta_time: float):
        for skill in self.skills.values():
            if skill.cooldown_remaining > 0:
                skill.cooldown_remaining = max(0, skill.cooldown_remaining - delta_time)
    
    def take_damage(self, amount: float, damage_type: str = "physical") -> float:
        armor = self.attributes.get_total(AttributeType.ARMOR)
        resist = 0
        
        resist_map = {
            "fire": AttributeType.FIRE_RESIST,
            "cold": AttributeType.COLD_RESIST,
            "lightning": AttributeType.LIGHTNING_RESIST,
            "poison": AttributeType.POISON_RESIST
        }
        
        if damage_type in resist_map:
            resist = self.attributes.get_total(resist_map[damage_type])
        
        damage_reduction = 1 - (armor / (armor + 100)) * (1 - resist / 100)
        actual_damage = amount * damage_reduction
        
        self.current_health -= actual_damage
        
        if self.current_health <= 0:
            self.current_health = 0
            self.is_alive = False
        
        return actual_damage
    
    def heal(self, amount: float):
        self.current_health = min(self.get_max_health(), self.current_health + amount)
    
    def regenerate(self, delta_time: float):
        if not self.is_alive:
            return
        
        health_regen = self.attributes.get_total(AttributeType.HEALTH_REGEN)
        self.heal(health_regen * delta_time)
        
        mana_regen = self.attributes.get_total(AttributeType.MANA_REGEN)
        self.current_resource = min(
            self.get_max_resource(),
            self.current_resource + mana_regen * delta_time
        )
    
    def equip_item(self, item, slot: str) -> Optional[Any]:
        if slot not in self.equipment:
            return None
        
        old_item = self.equipment[slot]
        self.equipment[slot] = item
        
        if old_item:
            self._remove_item_stats(old_item)
        if item:
            self._apply_item_stats(item)
        
        return old_item
    
    def unequip_item(self, slot: str) -> Optional[Any]:
        if slot not in self.equipment:
            return None
        
        item = self.equipment[slot]
        if item:
            self._remove_item_stats(item)
        self.equipment[slot] = None
        
        return item
    
    def _apply_item_stats(self, item):
        if not item:
            return
        
        from .attributes import AttributeType, AttributeModifier
        
        if hasattr(item, 'affixes'):
            for affix_inst in item.affixes:
                affix = affix_inst.affix
                value = affix_inst.get_effective_value()
                
                attr_mapping = {
                    "strength": AttributeType.STRENGTH,
                    "dexterity": AttributeType.DEXTERITY,
                    "intelligence": AttributeType.INTELLIGENCE,
                    "vitality": AttributeType.VITALITY,
                    "armor": AttributeType.ARMOR,
                    "max_health": AttributeType.MAX_HEALTH,
                    "max_mana": AttributeType.MAX_MANA,
                    "health_regen": AttributeType.HEALTH_REGEN,
                    "mana_regen": AttributeType.MANA_REGEN,
                    "attack_power": AttributeType.ATTACK_POWER,
                    "spell_power": AttributeType.SPELL_POWER,
                    "crit_chance": AttributeType.CRIT_CHANCE,
                    "crit_damage": AttributeType.CRIT_DAMAGE,
                    "attack_speed": AttributeType.ATTACK_SPEED,
                    "cast_speed": AttributeType.CAST_SPEED,
                    "movement_speed": AttributeType.MOVEMENT_SPEED,
                    "fire_resist": AttributeType.FIRE_RESIST,
                    "cold_resist": AttributeType.COLD_RESIST,
                    "lightning_resist": AttributeType.LIGHTNING_RESIST,
                    "poison_resist": AttributeType.POISON_RESIST,
                    "life_steal": AttributeType.LIFE_STEAL,
                    "magic_find": AttributeType.MAGIC_FIND,
                    "gold_find": AttributeType.GOLD_FIND,
                    "thorns": AttributeType.THORNS,
                    "dodge_chance": AttributeType.DODGE_CHANCE,
                    "block_chance": AttributeType.BLOCK_CHANCE,
                }
                
                attr_type = attr_mapping.get(affix.attribute)
                if attr_type:
                    is_percentage = affix.attribute.endswith("_percent") or affix.attribute in [
                        "crit_chance", "crit_damage", "life_steal", 
                        "magic_find", "gold_find", "dodge_chance", "block_chance"
                    ]
                    
                    modifier = AttributeModifier(
                        attribute=attr_type,
                        value=value,
                        is_percentage=is_percentage,
                        source=f"item_{item.id}"
                    )
                    self.attributes.add_modifier(modifier)
        
        if hasattr(item, 'socketed_items') and item.socketed_items:
            for socketed in item.socketed_items:
                if socketed and hasattr(socketed, 'get_stats'):
                    for stat, value in socketed.get_stats().items():
                        attr_mapping = {
                            "strength": AttributeType.STRENGTH,
                            "dexterity": AttributeType.DEXTERITY,
                            "intelligence": AttributeType.INTELLIGENCE,
                            "vitality": AttributeType.VITALITY,
                            "crit_chance": AttributeType.CRIT_CHANCE,
                            "crit_damage": AttributeType.CRIT_DAMAGE,
                            "attack_speed": AttributeType.ATTACK_SPEED,
                        }
                        
                        attr_type = attr_mapping.get(stat)
                        if attr_type:
                            modifier = AttributeModifier(
                                attribute=attr_type,
                                value=value,
                                is_percentage=stat in ["crit_chance", "crit_damage", "attack_speed"],
                                source=f"gem_{item.id}"
                            )
                            self.attributes.add_modifier(modifier)
        
        if hasattr(item, 'enchant_level') and item.enchant_level > 0:
            bonus_percent = item.enchant_level * 2
            
            if hasattr(item, 'base_stats'):
                for stat in item.base_stats:
                    if stat in ["min_damage", "max_damage", "armor"]:
                        pass
    
    def _remove_item_stats(self, item):
        if not item:
            return
        
        self.attributes.remove_modifiers_from_source(f"item_{item.id}")
        self.attributes.remove_modifiers_from_source(f"gem_{item.id}")
    
    def add_buff(self, buff_id: str, duration: float, effects: Dict[str, float]):
        self.buffs.append({
            "id": buff_id,
            "duration": duration,
            "remaining": duration,
            "effects": effects
        })
        
        for attr_name, value in effects.items():
            attr_type = getattr(AttributeType, attr_name.upper(), None)
            if attr_type:
                modifier = AttributeModifier(
                    attribute=attr_type,
                    value=value,
                    is_percentage="percent" in attr_name.lower(),
                    source=f"buff_{buff_id}"
                )
                self.attributes.add_modifier(modifier)
    
    def remove_buff(self, buff_id: str):
        self.buffs = [b for b in self.buffs if b["id"] != buff_id]
        self.attributes.remove_modifiers_from_source(f"buff_{buff_id}")
    
    def update_buffs(self, delta_time: float):
        expired = []
        for buff in self.buffs:
            buff["remaining"] -= delta_time
            if buff["remaining"] <= 0:
                expired.append(buff["id"])
        
        for buff_id in expired:
            self.remove_buff(buff_id)
    
    def learn_passive(self, passive_id: str) -> bool:
        if passive_id in self.passives:
            return False
        
        passive_def = None
        for passive in self.character_class.passives:
            if passive.id == passive_id:
                passive_def = passive
                break
        
        if not passive_def:
            return False
        
        if self.level < passive_def.required_level:
            return False
        
        self.passives[passive_id] = PassiveInstance(passive_id=passive_id)
        self._apply_passive_effects(passive_id)
        return True
    
    def upgrade_passive(self, passive_id: str) -> bool:
        if passive_id not in self.passives:
            return False
        
        if self._skill_points <= 0:
            return False
        
        passive = self.passives[passive_id]
        passive_def = None
        for p in self.character_class.passives:
            if p.id == passive_id:
                passive_def = p
                break
        
        if passive_def and passive.level >= passive_def.max_level:
            return False
        
        self._remove_passive_effects(passive_id)
        passive.level += 1
        self._apply_passive_effects(passive_id)
        self._skill_points -= 1
        return True
    
    def _apply_passive_effects(self, passive_id: str):
        if passive_id not in self.passives:
            return
        
        passive_inst = self.passives[passive_id]
        passive_def = None
        for p in self.character_class.passives:
            if p.id == passive_id:
                passive_def = p
                break
        
        if not passive_def:
            return
        
        level = passive_inst.level
        
        for effect_name, base_value in passive_def.effects.items():
            value = base_value * level
            
            attr_mapping = {
                "strength": AttributeType.STRENGTH,
                "dexterity": AttributeType.DEXTERITY,
                "intelligence": AttributeType.INTELLIGENCE,
                "vitality": AttributeType.VITALITY,
                "armor": AttributeType.ARMOR,
                "max_health": AttributeType.MAX_HEALTH,
                "max_mana": AttributeType.MAX_MANA,
                "health_regen": AttributeType.HEALTH_REGEN,
                "mana_regen": AttributeType.MANA_REGEN,
                "attack_power": AttributeType.ATTACK_POWER,
                "spell_power": AttributeType.SPELL_POWER,
                "crit_chance": AttributeType.CRIT_CHANCE,
                "crit_damage": AttributeType.CRIT_DAMAGE,
                "attack_speed": AttributeType.ATTACK_SPEED,
                "cast_speed": AttributeType.CAST_SPEED,
                "movement_speed": AttributeType.MOVEMENT_SPEED,
                "fire_resist": AttributeType.FIRE_RESIST,
                "cold_resist": AttributeType.COLD_RESIST,
                "lightning_resist": AttributeType.LIGHTNING_RESIST,
                "poison_resist": AttributeType.POISON_RESIST,
                "life_steal": AttributeType.LIFE_STEAL,
                "magic_find": AttributeType.MAGIC_FIND,
                "gold_find": AttributeType.GOLD_FIND,
                "dodge_chance": AttributeType.DODGE_CHANCE,
                "block_chance": AttributeType.BLOCK_CHANCE,
                "thorns": AttributeType.THORNS,
            }
            
            attr_type = attr_mapping.get(effect_name)
            if attr_type:
                is_percentage = effect_name in [
                    "crit_chance", "crit_damage", "life_steal",
                    "magic_find", "gold_find", "dodge_chance", "block_chance",
                    "attack_speed", "cast_speed", "movement_speed"
                ]
                
                modifier = AttributeModifier(
                    attribute=attr_type,
                    value=value,
                    is_percentage=is_percentage,
                    source=f"passive_{passive_id}"
                )
                self.attributes.add_modifier(modifier)
    
    def _remove_passive_effects(self, passive_id: str):
        self.attributes.remove_modifiers_from_source(f"passive_{passive_id}")
    
    def get_passive_level(self, passive_id: str) -> int:
        if passive_id in self.passives:
            return self.passives[passive_id].level
        return 0
    
    def recalculate_all_passive_effects(self):
        for passive_id in self.passives:
            self._remove_passive_effects(passive_id)
            self._apply_passive_effects(passive_id)
    
    def update(self, delta_time: float):
        self.play_time += delta_time
        self.update_cooldowns(delta_time)
        self.update_buffs(delta_time)
        self.attributes.update_durations(delta_time)
        self.regenerate(delta_time)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "class_id": self.class_id,
            "level": self.level,
            "experience": self.experience,
            "attributes": self.attributes.to_dict(),
            "paragon": self.paragon.to_dict(),
            "current_health": self.current_health,
            "current_resource": self.current_resource,
            "skills": {k: v.to_dict() for k, v in self.skills.items()},
            "passives": {k: v.to_dict() for k, v in self.passives.items()},
            "skill_bar": self.skill_bar,
            "equipment": {k: v.to_dict() if v else None for k, v in self.equipment.items()},
            "inventory": [v.to_dict() if v else None for v in self.inventory],
            "gold": self.gold,
            "play_time": self.play_time,
            "position": self.position,
            "attribute_points": self._attribute_points,
            "skill_points": self._skill_points
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        character = cls(data["class_id"], data.get("name", ""))
        
        character.id = data.get("id", character.id)
        character.level = data.get("level", 1)
        character.experience = data.get("experience", 0)
        character.current_health = data.get("current_health", character.get_max_health())
        character.current_resource = data.get("current_resource", character.get_max_resource())
        character.gold = data.get("gold", 0)
        character.play_time = data.get("play_time", 0)
        character.position = tuple(data.get("position", (0, 0)))
        character._attribute_points = data.get("attribute_points", 0)
        character._skill_points = data.get("skill_points", 0)
        
        if "attributes" in data:
            character.attributes = Attributes.from_dict(data["attributes"])
        
        if "paragon" in data:
            character.paragon = ParagonSystem.from_dict(data["paragon"])
        
        for skill_id, skill_data in data.get("skills", {}).items():
            character.skills[skill_id] = SkillInstance.from_dict(skill_data)
        
        character.skill_bar = data.get("skill_bar", [None] * 6)
        
        return character
