"""
职业技能扩展 - 为每个职业添加完整的技能列表
"""
from typing import Dict, List
from systems.skills.skill import Skill, SkillFactory, SkillType, TargetType, DamageType, SkillBranch


def create_barbarian_skills() -> List[Skill]:
    return [
        Skill(
            id="bash",
            name="猛击",
            description="对敌人造成强力打击，生成怒气",
            icon="skill_bash",
            skill_type=SkillType.ACTIVE,
            target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL,
            max_level=5,
            required_level=1,
            base_resource_cost=-6,
            resource_type="fury",
            base_damage_min=10,
            base_damage_max=20,
            weapon_damage_percent=150,
            branches=[
                SkillBranch(id="fury_bash", name="狂暴猛击", description="增加伤害和怒气生成",
                           level_requirement=1, modifiers={"damage_multiplier": 1.3, "resource_cost_multiplier": 1.5}),
                SkillBranch(id="stun_bash", name="眩晕猛击", description="有几率眩晕敌人",
                           level_requirement=1, effects={"stun_chance": 30, "stun_duration": 2}),
                SkillBranch(id="cleave", name="横扫", description="攻击前方多个敌人",
                           level_requirement=1, modifiers={"area_of_effect": 3})
            ],
            allowed_classes=["barbarian"]
        ),
        Skill(
            id="cleave", name="顺劈斩", description="挥舞武器攻击前方多个敌人",
            icon="skill_cleave", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=2,
            base_resource_cost=-3, resource_type="fury",
            base_damage_min=8, base_damage_max=15, weapon_damage_percent=120,
            base_area_of_effect=3, allowed_classes=["barbarian"]
        ),
        Skill(
            id="hammer_of_the_ancients", name="先祖之锤", description="召唤先祖之力重击敌人",
            icon="skill_hot_ancients", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=4,
            base_resource_cost=20, resource_type="fury",
            base_cooldown=5, base_damage_min=80, base_damage_max=150,
            weapon_damage_percent=200, base_area_of_effect=3, allowed_classes=["barbarian"]
        ),
        Skill(
            id="leap", name="跳跃攻击", description="跳向目标位置并造成范围伤害",
            icon="skill_leap", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=8,
            base_resource_cost=15, resource_type="fury",
            base_cooldown=10, base_damage_min=50, base_damage_max=100,
            weapon_damage_percent=100, base_range=15, base_area_of_effect=4, allowed_classes=["barbarian"]
        ),
        Skill(
            id="ground_stomp", name="大地践踏", description="践踏地面，眩晕周围敌人",
            icon="skill_ground_stomp", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=12,
            base_resource_cost=20, resource_type="fury",
            base_cooldown=12, base_damage_min=30, base_damage_max=60,
            base_area_of_effect=8, allowed_classes=["barbarian"]
        ),
        Skill(
            id="whirlwind", name="旋风斩", description="旋转攻击周围所有敌人",
            icon="skill_whirlwind", skill_type=SkillType.CHANNELING, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=15,
            base_resource_cost=10, resource_type="fury",
            base_damage_min=5, base_damage_max=10, weapon_damage_percent=50,
            base_area_of_effect=6, allowed_classes=["barbarian"]
        ),
        Skill(
            id="rend", name="撕裂", description="造成流血伤害",
            icon="skill_rend", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=18,
            base_resource_cost=20, resource_type="fury",
            base_damage_min=50, base_damage_max=80, weapon_damage_percent=150,
            base_area_of_effect=5, base_duration=5, allowed_classes=["barbarian"]
        ),
        Skill(
            id="ignore_pain", name="无视苦痛", description="减少受到的伤害",
            icon="skill_ignore_pain", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=22,
            base_resource_cost=25, resource_type="fury",
            base_cooldown=30, base_duration=5, allowed_classes=["barbarian"]
        ),
        Skill(
            id="seismic_slam", name="裂地斩", description="释放冲击波攻击远处的敌人",
            icon="skill_seismic_slam", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=26,
            base_resource_cost=25, resource_type="fury",
            base_damage_min=60, base_damage_max=100, weapon_damage_percent=180,
            base_range=15, base_area_of_effect=8, allowed_classes=["barbarian"]
        ),
        Skill(
            id="warcry", name="战吼", description="发出战吼提升自身和队友的护甲",
            icon="skill_warcry", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=30,
            base_resource_cost=-20, resource_type="fury",
            base_cooldown=20, base_duration=60, allowed_classes=["barbarian"]
        ),
        Skill(
            id="earthquake", name="地震", description="引发大地震动，造成巨大伤害",
            icon="skill_earthquake", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=50,
            base_resource_cost=50, resource_type="fury",
            base_cooldown=120, base_damage_min=200, base_damage_max=400,
            weapon_damage_percent=300, base_area_of_effect=15, base_duration=8, allowed_classes=["barbarian"]
        ),
    ]


