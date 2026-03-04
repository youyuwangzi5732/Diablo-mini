"""
怪物扩展 - 为每个区域添加专属怪物
"""
from typing import Dict, List
from dataclasses import dataclass
from systems.combat.monster import MonsterStats, MonsterType


@dataclass
class MonsterTemplate:
    id: str
    name: str
    base_stats: MonsterStats
    monster_type: MonsterType = MonsterType.NORMAL
    regions: List[str] = None
    special_abilities: List[str] = None
    description: str = ""


def create_monster_templates() -> Dict[str, Dict]:
    templates = {}
    
    templates.update(_create_forest_monsters())
    templates.update(_create_cathedral_monsters())
    templates.update(_create_desert_monsters())
    templates.update(_create_snow_monsters())
    templates.update(_create_hell_monsters())
    templates.update(_create_boss_monsters())
    
    return templates


def _create_forest_monsters() -> Dict[str, Dict]:
    return {
        "forest_zombie": {
            "name": "腐烂僵尸",
            "base_stats": MonsterStats(
                health=60, damage_min=6, damage_max=12, armor=5,
                movement_speed=0.7, experience=6, gold_min=2, gold_max=8
            ),
            "regions": ["weald"],
            "description": "在腐化林地游荡的不死者"
        },
        "forest_spider": {
            "name": "剧毒蜘蛛",
            "base_stats": MonsterStats(
                health=40, damage_min=8, damage_max=15, armor=2,
                movement_speed=1.4, poison_resist=50,
                experience=8, gold_min=3, gold_max=10
            ),
            "regions": ["weald"],
            "special_abilities": ["poison_bite"],
            "description": "潜伏在树林中的剧毒生物"
        },
        "forest_wolf": {
            "name": "狂暴狼",
            "base_stats": MonsterStats(
                health=55, damage_min=10, damage_max=18, armor=3,
                movement_speed=1.5, experience=10, gold_min=5, gold_max=15
            ),
            "regions": ["weald"],
            "special_abilities": ["pack_attack"],
            "description": "被黑暗力量侵蚀的狼群"
        },
        "forest_ent": {
            "name": "腐化树人",
            "base_stats": MonsterStats(
                health=120, damage_min=15, damage_max=25, armor=20,
                movement_speed=0.5, poison_resist=80,
                experience=20, gold_min=10, gold_max=30
            ),
            "regions": ["weald"],
            "monster_type": MonsterType.CHAMPION,
            "special_abilities": ["root_attack", "poison_cloud"],
            "description": "古老的守护者被腐化了"
        },
        "forest_witch": {
            "name": "森林女巫",
            "base_stats": MonsterStats(
                health=80, damage_min=12, damage_max=20, armor=5,
                movement_speed=0.9, attack_range=8,
                experience=15, gold_min=8, gold_max=25
            ),
            "regions": ["weald"],
            "special_abilities": ["curse", "summon_vines"],
            "description": "使用黑暗魔法的女巫"
        },
    }


def _create_cathedral_monsters() -> Dict[str, Dict]:
    return {
        "cathedral_skeleton": {
            "name": "教堂骷髅",
            "base_stats": MonsterStats(
                health=50, damage_min=10, damage_max=18, armor=5,
                movement_speed=1.0, experience=8, gold_min=3, gold_max=12
            ),
            "regions": ["cathedral"],
            "description": "在大教堂中徘徊的骷髅战士"
        },
        "cathedral_archer": {
            "name": "骷髅弓箭手",
            "base_stats": MonsterStats(
                health=40, damage_min=12, damage_max=22, armor=3,
                movement_speed=0.9, attack_range=12,
                experience=10, gold_min=5, gold_max=15
            ),
            "regions": ["cathedral"],
            "special_abilities": ["multishot"],
            "description": "远古的弓箭手亡灵"
        },
        "cathedral_ghost": {
            "name": "怨灵",
            "base_stats": MonsterStats(
                health=70, damage_min=10, damage_max=18, armor=0,
                movement_speed=1.3, cold_resist=100,
                experience=12, gold_min=6, gold_max=18
            ),
            "regions": ["cathedral"],
            "special_abilities": ["phase_through", "life_drain"],
            "description": "无法安息的灵魂"
        },
        "cathedral_knight": {
            "name": "堕落骑士",
            "base_stats": MonsterStats(
                health=150, damage_min=20, damage_max=35, armor=25,
                movement_speed=0.8, experience=30, gold_min=15, gold_max=40
            ),
            "regions": ["cathedral"],
            "monster_type": MonsterType.CHAMPION,
            "special_abilities": ["shield_bash", "charge"],
            "description": "曾经神圣的骑士堕落了"
        },
        "cathedral_priest": {
            "name": "黑暗牧师",
            "base_stats": MonsterStats(
                health=60, damage_min=8, damage_max=15, armor=3,
                movement_speed=0.8, attack_range=10,
                experience=12, gold_min=8, gold_max=20
            ),
            "regions": ["cathedral"],
            "special_abilities": ["heal_allies", "curse"],
            "description": "背叛信仰的牧师"
        },
        "cathedral_gargoyle": {
            "name": "石像鬼",
            "base_stats": MonsterStats(
                health=100, damage_min=15, damage_max=25, armor=30,
                movement_speed=1.0, experience=18, gold_min=10, gold_max=30
            ),
            "regions": ["cathedral"],
            "special_abilities": ["stone_form", "swoop"],
            "description": "被诅咒的石像复活了"
        },
    }


