"""
NPC系统
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class NPCType(Enum):
    MERCHANT = "merchant"
    BLACKSMITH = "blacksmith"
    JEWELER = "jeweler"
    QUEST_GIVER = "quest_giver"
    TRAINER = "trainer"
    STASH = "stash"
    HEALER = "healer"
    TELEPORTER = "teleporter"


@dataclass
class NPCDialog:
    id: str
    text: str
    responses: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ShopItem:
    item_id: str
    price: int
    currency: str = "gold"
    quantity: int = -1
    required_level: int = 1
    required_reputation: int = 0


@dataclass
class NPC:
    id: str
    name: str
    npc_type: NPCType
    position: tuple = (0, 0)
    area_id: str = "tristram"
    
    interaction_range: float = 2.0
    
    dialog: List[NPCDialog] = field(default_factory=list)
    shop_items: List[ShopItem] = field(default_factory=list)
    
    services: List[str] = field(default_factory=list)
    
    icon: str = ""
    model: str = ""
    
    greeting_messages: List[str] = field(default_factory=list)
    farewell_messages: List[str] = field(default_factory=list)
    
    quest_ids: List[str] = field(default_factory=list)
    
    def can_interact(self, player_pos: tuple) -> bool:
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= self.interaction_range
    
    def get_greeting(self) -> str:
        if self.greeting_messages:
            import random
            return random.choice(self.greeting_messages)
        return f"你好，旅行者。"
    
    def get_farewell(self) -> str:
        if self.farewell_messages:
            import random
            return random.choice(self.farewell_messages)
        return "再见，愿你的旅途平安。"
    
    def get_initial_dialog(self) -> Optional[NPCDialog]:
        if self.dialog:
            return self.dialog[0]
        return None
    
    def get_dialog(self, dialog_id: str) -> Optional[NPCDialog]:
        for d in self.dialog:
            if d.id == dialog_id:
                return d
        return None
    
    def has_service(self, service: str) -> bool:
        return service in self.services
    
    def get_shop_items(self, player_level: int = 1) -> List[ShopItem]:
        return [
            item for item in self.shop_items
            if item.required_level <= player_level
        ]


class NPCManager:
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self._create_default_npcs()
    
    def _create_default_npcs(self):
        merchant = NPC(
            id="merchant",
            name="商人",
            npc_type=NPCType.MERCHANT,
            position=(20, 15),
            services=["buy", "sell"],
            greeting_messages=[
                "欢迎光临！有什么需要吗？",
                "看看我的货物，都是上好的货色！",
                "旅行者，需要补给吗？"
            ],
            farewell_messages=[
                "欢迎下次光临！",
                "祝你好运！",
                "小心外面，最近不太平。"
            ],
            shop_items=[
                ShopItem("health_potion_small", 50, "gold", -1, 1),
                ShopItem("health_potion_large", 200, "gold", -1, 10),
                ShopItem("mana_potion_small", 50, "gold", -1, 1),
                ShopItem("mana_potion_large", 200, "gold", -1, 10),
                ShopItem("town_portal", 100, "gold", -1, 1),
            ]
        )
        
        blacksmith = NPC(
            id="blacksmith",
            name="铁匠",
            npc_type=NPCType.BLACKSMITH,
            position=(30, 20),
            services=["repair", "repair_all"],
            greeting_messages=[
                "需要修理装备吗？",
                "我的锤子随时为你服务。",
                "好钢需要好匠人。"
            ],
            dialog=[
                NPCDialog(
                    id="main",
                    text="我可以为你修理受损的装备。装备的耐久度会影响其性能。",
                    responses=[
                        {"text": "修理装备", "action": "repair"},
                        {"text": "修理全部", "action": "repair_all"},
                        {"text": "离开", "action": "exit"}
                    ]
                )
            ]
        )
        
        jeweler = NPC(
            id="jeweler",
            name="珠宝匠",
            npc_type=NPCType.JEWELER,
            position=(25, 30),
            services=["socket", "gem_combine", "remove_gem"],
            greeting_messages=[
                "宝石需要精心雕琢。",
                "一颗完美的宝石能让装备焕发光彩。",
                "需要我的服务吗？"
            ]
        )
        
        quest_giver = NPC(
            id="quest_giver",
            name="镇长",
            npc_type=NPCType.QUEST_GIVER,
            position=(15, 25),
            services=["quest"],
            greeting_messages=[
                "旅行者，我们正需要你的帮助。",
                "镇子最近遇到了一些麻烦...",
                "你来得正是时候。"
            ],
            quest_ids=["main_quest_1", "main_quest_2", "side_quest_1"]
        )
        
        stash = NPC(
            id="stash",
            name="仓库",
            npc_type=NPCType.STASH,
            position=(35, 35),
            services=["stash"],
            greeting_messages=[
                "这是你的私人仓库。"
            ]
        )
        
        healer = NPC(
            id="healer",
            name="治疗师",
            npc_type=NPCType.HEALER,
            position=(10, 20),
            services=["heal", "cure"],
            greeting_messages=[
                "你看起来受伤了，让我为你治疗。",
                "健康是最宝贵的财富。"
            ]
        )
        
        teleporter = NPC(
            id="teleporter",
            name="传送使者",
            npc_type=NPCType.TELEPORTER,
            position=(40, 25),
            services=["teleport"],
            greeting_messages=[
                "我可以帮你快速传送到已发现的传送点。",
                "世界很大，让我帮你缩短距离。",
                "传送点网络连接着各个角落。"
            ],
            dialog=[
                NPCDialog(
                    id="main",
                    text="我可以帮你传送到已激活的传送点。你想去哪里？",
                    responses=[
                        {"text": "打开传送地图", "action": "open_waypoints"},
                        {"text": "离开", "action": "exit"}
                    ]
                )
            ]
        )
        
        trainer = NPC(
            id="trainer",
            name="技能训练师",
            npc_type=NPCType.TRAINER,
            position=(45, 30),
            services=["reset_skills", "reset_paragon"],
            greeting_messages=[
                "需要重新分配你的技能点吗？",
                "有时候改变是必要的。",
                "我可以帮你重置技能和巅峰点数。"
            ],
            dialog=[
                NPCDialog(
                    id="main",
                    text="我可以帮你重置技能点或巅峰点数，但需要支付一定费用。",
                    responses=[
                        {"text": "重置技能点", "action": "reset_skills"},
                        {"text": "重置巅峰点数", "action": "reset_paragon"},
                        {"text": "离开", "action": "exit"}
                    ]
                )
            ]
        )
        
        self.npcs[merchant.id] = merchant
        self.npcs[blacksmith.id] = blacksmith
        self.npcs[jeweler.id] = jeweler
        self.npcs[quest_giver.id] = quest_giver
        self.npcs[stash.id] = stash
        self.npcs[healer.id] = healer
        self.npcs[teleporter.id] = teleporter
        self.npcs[trainer.id] = trainer
        
        self._create_regional_npcs()
    
    def _create_regional_npcs(self):
        caldeum_merchant = NPC(
            id="caldeum_merchant",
            name="卡尔蒂姆商人",
            npc_type=NPCType.MERCHANT,
            position=(25, 20),
            area_id="caldeum_city",
            services=["buy", "sell"],
            greeting_messages=[
                "沙漠中的旅人，欢迎！",
                "我有来自东方的珍品！"
            ]
        )
        
        caldeum_blacksmith = NPC(
            id="caldeum_blacksmith",
            name="卡尔蒂姆铁匠",
            npc_type=NPCType.BLACKSMITH,
            position=(35, 25),
            area_id="caldeum_city",
            services=["repair", "repair_all"],
            greeting_messages=[
                "沙漠的炎热让装备更容易损坏。",
                "需要修理吗？"
            ]
        )
        
        caldeum_waypoint = NPC(
            id="caldeum_waypoint",
            name="传送使者",
            npc_type=NPCType.TELEPORTER,
            position=(30, 35),
            area_id="caldeum_city",
            services=["teleport"],
            greeting_messages=[
                "卡尔蒂姆的传送点已经激活。",
                "需要传送到其他地方吗？"
            ]
        )
        
        self.npcs[caldeum_merchant.id] = caldeum_merchant
        self.npcs[caldeum_blacksmith.id] = caldeum_blacksmith
        self.npcs[caldeum_waypoint.id] = caldeum_waypoint
    
    def get_npc(self, npc_id: str) -> Optional[NPC]:
        return self.npcs.get(npc_id)
    
    def get_npcs_in_range(self, position: tuple, 
                           range_limit: float = 5.0) -> List[NPC]:
        nearby = []
        
        for npc in self.npcs.values():
            dx = position[0] - npc.position[0]
            dy = position[1] - npc.position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= range_limit:
                nearby.append(npc)
        
        return nearby
    
    def get_npcs_by_type(self, npc_type: NPCType) -> List[NPC]:
        return [npc for npc in self.npcs.values() if npc.npc_type == npc_type]
    
    def register_npc(self, npc: NPC):
        self.npcs[npc.id] = npc
    
    def remove_npc(self, npc_id: str):
        if npc_id in self.npcs:
            del self.npcs[npc_id]