def create_wizard_skills() -> List[Skill]:
    return [
        Skill(
            id="magic_missile", name="魔法飞弹", description="发射追踪敌人的魔法飞弹",
            icon="skill_magic_missile", skill_type=SkillType.ACTIVE, target_type=TargetType.PROJECTILE,
            damage_type=DamageType.ARCANE, max_level=5, required_level=1,
            base_resource_cost=10, resource_type="mana",
            base_damage_min=15, base_damage_max=25, base_range=20,
            branches=[
                SkillBranch(id="multi_missile", name="多重飞弹", description="发射多枚飞弹",
                           level_requirement=1, modifiers={"projectile_count": 3}),
                SkillBranch(id="seeking_missile", name="追踪飞弹", description="飞弹自动追踪敌人",
                           level_requirement=1, effects={"homing": 100}),
            ],
            allowed_classes=["wizard"]
        ),
        Skill(
            id="electrocute", name="电刑", description="释放闪电链攻击多个敌人",
            icon="skill_electrocute", skill_type=SkillType.CHANNELING, target_type=TargetType.ENEMY,
            damage_type=DamageType.LIGHTNING, max_level=5, required_level=2,
            base_resource_cost=12, resource_type="mana",
            base_damage_min=8, base_damage_max=15, weapon_damage_percent=80,
            allowed_classes=["wizard"]
        ),
        Skill(
            id="frost_nova", name="冰霜新星", description="释放冰霜能量，冻结周围敌人",
            icon="skill_frost_nova", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.COLD, max_level=5, required_level=4,
            base_resource_cost=25, resource_type="mana",
            base_cooldown=8, base_damage_min=30, base_damage_max=60,
            base_area_of_effect=8, allowed_classes=["wizard"]
        ),
        Skill(
            id="teleport", name="传送", description="瞬间移动到目标位置",
            icon="skill_teleport", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.ARCANE, max_level=5, required_level=8,
            base_resource_cost=20, resource_type="mana",
            base_cooldown=10, base_range=25, allowed_classes=["wizard"]
        ),
        Skill(
            id="arcane_orb", name="奥术球", description="发射一个奥术能量球",
            icon="skill_arcane_orb", skill_type=SkillType.ACTIVE, target_type=TargetType.PROJECTILE,
            damage_type=DamageType.ARCANE, max_level=5, required_level=12,
            base_resource_cost=30, resource_type="mana",
            base_damage_min=40, base_damage_max=70, weapon_damage_percent=150,
            base_range=20, base_area_of_effect=4, allowed_classes=["wizard"]
        ),
        Skill(
            id="meteor", name="陨石术", description="召唤陨石从天而降",
            icon="skill_meteor", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.FIRE, max_level=5, required_level=19,
            base_resource_cost=50, resource_type="mana",
            base_cooldown=12, base_damage_min=200, base_damage_max=400,
            weapon_damage_percent=200, base_range=20, base_area_of_effect=6, allowed_classes=["wizard"]
        ),
        Skill(
            id="blizzard", name="暴风雪", description="召唤暴风雪覆盖区域",
            icon="skill_blizzard", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.COLD, max_level=5, required_level=26,
            base_resource_cost=40, resource_type="mana",
            base_damage_min=30, base_damage_max=50, weapon_damage_percent=100,
            base_range=20, base_area_of_effect=10, base_duration=6, allowed_classes=["wizard"]
        ),
        Skill(
            id="hydra", name="九头蛇", description="召唤九头蛇为你战斗",
            icon="skill_hydra", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.FIRE, max_level=5, required_level=30,
            base_resource_cost=35, resource_type="mana",
            base_cooldown=5, base_duration=15, base_range=15, allowed_classes=["wizard"]
        ),
        Skill(
            id="energy_armor", name="能量护甲", description="提升护甲值",
            icon="skill_energy_armor", skill_type=SkillType.TOGGLE, target_type=TargetType.SELF,
            damage_type=DamageType.ARCANE, max_level=5, required_level=35,
            base_resource_cost=25, resource_type="mana", allowed_classes=["wizard"]
        ),
        Skill(
            id="archon", name="执政官", description="变身为强大的执政官形态",
            icon="skill_archon", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.ARCANE, max_level=5, required_level=50,
            base_resource_cost=100, resource_type="mana",
            base_cooldown=120, base_duration=20, allowed_classes=["wizard"]
        ),
    ]


