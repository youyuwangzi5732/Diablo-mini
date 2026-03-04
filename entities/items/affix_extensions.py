"""
词缀扩展 - 添加更多词缀类型
"""
from typing import Dict, List, Tuple
from dataclasses import dataclass
from random import random, randint, choice


@dataclass
class AffixDefinition:
    id: str
    name: str
    attribute: str
    min_value: float
    max_value: float
    is_percentage: bool = False
    required_level: int = 1
    weight: float = 1.0
    allowed_slots: List[str] = None


PREFIX_AFFIXES: List[AffixDefinition] = []
SUFFIX_AFFIXES: List[AffixDefinition] = []
LEGENDARY_AFFIXES: List[AffixDefinition] = []


def _create_prefix_affixes():
    PREFIX_AFFIXES.clear()
    PREFIX_AFFIXES.extend([
        AffixDefinition("str", "强壮的", "strength", 10, 50, required_level=1, weight=1.0),
        AffixDefinition("str_high", "巨力的", "strength", 50, 100, required_level=30, weight=0.5),
        AffixDefinition("dex", "敏捷的", "dexterity", 10, 50, required_level=1, weight=1.0),
        AffixDefinition("dex_high", "灵巧的", "dexterity", 50, 100, required_level=30, weight=0.5),
        AffixDefinition("int", "智慧的", "intelligence", 10, 50, required_level=1, weight=1.0),
        AffixDefinition("int_high", "睿智的", "intelligence", 50, 100, required_level=30, weight=0.5),
        AffixDefinition("vit", "活力的", "vitality", 10, 50, required_level=1, weight=1.0),
        AffixDefinition("vit_high", "健壮的", "vitality", 50, 100, required_level=30, weight=0.5),
        AffixDefinition("all_attr", "全能的", "all_attributes", 5, 25, required_level=20, weight=0.3),
        
        AffixDefinition("armor", "坚固的", "armor", 20, 100, required_level=1, weight=0.8),
        AffixDefinition("armor_high", "钢铁的", "armor", 100, 300, required_level=40, weight=0.4),
        AffixDefinition("max_health", "生命的", "max_health", 50, 200, required_level=1, weight=0.9),
        AffixDefinition("max_health_high", "不朽的", "max_health", 200, 500, required_level=40, weight=0.4),
        AffixDefinition("max_mana", "法力的", "max_mana", 30, 150, required_level=1, weight=0.8),
        
        AffixDefinition("attack_power", "锋利的", "attack_power", 10, 50, required_level=10, weight=0.7,
                        allowed_slots=["main_hand", "off_hand"]),
        AffixDefinition("spell_power", "魔力的", "spell_power", 10, 50, required_level=10, weight=0.7),
        
        AffixDefinition("fire_dmg", "火焰之", "fire_damage_percent", 3, 15, True, required_level=15, weight=0.6),
        AffixDefinition("cold_dmg", "冰冷之", "cold_damage_percent", 3, 15, True, required_level=15, weight=0.6),
        AffixDefinition("light_dmg", "闪电之", "lightning_damage_percent", 3, 15, True, required_level=15, weight=0.6),
        AffixDefinition("poison_dmg", "毒素之", "poison_damage_percent", 3, 15, True, required_level=15, weight=0.6),
        AffixDefinition("holy_dmg", "神圣之", "holy_damage_percent", 3, 15, True, required_level=20, weight=0.5),
        AffixDefinition("shadow_dmg", "暗影之", "shadow_damage_percent", 3, 15, True, required_level=20, weight=0.5),
        AffixDefinition("arcane_dmg", "奥术之", "arcane_damage_percent", 3, 15, True, required_level=20, weight=0.5),
        
        AffixDefinition("phys_dmg", "残暴之", "physical_damage_percent", 3, 15, True, required_level=15, weight=0.6),
        AffixDefinition("elite_dmg", "猎杀之", "elite_damage_percent", 3, 12, True, required_level=30, weight=0.4),
        AffixDefinition("skill_dmg", "技艺之", "skill_damage_percent", 2, 10, True, required_level=25, weight=0.5),

        AffixDefinition("assault_power", "征伐的", "attack_power", 35, 90, required_level=22, weight=0.65,
                        allowed_slots=["main_hand", "off_hand"]),
        AffixDefinition("assault_power_high", "战争领主的", "attack_power", 90, 180, required_level=48, weight=0.35,
                        allowed_slots=["main_hand", "off_hand"]),
        AffixDefinition("battle_armor", "堡垒的", "armor", 120, 260, required_level=26, weight=0.6,
                        allowed_slots=["head", "shoulders", "chest", "hands", "waist", "legs", "feet", "off_hand"]),
        AffixDefinition("battle_armor_high", "磐石的", "armor", 260, 520, required_level=52, weight=0.3,
                        allowed_slots=["head", "shoulders", "chest", "hands", "waist", "legs", "feet", "off_hand"]),
        AffixDefinition("blood_vitality", "鲜血的", "vitality", 25, 80, required_level=18, weight=0.7),
        AffixDefinition("blood_vitality_high", "不灭者的", "vitality", 80, 160, required_level=46, weight=0.3),
        AffixDefinition("mind_intelligence", "秘术的", "intelligence", 25, 80, required_level=18, weight=0.7),
        AffixDefinition("mind_intelligence_high", "大法师的", "intelligence", 80, 160, required_level=46, weight=0.3),
        AffixDefinition("agile_dexterity", "猎影的", "dexterity", 25, 80, required_level=18, weight=0.7),
        AffixDefinition("agile_dexterity_high", "天击者的", "dexterity", 80, 160, required_level=46, weight=0.3),
        AffixDefinition("brutal_strength", "裂山的", "strength", 25, 80, required_level=18, weight=0.7),
        AffixDefinition("brutal_strength_high", "泰坦的", "strength", 80, 160, required_level=46, weight=0.3),
        AffixDefinition("swift_attack", "疾袭的", "attack_speed", 3, 10, True, required_level=20, weight=0.55,
                        allowed_slots=["main_hand", "off_hand", "ring_left", "ring_right", "neck"]),
        AffixDefinition("arcane_cast", "咏唱的", "cast_speed", 3, 10, True, required_level=20, weight=0.55,
                        allowed_slots=["main_hand", "off_hand", "ring_left", "ring_right", "neck"]),
        AffixDefinition("traveler_move", "游侠的", "movement_speed", 4, 14, True, required_level=16, weight=0.5,
                        allowed_slots=["feet", "legs", "waist"]),
        AffixDefinition("hunter_crit", "精准猎手的", "crit_chance", 2, 7, True, required_level=24, weight=0.45,
                        allowed_slots=["main_hand", "off_hand", "ring_left", "ring_right", "neck", "hands"]),
        AffixDefinition("execution_crit", "终结者的", "crit_damage", 18, 65, True, required_level=28, weight=0.4,
                        allowed_slots=["main_hand", "off_hand", "ring_left", "ring_right", "neck", "hands"]),
        AffixDefinition("ward_fire_res", "炽焰守护的", "fire_resist", 10, 35, required_level=20, weight=0.55),
        AffixDefinition("ward_cold_res", "寒霜守护的", "cold_resist", 10, 35, required_level=20, weight=0.55),
        AffixDefinition("ward_light_res", "雷霆守护的", "lightning_resist", 10, 35, required_level=20, weight=0.55),
        AffixDefinition("ward_poison_res", "瘴气守护的", "poison_resist", 10, 35, required_level=20, weight=0.55),
    ])


