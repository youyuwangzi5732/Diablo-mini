"""
区域扩展 - 添加更多游戏区域
"""
from typing import Dict, List
from systems.world.world import Area, AreaType, AreaConnection


def create_extended_areas() -> Dict[str, Area]:
    areas = {}
    
    areas["spider_cave"] = Area(
        id="spider_cave",
        name="蜘蛛洞穴",
        area_type=AreaType.DUNGEON,
        level_range=(3, 10),
        width=100,
        height=100,
        is_dungeon=True,
        monster_spawns=[
            {"monster_id": "forest_spider", "count": 25, "level": 5},
            {"monster_id": "forest_spider", "count": 10, "level": 8, "elite": True},
        ],
        connections=[
            AreaConnection("weald", (5, 50)),
        ],
        description="充满剧毒蜘蛛的黑暗洞穴"
    )
    
    areas["crypts"] = Area(
        id="crypts",
        name="地下墓穴",
        area_type=AreaType.DUNGEON,
        level_range=(10, 18),
        width=120,
        height=120,
        is_dungeon=True,
        monster_spawns=[
            {"monster_id": "cathedral_skeleton", "count": 30, "level": 12},
            {"monster_id": "cathedral_ghost", "count": 15, "level": 14},
            {"monster_id": "cathedral_knight", "count": 5, "level": 16, "elite": True},
        ],
        connections=[
            AreaConnection("cathedral", (5, 60)),
            AreaConnection("catacombs", (115, 60)),
        ],
        description="大教堂下方的古老墓穴"
    )
    
    areas["catacombs"] = Area(
        id="catacombs",
        name="地下城深处",
        area_type=AreaType.DUNGEON,
        level_range=(16, 25),
        width=150,
        height=150,
        is_dungeon=True,
        monster_spawns=[
            {"monster_id": "cathedral_ghost", "count": 20, "level": 18},
            {"monster_id": "cathedral_knight", "count": 10, "level": 20},
            {"monster_id": "boss_skeleton_king", "count": 1, "level": 22, "boss": True},
        ],
        connections=[
            AreaConnection("crypts", (5, 75)),
        ],
        description="骷髅王的领地"
    )
    
    areas["oasis"] = Area(
        id="oasis",
        name="卡尔蒂姆绿洲",
        area_type=AreaType.DESERT,
        level_range=(12, 20),
        width=180,
        height=180,
        monster_spawns=[
            {"monster_id": "desert_scorpion", "count": 20, "level": 14},
            {"monster_id": "desert_scarab", "count": 30, "level": 12},
        ],
        connections=[
            AreaConnection("tristram", (90, 5)),
            AreaConnection("desert", (175, 90)),
        ],
        description="沙漠中的绿洲，但并不安全"
    )
    
    areas["ruins"] = Area(
        id="ruins",
        name="古老遗迹",
        area_type=AreaType.DUNGEON,
        level_range=(20, 28),
        width=160,
        height=160,
        is_dungeon=True,
        monster_spawns=[
            {"monster_id": "desert_mummy", "count": 25, "level": 22},
            {"monster_id": "desert_djinn", "count": 8, "level": 25},
            {"monster_id": "desert_sphinx", "count": 2, "level": 27, "elite": True},
        ],
        connections=[
            AreaConnection("desert", (5, 80)),
        ],
        description="远古文明的遗迹"
    )
    
    areas["caldeum_city"] = Area(
        id="caldeum_city",
        name="卡尔蒂姆城",
        area_type=AreaType.TOWN,
        level_range=(15, 70),
        width=60,
        height=60,
        is_safe_zone=True,
        npc_spawns=[
            {"npc_id": "merchant", "position": (25, 20)},
            {"npc_id": "blacksmith", "position": (35, 25)},
            {"npc_id": "jeweler", "position": (30, 35)},
        ],
        connections=[
            AreaConnection("desert", (30, 55)),
        ],
        description="沙漠中的繁华城市"
    )
    
    areas["highlands"] = Area(
        id="highlands",
        name="亚瑞特高地",
        area_type=AreaType.WILDERNESS,
        level_range=(25, 35),
        width=200,
        height=200,
        monster_spawns=[
            {"monster_id": "snow_wolf", "count": 20, "level": 28},
            {"monster_id": "snow_yeti", "count": 5, "level": 32, "elite": True},
        ],
        connections=[
            AreaConnection("snow", (100, 195)),
            AreaConnection("tristram", (100, 5)),
        ],
        description="通往亚瑞特山脉的高地"
    )
    
    areas["ice_caves"] = Area(
        id="ice_caves",
        name="冰霜洞穴",
        area_type=AreaType.DUNGEON,
        level_range=(32, 42),
        width=140,
        height=140,
        is_dungeon=True,
        monster_spawns=[
            {"monster_id": "snow_wraith", "count": 25, "level": 35},
            {"monster_id": "snow_yeti", "count": 10, "level": 38},
            {"monster_id": "snow_giant", "count": 3, "level": 40, "elite": True},
        ],
        connections=[
            AreaConnection("snow", (5, 70)),
        ],
        description="永冻的冰霜洞穴"
    )
    
    areas["mountain_peak"] = Area(
        id="mountain_peak",
        name="亚瑞特山顶",
        area_type=AreaType.SNOW,
        level_range=(40, 50),
        width=120,
        height=120,
        monster_spawns=[
            {"monster_id": "snow_giant", "count": 8, "level": 45},
            {"monster_id": "snow_mammoth", "count": 5, "level": 48},
        ],
        connections=[
            AreaConnection("snow", (60, 115)),
            AreaConnection("hell_gate", (60, 5)),
        ],
        description="亚瑞特山脉的最高点"
    )
    
    areas["hell_gate"] = Area(
        id="hell_gate",
        name="地狱之门",
        area_type=AreaType.DUNGEON,
        level_range=(45, 55),
        width=100,
        height=100,
        is_dungeon=True,
        monster_spawns=[
            {"monster_id": "hell_imp", "count": 30, "level": 48},
            {"monster_id": "hell_fiend", "count": 10, "level": 52},
        ],
        connections=[
            AreaConnection("mountain_peak", (50, 95)),
            AreaConnection("hell", (50, 5)),
        ],
        description="通往地狱的入口"
    )
    
    areas["hell_depths"] = Area(
        id="hell_depths",
        name="地狱深渊",
        area_type=AreaType.HELL,
        level_range=(55, 65),
        width=180,
        height=180,
        monster_spawns=[
            {"monster_id": "hell_demon", "count": 20, "level": 58},
            {"monster_id": "hell_succubus", "count": 15, "level": 60},
            {"monster_id": "hell_mage", "count": 8, "level": 62, "elite": True},
        ],
        connections=[
            AreaConnection("hell", (90, 175)),
        ],
        description="地狱的最深处"
    )
    
    areas["diablo_lair"] = Area(
        id="diablo_lair",
        name="恐惧领地",
        area_type=AreaType.HELL,
        level_range=(65, 70),
        width=150,
        height=150,
        monster_spawns=[
            {"monster_id": "hell_titan", "count": 5, "level": 68},
            {"monster_id": "boss_diablo", "count": 1, "level": 70, "boss": True},
        ],
        connections=[
            AreaConnection("hell_depths", (75, 145)),
        ],
        description="迪亚波罗的领地"
    )
    
    areas["rift_arena"] = Area(
        id="rift_arena",
        name="秘境竞技场",
        area_type=AreaType.DUNGEON,
        level_range=(1, 70),
        width=100,
        height=100,
        is_dungeon=True,
        is_rift=True,
        monster_spawns=[],
        connections=[],
        description="无限挑战的秘境"
    )
    
    return areas