def create_demon_hunter_skills() -> List[Skill]:
    return [
        Skill(
            id="hungering_arrow", name="饥饿箭", description="发射追踪敌人的箭矢",
            icon="skill_hungering_arrow", skill_type=SkillType.ACTIVE, target_type=TargetType.PROJECTILE,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=1,
            base_resource_cost=3, resource_type="hatred",
            base_damage_min=10, base_damage_max=20, weapon_damage_percent=100,
            base_range=25, allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="impale", name="刺穿", description="投掷匕首造成大量伤害",
            icon="skill_impale", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=2,
            base_resource_cost=25, resource_type="hatred",
            base_damage_min=80, base_damage_max=150, weapon_damage_percent=250,
            allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="vault", name="翻滚", description="快速翻滚到目标位置",
            icon="skill_vault", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=8,
            base_resource_cost=8, resource_type="discipline",
            base_cooldown=2, base_range=15, allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="rapid_fire", name="连射", description="快速射击敌人",
            icon="skill_rapid_fire", skill_type=SkillType.CHANNELING, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=12,
            base_resource_cost=15, resource_type="hatred",
            base_damage_min=15, base_damage_max=25, weapon_damage_percent=60,
            base_range=20, allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="multishot", name="多重射击", description="向多个方向发射箭矢",
            icon="skill_multishot", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=18,
            base_resource_cost=25, resource_type="hatred",
            base_damage_min=15, base_damage_max=30, weapon_damage_percent=80,
            base_area_of_effect=10, allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="caltrops", name="铁蒺藜", description="在地面放置铁蒺藜",
            icon="skill_caltrops", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=22,
            base_resource_cost=10, resource_type="discipline",
            base_cooldown=6, base_damage_min=20, base_damage_max=40,
            base_area_of_effect=5, base_duration=10, allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="smoke_screen", name="烟雾幕", description="隐身并提高移动速度",
            icon="skill_smoke_screen", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=26,
            base_resource_cost=15, resource_type="discipline",
            base_cooldown=15, base_duration=2, allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="sentry", name="哨兵", description="放置一个自动射击的哨兵炮塔",
            icon="skill_sentry", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=30,
            base_resource_cost=30, resource_type="discipline",
            base_cooldown=8, base_duration=30, base_range=15, allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="shadow_power", name="暗影之力", description="获得生命偷取",
            icon="skill_shadow_power", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.SHADOW, max_level=5, required_level=35,
            base_resource_cost=20, resource_type="discipline",
            base_cooldown=20, base_duration=5, allowed_classes=["demon_hunter"]
        ),
        Skill(
            id="rain_of_vengeance", name="复仇之雨", description="召唤箭雨覆盖区域",
            icon="skill_rain_veng", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=50,
            base_resource_cost=50, resource_type="hatred",
            base_cooldown=60, base_damage_min=150, base_damage_max=250,
            weapon_damage_percent=200, base_area_of_effect=15, base_duration=5, allowed_classes=["demon_hunter"]
        ),
    ]