def _create_suffix_affixes():
    SUFFIX_AFFIXES.clear()
    SUFFIX_AFFIXES.extend([
        AffixDefinition("crit_chance", "暴击", "crit_chance", 1, 8, True, required_level=10, weight=0.7),
        AffixDefinition("crit_chance_high", "致命暴击", "crit_chance", 5, 12, True, required_level=40, weight=0.3),
        AffixDefinition("crit_damage", "暴伤", "crit_damage", 10, 50, True, required_level=10, weight=0.7),
        AffixDefinition("crit_damage_high", "毁灭暴伤", "crit_damage", 40, 100, True, required_level=40, weight=0.3),
        
        AffixDefinition("atk_speed", "急速", "attack_speed", 2, 8, True, required_level=15, weight=0.6),
        AffixDefinition("cast_speed", "施法", "cast_speed", 2, 8, True, required_level=15, weight=0.6),
        AffixDefinition("move_speed", "疾风", "movement_speed", 3, 12, True, required_level=10, weight=0.5),
        
        AffixDefinition("life_steal", "吸血", "life_steal", 1, 5, True, required_level=25, weight=0.4),
        AffixDefinition("health_regen", "回复", "health_regen", 5, 30, required_level=10, weight=0.6),
        AffixDefinition("mana_regen", "法力回复", "mana_regen", 3, 15, required_level=10, weight=0.6),
        
        AffixDefinition("fire_res", "火焰抗性", "fire_resist", 5, 25, required_level=1, weight=0.7),
        AffixDefinition("cold_res", "冰冷抗性", "cold_resist", 5, 25, required_level=1, weight=0.7),
        AffixDefinition("light_res", "闪电抗性", "lightning_resist", 5, 25, required_level=1, weight=0.7),
        AffixDefinition("poison_res", "毒素抗性", "poison_resist", 5, 25, required_level=1, weight=0.7),
        AffixDefinition("all_res", "全抗性", "all_resist", 3, 15, required_level=30, weight=0.3),
        
        AffixDefinition("magic_find", "寻宝", "magic_find", 5, 25, True, required_level=20, weight=0.5),
        AffixDefinition("gold_find", "财富", "gold_find", 10, 40, True, required_level=15, weight=0.6),
        
        AffixDefinition("dodge", "闪避", "dodge_chance", 1, 6, True, required_level=20, weight=0.5),
        AffixDefinition("block", "格挡", "block_chance", 2, 10, True, required_level=15, weight=0.5,
                        allowed_slots=["off_hand", "head", "chest", "shoulders", "hands", "waist", "legs", "feet"]),
        AffixDefinition("thorns", "反伤", "thorns", 20, 100, required_level=20, weight=0.5),
        
        AffixDefinition("life_on_hit", "击中回复", "life_on_hit", 200, 1000, required_level=25, weight=0.4),
        AffixDefinition("resource_cost", "资源消耗降低", "resource_cost_reduce", 2, 8, True, required_level=30, weight=0.4),
        AffixDefinition("cooldown", "冷却缩减", "cooldown_reduce", 2, 10, True, required_level=25, weight=0.4),
        
        AffixDefinition("damage_reduce", "伤害减免", "damage_reduce", 2, 8, True, required_level=35, weight=0.3),
        AffixDefinition("elite_damage_reduce", "精英伤害减免", "elite_damage_reduce", 2, 10, True, required_level=40, weight=0.3),

        AffixDefinition("bastion_block", "壁垒", "block_chance", 6, 16, True, required_level=24, weight=0.45,
                        allowed_slots=["off_hand", "head", "chest", "shoulders"]),
        AffixDefinition("thorn_wall", "荆棘壁垒", "thorns", 90, 260, required_level=26, weight=0.45,
                        allowed_slots=["chest", "shoulders", "hands", "waist", "legs"]),
        AffixDefinition("plunderer_gold", "掠夺", "gold_find", 18, 55, True, required_level=18, weight=0.5),
        AffixDefinition("scholar_magic", "学识", "magic_find", 12, 40, True, required_level=18, weight=0.5),
        AffixDefinition("vampiric", "吸魂", "life_steal", 2, 8, True, required_level=32, weight=0.35,
                        allowed_slots=["main_hand", "off_hand", "ring_left", "ring_right", "neck"]),
        AffixDefinition("robust_hp", "磅礴生命", "max_health", 120, 380, required_level=22, weight=0.55),
        AffixDefinition("robust_hp_high", "永恒生命", "max_health", 380, 760, required_level=52, weight=0.25),
        AffixDefinition("deep_mana", "深邃法力", "max_mana", 80, 280, required_level=22, weight=0.55),
        AffixDefinition("deep_mana_high", "无尽法潮", "max_mana", 280, 620, required_level=52, weight=0.25),
        AffixDefinition("fleet_dodge", "幻步", "dodge_chance", 2, 9, True, required_level=24, weight=0.45,
                        allowed_slots=["head", "shoulders", "hands", "feet", "ring_left", "ring_right"]),
        AffixDefinition("combat_haste", "战斗狂热", "attack_speed", 2, 7, True, required_level=20, weight=0.5,
                        allowed_slots=["main_hand", "off_hand", "hands", "ring_left", "ring_right", "neck"]),
        AffixDefinition("ritual_focus", "仪式专注", "cast_speed", 2, 7, True, required_level=20, weight=0.5,
                        allowed_slots=["main_hand", "off_hand", "head", "ring_left", "ring_right", "neck"]),
        AffixDefinition("surge_regen", "生命潮汐", "health_regen", 12, 45, required_level=20, weight=0.55),
        AffixDefinition("aether_regen", "法力潮汐", "mana_regen", 8, 28, required_level=20, weight=0.55),
    ])


