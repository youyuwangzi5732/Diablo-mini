"""
系统模块初始化
"""
# 技能系统
from .skills import (
    Skill, SkillFactory, SkillType, TargetType,
    SkillTree, SkillNode, NodeType,
    Effect, EffectType, EffectManager,
    SkillExecutor, SkillExecutionContext, SkillExecutionResult,
    register_all_skills
)

# 战斗系统
from .combat import (
    CombatSystem, CombatResult, DamageResult,
    Monster, MonsterFactory, MonsterType,
    Projectile, ProjectileManager
)

# 世界系统
from .world import (
    World, Area, AreaType,
    Dungeon, DungeonGenerator, DungeonType,
    NPC, NPCType, NPCManager,
    Quest, QuestManager, QuestState
)

# 动画系统
from .animation import AnimationManager, Animation, Cutscene, IntroCutscene, AnimationType

# 输入系统
from .input_manager import InputManager, PlayerController, InputAction

# 音效系统
from .sound_manager import SoundManager, SoundCategory

# 游戏状态
from .game_state import GameStateMachine, GameState, GameStateType

# 掉落系统
from .loot import LootManager, LootTable, DroppedItem, DropSource

# 粒子系统
from .particles import ParticleSystem, ParticleEmitter, Particle, ParticleBlendMode

# 消耗品系统
from .consumables import PotionFactory, Potion, PotionType, PotionBelt

# 修理系统
from .repair import RepairSystem, RepairResult

# NPC服务
from .npc_services import NPCServiceManager, StashService, HealingService

# 合成系统
from .crafting import CraftingSystem, CraftingRecipe, RecipeType

# 交易系统
from .trading import TradingSystem, Vendor, Transaction, TransactionType

# 强化系统
from .enhancement import EnhancementSystem, EnhancementType, EnhancementResult

# 环境系统
from .environment import EnvironmentManager, InteractiveObject, InteractiveType, InteractiveState

# 数据分析系统
from .analytics import AnalyticsManager, EventType as AnalyticsEventType, SessionStats, get_analytics

# 排行榜系统
from .leaderboard import LeaderboardManager, LeaderboardEntry, LeaderboardType, get_leaderboard

# 赛季系统
from .season_system import SeasonManager, Season, SeasonJourneyProgress, get_season_manager

# 安全系统
from .security_system import SecurityManager, SecurityAlert, SecurityLevel, get_security_manager

__all__ = [
    # 技能
    'Skill', 'SkillFactory', 'SkillType', 'TargetType',
    'SkillTree', 'SkillNode', 'NodeType',
    'Effect', 'EffectType', 'EffectManager',
    'SkillExecutor', 'SkillExecutionContext', 'SkillExecutionResult',
    'register_all_skills',
    # 战斗
    'CombatSystem', 'CombatResult', 'DamageResult',
    'Monster', 'MonsterFactory', 'MonsterType',
    'Projectile', 'ProjectileManager',
    # 世界
    'World', 'Area', 'AreaType',
    'Dungeon', 'DungeonGenerator', 'DungeonType',
    'NPC', 'NPCType', 'NPCManager',
    'Quest', 'QuestManager', 'QuestState',
    # 其他系统
    'AnimationManager', 'Animation', 'Cutscene', 'IntroCutscene', 'AnimationType',
    'InputManager', 'PlayerController', 'InputAction',
    'SoundManager', 'SoundCategory',
    'GameStateMachine', 'GameState', 'GameStateType',
    'LootManager', 'LootTable', 'DroppedItem', 'DropSource',
    'ParticleSystem', 'ParticleEmitter', 'Particle', 'ParticleBlendMode',
    'PotionFactory', 'Potion', 'PotionType', 'PotionBelt',
    'RepairSystem', 'RepairResult',
    'NPCServiceManager', 'StashService', 'HealingService',
    'CraftingSystem', 'CraftingRecipe', 'RecipeType',
    'TradingSystem', 'Vendor', 'Transaction', 'TransactionType',
    'EnhancementSystem', 'EnhancementType', 'EnhancementResult',
    'EnvironmentManager', 'InteractiveObject', 'InteractiveType', 'InteractiveState',
    # 新增系统
    'AnalyticsManager', 'AnalyticsEventType', 'SessionStats', 'get_analytics',
    'LeaderboardManager', 'LeaderboardEntry', 'LeaderboardType', 'get_leaderboard',
    'SeasonManager', 'Season', 'SeasonJourneyProgress', 'get_season_manager',
    'SecurityManager', 'SecurityAlert', 'SecurityLevel', 'get_security_manager',
]