def _create_desert_monsters() -> Dict[str, Dict]:
    return {
        "desert_scorpion": {
            "name": "沙漠巨蝎",
            "base_stats": MonsterStats(
                health=80, damage_min=15, damage_max=25, armor=12,
                movement_speed=1.1, poison_resist=80,
                experience=15, gold_min=8, gold_max=20
            ),
            "regions": ["desert"],
            "special_abilities": ["poison_sting"],
            "description": "沙漠中的致命猎手"
        },
        "desert_mummy": {
            "name": "沙漠木乃伊",
            "base_stats": MonsterStats(
                health=100, damage_min=12, damage_max=22, armor=15,
                movement_speed=0.8, poison_resist=50,
                experience=18, gold_min=10, gold_max=25
            ),
            "regions": ["desert"],
            "special_abilities": ["wrap", "curse"],
            "description": "远古的亡灵守卫"
        },
        "desert_scarab": {
            "name": "圣甲虫群",
            "base_stats": MonsterStats(
                health=30, damage_min=5, damage_max=10, armor=5,
                movement_speed=1.5, experience=5, gold_min=2, gold_max=8
            ),
            "regions": ["desert"],
            "special_abilities": ["swarm"],
            "description": "成群结队的甲虫"
        },
        "desert_djinn": {
            "name": "沙漠精灵",
            "base_stats": MonsterStats(
                health=90, damage_min=18, damage_max=30, armor=5,
                movement_speed=1.2, fire_resist=60, lightning_resist=60,
                experience=22, gold_min=12, gold_max=35
            ),
            "regions": ["desert"],
            "monster_type": MonsterType.RARE,
            "special_abilities": ["sandstorm", "teleport"],
            "description": "被囚禁的元素精灵"
        },
        "desert_raider": {
            "name": "沙漠掠夺者",
            "base_stats": MonsterStats(
                health=70, damage_min=14, damage_max=24, armor=8,
                movement_speed=1.3, experience=14, gold_min=10, gold_max=30
            ),
            "regions": ["desert"],
            "special_abilities": ["ambush", "dual_strike"],
            "description": "沙漠中的强盗"
        },
        "desert_sphinx": {
            "name": "斯芬克斯",
            "base_stats": MonsterStats(
                health=200, damage_min=25, damage_max=40, armor=20,
                movement_speed=0.9, fire_resist=50,
                experience=50, gold_min=30, gold_max=80
            ),
            "regions": ["desert"],
            "monster_type": MonsterType.UNIQUE,
            "special_abilities": ["riddle", "pounce", "sand_breath"],
            "description": "传说中的守护者"
        },
    }


