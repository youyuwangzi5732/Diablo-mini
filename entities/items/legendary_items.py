"""
传奇装备定义 - 包含所有传奇装备的具体定义
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


@dataclass
class LegendaryPower:
    id: str
    name: str
    description: str
    effect_type: str
    effect_value: float
    effect_value_ancient: float = 0
    
    def get_value(self, is_ancient: bool = False) -> float:
        if is_ancient and self.effect_value_ancient > 0:
            return self.effect_value_ancient
        return self.effect_value


@dataclass
class LegendaryItem:
    id: str
    name: str
    item_type: str
    slot: str
    required_level: int
    description: str
    flavor_text: str = ""
    base_armor: int = 0
    base_damage_min: int = 0
    base_damage_max: int = 0
    primary_stats: Dict[str, float] = field(default_factory=dict)
    secondary_stats: Dict[str, float] = field(default_factory=dict)
    legendary_power: Optional[LegendaryPower] = None
    class_restriction: Optional[str] = None
    set_id: Optional[str] = None
    is_ancient: bool = False


LEGENDARY_ITEMS: Dict[str, LegendaryItem] = {}


def _create_barbarian_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_barb_helm_1",
            name="不朽之王的永恒统治",
            item_type="helm",
            slot="head",
            required_level=60,
            description="不朽之王套装头盔",
            flavor_text="不朽之王的头盔，承载着远古的力量。",
            base_armor=500,
            primary_stats={"strength": 650, "vitality": 550, "armor": 100},
            secondary_stats={"physical_resist": 100, "crowd_control_reduce": 20},
            set_id="immortal_king",
            class_restriction="barbarian"
        ),
        LegendaryItem(
            id="leg_barb_weapon_1",
            name="不朽之王的碎岩者",
            item_type="two_hand_mace",
            slot="main_hand",
            required_level=60,
            description="不朽之王套装武器",
            flavor_text="这把巨锤曾经粉碎过无数恶魔。",
            base_damage_min=1200,
            base_damage_max=1800,
            primary_stats={"strength": 800, "damage_percent": 25},
            secondary_stats={"attack_speed": 10, "crit_damage": 50},
            legendary_power=LegendaryPower(
                id="power_ww_damage",
                name="旋风斩伤害",
                description="旋风斩伤害提高",
                effect_type="skill_damage",
                effect_value=150,
                effect_value_ancient=200
            ),
            set_id="immortal_king",
            class_restriction="barbarian"
        ),
        LegendaryItem(
            id="leg_barb_chest_1",
            name="雷神的胸甲",
            item_type="chest_armor",
            slot="chest",
            required_level=50,
            description="传说中雷神穿过的胸甲",
            flavor_text="雷霆之力护佑着穿戴者。",
            base_armor=800,
            primary_stats={"strength": 500, "vitality": 500, "armor": 150},
            secondary_stats={"lightning_resist": 150, "thorns": 200},
            legendary_power=LegendaryPower(
                id="power_thunder",
                name="雷霆一击",
                description="攻击有几率释放闪电链",
                effect_type="on_hit_lightning",
                effect_value=30,
                effect_value_ancient=50
            ),
            class_restriction="barbarian"
        ),
        LegendaryItem(
            id="leg_barb_belt_1",
            name="不朽之王的铁拳腰带",
            item_type="belt",
            slot="waist",
            required_level=60,
            description="不朽之王套装腰带",
            flavor_text="力量之源。",
            base_armor=300,
            primary_stats={"strength": 600, "vitality": 400},
            secondary_stats={"life_percent": 10, "armor": 50},
            set_id="immortal_king",
            class_restriction="barbarian"
        ),
        LegendaryItem(
            id="leg_barb_gloves_1",
            name="不朽之王的铁拳",
            item_type="gloves",
            slot="hands",
            required_level=60,
            description="不朽之王套装手套",
            flavor_text="粉碎一切的力量。",
            base_armor=250,
            primary_stats={"strength": 550, "crit_chance": 8, "crit_damage": 40},
            secondary_stats={"attack_speed": 5},
            set_id="immortal_king",
            class_restriction="barbarian"
        ),
        LegendaryItem(
            id="leg_barb_boots_1",
            name="不朽之王的步伐",
            item_type="boots",
            slot="feet",
            required_level=60,
            description="不朽之王套装靴子",
            flavor_text="踏遍战场的足迹。",
            base_armor=280,
            primary_stats={"strength": 550, "vitality": 450, "movement_speed": 12},
            secondary_stats={"physical_resist": 80},
            set_id="immortal_king",
            class_restriction="barbarian"
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def _create_wizard_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_wiz_helm_1",
            name="塔拉夏的敏锐目光",
            item_type="helm",
            slot="head",
            required_level=60,
            description="塔拉夏套装头盔",
            flavor_text="大法师塔拉夏的智慧结晶。",
            base_armor=400,
            primary_stats={"intelligence": 650, "vitality": 500, "crit_chance": 6},
            secondary_stats={"arcane_resist": 100},
            set_id="tal_rasha",
            class_restriction="wizard"
        ),
        LegendaryItem(
            id="leg_wiz_weapon_1",
            name="塔拉夏的执政官法杖",
            item_type="staff",
            slot="main_hand",
            required_level=60,
            description="塔拉夏套装武器",
            flavor_text="蕴含着元素之力。",
            base_damage_min=900,
            base_damage_max=1400,
            primary_stats={"intelligence": 900, "spell_damage_percent": 20},
            secondary_stats={"cast_speed": 10, "mana_regen": 15},
            legendary_power=LegendaryPower(
                id="power_meteor",
                name="陨石伤害",
                description="陨石伤害提高",
                effect_type="skill_damage",
                effect_value=200,
                effect_value_ancient=300
            ),
            set_id="tal_rasha",
            class_restriction="wizard"
        ),
        LegendaryItem(
            id="leg_wiz_orb_1",
            name="无尽之球",
            item_type="orb",
            slot="off_hand",
            required_level=50,
            description="蕴含无限奥术能量的法球",
            flavor_text="凝视其中，你会看到无限可能。",
            primary_stats={"intelligence": 600, "spell_damage_percent": 15, "crit_chance": 8},
            secondary_stats={"arcane_power_regen": 10},
            legendary_power=LegendaryPower(
                id="power_magic_missile",
                name="魔法飞弹",
                description="魔法飞弹发射数量增加",
                effect_type="projectile_count",
                effect_value=2,
                effect_value_ancient=3
            ),
            class_restriction="wizard"
        ),
        LegendaryItem(
            id="leg_wiz_chest_1",
            name="塔拉夏的无情追猎",
            item_type="chest_armor",
            slot="chest",
            required_level=60,
            description="塔拉夏套装胸甲",
            flavor_text="元素守护。",
            base_armor=650,
            primary_stats={"intelligence": 600, "vitality": 550, "armor": 100},
            secondary_stats={"all_resist": 80},
            set_id="tal_rasha",
            class_restriction="wizard"
        ),
        LegendaryItem(
            id="leg_wiz_belt_1",
            name="塔拉夏的腰带",
            item_type="belt",
            slot="waist",
            required_level=60,
            description="塔拉夏套装腰带",
            flavor_text="元素协调。",
            base_armor=250,
            primary_stats={"intelligence": 550, "vitality": 450},
            secondary_stats={"mana_regen": 10},
            set_id="tal_rasha",
            class_restriction="wizard"
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def _create_demon_hunter_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_dh_helm_1",
            name="娜塔亚的杀戮之视",
            item_type="helm",
            slot="head",
            required_level=60,
            description="娜塔亚套装头盔",
            flavor_text="猎魔人的敏锐目光。",
            base_armor=420,
            primary_stats={"dexterity": 650, "vitality": 500, "crit_chance": 6},
            secondary_stats={"hatred_regen": 5},
            set_id="natalya",
            class_restriction="demon_hunter"
        ),
        LegendaryItem(
            id="leg_dh_weapon_1",
            name="娜塔亚的杀戮之刃",
            item_type="hand_crossbow",
            slot="main_hand",
            required_level=60,
            description="娜塔亚套装武器",
            flavor_text="暗影中的杀意。",
            base_damage_min=1000,
            base_damage_max=1500,
            primary_stats={"dexterity": 850, "crit_damage": 50},
            secondary_stats={"attack_speed": 15, "hatred_regen": 8},
            set_id="natalya",
            class_restriction="demon_hunter"
        ),
        LegendaryItem(
            id="leg_dh_bow_1",
            name="灾厄之弓",
            item_type="bow",
            slot="main_hand",
            required_level=50,
            description="传说中的灾厄之弓",
            flavor_text="每一支箭都带着毁灭。",
            base_damage_min=1100,
            base_damage_max=1650,
            primary_stats={"dexterity": 800, "crit_damage": 60},
            secondary_stats={"attack_speed": 10},
            legendary_power=LegendaryPower(
                id="power_multishot",
                name="多重射击",
                description="多重射击伤害提高",
                effect_type="skill_damage",
                effect_value=150,
                effect_value_ancient=200
            ),
            class_restriction="demon_hunter"
        ),
        LegendaryItem(
            id="leg_dh_chest_1",
            name="娜塔亚的暗影护甲",
            item_type="chest_armor",
            slot="chest",
            required_level=60,
            description="娜塔亚套装胸甲",
            flavor_text="暗影庇护。",
            base_armor=680,
            primary_stats={"dexterity": 600, "vitality": 550},
            secondary_stats={"dodge_chance": 8},
            set_id="natalya",
            class_restriction="demon_hunter"
        ),
        LegendaryItem(
            id="leg_dh_boots_1",
            name="娜塔亚的步伐",
            item_type="boots",
            slot="feet",
            required_level=60,
            description="娜塔亚套装靴子",
            flavor_text="如影随形。",
            base_armor=300,
            primary_stats={"dexterity": 550, "vitality": 450, "movement_speed": 12},
            secondary_stats={"discipline_regen": 2},
            set_id="natalya",
            class_restriction="demon_hunter"
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def _create_monk_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_monk_helm_1",
            name="孙吾空的王冠",
            item_type="helm",
            slot="head",
            required_level=60,
            description="孙吾空套装头盔",
            flavor_text="齐天大圣的力量。",
            base_armor=430,
            primary_stats={"dexterity": 650, "vitality": 500, "spirit_regen": 5},
            secondary_stats={"dodge_chance": 10},
            set_id="sunwuko",
            class_restriction="monk"
        ),
        LegendaryItem(
            id="leg_monk_weapon_1",
            name="孙吾空的金刚棒",
            item_type="daibo",
            slot="main_hand",
            required_level=60,
            description="孙吾空套装武器",
            flavor_text="定海神针。",
            base_damage_min=950,
            base_damage_max=1450,
            primary_stats={"dexterity": 850, "attack_speed": 10},
            secondary_stats={"spirit_regen": 8, "crit_damage": 50},
            set_id="sunwuko",
            class_restriction="monk"
        ),
        LegendaryItem(
            id="leg_monk_fist_1",
            name="神圣拳套",
            item_type="fist_weapon",
            slot="main_hand",
            required_level=50,
            description="神圣力量凝聚的拳套",
            flavor_text="以拳证道。",
            base_damage_min=700,
            base_damage_max=1100,
            primary_stats={"dexterity": 750, "attack_speed": 15, "crit_chance": 8},
            secondary_stats={"holy_damage_percent": 20},
            legendary_power=LegendaryPower(
                id="power_fist",
                name="雷光拳",
                description="雷光拳伤害提高",
                effect_type="skill_damage",
                effect_value=200,
                effect_value_ancient=300
            ),
            class_restriction="monk"
        ),
        LegendaryItem(
            id="leg_monk_chest_1",
            name="孙吾空的战甲",
            item_type="chest_armor",
            slot="chest",
            required_level=60,
            description="孙吾空套装胸甲",
            flavor_text="金刚不坏。",
            base_armor=700,
            primary_stats={"dexterity": 600, "vitality": 550},
            secondary_stats={"all_resist": 100},
            set_id="sunwuko",
            class_restriction="monk"
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def _create_necromancer_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_necro_helm_1",
            name="伊纳瑞斯的低语",
            item_type="helm",
            slot="head",
            required_level=60,
            description="伊纳瑞斯套装头盔",
            flavor_text="死亡的低语。",
            base_armor=410,
            primary_stats={"intelligence": 650, "vitality": 500, "essence_max": 50},
            secondary_stats={"minion_damage_percent": 20},
            set_id="inarius",
            class_restriction="necromancer"
        ),
        LegendaryItem(
            id="leg_necro_weapon_1",
            name="伊纳瑞斯的死亡之镰",
            item_type="scythe",
            slot="main_hand",
            required_level=60,
            description="伊纳瑞斯套装武器",
            flavor_text="收割灵魂。",
            base_damage_min=900,
            base_damage_max=1400,
            primary_stats={"intelligence": 850, "essence_regen": 5},
            secondary_stats={"bone_damage_percent": 25, "crit_damage": 50},
            set_id="inarius",
            class_restriction="necromancer"
        ),
        LegendaryItem(
            id="leg_necro_chest_1",
            name="伊纳瑞斯的骨甲",
            item_type="chest_armor",
            slot="chest",
            required_level=60,
            description="伊纳瑞斯套装胸甲",
            flavor_text="白骨守护。",
            base_armor=720,
            primary_stats={"intelligence": 600, "vitality": 550, "armor": 100},
            secondary_stats={"physical_resist": 100},
            set_id="inarius",
            class_restriction="necromancer"
        ),
        LegendaryItem(
            id="leg_necro_offhand_1",
            name="死者之书",
            item_type="off_hand",
            slot="off_hand",
            required_level=50,
            description="记载着亡灵法术的古老书籍",
            flavor_text="知识就是力量。",
            primary_stats={"intelligence": 600, "minion_damage_percent": 25, "essence_max": 30},
            secondary_stats={"minion_health_percent": 20},
            legendary_power=LegendaryPower(
                id="power_skeleton",
                name="骷髅召唤",
                description="骷髅数量增加",
                effect_type="minion_count",
                effect_value=2,
                effect_value_ancient=4
            ),
            class_restriction="necromancer"
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def _create_crusader_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_crus_helm_1",
            name="阿克汉的凝视",
            item_type="helm",
            slot="head",
            required_level=60,
            description="阿克汉套装头盔",
            flavor_text="圣光护佑。",
            base_armor=520,
            primary_stats={"strength": 650, "vitality": 500, "block_chance": 10},
            secondary_stats={"holy_damage_percent": 15},
            set_id="akkhan",
            class_restriction="crusader"
        ),
        LegendaryItem(
            id="leg_crus_weapon_1",
            name="阿克汉的审判之剑",
            item_type="two_hand_sword",
            slot="main_hand",
            required_level=60,
            description="阿克汉套装武器",
            flavor_text="神圣审判。",
            base_damage_min=1100,
            base_damage_max=1700,
            primary_stats={"strength": 900, "holy_damage_percent": 20},
            secondary_stats={"wrath_regen": 8, "crit_damage": 50},
            set_id="akkhan",
            class_restriction="crusader"
        ),
        LegendaryItem(
            id="leg_crus_shield_1",
            name="神圣之盾",
            item_type="shield",
            slot="off_hand",
            required_level=50,
            description="传说中的神圣之盾",
            flavor_text="坚不可摧。",
            base_armor=600,
            primary_stats={"strength": 500, "block_chance": 20, "armor": 150},
            secondary_stats={"thorns": 300},
            legendary_power=LegendaryPower(
                id="power_shield_bash",
                name="盾击",
                description="盾击伤害提高",
                effect_type="skill_damage",
                effect_value=200,
                effect_value_ancient=300
            ),
            class_restriction="crusader"
        ),
        LegendaryItem(
            id="leg_crus_chest_1",
            name="阿克汉的战铠",
            item_type="chest_armor",
            slot="chest",
            required_level=60,
            description="阿克汉套装胸甲",
            flavor_text="钢铁意志。",
            base_armor=850,
            primary_stats={"strength": 600, "vitality": 550, "armor": 150},
            secondary_stats={"all_resist": 80},
            set_id="akkhan",
            class_restriction="crusader"
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def _create_druid_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_druid_helm_1",
            name="祖尼玛萨的视野",
            item_type="helm",
            slot="head",
            required_level=60,
            description="祖尼玛萨套装头盔",
            flavor_text="自然之眼。",
            base_armor=400,
            primary_stats={"strength": 400, "intelligence": 400, "vitality": 500},
            secondary_stats={"summon_damage_percent": 20},
            set_id="zunimassa",
            class_restriction="druid"
        ),
        LegendaryItem(
            id="leg_druid_weapon_1",
            name="祖尼玛萨的图腾",
            item_type="staff",
            slot="main_hand",
            required_level=60,
            description="祖尼玛萨套装武器",
            flavor_text="自然之力。",
            base_damage_min=900,
            base_damage_max=1400,
            primary_stats={"intelligence": 700, "strength": 300, "nature_damage_percent": 25},
            secondary_stats={"summon_damage_percent": 15, "crit_damage": 50},
            set_id="zunimassa",
            class_restriction="druid"
        ),
        LegendaryItem(
            id="leg_druid_chest_1",
            name="祖尼玛萨的护甲",
            item_type="chest_armor",
            slot="chest",
            required_level=60,
            description="祖尼玛萨套装胸甲",
            flavor_text="野性守护。",
            base_armor=680,
            primary_stats={"vitality": 600, "intelligence": 400, "strength": 300},
            secondary_stats={"all_resist": 80},
            set_id="zunimassa",
            class_restriction="druid"
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def _create_assassin_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_asin_helm_1",
            name="暗影之冠",
            item_type="helm",
            slot="head",
            required_level=60,
            description="暗影套装头盔",
            flavor_text="暗影笼罩。",
            base_armor=420,
            primary_stats={"dexterity": 650, "vitality": 500, "crit_chance": 8},
            secondary_stats={"shadow_damage_percent": 15},
            set_id="shadow",
            class_restriction="assassin"
        ),
        LegendaryItem(
            id="leg_asin_claw_1",
            name="暗影之爪",
            item_type="claw",
            slot="main_hand",
            required_level=60,
            description="暗影套装武器",
            flavor_text="撕裂暗影。",
            base_damage_min=750,
            base_damage_max=1150,
            primary_stats={"dexterity": 800, "attack_speed": 15, "crit_damage": 60},
            secondary_stats={"shadow_damage_percent": 20},
            set_id="shadow",
            class_restriction="assassin"
        ),
        LegendaryItem(
            id="leg_asin_claw_2",
            name="暗影之刃",
            item_type="claw",
            slot="off_hand",
            required_level=60,
            description="暗影套装副手武器",
            flavor_text="双刃合璧。",
            base_damage_min=700,
            base_damage_max=1100,
            primary_stats={"dexterity": 750, "crit_chance": 10, "crit_damage": 40},
            secondary_stats={"attack_speed": 10},
            set_id="shadow",
            class_restriction="assassin"
        ),
        LegendaryItem(
            id="leg_asin_chest_1",
            name="暗影之甲",
            item_type="chest_armor",
            slot="chest",
            required_level=60,
            description="暗影套装胸甲",
            flavor_text="如影随形。",
            base_armor=680,
            primary_stats={"dexterity": 600, "vitality": 550, "dodge_chance": 10},
            secondary_stats={"all_resist": 70},
            set_id="shadow",
            class_restriction="assassin"
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def _create_generic_legendaries():
    legendaries = [
        LegendaryItem(
            id="leg_ring_1",
            name="团结之戒",
            item_type="ring",
            slot="ring_left",
            required_level=50,
            description="传说中的团结之戒",
            flavor_text="团结就是力量。",
            primary_stats={"all_attributes": 150, "crit_chance": 5, "crit_damage": 30},
            secondary_stats={"elite_damage_percent": 15},
            legendary_power=LegendaryPower(
                id="power_unity",
                name="团结",
                description="伤害分摊给队友",
                effect_type="damage_split",
                effect_value=50,
                effect_value_ancient=50
            )
        ),
        LegendaryItem(
            id="leg_ring_2",
            name="皇家华戒",
            item_type="ring",
            slot="ring_right",
            required_level=50,
            description="传说中的皇家华戒",
            flavor_text="皇室的荣耀。",
            primary_stats={"attack_speed": 8, "crit_chance": 6, "crit_damage": 35},
            secondary_stats={"life_percent": 10},
            legendary_power=LegendaryPower(
                id="power_rorg",
                name="套装加成",
                description="套装需求减少一件",
                effect_type="set_bonus",
                effect_value=1,
                effect_value_ancient=1
            )
        ),
        LegendaryItem(
            id="leg_amulet_1",
            name="地狱火项链",
            item_type="amulet",
            slot="neck",
            required_level=60,
            description="传说中的地狱火项链",
            flavor_text="地狱的火焰永不熄灭。",
            primary_stats={"all_attributes": 200, "crit_chance": 8, "crit_damage": 50},
            secondary_stats={"fire_damage_percent": 20},
            legendary_power=LegendaryPower(
                id="power_hellfire",
                name="地狱火",
                description="获得额外被动技能",
                effect_type="extra_passive",
                effect_value=1,
                effect_value_ancient=1
            )
        ),
        LegendaryItem(
            id="leg_amulet_2",
            name="旅者之誓",
            item_type="amulet",
            slot="neck",
            required_level=50,
            description="旅者套装项链",
            flavor_text="旅途的终点是家。",
            primary_stats={"dexterity": 600, "intelligence": 600, "strength": 600},
            secondary_stats={"damage_percent": 10}
        ),
    ]
    for item in legendaries:
        LEGENDARY_ITEMS[item.id] = item


def initialize_legendaries():
    _create_barbarian_legendaries()
    _create_wizard_legendaries()
    _create_demon_hunter_legendaries()
    _create_monk_legendaries()
    _create_necromancer_legendaries()
    _create_crusader_legendaries()
    _create_druid_legendaries()
    _create_assassin_legendaries()
    _create_generic_legendaries()


def get_legendary(item_id: str) -> Optional[LegendaryItem]:
    if not LEGENDARY_ITEMS:
        initialize_legendaries()
    return LEGENDARY_ITEMS.get(item_id)


def get_legendaries_for_class(class_id: str) -> List[LegendaryItem]:
    if not LEGENDARY_ITEMS:
        initialize_legendaries()
    return [item for item in LEGENDARY_ITEMS.values() 
            if item.class_restriction is None or item.class_restriction == class_id]


def get_legendaries_for_slot(slot: str) -> List[LegendaryItem]:
    if not LEGENDARY_ITEMS:
        initialize_legendaries()
    return [item for item in LEGENDARY_ITEMS.values() if item.slot == slot]


def get_all_legendaries() -> Dict[str, LegendaryItem]:
    if not LEGENDARY_ITEMS:
        initialize_legendaries()
    return LEGENDARY_ITEMS.copy()
