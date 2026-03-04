"""
任务系统
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json


class QuestState(Enum):
    LOCKED = "locked"
    AVAILABLE = "available"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class QuestType(Enum):
    MAIN = "main"
    SIDE = "side"
    EVENT = "event"


@dataclass
class QuestObjective:
    id: str
    description: str
    target_type: str
    target_id: str
    required_count: int
    current_count: int = 0
    
    def is_complete(self) -> bool:
        return self.current_count >= self.required_count
    
    def get_progress_text(self) -> str:
        return f"{self.current_count}/{self.required_count}"


@dataclass
class QuestReward:
    experience: int = 0
    gold: int = 0
    items: List[Dict[str, Any]] = field(default_factory=list)
    skill_points: int = 0
    attribute_points: int = 0
    reputation: int = 0


@dataclass
class Quest:
    id: str
    name: str
    description: str
    quest_type: QuestType
    
    objectives: List[QuestObjective] = field(default_factory=list)
    rewards: QuestReward = field(default_factory=QuestReward)
    
    prerequisites: List[str] = field(default_factory=list)
    required_level: int = 1
    
    giver_npc_id: Optional[str] = None
    turn_in_npc_id: Optional[str] = None
    
    time_limit: Optional[float] = None
    
    dialog_start: str = ""
    dialog_progress: str = ""
    dialog_complete: str = ""
    branch_outcomes: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    resolved_outcome: str = ""
    ending_summary: str = ""
    
    state: QuestState = QuestState.LOCKED
    
    start_time: Optional[float] = None
    completion_time: Optional[float] = None
    
    def is_available(self, completed_quests: List[str], player_level: int) -> bool:
        if self.state != QuestState.LOCKED:
            return False
        
        if player_level < self.required_level:
            return False
        
        for prereq in self.prerequisites:
            if prereq not in completed_quests:
                return False
        
        return True
    
    def start(self) -> bool:
        if self.state != QuestState.AVAILABLE:
            return False
        
        self.state = QuestState.IN_PROGRESS
        return True
    
    def update_objective(self, objective_type: str, target_id: str, 
                          count: int = 1) -> bool:
        if self.state != QuestState.IN_PROGRESS:
            return False
        
        updated = False
        
        for objective in self.objectives:
            if (objective.target_type == objective_type and 
                (objective.target_id == target_id or objective.target_id.startswith("any_")) and
                not objective.is_complete()):
                objective.current_count = min(
                    objective.required_count,
                    objective.current_count + count
                )
                updated = True
        
        return updated
    
    def is_complete(self) -> bool:
        if self.state != QuestState.IN_PROGRESS:
            return False
        
        return all(obj.is_complete() for obj in self.objectives)
    
    def complete(self) -> bool:
        if not self.is_complete():
            return False
        
        self.state = QuestState.COMPLETED
        return True
    
    def fail(self):
        self.state = QuestState.FAILED
    
    def get_progress(self) -> float:
        if not self.objectives:
            return 0.0
        
        completed = sum(1 for obj in self.objectives if obj.is_complete())
        return completed / len(self.objectives)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "quest_type": self.quest_type.value,
            "objectives": [
                {
                    "id": obj.id,
                    "description": obj.description,
                    "target_type": obj.target_type,
                    "target_id": obj.target_id,
                    "required_count": obj.required_count,
                    "current_count": obj.current_count
                }
                for obj in self.objectives
            ],
            "state": self.state.value,
            "resolved_outcome": self.resolved_outcome,
            "ending_summary": self.ending_summary
        }


class QuestManager:
    def __init__(self):
        self.quests: Dict[str, Quest] = {}
        self.active_quests: Dict[str, Quest] = {}
        self.completed_quests: List[str] = []
        self.story_flags: Dict[str, str] = {}
        self.quest_outcomes: Dict[str, Dict[str, str]] = {}
        
        self._create_default_quests()
    
    def _create_default_quests(self):
        main_quests = [
            Quest(
                id="main_quest_1",
                name="灰烬中的钟声",
                description="新崔斯特姆外的钟声在午夜响起，镇长请求你先去林地查明异变。",
                quest_type=QuestType.MAIN,
                objectives=[
                    QuestObjective("obj_1", "与镇长交谈", "talk", "quest_giver", 1),
                    QuestObjective("obj_2", "探索腐化林地", "explore", "weald", 1),
                    QuestObjective("obj_3", "清剿僵尸", "kill", "zombie", 12),
                ],
                rewards=QuestReward(experience=800, gold=180, items=[{"item_id": "health_potion_small", "quantity": 6}]),
                giver_npc_id="quest_giver",
                dialog_start="钟声不该在这个时辰响起，愿圣光与你同在。",
                dialog_complete="你带回来的泥土，像是墓地深处翻出来的一样。"
            ),
            Quest(
                id="main_quest_2",
                name="林地回响",
                description="林地深处出现了堕落者营火，清理威胁并带回线索。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_1"],
                objectives=[
                    QuestObjective("obj_1", "击杀堕落者", "kill", "fallen", 18),
                    QuestObjective("obj_2", "与商人核对失物清单", "talk", "merchant", 1),
                    QuestObjective("obj_3", "再次巡查腐化林地", "enter", "weald", 1),
                ],
                rewards=QuestReward(experience=1300, gold=320, items=[{"item_id": "mana_potion_small", "quantity": 4}]),
                giver_npc_id="quest_giver",
                required_level=3,
                dialog_start="他们在林地里竖起了火堆，像在召唤什么。",
                dialog_complete="线索指向大教堂，那里沉寂太久了。"
            ),
            Quest(
                id="main_quest_3",
                name="大教堂封印",
                description="进入大教堂，压制不断涌出的骷髅军。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_2"],
                required_level=6,
                objectives=[
                    QuestObjective("obj_1", "进入大教堂", "enter", "cathedral", 1),
                    QuestObjective("obj_2", "击杀骷髅", "kill", "skeleton", 20),
                    QuestObjective("obj_3", "击杀骷髅弓手", "kill", "skeleton_archer", 8),
                ],
                rewards=QuestReward(experience=2200, gold=600, skill_points=1),
                giver_npc_id="quest_giver",
                dialog_start="石门后的低语越来越清晰，像在呼唤活人。",
                dialog_complete="封印暂时稳住了，但我们听见更深处的脚步。"
            ),
            Quest(
                id="main_quest_4",
                name="亡者圣歌",
                description="治疗师说亡魂无法安息，去查明它们的执念源头。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_3"],
                required_level=9,
                objectives=[
                    QuestObjective("obj_1", "击杀幽灵", "kill", "ghost", 14),
                    QuestObjective("obj_2", "向治疗师汇报", "talk", "healer", 1),
                    QuestObjective("obj_3", "继续深入大教堂", "explore", "cathedral", 1),
                ],
                rewards=QuestReward(experience=2800, gold=780, attribute_points=1),
                giver_npc_id="quest_giver",
                dialog_start="那不是普通怨灵，它们在守着某个名字。",
                dialog_complete="名字出现了，王座也该被唤醒。"
            ),
            Quest(
                id="main_quest_5",
                name="王座阴影",
                description="王座大厅的骸骨再度起身，击破亡者之王的号令。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_4"],
                required_level=12,
                objectives=[
                    QuestObjective("obj_1", "击败骷髅王", "kill", "skeleton_king", 1),
                    QuestObjective("obj_2", "净化残余亡灵", "kill", "skeleton", 10),
                ],
                rewards=QuestReward(experience=4200, gold=1200, skill_points=1, items=[{"id": "random_legendary", "rarity": 3}]),
                giver_npc_id="quest_giver",
                dialog_start="他曾守护王国，如今只剩执念与铁锈。",
                dialog_complete="大教堂回归寂静，但真正的黑暗已南下。"
            ),
            Quest(
                id="main_quest_6",
                name="沙海来信",
                description="南方沙漠商路求援，先抵达沙海前哨重建补给线。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_5"],
                required_level=15,
                objectives=[
                    QuestObjective("obj_1", "进入卡尔蒂姆沙漠", "enter", "desert", 1),
                    QuestObjective("obj_2", "击杀堕落者", "kill", "fallen", 20),
                    QuestObjective("obj_3", "与卡尔蒂姆商人会合", "talk", "caldeum_merchant", 1),
                ],
                rewards=QuestReward(experience=5600, gold=1650, items=[{"item_id": "health_potion_large", "quantity": 2}]),
                giver_npc_id="quest_giver",
                dialog_start="沙海的风带来求救信，你必须立刻启程。",
                dialog_complete="补给线恢复了，但恶魔已在沙丘筑巢。"
            ),
            Quest(
                id="main_quest_7",
                name="沙暴深处",
                description="追踪沙暴中的恶魔军团，切断它们的先锋攻势。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_6"],
                required_level=19,
                objectives=[
                    QuestObjective("obj_1", "击杀恶魔", "kill", "demon", 22),
                    QuestObjective("obj_2", "再次勘探沙漠腹地", "explore", "desert", 1),
                    QuestObjective("obj_3", "击杀哥布林斥候", "kill", "goblin", 10),
                ],
                rewards=QuestReward(experience=7600, gold=2400, skill_points=1),
                giver_npc_id="quest_giver",
                dialog_start="每一阵沙暴都在掩护它们的行军。",
                dialog_complete="先锋军被打散，但主力开始向雪山转移。"
            ),
            Quest(
                id="main_quest_8",
                name="寒脊烽火",
                description="前往亚瑞特山脉，修复古烽火台，截断北线入侵。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_7"],
                required_level=30,
                objectives=[
                    QuestObjective("obj_1", "进入亚瑞特山脉", "enter", "snow", 1),
                    QuestObjective("obj_2", "击杀山脉恶魔", "kill", "demon", 28),
                    QuestObjective("obj_3", "向训练师确认战线", "talk", "trainer", 1),
                ],
                rewards=QuestReward(experience=11000, gold=3600, attribute_points=2),
                giver_npc_id="quest_giver",
                dialog_start="山脉烽火一旦熄灭，防线就会崩塌。",
                dialog_complete="烽火重新点亮，最后的门将开在地狱。"
            ),
            Quest(
                id="main_quest_9",
                name="地狱裂口",
                description="追随裂口边缘的符文痕迹，强行突破地狱外圈。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_8"],
                required_level=46,
                objectives=[
                    QuestObjective("obj_1", "进入地狱", "enter", "hell", 1),
                    QuestObjective("obj_2", "击杀地狱恶魔", "kill", "demon", 45),
                    QuestObjective("obj_3", "剿灭复生骸骨军", "kill", "skeleton", 25),
                ],
                rewards=QuestReward(experience=18000, gold=6200, skill_points=1, items=[{"id": "rune_weapon", "rarity": 3}]),
                giver_npc_id="quest_giver",
                dialog_start="裂口后方没有退路，只有前进。",
                dialog_complete="外圈阵线已破，最终仪式即将开始。"
            ),
            Quest(
                id="main_quest_10",
                name="黎明之誓",
                description="在地狱深处发起最终清剿，阻止黑暗仪式完成。",
                quest_type=QuestType.MAIN,
                prerequisites=["main_quest_9"],
                required_level=55,
                objectives=[
                    QuestObjective("obj_1", "击杀地狱恶魔", "kill", "demon", 70),
                    QuestObjective("obj_2", "清理所有威胁", "kill", "any_monster", 120),
                    QuestObjective("obj_3", "返回新崔斯特姆宣告胜利", "talk", "quest_giver", 1),
                ],
                rewards=QuestReward(
                    experience=32000,
                    gold=12000,
                    skill_points=3,
                    attribute_points=3,
                    items=[{"id": "blood_moon_item", "rarity": 4}]
                ),
                branch_outcomes={
                    "merchant_alliance": {
                        "flag_key": "faction_alignment",
                        "flag_value": "merchant",
                        "rewards": QuestReward(
                            experience=30000,
                            gold=18000,
                            skill_points=2,
                            attribute_points=3,
                            items=[{"id": "random_legendary", "rarity": 3}]
                        ),
                        "ending_summary": "你选择了商会后勤线，战争因补给而迅速终结。",
                    },
                    "guard_alliance": {
                        "flag_key": "faction_alignment",
                        "flag_value": "guard",
                        "rewards": QuestReward(
                            experience=36000,
                            gold=10000,
                            skill_points=4,
                            attribute_points=3,
                            items=[{"id": "blood_moon_item", "rarity": 4}]
                        ),
                        "ending_summary": "你选择了镇卫军强攻线，代价更大但威胁被彻底清除。",
                    },
                    "default": {
                        "rewards": QuestReward(
                            experience=32000,
                            gold=12000,
                            skill_points=3,
                            attribute_points=3,
                            items=[{"id": "blood_moon_item", "rarity": 4}]
                        ),
                        "ending_summary": "你在两派之间维持平衡，勉强守住了黎明前线。",
                    },
                },
                giver_npc_id="quest_giver",
                dialog_start="这是最后一次集结，也是最漫长的一夜。",
                dialog_complete="钟声再次响起，这一次是为生者。"
            ),
        ]

        side_quests = [
            Quest(
                id="side_quest_1",
                name="失踪的商队",
                description="商路上的车队失联，先确认残迹再清理伏击者。",
                quest_type=QuestType.SIDE,
                objectives=[
                    QuestObjective("obj_1", "与商人交谈", "talk", "merchant", 1),
                    QuestObjective("obj_2", "搜索腐化林地", "explore", "weald", 1),
                    QuestObjective("obj_3", "击杀堕落者", "kill", "fallen", 8),
                ],
                rewards=QuestReward(experience=520, gold=300),
                giver_npc_id="merchant"
            ),
            Quest(
                id="side_quest_2",
                name="猎杀哥布林",
                description="清理偷袭补给箱的哥布林群。",
                quest_type=QuestType.SIDE,
                required_level=5,
                objectives=[
                    QuestObjective("obj_1", "击杀哥布林", "kill", "goblin", 12),
                    QuestObjective("obj_2", "返回商人处汇报", "talk", "merchant", 1),
                ],
                rewards=QuestReward(experience=700, gold=420),
                giver_npc_id="merchant"
            ),
            Quest(
                id="side_quest_3",
                name="无眠墓园",
                description="墓园外墙破裂，骷髅正不断涌出。",
                quest_type=QuestType.SIDE,
                required_level=7,
                objectives=[
                    QuestObjective("obj_1", "击杀骷髅", "kill", "skeleton", 16),
                    QuestObjective("obj_2", "击杀骷髅弓手", "kill", "skeleton_archer", 6),
                ],
                rewards=QuestReward(experience=900, gold=500),
                giver_npc_id="healer"
            ),
            Quest(
                id="side_quest_4",
                name="冷焰祈祷",
                description="治疗师需要你压制大教堂中的幽魂躁动。",
                quest_type=QuestType.SIDE,
                required_level=10,
                prerequisites=["main_quest_3"],
                objectives=[
                    QuestObjective("obj_1", "进入大教堂", "enter", "cathedral", 1),
                    QuestObjective("obj_2", "击杀幽灵", "kill", "ghost", 12),
                    QuestObjective("obj_3", "向治疗师回报", "talk", "healer", 1),
                ],
                rewards=QuestReward(experience=1300, gold=700, items=[{"item_id": "mana_potion_medium", "quantity": 3}]),
                giver_npc_id="healer"
            ),
            Quest(
                id="side_quest_5",
                name="铁与灰",
                description="铁匠要测试新配方强度，委托你采集战斗数据。",
                quest_type=QuestType.SIDE,
                required_level=12,
                objectives=[
                    QuestObjective("obj_1", "与铁匠交谈", "talk", "blacksmith", 1),
                    QuestObjective("obj_2", "击杀任意怪物", "kill", "any_monster", 35),
                ],
                rewards=QuestReward(experience=1500, gold=820, items=[{"id": "rune_weapon", "rarity": 3}]),
                giver_npc_id="blacksmith"
            ),
            Quest(
                id="side_quest_6",
                name="匠人的试炼",
                description="珠宝匠希望验证高压环境下的镶嵌工艺。",
                quest_type=QuestType.SIDE,
                required_level=14,
                objectives=[
                    QuestObjective("obj_1", "与珠宝匠交谈", "talk", "jeweler", 1),
                    QuestObjective("obj_2", "击杀任意怪物", "kill", "any_monster", 40),
                ],
                rewards=QuestReward(experience=1700, gold=900, items=[{"id": "perfect_gem", "quality": 5}]),
                giver_npc_id="jeweler"
            ),
            Quest(
                id="side_quest_7",
                name="沙海护路",
                description="商会请求你在沙漠开辟安全商道。",
                quest_type=QuestType.SIDE,
                required_level=17,
                prerequisites=["main_quest_6"],
                objectives=[
                    QuestObjective("obj_1", "进入沙漠", "enter", "desert", 1),
                    QuestObjective("obj_2", "击杀堕落者", "kill", "fallen", 18),
                    QuestObjective("obj_3", "击杀哥布林劫匪", "kill", "goblin", 10),
                ],
                rewards=QuestReward(experience=2100, gold=1200),
                giver_npc_id="caldeum_merchant"
            ),
            Quest(
                id="side_quest_8",
                name="火线补给",
                description="前线物资紧缺，请护送最后一车药剂。",
                quest_type=QuestType.SIDE,
                required_level=20,
                prerequisites=["main_quest_6"],
                objectives=[
                    QuestObjective("obj_1", "击杀恶魔", "kill", "demon", 15),
                    QuestObjective("obj_2", "返回镇中交付物资", "talk", "merchant", 1),
                ],
                rewards=QuestReward(experience=2400, gold=1300, items=[{"item_id": "health_potion_large", "quantity": 4}]),
                giver_npc_id="merchant"
            ),
            Quest(
                id="side_quest_9",
                name="财宝狂奔",
                description="传送使者记录到宝藏哥布林轨迹，请你立刻截击。",
                quest_type=QuestType.SIDE,
                required_level=21,
                objectives=[
                    QuestObjective("obj_1", "击杀宝藏哥布林", "kill", "treasure_goblin", 1),
                    QuestObjective("obj_2", "击杀任意怪物", "kill", "any_monster", 20),
                ],
                rewards=QuestReward(experience=2600, gold=1800, items=[{"id": "random_legendary", "rarity": 3}]),
                giver_npc_id="teleporter"
            ),
            Quest(
                id="side_quest_10",
                name="冰线哨岗",
                description="亚瑞特山脉外围哨岗失守，重新夺回控制权。",
                quest_type=QuestType.SIDE,
                required_level=31,
                prerequisites=["main_quest_8"],
                objectives=[
                    QuestObjective("obj_1", "进入亚瑞特山脉", "enter", "snow", 1),
                    QuestObjective("obj_2", "击杀恶魔", "kill", "demon", 22),
                ],
                rewards=QuestReward(experience=3600, gold=2200),
                giver_npc_id="trainer"
            ),
            Quest(
                id="side_quest_11",
                name="北风猎团",
                description="猎团需要你协助清剿雪线上游荡的魔物。",
                quest_type=QuestType.SIDE,
                required_level=34,
                prerequisites=["main_quest_8"],
                objectives=[
                    QuestObjective("obj_1", "击杀恶魔", "kill", "demon", 26),
                    QuestObjective("obj_2", "击杀任意怪物", "kill", "any_monster", 45),
                ],
                rewards=QuestReward(experience=4100, gold=2600, items=[{"item_id": "mana_potion_large", "quantity": 3}]),
                giver_npc_id="trainer"
            ),
            Quest(
                id="side_quest_12",
                name="回声密室",
                description="大教堂下层仍有残响，最后清扫一次。",
                quest_type=QuestType.SIDE,
                required_level=28,
                prerequisites=["main_quest_5"],
                objectives=[
                    QuestObjective("obj_1", "进入大教堂", "enter", "cathedral", 1),
                    QuestObjective("obj_2", "击杀幽灵", "kill", "ghost", 10),
                    QuestObjective("obj_3", "击杀骷髅", "kill", "skeleton", 12),
                ],
                rewards=QuestReward(experience=3200, gold=1900),
                giver_npc_id="healer"
            ),
            Quest(
                id="side_quest_13",
                name="地狱测绘",
                description="传送使者需要地狱外圈的稳定坐标。",
                quest_type=QuestType.SIDE,
                required_level=50,
                prerequisites=["main_quest_9"],
                objectives=[
                    QuestObjective("obj_1", "进入地狱", "enter", "hell", 1),
                    QuestObjective("obj_2", "击杀地狱恶魔", "kill", "demon", 30),
                    QuestObjective("obj_3", "返回传送使者处", "talk", "teleporter", 1),
                ],
                rewards=QuestReward(experience=6500, gold=4200),
                giver_npc_id="teleporter"
            ),
            Quest(
                id="side_quest_14",
                name="终局军需",
                description="决战前夜，镇长下令最后一次补给整备。",
                quest_type=QuestType.SIDE,
                required_level=54,
                prerequisites=["main_quest_9"],
                objectives=[
                    QuestObjective("obj_1", "与镇长交谈", "talk", "quest_giver", 1),
                    QuestObjective("obj_2", "击杀任意怪物", "kill", "any_monster", 60),
                ],
                rewards=QuestReward(experience=7200, gold=5000, items=[{"id": "blood_moon_item", "rarity": 4}]),
                branch_outcomes={
                    "merchant_alliance": {
                        "flag_key": "faction_alignment",
                        "flag_value": "merchant",
                        "rewards": QuestReward(
                            experience=6800,
                            gold=6500,
                            items=[{"item_id": "health_potion_large", "quantity": 6}]
                        ),
                        "ending_summary": "军需改由商会统筹，补给线更稳定。",
                    },
                    "guard_alliance": {
                        "flag_key": "faction_alignment",
                        "flag_value": "guard",
                        "rewards": QuestReward(
                            experience=7600,
                            gold=4300,
                            items=[{"id": "rune_weapon", "rarity": 3}]
                        ),
                        "ending_summary": "军需优先前线战团，冲锋强度显著提升。",
                    },
                },
                giver_npc_id="quest_giver"
            ),
        ]

        event_quest_1 = Quest(
            id="event_quest_1",
            name="血月降临",
            description="血月期间怪物更凶猛，完成挑战可获得高阶战利品。",
            quest_type=QuestType.EVENT,
            required_level=24,
            objectives=[
                QuestObjective("obj_1", "在血月期间击杀怪物", "kill", "any_monster", 100),
                QuestObjective("obj_2", "击败地狱恶魔", "kill", "demon", 25),
            ],
            rewards=QuestReward(
                experience=5000,
                gold=3200,
                items=[{"id": "blood_moon_item", "rarity": 4}]
            ),
            giver_npc_id="quest_giver"
        )

        for quest in main_quests + side_quests + [event_quest_1]:
            self.quests[quest.id] = quest
    
    def get_quest(self, quest_id: str) -> Optional[Quest]:
        return self.quests.get(quest_id)
    
    def get_available_quests(self, player_level: int) -> List[Quest]:
        return [
            quest for quest in self.quests.values()
            if quest.is_available(self.completed_quests, player_level)
        ]
    
    def get_active_quests(self) -> List[Quest]:
        return list(self.active_quests.values())
    
    def accept_quest(self, quest_id: str, player_level: int = 1) -> bool:
        quest = self.quests.get(quest_id)
        if not quest:
            return False
        
        if quest.state not in [QuestState.LOCKED, QuestState.AVAILABLE]:
            return False
        
        if not quest.is_available(self.completed_quests, player_level):
            return False
        
        quest.state = QuestState.AVAILABLE
        if quest.start():
            self.active_quests[quest_id] = quest
            return True
        
        return False
    
    def update_quest_progress(self, objective_type: str, target_id: str, 
                                count: int = 1) -> List[Quest]:
        completed_quests = []
        
        for quest in self.active_quests.values():
            if quest.update_objective(objective_type, target_id, count):
                if quest.is_complete():
                    completed_quests.append(quest)
        
        return completed_quests
    
    def complete_quest(self, quest_id: str) -> Optional[QuestReward]:
        quest = self.active_quests.get(quest_id)
        if not quest:
            return None

        resolved_reward = self._resolve_quest_outcome(quest)
        if quest.complete():
            quest.rewards = resolved_reward
            self.completed_quests.append(quest_id)
            del self.active_quests[quest_id]
            self.quest_outcomes[quest_id] = {
                "resolved_outcome": quest.resolved_outcome,
                "ending_summary": quest.ending_summary
            }
            return resolved_reward
        
        return None

    def _resolve_quest_outcome(self, quest: Quest) -> QuestReward:
        if not quest.branch_outcomes:
            return quest.rewards

        selected_outcome = None
        for outcome_id, outcome_data in quest.branch_outcomes.items():
            flag_key = outcome_data.get("flag_key")
            flag_value = outcome_data.get("flag_value")
            if not flag_key:
                continue
            if self.story_flags.get(flag_key) == flag_value:
                selected_outcome = (outcome_id, outcome_data)
                break

        if not selected_outcome and "default" in quest.branch_outcomes:
            selected_outcome = ("default", quest.branch_outcomes["default"])
        if not selected_outcome:
            first_key = next(iter(quest.branch_outcomes.keys()))
            selected_outcome = (first_key, quest.branch_outcomes[first_key])

        quest.resolved_outcome = selected_outcome[0]
        quest.ending_summary = selected_outcome[1].get("ending_summary", "")
        return selected_outcome[1].get("rewards", quest.rewards)

    def set_story_flag(self, key: str, value: str):
        self.story_flags[key] = value
    
    def abandon_quest(self, quest_id: str) -> bool:
        if quest_id not in self.active_quests:
            return False
        
        quest = self.active_quests[quest_id]
        quest.state = QuestState.AVAILABLE
        
        for objective in quest.objectives:
            objective.current_count = 0
        
        del self.active_quests[quest_id]
        return True
    
    def is_quest_completed(self, quest_id: str) -> bool:
        return quest_id in self.completed_quests
    
    def is_quest_active(self, quest_id: str) -> bool:
        return quest_id in self.active_quests
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "active_quests": {
                k: v.to_dict() for k, v in self.active_quests.items()
            },
            "completed_quests": self.completed_quests,
            "story_flags": self.story_flags,
            "quest_outcomes": self.quest_outcomes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'QuestManager':
        manager = cls()
        
        manager.completed_quests = data.get("completed_quests", [])
        manager.story_flags = data.get("story_flags", {})
        manager.quest_outcomes = data.get("quest_outcomes", {})
        
        for quest_id, quest_data in data.get("active_quests", {}).items():
            quest = manager.quests.get(quest_id)
            if quest:
                quest.state = QuestState.IN_PROGRESS
                
                for obj_data in quest_data.get("objectives", []):
                    for obj in quest.objectives:
                        if obj.id == obj_data["id"]:
                            obj.current_count = obj_data.get("current_count", 0)
                quest.resolved_outcome = quest_data.get("resolved_outcome", "")
                quest.ending_summary = quest_data.get("ending_summary", "")
                
                manager.active_quests[quest_id] = quest

        for quest_id, outcome_data in manager.quest_outcomes.items():
            quest = manager.quests.get(quest_id)
            if not quest:
                continue
            quest.resolved_outcome = outcome_data.get("resolved_outcome", "")
            quest.ending_summary = outcome_data.get("ending_summary", "")
            if quest_id in manager.completed_quests:
                quest.state = QuestState.COMPLETED
        
        return manager