def _create_snow_monsters() -> Dict[str, Dict]:
    return {
        "snow_wolf": {
            "name": "冰原狼",
            "base_stats": MonsterStats(
                health=90, damage_min=18, damage_max=28, armor=8,
                movement_speed=1.4, cold_resist=80,
                experience=20, gold_min=10, gold_max=25
            ),
            "regions": ["snow"],
            "special_abilities": ["frost_bite", "pack_attack"],
            "description": "适应严寒的狼群"
        },
        "snow_yeti": {
            "name": "雪人",
            "base_stats": MonsterStats(
                health=180, damage_min=25, damage_max=40, armor=15,
                movement_speed=0.9, cold_resist=100,
                experience=40, gold_min=20, gold_max=50
            ),
            "regions": ["snow"],
            "monster_type": MonsterType.CHAMPION,
            "special_abilities": ["ice_throw", "ground_pound"],
            "description": "传说中的雪人"
        },
        "snow_wraith": {
            "name": "冰霜怨灵",
            "base_stats": MonsterStats(
                health=80, damage_min=15, damage_max=25, armor=0,
                movement_speed=1.5, cold_resist=100,
                experience=25, gold_min=12, gold_max=30
            ),
            "regions": ["snow"],
            "special_abilities": ["freeze_touch", "phase_through"],
            "description": "在暴风雪中游荡的灵魂"
        },
        "snow_giant": {
            "name": "冰霜巨人",
            "base_stats": MonsterStats(
                health=250, damage_min=30, damage_max=50, armor=25,
                movement_speed=0.7, cold_resist=100,
                experience=60, gold_min=30, gold_max=80
            ),
            "regions": ["snow"],
            "monster_type": MonsterType.RARE,
            "special_abilities": ["ice_cleave", "frost_nova", "summon_ice_shards"],
            "description": "远古的冰霜巨人"
        },
        "snow_mammoth": {
            "name": "猛犸象",
            "base_stats": MonsterStats(
                health=200, damage_min=22, damage_max=35, armor=30,
                movement_speed=0.8, cold_resist=80,
                experience=45, gold_min=25, gold_max=60
            ),
            "regions": ["snow"],
            "special_abilities": ["charge", "trample"],
            "description": "远古的巨兽"
        },
    }


def _create_hell_monsters() -> Dict[str, Dict]:
    return {
        "hell_imp": {
            "name": "地狱小鬼",
            "base_stats": MonsterStats(
                health=60, damage_min=12, damage_max=20, armor=3,
                movement_speed=1.3, fire_resist=80,
                experience=15, gold_min=8, gold_max=20
            ),
            "regions": ["hell"],
            "special_abilities": ["fireball", "teleport"],
            "description": "地狱中最常见的恶魔"
        },
        "hell_demon": {
            "name": "深渊恶魔",
            "base_stats": MonsterStats(
                health=150, damage_min=25, damage_max=40, armor=15,
                movement_speed=1.0, fire_resist=70,
                experience=35, gold_min=20, gold_max=50
            ),
            "regions": ["hell"],
            "special_abilities": ["fire_breath", "charge"],
            "description": "来自深渊的强大恶魔"
        },
        "hell_succubus": {
            "name": "魅魔",
            "base_stats": MonsterStats(
                health=100, damage_min=20, damage_max=35, armor=5,
                movement_speed=1.2, fire_resist=50,
                experience=30, gold_min=15, gold_max=40
            ),
            "regions": ["hell"],
            "special_abilities": ["charm", "life_drain", "whip"],
            "description": "诱惑与毁灭的化身"
        },
        "hell_fiend": {
            "name": "地狱恶犬",
            "base_stats": MonsterStats(
                health=120, damage_min=22, damage_max=35, armor=10,
                movement_speed=1.5, fire_resist=90,
                experience=28, gold_min=15, gold_max=35
            ),
            "regions": ["hell"],
            "special_abilities": ["fire_bite", "triple_strike"],
            "description": "三头地狱犬"
        },
        "hell_mage": {
            "name": "地狱法师",
            "base_stats": MonsterStats(
                health=90, damage_min=25, damage_max=45, armor=3,
                movement_speed=0.9, fire_resist=80, lightning_resist=60,
                experience=35, gold_min=18, gold_max=45
            ),
            "regions": ["hell"],
            "monster_type": MonsterType.CHAMPION,
            "special_abilities": ["meteor", "fire_wall", "summon_imp"],
            "description": "掌握地狱火焰的法师"
        },
        "hell_titan": {
            "name": "地狱泰坦",
            "base_stats": MonsterStats(
                health=400, damage_min=40, damage_max=60, armor=30,
                movement_speed=0.7, fire_resist=100,
                experience=100, gold_min=50, gold_max=150
            ),
            "regions": ["hell"],
            "monster_type": MonsterType.UNIQUE,
            "special_abilities": ["earthquake", "fire_storm", "summon_demons"],
            "description": "地狱中最强大的恶魔之一"
        },
    }