def create_monk_skills() -> List[Skill]:
    return [
        Skill(
            id="fists_of_thunder", name="雷光拳", description="快速连击，第三击释放闪电",
            icon="skill_fists_thunder", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.LIGHTNING, max_level=5, required_level=1,
            base_resource_cost=0, resource_type="spirit",
            base_damage_min=8, base_damage_max=16, weapon_damage_percent=120,
            allowed_classes=["monk"]
        ),
        Skill(
            id="deadly_reach", name="致命长拳", description="中距离攻击",
            icon="skill_deadly_reach", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=2,
            base_resource_cost=0, resource_type="spirit",
            base_damage_min=10, base_damage_max=18, weapon_damage_percent=100,
            base_range=3, allowed_classes=["monk"]
        ),
        Skill(
            id="lashing_tail_kick", name="扫堂腿", description="踢击周围敌人",
            icon="skill_lashing_tail", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=8,
            base_resource_cost=30, resource_type="spirit",
            base_damage_min=50, base_damage_max=100, weapon_damage_percent=150,
            base_area_of_effect=5, allowed_classes=["monk"]
        ),
        Skill(
            id="dashing_strike", name="疾风击", description="瞬间移动到敌人身边进行攻击",
            icon="skill_dashing_strike", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=12,
            base_resource_cost=25, resource_type="spirit",
            base_cooldown=6, base_damage_min=20, base_damage_max=40,
            weapon_damage_percent=100, base_range=20, allowed_classes=["monk"]
        ),
        Skill(
            id="laceration", name="裂空斩", description="释放真气攻击敌人",
            icon="skill_laceration", skill_type=SkillType.ACTIVE, target_type=TargetType.PROJECTILE,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=18,
            base_resource_cost=35, resource_type="spirit",
            base_damage_min=60, base_damage_max=100, weapon_damage_percent=180,
            base_range=15, allowed_classes=["monk"]
        ),
        Skill(
            id="blinding_flash", name="致盲闪光", description="致盲周围敌人",
            icon="skill_blinding_flash", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.HOLY, max_level=5, required_level=22,
            base_resource_cost=10, resource_type="spirit",
            base_cooldown=15, base_duration=3, base_area_of_effect=10, allowed_classes=["monk"]
        ),
        Skill(
            id="breath_of_heaven", name="天堂之息", description="治疗自身并提高伤害",
            icon="skill_breath_heaven", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.HOLY, max_level=5, required_level=26,
            base_resource_cost=25, resource_type="spirit",
            base_cooldown=15, allowed_classes=["monk"]
        ),
        Skill(
            id="serenity", name="宁静", description="免疫所有伤害",
            icon="skill_serenity", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.HOLY, max_level=5, required_level=30,
            base_resource_cost=30, resource_type="spirit",
            base_cooldown=30, base_duration=3, allowed_classes=["monk"]
        ),
        Skill(
            id="inner_sanctuary", name="内在圣域", description="创造一个敌人无法进入的区域",
            icon="skill_inner_sanctuary", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.HOLY, max_level=5, required_level=35,
            base_resource_cost=40, resource_type="spirit",
            base_cooldown=20, base_duration=6, base_area_of_effect=5, allowed_classes=["monk"]
        ),
        Skill(
            id="seven_sided_strike", name="七相拳", description="快速攻击多个敌人",
            icon="skill_seven_sided", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=50,
            base_resource_cost=50, resource_type="spirit",
            base_cooldown=30, base_damage_min=100, base_damage_max=200,
            weapon_damage_percent=250, base_area_of_effect=10, allowed_classes=["monk"]
        ),
    ]


