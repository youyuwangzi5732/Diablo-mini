"""
游戏初始化模块 - 统一注册所有扩展内容
"""
from typing import Optional


def initialize_all_systems():
    """
    初始化所有游戏系统和扩展内容
    应该在游戏启动时调用此函数
    """
    _initialize_factories()
    _initialize_extensions()
    _register_callbacks()
    
    return True


def _initialize_factories():
    """初始化所有工厂类"""
    from entities.character import ClassFactory
    from entities.items import ItemFactory, AffixGenerator
    from systems.skills import SkillFactory
    from systems.combat import MonsterFactory
    
    ClassFactory.initialize()
    ItemFactory.initialize()
    AffixGenerator.initialize()
    SkillFactory.initialize()
    MonsterFactory.initialize()


def _initialize_extensions():
    """注册所有扩展内容"""
    _register_skill_extensions()
    _register_skill_tree_extensions()
    _register_legendary_items()
    _register_monster_extensions()
    _register_affix_extensions()
    _register_area_extensions()


def _register_skill_extensions():
    """注册技能扩展"""
    try:
        from systems.skills.skill_extensions import register_all_skills
        count = register_all_skills()
        print(f"[初始化] 注册了 {count} 个扩展技能")
    except Exception as e:
        print(f"[警告] 技能扩展注册失败: {e}")


def _register_skill_tree_extensions():
    """注册技能树扩展"""
    try:
        from systems.skills.skill_tree_extensions import register_all_skill_trees
        nodes = register_all_skill_trees()
        print(f"[初始化] 注册了 {len(nodes)} 个技能树节点")
    except Exception as e:
        print(f"[警告] 技能树扩展注册失败: {e}")


def _register_legendary_items():
    """注册传奇物品"""
    try:
        from entities.items.legendary_items import initialize_legendaries, LEGENDARY_ITEMS
        initialize_legendaries()
        print(f"[初始化] 注册了 {len(LEGENDARY_ITEMS)} 个传奇物品")
    except Exception as e:
        print(f"[警告] 传奇物品注册失败: {e}")


def _register_monster_extensions():
    """注册怪物扩展"""
    try:
        from systems.combat.monster_extensions import get_monster_templates, MONSTER_TEMPLATES
        templates = get_monster_templates()
        print(f"[初始化] 注册了 {len(templates)} 个怪物模板")
    except Exception as e:
        print(f"[警告] 怪物扩展注册失败: {e}")


def _register_affix_extensions():
    """注册词缀扩展"""
    try:
        from entities.items import affix_extensions
        affix_extensions.initialize_affix_extensions()
        total = (
            len(affix_extensions.PREFIX_AFFIXES)
            + len(affix_extensions.SUFFIX_AFFIXES)
            + len(affix_extensions.LEGENDARY_AFFIXES)
        )
        print(f"[初始化] 注册了 {total} 个词缀")
    except Exception as e:
        print(f"[警告] 词缀扩展注册失败: {e}")


def _register_area_extensions():
    """注册区域扩展"""
    try:
        from systems.world.area_extensions import create_extended_areas
        areas = create_extended_areas()
        print(f"[初始化] 注册了 {len(areas)} 个扩展区域")
    except Exception as e:
        print(f"[警告] 区域扩展注册失败: {e}")


def _register_callbacks():
    """注册全局回调"""
    pass


def get_game_config() -> dict:
    """获取游戏配置"""
    from config.game_config import GameConfig, ColorConfig
    
    return {
        "screen_width": GameConfig.SCREEN_WIDTH,
        "screen_height": GameConfig.SCREEN_HEIGHT,
        "fps": GameConfig.FPS,
        "tile_size": GameConfig.TILE_SIZE,
    }


def validate_game_state() -> bool:
    """验证游戏状态是否正常"""
    errors = []
    
    try:
        from entities.character import ClassFactory
        if not ClassFactory._classes:
            errors.append("职业工厂未初始化")
    except Exception as e:
        errors.append(f"职业工厂错误: {e}")
    
    try:
        from entities.items import ItemFactory
        if not ItemFactory._base_items:
            errors.append("物品工厂未初始化")
    except Exception as e:
        errors.append(f"物品工厂错误: {e}")
    
    try:
        from systems.skills import SkillFactory
        if not SkillFactory._skills:
            errors.append("技能工厂未初始化")
    except Exception as e:
        errors.append(f"技能工厂错误: {e}")
    
    if errors:
        print("[验证错误]")
        for error in errors:
            print(f"  - {error}")
        return False
    
    return True


class GameInitializer:
    """游戏初始化管理器"""
    
    _initialized: bool = False
    
    @classmethod
    def initialize(cls) -> bool:
        if cls._initialized:
            return True
        
        result = initialize_all_systems()
        cls._initialized = result
        return result
    
    @classmethod
    def is_initialized(cls) -> bool:
        return cls._initialized
    
    @classmethod
    def reset(cls):
        cls._initialized = False