def _create_boss_monsters() -> Dict[str, Dict]:
    return {
        "boss_skeleton_king": {
            "name": "骷髅王",
            "base_stats": MonsterStats(
                health=1500, damage_min=50, damage_max=80, armor=35,
                movement_speed=0.8, cold_resist=50,
                experience=500, gold_min=200, gold_max=500
            ),
            "regions": ["cathedral"],
            "monster_type": MonsterType.BOSS,
            "special_abilities": ["summon_skeletons", "cleave", "whirlwind", "teleport"],
            "description": "曾经的国王，现在的亡灵领主"
        },
        "boss_butcher": {
            "name": "屠夫",
            "base_stats": MonsterStats(
                health=2000, damage_min=60, damage_max=100, armor=25,
                movement_speed=1.0, fire_resist=30,
                experience=600, gold_min=300, gold_max=800
            ),
            "regions": ["cathedral"],
            "monster_type": MonsterType.BOSS,
            "special_abilities": ["charge", "hook", "frenzy", "meat_cleave"],
            "description": "恐怖的屠夫"
        },
        "boss_belial": {
            "name": "彼列",
            "base_stats": MonsterStats(
                health=3000, damage_min=70, damage_max=120, armor=20,
                movement_speed=0.9, fire_resist=60, poison_resist=80,
                experience=1000, gold_min=500, gold_max=1500
            ),
            "regions": ["desert"],
            "monster_type": MonsterType.BOSS,
            "special_abilities": ["deception", "breath_attack", "summon_adds", "phase_shift"],
            "description": "谎言之王"
        },
        "boss_azmodan": {
            "name": "阿兹莫丹",
            "base_stats": MonsterStats(
                health=4000, damage_min=80, damage_max=140, armor=30,
                movement_speed=0.7, fire_resist=80,
                experience=1500, gold_min=800, gold_max=2000
            ),
            "regions": ["hell"],
            "monster_type": MonsterType.BOSS,
            "special_abilities": ["fireball_barrage", "summon_demons", "laser_beam", "darkness"],
            "description": "罪恶之王"
        },
        "boss_diablo": {
            "name": "迪亚波罗",
            "base_stats": MonsterStats(
                health=6000, damage_min=100, damage_max=180, armor=40,
                movement_speed=1.0, fire_resist=100, lightning_resist=80,
                experience=3000, gold_min=1500, gold_max=5000
            ),
            "regions": ["hell"],
            "monster_type": MonsterType.BOSS,
            "special_abilities": ["fire_storm", "lightning_breath", "shadow_clone", 
                                  "bone_prison", "charge", "stomp"],
            "description": "恐惧之王"
        },
        "boss_blood_moon": {
            "name": "血月领主",
            "base_stats": MonsterStats(
                health=2500, damage_min=65, damage_max=110, armor=25,
                movement_speed=1.1, fire_resist=50, cold_resist=50,
                experience=800, gold_min=400, gold_max=1000
            ),
            "regions": ["event"],
            "monster_type": MonsterType.BOSS,
            "special_abilities": ["blood_rain", "summon_blood_spawn", "life_drain_aoe", "berserk"],
            "description": "血月事件的首领"
        },
    }


MONSTER_TEMPLATES = None


def get_monster_templates() -> Dict[str, Dict]:
    global MONSTER_TEMPLATES
    if MONSTER_TEMPLATES is None:
        MONSTER_TEMPLATES = create_monster_templates()
    return MONSTER_TEMPLATES


def get_monsters_for_region(region_id: str) -> List[str]:
    templates = get_monster_templates()
    return [monster_id for monster_id, data in templates.items()
            if region_id in data.get("regions", [])]


def get_boss_templates() -> Dict[str, Dict]:
    templates = get_monster_templates()
    return {k: v for k, v in templates.items()
            if v.get("monster_type") == MonsterType.BOSS}