def _create_legendary_affixes():
    LEGENDARY_AFFIXES.clear()
    LEGENDARY_AFFIXES.extend([
        AffixDefinition("leg_fire_skill", "火焰技能伤害", "fire_skill_damage", 10, 30, True, required_level=50, weight=0.2),
        AffixDefinition("leg_cold_skill", "冰冷技能伤害", "cold_skill_damage", 10, 30, True, required_level=50, weight=0.2),
        AffixDefinition("leg_light_skill", "闪电技能伤害", "lightning_skill_damage", 10, 30, True, required_level=50, weight=0.2),
        AffixDefinition("leg_poison_skill", "毒素技能伤害", "poison_skill_damage", 10, 30, True, required_level=50, weight=0.2),
        
        AffixDefinition("leg_barb_skill", "野蛮人技能伤害", "barbarian_skill_damage", 8, 25, True, required_level=50, weight=0.15),
        AffixDefinition("leg_wiz_skill", "魔法师技能伤害", "wizard_skill_damage", 8, 25, True, required_level=50, weight=0.15),
        AffixDefinition("leg_dh_skill", "猎魔人技能伤害", "demon_hunter_skill_damage", 8, 25, True, required_level=50, weight=0.15),
        AffixDefinition("leg_monk_skill", "武僧技能伤害", "monk_skill_damage", 8, 25, True, required_level=50, weight=0.15),
        AffixDefinition("leg_necro_skill", "死灵法师技能伤害", "necromancer_skill_damage", 8, 25, True, required_level=50, weight=0.15),
        AffixDefinition("leg_crus_skill", "圣教军技能伤害", "crusader_skill_damage", 8, 25, True, required_level=50, weight=0.15),
        AffixDefinition("leg_druid_skill", "德鲁伊技能伤害", "druid_skill_damage", 8, 25, True, required_level=50, weight=0.15),
        AffixDefinition("leg_asin_skill", "刺客技能伤害", "assassin_skill_damage", 8, 25, True, required_level=50, weight=0.15),
        
        AffixDefinition("leg_skill_level", "技能等级", "skill_level_all", 1, 3, required_level=60, weight=0.1),
        AffixDefinition("leg_passive_skill", "被动技能", "extra_passive", 1, 1, required_level=60, weight=0.05),
        
        AffixDefinition("leg_set_bonus", "套装需求减少", "set_requirement_reduce", 1, 1, required_level=50, weight=0.1),
        AffixDefinition("leg_damage_split", "伤害分摊", "damage_split", 25, 50, True, required_level=50, weight=0.1),
        
        AffixDefinition("leg_minion_dmg", "召唤物伤害", "minion_damage_percent", 20, 50, True, required_level=40, weight=0.2),
        AffixDefinition("leg_minion_health", "召唤物生命", "minion_health_percent", 20, 50, True, required_level=40, weight=0.2),
        
        AffixDefinition("leg_ww_dmg", "旋风斩伤害", "whirlwind_damage", 50, 150, True, required_level=50, weight=0.15),
        AffixDefinition("leg_meteor_dmg", "陨石伤害", "meteor_damage", 50, 150, True, required_level=50, weight=0.15),
        AffixDefinition("leg_multishot_dmg", "多重射击伤害", "multishot_damage", 50, 150, True, required_level=50, weight=0.15),
        AffixDefinition("leg_skeleton_dmg", "骷髅伤害", "skeleton_damage", 50, 150, True, required_level=50, weight=0.15),
        AffixDefinition("leg_shield_bash_dmg", "盾击伤害", "shield_bash_damage", 50, 150, True, required_level=50, weight=0.15),
        AffixDefinition("leg_titan_str", "泰坦之力", "strength", 120, 280, required_level=58, weight=0.12),
        AffixDefinition("leg_astral_int", "星穹奥术", "intelligence", 120, 280, required_level=58, weight=0.12),
        AffixDefinition("leg_hunter_dex", "猎天之速", "dexterity", 120, 280, required_level=58, weight=0.12),
        AffixDefinition("leg_vital_heart", "永生之心", "vitality", 120, 280, required_level=58, weight=0.12),
        AffixDefinition("leg_bulwark", "神佑壁垒", "armor", 400, 900, required_level=60, weight=0.1),
        AffixDefinition("leg_predator", "掠食者印记", "crit_chance", 6, 14, True, required_level=60, weight=0.1),
        AffixDefinition("leg_ruin", "毁灭回响", "crit_damage", 60, 140, True, required_level=60, weight=0.1),
    ])


