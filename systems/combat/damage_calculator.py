"""
伤害计算系统 - 商业化级别的统一伤害公式
支持多种伤害类型、快照机制、伤害修正
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import random
import math


class DamageType(Enum):
    PHYSICAL = "physical"
    FIRE = "fire"
    COLD = "cold"
    LIGHTNING = "lightning"
    POISON = "poison"
    HOLY = "holy"
    SHADOW = "shadow"
    ARCANE = "arcane"
    TRUE = "true"  # 真实伤害，无视抗性


class DamageSource(Enum):
    ATTACK = "attack"
    SKILL = "skill"
    DOT = "dot"  # 持续伤害
    REFLECT = "reflect"  # 反伤
    THORNS = "thorns"  # 荆棘
    BLEED = "bleed"  # 流血


@dataclass
class DamageSnapshot:
    """伤害快照 - 记录造成伤害时的属性状态"""
    attacker_id: str
    attacker_level: int
    
    # 基础属性
    strength: float = 0
    dexterity: float = 0
    intelligence: float = 0
    vitality: float = 0
    
    # 攻击属性
    base_damage_min: float = 0
    base_damage_max: float = 0
    attack_speed: float = 1.0
    critical_chance: float = 0.05
    critical_damage: float = 1.5
    
    # 伤害加成
    damage_percent: float = 0
    skill_damage_percent: float = 0
    elemental_damage_percent: float = 0
    
    # 特定伤害类型加成
    damage_type_bonuses: Dict[DamageType, float] = field(default_factory=dict)
    
    # 速度加成
    attack_speed_percent: float = 0
    cast_speed_percent: float = 0
    
    # 其他修正
    armor_penetration: float = 0
    resistance_penetration: float = 0
    
    # 时间戳
    timestamp: float = 0


@dataclass
class DamageResult:
    """伤害结果"""
    final_damage: float
    damage_type: DamageType
    source_type: DamageSource
    
    is_critical: bool = False
    is_blocked: bool = False
    is_dodged: bool = False
    is_missed: bool = False
    
    original_damage: float = 0
    damage_reduction: float = 0
    armor_mitigation: float = 0
    resistance_mitigation: float = 0
    
    overkill: float = 0
    
    # 分解伤害
    physical_damage: float = 0
    elemental_damage: Dict[DamageType, float] = field(default_factory=dict)
    
    def get_total_elemental_damage(self) -> float:
        return sum(self.elemental_damage.values())


class DamageCalculator:
    """统一伤害计算器"""
    
    # 全局伤害修正系数
    GLOBAL_DAMAGE_MULTIPLIER = 1.0
    
    # 护甲减伤公式参数
    ARMOR_COEFFICIENT = 1000  # 护甲系数
    
    # 等级差修正
    LEVEL_DIFF_PENALTY = 0.1  # 每级差距的惩罚
    
    @staticmethod
    def calculate_damage(
        snapshot: DamageSnapshot,
        target: Any,
        damage_type: DamageType = DamageType.PHYSICAL,
        source_type: DamageSource = DamageSource.ATTACK,
        skill_multiplier: float = 1.0,
        additional_bonus: float = 0
    ) -> DamageResult:
        """计算伤害"""
        result = DamageResult(
            final_damage=0,
            damage_type=damage_type,
            source_type=source_type
        )
        
        # 1. 计算基础伤害
        base_damage = random.uniform(snapshot.base_damage_min, snapshot.base_damage_max)
        result.original_damage = base_damage
        
        # 2. 应用属性加成
        attribute_bonus = DamageCalculator._calculate_attribute_bonus(snapshot, damage_type)
        base_damage *= attribute_bonus
        
        # 3. 应用伤害百分比加成
        base_damage *= (1 + snapshot.damage_percent / 100)
        
        # 4. 应用技能伤害加成
        if source_type == DamageSource.SKILL:
            base_damage *= (1 + snapshot.skill_damage_percent / 100)
        
        # 5. 应用元素伤害加成
        if damage_type != DamageType.PHYSICAL and damage_type != DamageType.TRUE:
            base_damage *= (1 + snapshot.elemental_damage_percent / 100)
            type_bonus = snapshot.damage_type_bonuses.get(damage_type, 0)
            base_damage *= (1 + type_bonus / 100)
        
        # 6. 应用技能倍率
        base_damage *= skill_multiplier
        
        # 7. 应用额外加成
        base_damage *= (1 + additional_bonus / 100)
        
        # 8. 暴击判定
        if random.random() < snapshot.critical_chance:
            result.is_critical = True
            base_damage *= snapshot.critical_damage
        
        # 9. 目标防御计算
        if target is not None:
            # 闪避判定
            dodge_chance = getattr(target, 'dodge_chance', 0)
            if random.random() < dodge_chance / 100:
                result.is_dodged = True
                result.final_damage = 0
                return result
            
            # 格挡判定
            block_chance = getattr(target, 'block_chance', 0)
            if random.random() < block_chance / 100:
                result.is_blocked = True
                base_damage *= 0.5  # 格挡减伤50%
            
            # 护甲减伤（仅物理伤害）
            if damage_type == DamageType.PHYSICAL:
                armor = getattr(target, 'armor', 0)
                armor_percent = getattr(target, 'armor_percent', 0)
                total_armor = armor * (1 + armor_percent / 100)
                
                # 护甲穿透
                effective_armor = max(0, total_armor - snapshot.armor_penetration)
                
                armor_reduction = DamageCalculator._calculate_armor_reduction(
                    effective_armor, snapshot.attacker_level
                )
                result.armor_mitigation = armor_reduction
                base_damage *= (1 - armor_reduction)
            
            # 抗性减伤（元素伤害）
            elif damage_type != DamageType.TRUE:
                resistance_attr = f"{damage_type.value}_resistance"
                resistance = getattr(target, resistance_attr, 0)
                all_resistance = getattr(target, 'all_resistance', 0)
                total_resistance = resistance + all_resistance
                
                # 抗性穿透
                effective_resistance = max(0, total_resistance - snapshot.resistance_penetration)
                
                resistance_reduction = DamageCalculator._calculate_resistance_reduction(effective_resistance)
                result.resistance_mitigation = resistance_reduction
                base_damage *= (1 - resistance_reduction)
            
            # 全局伤害减免
            damage_reduction = getattr(target, 'damage_reduction', 0)
            if damage_reduction > 0:
                result.damage_reduction = damage_reduction / 100
                base_damage *= (1 - damage_reduction / 100)
        
        # 10. 应用全局修正
        base_damage *= DamageCalculator.GLOBAL_DAMAGE_MULTIPLIER
        
        # 11. 随机波动 (±5%)
        base_damage *= random.uniform(0.95, 1.05)
        
        # 12. 最终伤害
        result.final_damage = max(1, int(base_damage))
        
        # 记录伤害类型分解
        if damage_type == DamageType.PHYSICAL:
            result.physical_damage = result.final_damage
        else:
            result.elemental_damage[damage_type] = result.final_damage
        
        return result
    
    @staticmethod
    def _calculate_attribute_bonus(snapshot: DamageSnapshot, damage_type: DamageType) -> float:
        """计算属性加成"""
        # 力量增加物理伤害
        # 敏捷增加暴击和闪避
        # 智力增加元素伤害
        
        bonus = 1.0
        
        if damage_type == DamageType.PHYSICAL:
            # 力量: 每1点增加0.1%物理伤害
            bonus += snapshot.strength * 0.001
        elif damage_type in [DamageType.FIRE, DamageType.COLD, DamageType.LIGHTNING, 
                            DamageType.POISON, DamageType.ARCANE]:
            # 智力: 每1点增加0.1%元素伤害
            bonus += snapshot.intelligence * 0.001
        elif damage_type == DamageType.HOLY or damage_type == DamageType.SHADOW:
            # 智力和力量都有效
            bonus += (snapshot.intelligence + snapshot.strength) * 0.0005
        
        return bonus
    
    @staticmethod
    def _calculate_armor_reduction(armor: float, attacker_level: int) -> float:
        """计算护甲减伤"""
        # 公式: 减伤% = 护甲 / (护甲 + 护甲系数 * 等级)
        if armor <= 0:
            return 0
        
        reduction = armor / (armor + DamageCalculator.ARMOR_COEFFICIENT * attacker_level / 70)
        
        # 减伤上限75%
        return min(0.75, reduction)
    
    @staticmethod
    def _calculate_resistance_reduction(resistance: float) -> float:
        """计算抗性减伤"""
        # 公式: 减伤% = 抗性 / (抗性 + 100)
        if resistance <= 0:
            return 0
        
        reduction = resistance / (resistance + 100)
        
        # 抗性上限75%
        return min(0.75, reduction)
    
    @staticmethod
    def create_snapshot_from_character(character: Any) -> DamageSnapshot:
        """从角色创建伤害快照"""
        attributes = getattr(character, 'attributes', None)
        
        snapshot = DamageSnapshot(
            attacker_id=getattr(character, 'id', ''),
            attacker_level=getattr(character, 'level', 1)
        )
        
        if attributes:
            from entities.character.attributes import AttributeType
            
            snapshot.strength = attributes.get_total(AttributeType.STRENGTH)
            snapshot.dexterity = attributes.get_total(AttributeType.DEXTERITY)
            snapshot.intelligence = attributes.get_total(AttributeType.INTELLIGENCE)
            snapshot.vitality = attributes.get_total(AttributeType.VITALITY)
            
            snapshot.critical_chance = attributes.get_total(AttributeType.CRITICAL_CHANCE)
            snapshot.critical_damage = attributes.get_total(AttributeType.CRITICAL_DAMAGE) / 100 + 0.5
        
        # 武器伤害
        equipment = getattr(character, 'equipment', None)
        if equipment:
            main_hand = getattr(equipment, 'main_hand', None)
            if main_hand:
                snapshot.base_damage_min = getattr(main_hand, 'damage_min', 1)
                snapshot.base_damage_max = getattr(main_hand, 'damage_max', 10)
                snapshot.attack_speed = getattr(main_hand, 'attack_speed', 1.0)
        
        # 伤害加成
        snapshot.damage_percent = getattr(character, 'damage_percent', 0)
        snapshot.skill_damage_percent = getattr(character, 'skill_damage_percent', 0)
        snapshot.elemental_damage_percent = getattr(character, 'elemental_damage_percent', 0)
        
        # 穿透
        snapshot.armor_penetration = getattr(character, 'armor_penetration', 0)
        snapshot.resistance_penetration = getattr(character, 'resistance_penetration', 0)
        
        import time
        snapshot.timestamp = time.time()
        
        return snapshot
    
    @staticmethod
    def calculate_dps(snapshot: DamageSnapshot) -> float:
        """计算DPS"""
        avg_damage = (snapshot.base_damage_min + snapshot.base_damage_max) / 2
        
        # 属性加成
        avg_damage *= DamageCalculator._calculate_attribute_bonus(snapshot, DamageType.PHYSICAL)
        
        # 伤害加成
        avg_damage *= (1 + snapshot.damage_percent / 100)
        
        # 暴击期望
        crit_multiplier = 1 + snapshot.critical_chance * (snapshot.critical_damage - 1)
        avg_damage *= crit_multiplier
        
        # 攻击速度
        effective_speed = snapshot.attack_speed * (1 + snapshot.attack_speed_percent / 100)
        
        return avg_damage * effective_speed


class DamageEvent:
    """伤害事件"""
    
    def __init__(self, attacker: Any, target: Any, result: DamageResult):
        self.attacker = attacker
        self.target = target
        self.result = result
        self.timestamp = 0
    
    def get_total_damage(self) -> float:
        return self.result.final_damage
    
    def is_lethal(self) -> bool:
        if self.target is None:
            return False
        current_health = getattr(self.target, 'current_health', 0)
        return self.result.final_damage >= current_health


class DamageEventManager:
    """伤害事件管理器"""
    
    def __init__(self):
        self._events: List[DamageEvent] = []
        self._max_events = 1000
        self._damage_callbacks: List[Callable] = []
    
    def record_damage(self, event: DamageEvent):
        """记录伤害事件"""
        import time
        event.timestamp = time.time()
        
        self._events.append(event)
        
        # 保持事件数量限制
        if len(self._events) > self._max_events:
            self._events.pop(0)
        
        # 触发回调
        for callback in self._damage_callbacks:
            try:
                callback(event)
            except Exception as e:
                print(f"Damage callback error: {e}")
    
    def add_callback(self, callback: Callable):
        """添加伤害回调"""
        self._damage_callbacks.append(callback)
    
    def get_recent_events(self, count: int = 10) -> List[DamageEvent]:
        """获取最近的伤害事件"""
        return self._events[-count:]
    
    def get_total_damage_by_attacker(self, attacker_id: str) -> float:
        """获取指定攻击者的总伤害"""
        return sum(
            e.result.final_damage 
            for e in self._events 
            if e.attacker and getattr(e.attacker, 'id', None) == attacker_id
        )
    
    def get_damage_breakdown(self, attacker_id: str) -> Dict[DamageType, float]:
        """获取伤害类型分解"""
        breakdown = {}
        
        for event in self._events:
            if not event.attacker or getattr(event.attacker, 'id', None) != attacker_id:
                continue
            
            damage_type = event.result.damage_type
            breakdown[damage_type] = breakdown.get(damage_type, 0) + event.result.final_damage
        
        return breakdown


# 全局伤害事件管理器
_damage_event_manager: Optional[DamageEventManager] = None


def get_damage_event_manager() -> DamageEventManager:
    """获取伤害事件管理器"""
    global _damage_event_manager
    if _damage_event_manager is None:
        _damage_event_manager = DamageEventManager()
    return _damage_event_manager