def create_necromancer_skills() -> List[Skill]:
    return [
        Skill(
            id="raise_skeleton", name="召唤骷髅", description="召唤骷髅战士为你战斗",
            icon="skill_raise_skeleton", skill_type=SkillType.ACTIVE, target_type=TargetType.NO_TARGET,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=1,
            base_resource_cost=30, resource_type="essence",
            base_cooldown=2, base_duration=60, allowed_classes=["necromancer"]
        ),
        Skill(
            id="bone_spear", name="骨矛", description="发射穿透敌人的骨矛",
            icon="skill_bone_spear", skill_type=SkillType.ACTIVE, target_type=TargetType.PROJECTILE,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=2,
            base_resource_cost=20, resource_type="essence",
            base_damage_min=50, base_damage_max=100, weapon_damage_percent=150,
            base_range=20, allowed_classes=["necromancer"]
        ),
        Skill(
            id="corpse_explosion", name="尸体爆炸", description="引爆尸体造成范围伤害",
            icon="skill_corpse_exp", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=8,
            base_resource_cost=10, resource_type="essence",
            base_damage_min=80, base_damage_max=150, base_area_of_effect=6, allowed_classes=["necromancer"]
        ),
        Skill(
            id="bone_armor", name="骨甲", description="获得额外的护甲",
            icon="skill_bone_armor", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=12,
            base_resource_cost=25, resource_type="essence",
            base_cooldown=10, base_duration=60, allowed_classes=["necromancer"]
        ),
        Skill(
            id="grim_scythe", name="死神之镰", description="挥舞镰刀攻击敌人并恢复精华",
            icon="skill_grim_scythe", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=18,
            base_resource_cost=-10, resource_type="essence",
            base_damage_min=30, base_damage_max=60, weapon_damage_percent=130,
            base_area_of_effect=4, allowed_classes=["necromancer"]
        ),
        Skill(
            id="blood_rush", name="血冲", description="瞬移到目标位置",
            icon="skill_blood_rush", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=22,
            base_resource_cost=15, resource_type="essence",
            base_cooldown=5, base_range=20, allowed_classes=["necromancer"]
        ),
        Skill(
            id="decay", name="衰败", description="对区域内的敌人造成持续伤害",
            icon="skill_decay", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.POISON, max_level=5, required_level=26,
            base_resource_cost=30, resource_type="essence",
            base_damage_min=20, base_damage_max=40, weapon_damage_percent=100,
            base_area_of_effect=8, base_duration=5, allowed_classes=["necromancer"]
        ),
        Skill(
            id="bone_storm", name="骨风暴", description="召唤骨风暴攻击周围敌人",
            icon="skill_bone_storm", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=30,
            base_resource_cost=40, resource_type="essence",
            base_damage_min=40, base_damage_max=80, weapon_damage_percent=120,
            base_area_of_effect=10, base_duration=5, allowed_classes=["necromancer"]
        ),
        Skill(
            id="devour", name="吞噬", description="吞噬尸体恢复精华和生命",
            icon="skill_devour", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=35,
            base_resource_cost=0, resource_type="essence",
            base_cooldown=8, base_area_of_effect=15, allowed_classes=["necromancer"]
        ),
        Skill(
            id="army_of_the_dead", name="亡者大军", description="召唤大量亡灵攻击敌人",
            icon="skill_army_dead", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=50,
            base_resource_cost=80, resource_type="essence",
            base_cooldown=120, base_damage_min=200, base_damage_max=400,
            weapon_damage_percent=300, base_area_of_effect=15, base_duration=4, allowed_classes=["necromancer"]
        ),
    ]


