"""
NPC服务系统 - 商业化级别的NPC服务模块化
支持交易、修理、强化、合成、传送等服务
"""
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum
import random


class ServiceType(Enum):
    TRADE = "trade"               # 交易
    REPAIR = "repair"             # 修理
    IDENTIFY = "identify"         # 鉴定
    ENCHANT = "enchant"           # 附魔
    SOCKET = "socket"             # 打孔
    UPGRADE = "upgrade"           # 升级
    TRANSMOG = "transmog"         # 幻化
    TELEPORT = "teleport"         # 传送
    STASH = "stash"               # 仓库
    CRAFTING = "crafting"         # 合成
    GAMBLING = "gambling"         # 赌博
    HEALING = "healing"           # 治疗
    TRAINING = "training"         # 训练
    QUEST = "quest"               # 任务


class ServiceResult(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    INSUFFICIENT_GOLD = "insufficient_gold"
    INSUFFICIENT_RESOURCES = "insufficient_resources"
    INVALID_TARGET = "invalid_target"
    ON_COOLDOWN = "on_cooldown"


@dataclass
class ServiceConfig:
    """服务配置"""
    service_type: ServiceType
    base_cost: int = 0
    cost_formula: str = ""  # "level * 100", "item_value * 0.1"
    cooldown: float = 0
    requires_target: bool = False
    target_types: List[str] = field(default_factory=list)
    max_uses: int = -1  # -1表示无限
    
    def calculate_cost(self, context: Dict[str, Any]) -> int:
        """计算服务费用"""
        if not self.cost_formula:
            return self.base_cost
        
        try:
            # 安全的公式计算
            formula = self.cost_formula
            for key, value in context.items():
                formula = formula.replace(key, str(value))
            
            # 只允许数学运算
            allowed_chars = set("0123456789+-*/(). ")
            if all(c in allowed_chars for c in formula):
                return int(eval(formula))
        except:
            pass
        
        return self.base_cost


@dataclass
class ServiceResultData:
    """服务结果数据"""
    result: ServiceResult
    cost: int = 0
    message: str = ""
    data: Dict[str, Any] = field(default_factory=dict)


class NPCService:
    """NPC服务基类"""
    
    def __init__(self, config: ServiceConfig):
        self.config = config
        self._cooldowns: Dict[str, float] = {}
        self._use_counts: Dict[str, int] = {}
    
    def can_use(self, character: Any, target: Any = None) -> Tuple[bool, str]:
        """检查是否可以使用服务"""
        # 检查冷却
        char_id = getattr(character, 'id', str(id(character)))
        if char_id in self._cooldowns:
            import time
            if time.time() < self._cooldowns[char_id]:
                return False, "服务冷却中"
        
        # 检查使用次数
        if self.config.max_uses > 0:
            if self._use_counts.get(char_id, 0) >= self.config.max_uses:
                return False, "已达到使用上限"
        
        # 检查目标
        if self.config.requires_target and target is None:
            return False, "需要指定目标"
        
        return True, ""
    
    def execute(self, character: Any, target: Any = None, **kwargs) -> ServiceResultData:
        """执行服务"""
        can_use, message = self.can_use(character, target)
        if not can_use:
            return ServiceResultData(
                result=ServiceResult.FAILED,
                message=message
            )
        
        # 计算费用
        context = self._build_context(character, target)
        cost = self.config.calculate_cost(context)
        
        # 检查金币
        character_gold = getattr(character, 'gold', 0)
        if character_gold < cost:
            return ServiceResultData(
                result=ServiceResult.INSUFFICIENT_GOLD,
                cost=cost,
                message=f"金币不足，需要 {cost} 金币"
            )
        
        # 执行具体服务
        result = self._execute_service(character, target, cost, **kwargs)
        
        if result.result == ServiceResult.SUCCESS:
            # 扣除金币
            character.gold -= cost
            
            # 设置冷却
            if self.config.cooldown > 0:
                import time
                char_id = getattr(character, 'id', str(id(character)))
                self._cooldowns[char_id] = time.time() + self.config.cooldown
                self._use_counts[char_id] = self._use_counts.get(char_id, 0) + 1
        
        return result
    
    def _build_context(self, character: Any, target: Any) -> Dict[str, Any]:
        """构建费用计算上下文"""
        context = {
            "level": getattr(character, 'level', 1),
            "gold": getattr(character, 'gold', 0),
        }
        
        if target:
            context.update({
                "item_level": getattr(target, 'item_level', 1),
                "item_value": getattr(target, 'value', 0),
                "durability": getattr(target, 'durability', 100),
                "max_durability": getattr(target, 'max_durability', 100),
            })
        
        return context
    
    def _execute_service(self, character: Any, target: Any, cost: int, **kwargs) -> ServiceResultData:
        """执行具体服务（子类实现）"""
        return ServiceResultData(
            result=ServiceResult.SUCCESS,
            cost=cost,
            message="服务完成"
        )


class RepairService(NPCService):
    """修理服务"""
    
    def __init__(self):
        super().__init__(ServiceConfig(
            service_type=ServiceType.REPAIR,
            cost_formula="(max_durability - durability) * level * 10",
            requires_target=True,
            target_types=["weapon", "armor"]
        ))
    
    def _execute_service(self, character: Any, target: Any, cost: int, **kwargs) -> ServiceResultData:
        repair_all = kwargs.get('repair_all', False)
        
        if repair_all:
            # 修理所有装备
            total_repaired = 0
            total_cost = 0
            
            equipment = getattr(character, 'equipment', None)
            if equipment:
                for slot, item in vars(equipment).items():
                    if item and hasattr(item, 'durability'):
                        max_dur = getattr(item, 'max_durability', 100)
                        current_dur = getattr(item, 'durability', 100)
                        
                        if current_dur < max_dur:
                            item.durability = max_dur
                            total_repaired += 1
            
            return ServiceResultData(
                result=ServiceResult.SUCCESS,
                cost=cost,
                message=f"已修理 {total_repaired} 件装备",
                data={"repaired_count": total_repaired}
            )
        else:
            # 修理单个装备
            if target and hasattr(target, 'durability'):
                max_dur = getattr(target, 'max_durability', 100)
                target.durability = max_dur
                
                return ServiceResultData(
                    result=ServiceResult.SUCCESS,
                    cost=cost,
                    message=f"已修理 {getattr(target, 'name', '装备')}"
                )
        
        return ServiceResultData(
            result=ServiceResult.INVALID_TARGET,
            message="没有可修理的装备"
        )


class IdentifyService(NPCService):
    """鉴定服务"""
    
    def __init__(self):
        super().__init__(ServiceConfig(
            service_type=ServiceType.IDENTIFY,
            base_cost=100,
            requires_target=True,
            target_types=["unidentified_item"]
        ))
    
    def _execute_service(self, character: Any, target: Any, cost: int, **kwargs) -> ServiceResultData:
        if not target:
            return ServiceResultData(
                result=ServiceResult.INVALID_TARGET,
                message="需要指定要鉴定的物品"
            )
        
        is_identified = getattr(target, 'identified', True)
        if is_identified:
            return ServiceResultData(
                result=ServiceResult.FAILED,
                message="该物品已被鉴定"
            )
        
        # 鉴定物品
        target.identified = True
        
        return ServiceResultData(
            result=ServiceResult.SUCCESS,
            cost=cost,
            message=f"已鉴定 {getattr(target, 'name', '物品')}"
        )


class TeleportService(NPCService):
    """传送服务"""
    
    DESTINATIONS = {
        "tristram": {"name": "新崔斯特姆", "cost": 0, "required_level": 1},
        "old_tristram": {"name": "旧崔斯特姆", "cost": 500, "required_level": 10},
        "caldeum": {"name": "卡尔蒂姆", "cost": 1000, "required_level": 20},
        "westmarch": {"name": "威斯特玛", "cost": 2000, "required_level": 35},
        "heaven": {"name": "天堂", "cost": 5000, "required_level": 50},
        "hell": {"name": "地狱", "cost": 5000, "required_level": 50},
    }
    
    def __init__(self):
        super().__init__(ServiceConfig(
            service_type=ServiceType.TELEPORT,
            requires_target=False
        ))
    
    def get_available_destinations(self, character: Any) -> List[Dict]:
        """获取可用的传送目的地"""
        char_level = getattr(character, 'level', 1)
        unlocked_waypoints = getattr(character, 'unlocked_waypoints', set())
        
        available = []
        for dest_id, dest_info in self.DESTINATIONS.items():
            if dest_id == "tristram" or dest_id in unlocked_waypoints:
                if char_level >= dest_info["required_level"]:
                    available.append({
                        "id": dest_id,
                        "name": dest_info["name"],
                        "cost": dest_info["cost"],
                        "level": dest_info["required_level"]
                    })
        
        return available
    
    def _execute_service(self, character: Any, target: Any, cost: int, **kwargs) -> ServiceResultData:
        destination = kwargs.get('destination', '')
        
        if not destination or destination not in self.DESTINATIONS:
            return ServiceResultData(
                result=ServiceResult.INVALID_TARGET,
                message="无效的目的地"
            )
        
        dest_info = self.DESTINATIONS[destination]
        char_level = getattr(character, 'level', 1)
        
        if char_level < dest_info["required_level"]:
            return ServiceResultData(
                result=ServiceResult.FAILED,
                message=f"需要等级 {dest_info['required_level']}"
            )
        
        # 执行传送
        return ServiceResultData(
            result=ServiceResult.SUCCESS,
            cost=cost,
            message=f"已传送到 {dest_info['name']}",
            data={"destination": destination}
        )


class GamblingService(NPCService):
    """赌博服务"""
    
    GAMBLING_ITEMS = [
        {"type": "weapon", "weight": 30},
        {"type": "armor", "weight": 40},
        {"type": "accessory", "weight": 20},
        {"type": "legendary", "weight": 5},
        {"type": "set_item", "weight": 5},
    ]
    
    def __init__(self):
        super().__init__(ServiceConfig(
            service_type=ServiceType.GAMBLING,
            base_cost=1000,
            requires_target=False
        ))
    
    def _execute_service(self, character: Any, target: Any, cost: int, **kwargs) -> ServiceResultData:
        char_level = getattr(character, 'level', 1)
        
        # 根据权重随机选择物品类型
        total_weight = sum(item["weight"] for item in self.GAMBLING_ITEMS)
        roll = random.randint(1, total_weight)
        cumulative = 0
        selected_type = "armor"
        
        for item in self.GAMBLING_ITEMS:
            cumulative += item["weight"]
            if roll <= cumulative:
                selected_type = item["type"]
                break
        
        # 生成物品
        from entities.items.item_factory import ItemFactory
        rarity = self._determine_rarity(selected_type)
        
        item = ItemFactory.create_random_item(
            item_type=selected_type,
            level=char_level,
            rarity=rarity
        )
        
        if item:
            return ServiceResultData(
                result=ServiceResult.SUCCESS,
                cost=cost,
                message=f"获得了 {item.name}",
                data={"item": item}
            )
        
        return ServiceResultData(
            result=ServiceResult.FAILED,
            message="赌博失败"
        )
    
    def _determine_rarity(self, item_type: str) -> str:
        """确定物品稀有度"""
        if item_type == "legendary":
            return "legendary"
        elif item_type == "set_item":
            return "set"
        
        # 普通赌博稀有度分布
        roll = random.randint(1, 100)
        if roll <= 5:
            return "legendary"
        elif roll <= 15:
            return "rare"
        elif roll <= 40:
            return "magic"
        else:
            return "common"


class HealingService(NPCService):
    """治疗服务"""
    
    def __init__(self):
        super().__init__(ServiceConfig(
            service_type=ServiceType.HEALING,
            cost_formula="level * 5",
            cooldown=5.0
        ))
    
    def _execute_service(self, character: Any, target: Any, cost: int, **kwargs) -> ServiceResultData:
        max_health = getattr(character, 'get_max_health', lambda: 100)()
        current_health = getattr(character, 'current_health', 0)
        
        if current_health >= max_health:
            return ServiceResultData(
                result=ServiceResult.FAILED,
                message="生命值已满"
            )
        
        # 完全恢复
        character.current_health = max_health
        
        return ServiceResultData(
            result=ServiceResult.SUCCESS,
            cost=cost,
            message="已完全恢复生命值"
        )


class StashService(NPCService):
    """仓库服务"""
    
    def __init__(self, stash_size: int = 100):
        super().__init__(ServiceConfig(
            service_type=ServiceType.STASH,
            base_cost=0
        ))
        self.stash_size = stash_size
        self._stashes: Dict[str, List[Any]] = {}
    
    def get_stash(self, character: Any) -> List[Any]:
        """获取角色仓库"""
        char_id = getattr(character, 'id', str(id(character)))
        if char_id not in self._stashes:
            self._stashes[char_id] = [None] * self.stash_size
        return self._stashes[char_id]
    
    def deposit_item(self, character: Any, item: Any, slot: int = -1) -> ServiceResultData:
        """存入物品"""
        stash = self.get_stash(character)
        
        if slot >= 0 and slot < len(stash):
            if stash[slot] is not None:
                return ServiceResultData(
                    result=ServiceResult.FAILED,
                    message="该位置已有物品"
                )
            stash[slot] = item
        else:
            # 找空位
            for i, s in enumerate(stash):
                if s is None:
                    stash[i] = item
                    break
            else:
                return ServiceResultData(
                    result=ServiceResult.FAILED,
                    message="仓库已满"
                )
        
        return ServiceResultData(
            result=ServiceResult.SUCCESS,
            message=f"已存入 {getattr(item, 'name', '物品')}"
        )
    
    def withdraw_item(self, character: Any, slot: int) -> ServiceResultData:
        """取出物品"""
        stash = self.get_stash(character)
        
        if slot < 0 or slot >= len(stash) or stash[slot] is None:
            return ServiceResultData(
                result=ServiceResult.INVALID_TARGET,
                message="无效的仓库位置"
            )
        
        item = stash[slot]
        stash[slot] = None
        
        return ServiceResultData(
            result=ServiceResult.SUCCESS,
            message=f"已取出 {getattr(item, 'name', '物品')}",
            data={"item": item, "slot": slot}
        )


class NPCServiceManager:
    """NPC服务管理器"""
    
    def __init__(self):
        self._services: Dict[ServiceType, NPCService] = {}
        self._initialize_services()
    
    def _initialize_services(self):
        """初始化所有服务"""
        self._services = {
            ServiceType.REPAIR: RepairService(),
            ServiceType.IDENTIFY: IdentifyService(),
            ServiceType.TELEPORT: TeleportService(),
            ServiceType.GAMBLING: GamblingService(),
            ServiceType.HEALING: HealingService(),
            ServiceType.STASH: StashService(),
        }
    
    def get_service(self, service_type: ServiceType) -> Optional[NPCService]:
        """获取服务"""
        return self._services.get(service_type)
    
    def execute_service(self, service_type: ServiceType, character: Any, 
                        target: Any = None, **kwargs) -> ServiceResultData:
        """执行服务"""
        service = self.get_service(service_type)
        if not service:
            return ServiceResultData(
                result=ServiceResult.FAILED,
                message="服务不可用"
            )
        
        return service.execute(character, target, **kwargs)
    
    def get_available_services(self, npc_type: str) -> List[ServiceType]:
        """获取NPC可用的服务类型"""
        service_mapping = {
            "blacksmith": [ServiceType.REPAIR, ServiceType.UPGRADE, ServiceType.SOCKET],
            "merchant": [ServiceType.TRADE, ServiceType.GAMBLING],
            "healer": [ServiceType.HEALING],
            "teleporter": [ServiceType.TELEPORT],
            "stash_keeper": [ServiceType.STASH],
            "jeweler": [ServiceType.SOCKET, ServiceType.ENCHANT],
            "enchanter": [ServiceType.ENCHANT, ServiceType.TRANSMOG],
        }
        
        return service_mapping.get(npc_type, [])


# 全局服务管理器
_service_manager: Optional[NPCServiceManager] = None


def get_service_manager() -> NPCServiceManager:
    """获取服务管理器"""
    global _service_manager
    if _service_manager is None:
        _service_manager = NPCServiceManager()
    return _service_manager
