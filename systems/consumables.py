"""
消耗品系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum


class PotionType(Enum):
    HEALTH = "health"
    MANA = "mana"
    RESOURCE = "resource"
    SPECIAL = "special"


@dataclass
class Potion:
    id: str
    name: str
    potion_type: PotionType
    
    restore_amount: float = 0
    restore_percent: float = 0
    
    cooldown: float = 10.0
    
    required_level: int = 1
    
    instant: bool = True
    duration: float = 0.0
    
    additional_effects: Dict[str, float] = field(default_factory=dict)
    
    icon: str = ""
    description: str = ""
    
    def use(self, character: Any) -> Dict[str, Any]:
        if self.required_level > getattr(character, 'level', 1):
            return {"success": False, "message": f"需要等级 {self.required_level}"}
        
        if self.potion_type == PotionType.HEALTH:
            return self._apply_health(character)
        elif self.potion_type == PotionType.MANA:
            return self._apply_mana(character)
        elif self.potion_type == PotionType.RESOURCE:
            return self._apply_resource(character)
        elif self.potion_type == PotionType.SPECIAL:
            return self._apply_special(character)
        
        return {"success": False, "message": "无效的药水类型"}
    
    def _apply_health(self, character: Any) -> Dict[str, Any]:
        if not hasattr(character, 'current_health'):
            return {"success": False, "message": "无法使用"}
        
        max_health = 100
        if hasattr(character, 'attributes') and hasattr(character.attributes, 'get_total'):
            max_health = character.attributes.get_total('max_health')
        elif hasattr(character, 'get_max_health'):
            max_health = character.get_max_health() if callable(character.get_max_health) else character.get_max_health
        
        if character.current_health >= max_health:
            return {"success": False, "message": "生命值已满"}
        
        restore = self.restore_amount
        if self.restore_percent > 0:
            restore += max_health * self.restore_percent / 100
        
        character.current_health = min(max_health, character.current_health + restore)
        
        return {"success": True, "message": f"恢复了 {int(restore)} 点生命值", "heal": int(restore)}
    
    def _apply_mana(self, character: Any) -> Dict[str, Any]:
        if not hasattr(character, 'current_resource'):
            return {"success": False, "message": "无法使用"}
        
        max_resource = 100
        if hasattr(character, 'get_max_resource'):
            max_resource = character.get_max_resource() if callable(character.get_max_resource) else character.get_max_resource
        
        if character.current_resource >= max_resource:
            return {"success": False, "message": "法力值已满"}
        
        restore = self.restore_amount
        if self.restore_percent > 0:
            restore += max_resource * self.restore_percent / 100
        
        character.current_resource = min(max_resource, character.current_resource + restore)
        
        return {"success": True, "message": f"恢复了 {int(restore)} 点法力值", "restore": int(restore)}
    
    def _apply_resource(self, character: Any) -> Dict[str, Any]:
        return self._apply_mana(character)
    
    def _apply_special(self, character: Any) -> Dict[str, Any]:
        for effect_name, value in self.additional_effects.items():
            if hasattr(character, 'attributes'):
                from entities.character.attributes import AttributeType, AttributeModifier
                
                attr_type = getattr(AttributeType, effect_name.upper(), None)
                if attr_type:
                    modifier = AttributeModifier(
                        attribute=attr_type,
                        value=value,
                        is_percentage=True,
                        source=f"potion_{self.id}",
                        duration=self.duration
                    )
                    character.attributes.add_modifier(modifier)
        
        return {"success": True, "message": f"使用了 {self.name}"}


class PotionFactory:
    POTIONS = {
        "health_potion_small": Potion(
            id="health_potion_small",
            name="小型生命药水",
            potion_type=PotionType.HEALTH,
            restore_amount=50,
            cooldown=10.0,
            required_level=1,
            description="恢复50点生命值"
        ),
        "health_potion_medium": Potion(
            id="health_potion_medium",
            name="中型生命药水",
            potion_type=PotionType.HEALTH,
            restore_amount=150,
            cooldown=10.0,
            required_level=10,
            description="恢复150点生命值"
        ),
        "health_potion_large": Potion(
            id="health_potion_large",
            name="大型生命药水",
            potion_type=PotionType.HEALTH,
            restore_amount=300,
            cooldown=10.0,
            required_level=20,
            description="恢复300点生命值"
        ),
        "health_potion_super": Potion(
            id="health_potion_super",
            name="超级生命药水",
            potion_type=PotionType.HEALTH,
            restore_percent=60,
            cooldown=10.0,
            required_level=40,
            description="恢复60%最大生命值"
        ),
        "mana_potion_small": Potion(
            id="mana_potion_small",
            name="小型法力药水",
            potion_type=PotionType.MANA,
            restore_amount=30,
            cooldown=10.0,
            required_level=1,
            description="恢复30点法力值"
        ),
        "mana_potion_medium": Potion(
            id="mana_potion_medium",
            name="中型法力药水",
            potion_type=PotionType.MANA,
            restore_amount=80,
            cooldown=10.0,
            required_level=10,
            description="恢复80点法力值"
        ),
        "mana_potion_large": Potion(
            id="mana_potion_large",
            name="大型法力药水",
            potion_type=PotionType.MANA,
            restore_amount=150,
            cooldown=10.0,
            required_level=20,
            description="恢复150点法力值"
        ),
        "rejuvenation_potion": Potion(
            id="rejuvenation_potion",
            name="恢复药水",
            potion_type=PotionType.SPECIAL,
            restore_percent=30,
            cooldown=15.0,
            required_level=15,
            additional_effects={"health_regen": 50, "mana_regen": 30},
            duration=10.0,
            description="恢复30%生命和法力，并提升回复速度"
        ),
        "invulnerability_potion": Potion(
            id="invulnerability_potion",
            name="无敌药水",
            potion_type=PotionType.SPECIAL,
            cooldown=120.0,
            required_level=50,
            additional_effects={"damage_reduction": 100},
            duration=5.0,
            description="免疫所有伤害，持续5秒"
        ),
        "speed_potion": Potion(
            id="speed_potion",
            name="加速药水",
            potion_type=PotionType.SPECIAL,
            cooldown=60.0,
            required_level=20,
            additional_effects={"movement_speed_percent": 50, "attack_speed_percent": 25},
            duration=15.0,
            description="移动速度+50%，攻击速度+25%，持续15秒"
        ),
    }
    
    @classmethod
    def get_potion(cls, potion_id: str) -> Optional[Potion]:
        return cls.POTIONS.get(potion_id)
    
    @classmethod
    def get_all_potions(cls) -> Dict[str, Potion]:
        return cls.POTIONS.copy()
    
    @classmethod
    def get_potions_for_level(cls, level: int) -> List[Potion]:
        return [
            potion for potion in cls.POTIONS.values()
            if potion.required_level <= level
        ]


class PotionBelt:
    def __init__(self, slots: int = 4):
        self.slots = slots
        self.potions: List[Optional[Tuple[Potion, int]]] = [None] * slots
        self.cooldowns: List[float] = [0.0] * slots
    
    def add_potion(self, potion: Potion, count: int = 1) -> Tuple[bool, int]:
        for i, slot in enumerate(self.potions):
            if slot and slot[0].id == potion.id:
                new_count = slot[1] + count
                self.potions[i] = (potion, min(new_count, 99))
                return True, count
        
        for i, slot in enumerate(self.potions):
            if slot is None:
                self.potions[i] = (potion, min(count, 99))
                return True, count
        
        return False, 0
    
    def use_potion(self, slot_index: int, character: Any) -> Tuple[bool, str]:
        if slot_index < 0 or slot_index >= self.slots:
            return False, "无效的槽位"
        
        if self.cooldowns[slot_index] > 0:
            return False, f"冷却中 ({self.cooldowns[slot_index]:.1f}秒)"
        
        slot = self.potions[slot_index]
        if not slot:
            return False, "槽位为空"
        
        potion, count = slot
        success, message = potion.use(character)
        
        if success:
            count -= 1
            if count <= 0:
                self.potions[slot_index] = None
            else:
                self.potions[slot_index] = (potion, count)
            
            self.cooldowns[slot_index] = potion.cooldown
        
        return success, message
    
    def update(self, delta_time: float):
        for i in range(self.slots):
            if self.cooldowns[i] > 0:
                self.cooldowns[i] = max(0, self.cooldowns[i] - delta_time)
    
    def get_slot(self, index: int) -> Optional[Tuple[Potion, int]]:
        if 0 <= index < self.slots:
            return self.potions[index]
        return None
    
    def get_cooldown(self, index: int) -> float:
        if 0 <= index < self.slots:
            return self.cooldowns[index]
        return 0.0