def create_crusader_skills() -> List[Skill]:
    return [
        Skill(
            id="punish", name="惩罚", description="打击敌人并获得格挡加成",
            icon="skill_punish", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.HOLY, max_level=5, required_level=1,
            base_resource_cost=5, resource_type="wrath",
            base_damage_min=10, base_damage_max=20, weapon_damage_percent=130,
            allowed_classes=["crusader"]
        ),
        Skill(
            id="shield_bash", name="盾击", description="用盾牌猛击敌人",
            icon="skill_shield_bash", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.HOLY, max_level=5, required_level=2,
            base_resource_cost=20, resource_type="wrath",
            base_damage_min=60, base_damage_max=120, weapon_damage_percent=200,
            allowed_classes=["crusader"]
        ),
        Skill(
            id="sweep_attack", name="横扫攻击", description="横扫前方敌人",
            icon="skill_sweep_attack", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.HOLY, max_level=5, required_level=8,
            base_resource_cost=15, resource_type="wrath",
            base_damage_min=30, base_damage_max=60, weapon_damage_percent=120,
            base_area_of_effect=5, allowed_classes=["crusader"]
        ),
        Skill(
            id="iron_skin", name="钢铁之肤", description="获得伤害减免",
            icon="skill_iron_skin", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=12,
            base_resource_cost=25, resource_type="wrath",
            base_cooldown=20, base_duration=4, allowed_classes=["crusader"]
        ),
        Skill(
            id="consecration", name="奉献", description="在地面创造神圣区域",
            icon="skill_consecration", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.HOLY, max_level=5, required_level=18,
            base_resource_cost=30, resource_type="wrath",
            base_damage_min=20, base_damage_max=40, weapon_damage_percent=80,
            base_area_of_effect=8, base_duration=10, allowed_classes=["crusader"]
        ),
        Skill(
            id="steed_charge", name="战马冲锋", description="骑马冲锋",
            icon="skill_steed_charge", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=22,
            base_resource_cost=20, resource_type="wrath",
            base_cooldown=16, base_damage_min=50, base_damage_max=100,
            base_range=20, allowed_classes=["crusader"]
        ),
        Skill(
            id="bombardment", name="轰炸", description="召唤天界轰炸",
            icon="skill_bombardment", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.HOLY, max_level=5, required_level=26,
            base_resource_cost=40, resource_type="wrath",
            base_cooldown=60, base_damage_min=100, base_damage_max=200,
            weapon_damage_percent=200, base_area_of_effect=15, allowed_classes=["crusader"]
        ),
        Skill(
            id="akarat_champion", name="阿卡拉特勇士", description="变身为神圣战士",
            icon="skill_akarat", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.HOLY, max_level=5, required_level=30,
            base_resource_cost=50, resource_type="wrath",
            base_cooldown=90, base_duration=20, allowed_classes=["crusader"]
        ),
        Skill(
            id="phalanx", name="方阵", description="召唤骑士冲锋",
            icon="skill_phalanx", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.HOLY, max_level=5, required_level=35,
            base_resource_cost=35, resource_type="wrath",
            base_damage_min=80, base_damage_max=150, weapon_damage_percent=180,
            base_range=15, allowed_classes=["crusader"]
        ),
        Skill(
            id="heavens_fury", name="天罚之剑", description="召唤天界之剑攻击敌人",
            icon="skill_heavens_fury", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.HOLY, max_level=5, required_level=50,
            base_resource_cost=50, resource_type="wrath",
            base_cooldown=20, base_damage_min=150, base_damage_max=300,
            weapon_damage_percent=250, base_area_of_effect=8, allowed_classes=["crusader"]
        ),
    ]