def get_area_connections() -> Dict[str, List[str]]:
    return {
        "tristram": ["weald", "desert", "snow", "oasis", "highlands"],
        "weald": ["tristram", "cathedral", "spider_cave"],
        "spider_cave": ["weald"],
        "cathedral": ["weald", "crypts"],
        "crypts": ["cathedral", "catacombs"],
        "catacombs": ["crypts"],
        "oasis": ["tristram", "desert"],
        "desert": ["oasis", "ruins", "caldeum_city"],
        "ruins": ["desert"],
        "caldeum_city": ["desert"],
        "highlands": ["tristram", "snow"],
        "snow": ["highlands", "ice_caves", "mountain_peak"],
        "ice_caves": ["snow"],
        "mountain_peak": ["snow", "hell_gate"],
        "hell_gate": ["mountain_peak", "hell"],
        "hell": ["hell_gate", "hell_depths"],
        "hell_depths": ["hell", "diablo_lair"],
        "diablo_lair": ["hell_depths"],
        "rift_arena": ["tristram"],
    }


def get_area_by_level(level: int) -> List[str]:
    area_levels = {
        (1, 5): ["weald", "spider_cave"],
        (5, 12): ["cathedral", "weald"],
        (10, 18): ["crypts", "oasis"],
        (16, 25): ["catacombs", "ruins"],
        (20, 30): ["desert", "caldeum_city"],
        (25, 35): ["highlands"],
        (30, 42): ["snow", "ice_caves"],
        (40, 50): ["mountain_peak"],
        (45, 55): ["hell_gate"],
        (50, 65): ["hell", "hell_depths"],
        (65, 70): ["diablo_lair"],
    }
    
    suitable_areas = []
    for level_range, areas in area_levels.items():
        if level_range[0] <= level <= level_range[1]:
            suitable_areas.extend(areas)
    
    return suitable_areas
