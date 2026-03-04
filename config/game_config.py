"""
游戏全局配置文件
"""

class GameConfig:
    SCREEN_WIDTH = 1920
    SCREEN_HEIGHT = 1080
    FPS = 60
    FULLSCREEN = False
    VSYNC = True
    
    TILE_SIZE = 64
    CHUNK_SIZE = 16
    
    MAX_LEVEL = 70
    MAX_PARAGON_LEVEL = 9999
    
    INVENTORY_WIDTH = 10
    INVENTORY_HEIGHT = 6
    STASH_PAGES = 10
    STASH_WIDTH = 10
    STASH_HEIGHT = 10
    
    SAVE_PATH = "saves"
    ASSET_PATH = "assets"
    DEFAULT_SETTINGS = {
        "master_volume": 100,
        "music_volume": 80,
        "sfx_volume": 100,
        "fullscreen": False,
        "vsync": True,
        "ui_scale": 1.0,
        "show_damage_numbers": True,
        "show_health_bars": True,
    }

class ColorConfig:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    DARK_GRAY = (64, 64, 64)
    
    RARITY_COMMON = (200, 200, 200)
    RARITY_MAGIC = (100, 150, 255)
    RARITY_RARE = (255, 200, 50)
    RARITY_LEGENDARY = (255, 150, 50)
    RARITY_SET = (50, 255, 100)
    RARITY_CRAFTED = (200, 100, 255)
    
    HEALTH_BAR = (220, 50, 50)
    MANA_BAR = (50, 100, 220)
    ENERGY_BAR = (200, 150, 50)
    EXPERIENCE_BAR = (100, 200, 100)

class ClassConfig:
    BARBARIAN = "barbarian"
    MONK = "monk"
    ASSASSIN = "assassin"
    WIZARD = "wizard"
    DEMON_HUNTER = "demon_hunter"
    DRUID = "druid"
    NECROMANCER = "necromancer"
    CRUSADER = "crusader"
    
    CLASS_NAMES = {
        "barbarian": "野蛮人",
        "monk": "武僧",
        "assassin": "刺客",
        "wizard": "魔法师",
        "demon_hunter": "猎魔人",
        "druid": "德鲁伊",
        "necromancer": "死灵法师",
        "crusader": "圣教军"
    }

class AttributeConfig:
    BASE_ATTRIBUTES = ["strength", "dexterity", "intelligence", "vitality"]
    
    DERIVED_ATTRIBUTES = [
        "max_health", "health_regen",
        "max_mana", "mana_regen",
        "attack_power", "spell_power",
        "armor", "dodge_chance",
        "crit_chance", "crit_damage",
        "attack_speed", "cast_speed",
        "movement_speed",
        "fire_resist", "cold_resist", "lightning_resist", "poison_resist",
        "life_steal", "magic_find", "gold_find"
    ]

class EquipmentConfig:
    SLOT_HEAD = "head"
    SLOT_SHOULDERS = "shoulders"
    SLOT_CHEST = "chest"
    SLOT_HANDS = "hands"
    SLOT_WAIST = "waist"
    SLOT_LEGS = "legs"
    SLOT_FEET = "feet"
    SLOT_MAIN_HAND = "main_hand"
    SLOT_OFF_HAND = "off_hand"
    SLOT_NECK = "neck"
    SLOT_RING_LEFT = "ring_left"
    SLOT_RING_RIGHT = "ring_right"
    
    EQUIPMENT_SLOTS = [
        "head", "shoulders", "chest", "hands", "waist", "legs", "feet",
        "main_hand", "off_hand", "neck", "ring_left", "ring_right"
    ]
    
    WEAPON_TYPES = [
        "sword", "axe", "mace", "dagger", "spear", "staff", "wand",
        "bow", "crossbow", "shield", "orb", "fist_weapon"
    ]
    
    ARMOR_TYPES = ["light", "medium", "heavy", "cloth"]

class RarityConfig:
    COMMON = 0
    MAGIC = 1
    RARE = 2
    LEGENDARY = 3
    SET = 4
    CRAFTED = 5
    
    RARITY_NAMES = {
        0: "普通",
        1: "魔法",
        2: "稀有",
        3: "传奇",
        4: "套装",
        5: "合成"
    }
    
    RARITY_DROP_WEIGHTS = {
        0: 70,
        1: 20,
        2: 7,
        3: 2,
        4: 1,
        5: 0
    }