def create_druid_skills() -> List[Skill]:
    return [
        Skill(
            id="werewolf", name="狼人变身", description="变身为狼人形态，提升攻击速度",
            icon="skill_werewolf", skill_type=SkillType.TOGGLE, target_type=TargetType.SELF,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=1,
            base_resource_cost=50, resource_type="mana", allowed_classes=["druid"]
        ),
        Skill(
            id="earth_spike", name="地刺", description="从地面召唤尖刺攻击敌人",
            icon="skill_earth_spike", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=2,
            base_resource_cost=15, resource_type="mana",
            base_damage_min=30, base_damage_max=60, weapon_damage_percent=120,
            allowed_classes=["druid"]
        ),
        Skill(
            id="wind_shear", name="风剪", description="释放风刃攻击敌人",
            icon="skill_wind_shear", skill_type=SkillType.ACTIVE, target_type=TargetType.PROJECTILE,
            damage_type=DamageType.COLD, max_level=5, required_level=8,
            base_resource_cost=20, resource_type="mana",
            base_damage_min=25, base_damage_max=50, weapon_damage_percent=100,
            base_range=15, allowed_classes=["druid"]
        ),
        Skill(
            id="tornado", name="龙卷风", description="召唤龙卷风攻击敌人",
            icon="skill_tornado", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.COLD, max_level=5, required_level=12,
            base_resource_cost=30, resource_type="mana",
            base_damage_min=30, base_damage_max=60, base_duration=5, base_range=15, allowed_classes=["druid"]
        ),
        Skill(
            id="boulder", name="巨石", description="召唤巨石滚向敌人",
            icon="skill_boulder", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=18,
            base_resource_cost=40, resource_type="mana",
            base_damage_min=80, base_damage_max=150, weapon_damage_percent=200,
            base_range=20, allowed_classes=["druid"]
        ),
        Skill(
            id="grizzly", name="灰熊", description="召唤熊灵攻击敌人",
            icon="skill_grizzly", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=22,
            base_resource_cost=35, resource_type="mana",
            base_damage_min=60, base_damage_max=120, weapon_damage_percent=180,
            allowed_classes=["druid"]
        ),
        Skill(
            id="vine_creeper", name="藤蔓", description="召唤藤蔓缠绕敌人",
            icon="skill_vine", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.POISON, max_level=5, required_level=26,
            base_resource_cost=25, resource_type="mana",
            base_damage_min=20, base_damage_max=40, base_duration=5, base_area_of_effect=6, allowed_classes=["druid"]
        ),
        Skill(
            id="hurricane", name="飓风", description="召唤飓风围绕自己",
            icon="skill_hurricane", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.COLD, max_level=5, required_level=30,
            base_resource_cost=50, resource_type="mana",
            base_cooldown=30, base_damage_min=40, base_damage_max=80, base_duration=6, allowed_classes=["druid"]
        ),
        Skill(
            id="werebear", name="熊人变身", description="变身为熊人形态，提升防御",
            icon="skill_werebear", skill_type=SkillType.TOGGLE, target_type=TargetType.SELF,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=35,
            base_resource_cost=50, resource_type="mana", allowed_classes=["druid"]
        ),
        Skill(
            id="armageddon", name="末日", description="召唤陨石雨毁灭一切",
            icon="skill_armageddon", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.FIRE, max_level=5, required_level=50,
            base_resource_cost=80, resource_type="mana",
            base_cooldown=120, base_damage_min=150, base_damage_max=300,
            weapon_damage_percent=250, base_area_of_effect=20, base_duration=5, allowed_classes=["druid"]
        ),
    ]