def initialize_affix_extensions():
    _create_prefix_affixes()
    _create_suffix_affixes()
    _create_legendary_affixes()


def get_random_prefix(item_level: int, slot: str = None) -> Tuple[AffixDefinition, float]:
    if not PREFIX_AFFIXES:
        initialize_affix_extensions()
    
    available = [a for a in PREFIX_AFFIXES 
                 if a.required_level <= item_level and
                 (a.allowed_slots is None or slot in a.allowed_slots)]
    
    if not available:
        return None, 0
    
    total_weight = sum(a.weight for a in available)
    roll = random() * total_weight
    
    cumulative = 0
    for affix in available:
        cumulative += affix.weight
        if roll <= cumulative:
            value = affix.min_value + random() * (affix.max_value - affix.min_value)
            return affix, value
    
    return available[0], available[0].min_value


def get_random_suffix(item_level: int, slot: str = None) -> Tuple[AffixDefinition, float]:
    if not SUFFIX_AFFIXES:
        initialize_affix_extensions()
    
    available = [a for a in SUFFIX_AFFIXES 
                 if a.required_level <= item_level and
                 (a.allowed_slots is None or slot in a.allowed_slots)]
    
    if not available:
        return None, 0
    
    total_weight = sum(a.weight for a in available)
    roll = random() * total_weight
    
    cumulative = 0
    for affix in available:
        cumulative += affix.weight
        if roll <= cumulative:
            value = affix.min_value + random() * (affix.max_value - affix.min_value)
            return affix, value
    
    return available[0], available[0].min_value


def get_random_legendary_affix(item_level: int) -> Tuple[AffixDefinition, float]:
    if not LEGENDARY_AFFIXES:
        initialize_affix_extensions()
    
    available = [a for a in LEGENDARY_AFFIXES if a.required_level <= item_level]
    
    if not available:
        return None, 0
    
    total_weight = sum(a.weight for a in available)
    roll = random() * total_weight
    
    cumulative = 0
    for affix in available:
        cumulative += affix.weight
        if roll <= cumulative:
            value = affix.min_value + random() * (affix.max_value - affix.min_value)
            return affix, value
    
    return available[0], available[0].min_value


def get_all_prefixes() -> List[AffixDefinition]:
    if not PREFIX_AFFIXES:
        initialize_affix_extensions()
    return PREFIX_AFFIXES.copy()


def get_all_suffixes() -> List[AffixDefinition]:
    if not SUFFIX_AFFIXES:
        initialize_affix_extensions()
    return SUFFIX_AFFIXES.copy()


def get_all_legendary_affixes() -> List[AffixDefinition]:
    if not LEGENDARY_AFFIXES:
        initialize_affix_extensions()
    return LEGENDARY_AFFIXES.copy()