def create_assassin_skills() -> List[Skill]:
    return [
        Skill(
            id="tiger_strike", name="虎击", description="蓄力攻击，释放时造成巨额伤害",
            icon="skill_tiger_strike", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=1,
            base_resource_cost=5, resource_type="mana",
            base_damage_min=5, base_damage_max=10, weapon_damage_percent=50,
            allowed_classes=["assassin"]
        ),
        Skill(
            id="claw_mastery", name="利爪精通", description="被动提升爪类武器伤害",
            icon="skill_claw_mastery", skill_type=SkillType.PASSIVE, target_type=TargetType.SELF,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=2,
            allowed_classes=["assassin"]
        ),
        Skill(
            id="dragon_claw", name="龙爪", description="双爪连击",
            icon="skill_dragon_claw", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=8,
            base_resource_cost=15, resource_type="mana",
            base_damage_min=20, base_damage_max=40, weapon_damage_percent=140,
            allowed_classes=["assassin"]
        ),
        Skill(
            id="cloak_of_shadows", name="暗影斗篷", description="隐身并提高闪避",
            icon="skill_cloak_shadows", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.SHADOW, max_level=5, required_level=12,
            base_resource_cost=20, resource_type="mana",
            base_cooldown=20, base_duration=5, allowed_classes=["assassin"]
        ),
        Skill(
            id="blade_sentinel", name="刀刃哨兵", description="释放旋转的刀刃",
            icon="skill_blade_sentinel", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=18,
            base_resource_cost=25, resource_type="mana",
            base_damage_min=30, base_damage_max=60, weapon_damage_percent=100,
            base_area_of_effect=8, base_duration=5, allowed_classes=["assassin"]
        ),
        Skill(
            id="dragon_flight", name="龙翔", description="瞬移到敌人身边进行攻击",
            icon="skill_dragon_flight", skill_type=SkillType.ACTIVE, target_type=TargetType.ENEMY,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=22,
            base_resource_cost=20, resource_type="mana",
            base_cooldown=8, base_damage_min=40, base_damage_max=80,
            weapon_damage_percent=150, base_range=20, allowed_classes=["assassin"]
        ),
        Skill(
            id="death_sentry", name="死亡陷阱", description="放置一个陷阱",
            icon="skill_death_sentry", skill_type=SkillType.ACTIVE, target_type=TargetType.GROUND,
            damage_type=DamageType.PHYSICAL, max_level=5, required_level=26,
            base_resource_cost=30, resource_type="mana",
            base_cooldown=5, base_damage_min=50, base_damage_max=100,
            base_area_of_effect=6, base_duration=20, allowed_classes=["assassin"]
        ),
        Skill(
            id="fade", name="消褪", description="减少受到的伤害并提高抗性",
            icon="skill_fade", skill_type=SkillType.ACTIVE, target_type=TargetType.SELF,
            damage_type=DamageType.SHADOW, max_level=5, required_level=30,
            base_resource_cost=25, resource_type="mana",
            base_cooldown=30, base_duration=10, allowed_classes=["assassin"]
        ),
        Skill(
            id="shadow_master", name="影子大师", description="召唤一个影子分身协助战斗",
            icon="skill_shadow_master", skill_type=SkillType.ACTIVE, target_type=TargetType.NO_TARGET,
            damage_type=DamageType.SHADOW, max_level=5, required_level=35,
            base_resource_cost=40, resource_type="mana",
            base_cooldown=30, base_duration=60, allowed_classes=["assassin"]
        ),
        Skill(
            id="phoenix_strike", name="凤凰击", description="释放凤凰之力攻击敌人",
            icon="skill_phoenix_strike", skill_type=SkillType.ACTIVE, target_type=TargetType.AREA,
            damage_type=DamageType.FIRE, max_level=5, required_level=50,
            base_resource_cost=50, resource_type="mana",
            base_cooldown=20, base_damage_min=100, base_damage_max=200,
            weapon_damage_percent=300, base_area_of_effect=10, allowed_classes=["assassin"]
        ),
    ]


def register_all_skills():
    all_skills = (
        create_barbarian_skills() +
        create_wizard_skills() +
        create_demon_hunter_skills() +
        create_monk_skills() +
        create_necromancer_skills() +
        create_crusader_skills() +
        create_druid_skills() +
        create_assassin_skills()
    )
    
    for skill in all_skills:
        SkillFactory._skills[skill.id] = skill
    
    return len(all_skills)
