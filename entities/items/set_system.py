"""
套装系统 - 商业化级别的套装奖励计算
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class SetBonusType(Enum):
    STAT_BONUS = "stat_bonus"
    SKILL_BONUS = "skill_bonus"
    SPECIAL_EFFECT = "special_effect"
    RESISTANCE = "resistance"
    DAMAGE_BONUS = "damage_bonus"
    DEFENSE_BONUS = "defense_bonus"


@dataclass
class SetBonus:
    """套装奖励"""
    required_pieces: int
    bonus_type: SetBonusType
    stat_name: str = ""
    value: float = 0.0
    description: str = ""
    is_percentage: bool = False
    
    def get_description(self) -> str:
        if self.bonus_type == SetBonusType.STAT_BONUS:
            if self.is_percentage:
                return f"+{self.value}% {self.stat_name}"
            return f"+{self.value} {self.stat_name}"
        elif self.bonus_type == SetBonusType.DAMAGE_BONUS:
            return f"+{self.value}% 伤害"
        elif self.bonus_type == SetBonusType.DEFENSE_BONUS:
            return f"+{self.value}% 防御"
        elif self.bonus_type == SetBonusType.RESISTANCE:
            return f"+{self.value}% {self.stat_name}抗性"
        elif self.bonus_type == SetBonusType.SPECIAL_EFFECT:
            return self.description
        return self.description


@dataclass
class ItemSet:
    """装备套装"""
    id: str
    name: str
    item_ids: List[str]
    bonuses: List[SetBonus]
    description: str = ""
    
    def get_bonus_for_pieces(self, piece_count: int) -> List[SetBonus]:
        """获取指定件数的奖励"""
        active_bonuses = []
        for bonus in self.bonuses:
            if piece_count >= bonus.required_pieces:
                active_bonuses.append(bonus)
        return active_bonuses
    
    def get_next_bonus_threshold(self, current_pieces: int) -> Optional[int]:
        """获取下一个奖励阈值"""
        thresholds = sorted(set(b.required_pieces for b in self.bonuses))
        for threshold in thresholds:
            if threshold > current_pieces:
                return threshold
        return None


class SetManager:
    """套装管理器"""
    
    # 预定义套装数据
    SET_DEFINITIONS = {
        "immortal_king": {
            "name": "不朽之王",
            "items": ["immortal_king_helm", "immortal_king_armor", "immortal_king_gloves", 
                     "immortal_king_belt", "immortal_king_boots", "immortal_king_weapon"],
            "bonuses": [
                {"pieces": 2, "type": "stat_bonus", "stat": "力量", "value": 50, "desc": "+50 力量"},
                {"pieces": 3, "type": "stat_bonus", "stat": "生命值", "value": 100, "desc": "+100 生命值"},
                {"pieces": 4, "type": "defense_bonus", "value": 15, "desc": "+15% 防御"},
                {"pieces": 5, "type": "damage_bonus", "value": 20, "desc": "+20% 伤害"},
                {"pieces": 6, "type": "special_effect", "desc": "野蛮人之魂：受到致命伤害时，有50%几率存活并恢复25%生命值"},
            ],
            "description": "传说中的不朽之王套装，蕴含着远古野蛮人的力量。"
        },
        "tal_rasha": {
            "name": "塔拉夏",
            "items": ["tal_rasha_helm", "tal_rasha_armor", "tal_rasha_amulet",
                     "tal_rasha_belt", "tal_rasha_orb"],
            "bonuses": [
                {"pieces": 2, "type": "stat_bonus", "stat": "法力值", "value": 60, "desc": "+60 法力值"},
                {"pieces": 3, "type": "stat_bonus", "stat": "智力", "value": 40, "desc": "+40 智力"},
                {"pieces": 4, "type": "damage_bonus", "value": 25, "desc": "+25% 法术伤害"},
                {"pieces": 5, "type": "special_effect", "desc": "元素精通：所有元素法术伤害提高30%，法力消耗降低20%"},
            ],
            "description": "大法师塔拉夏的遗物，蕴含着强大的魔法力量。"
        },
        "natalya": {
            "name": "娜塔亚",
            "items": ["natalya_helm", "natalya_armor", "natalya_weapon",
                     "natalya_boots", "natalya_ring"],
            "bonuses": [
                {"pieces": 2, "type": "stat_bonus", "stat": "敏捷", "value": 45, "desc": "+45 敏捷"},
                {"pieces": 3, "type": "stat_bonus", "stat": "暴击率", "value": 5, "is_pct": True, "desc": "+5% 暴击率"},
                {"pieces": 4, "type": "damage_bonus", "value": 20, "desc": "+20% 伤害"},
                {"pieces": 5, "type": "special_effect", "desc": "暗影步：移动速度提高25%，攻击有15%几率触发暗影伤害"},
            ],
            "description": "刺客娜塔亚的装备，专为暗杀而设计。"
        },
        "griswold": {
            "name": "格里华德",
            "items": ["griswold_helm", "griswold_armor", "griswold_weapon",
                     "griswold_shield", "griswold_ring"],
            "bonuses": [
                {"pieces": 2, "type": "stat_bonus", "stat": "力量", "value": 30, "desc": "+30 力量"},
                {"pieces": 3, "type": "defense_bonus", "value": 20, "desc": "+20% 防御"},
                {"pieces": 4, "type": "stat_bonus", "stat": "生命值", "value": 150, "desc": "+150 生命值"},
                {"pieces": 5, "type": "special_effect", "desc": "圣骑士之盾：受到的所有伤害降低15%，格挡率提高10%"},
            ],
            "description": "铁匠格里华德的杰作，坚固无比。"
        },
        "trang_oul": {
            "name": "塔格奥",
            "items": ["trang_oul_helm", "trang_oul_armor", "trang_oul_gloves",
                     "trang_oul_belt", "trang_oul_wing"],
            "bonuses": [
                {"pieces": 2, "type": "resistance", "stat": "毒素", "value": 30, "desc": "+30% 毒素抗性"},
                {"pieces": 3, "type": "stat_bonus", "stat": "法力值", "value": 80, "desc": "+80 法力值"},
                {"pieces": 4, "type": "damage_bonus", "value": 25, "desc": "+25% 召唤伤害"},
                {"pieces": 5, "type": "special_effect", "desc": "亡灵形态：变身为亡灵法师，所有召唤物伤害提高50%，受到伤害降低10%"},
            ],
            "description": "死灵法师塔格奥的遗物，蕴含着死亡的力量。"
        },
        "heaven_breath": {
            "name": "天堂之息",
            "items": ["heaven_helm", "heaven_armor", "heaven_weapon",
                     "heaven_shield", "heaven_amulet"],
            "bonuses": [
                {"pieces": 2, "type": "stat_bonus", "stat": "全属性", "value": 20, "desc": "+20 全属性"},
                {"pieces": 3, "type": "resistance", "stat": "全部", "value": 25, "desc": "+25% 全抗性"},
                {"pieces": 4, "type": "defense_bonus", "value": 25, "desc": "+25% 防御"},
                {"pieces": 5, "type": "special_effect", "desc": "神圣庇护：受到致命伤害时，免疫该伤害并恢复50%生命值（冷却时间60秒）"},
            ],
            "description": "天堂的祝福，神圣而强大。"
        },
    }
    
    def __init__(self):
        self.sets: Dict[str, ItemSet] = {}
        self._load_sets()
    
    def _load_sets(self):
        """加载套装数据"""
        for set_id, data in self.SET_DEFINITIONS.items():
            bonuses = []
            for bonus_data in data["bonuses"]:
                bonus_type = SetBonusType.STAT_BONUS
                if "type" in bonus_data:
                    type_map = {
                        "stat_bonus": SetBonusType.STAT_BONUS,
                        "skill_bonus": SetBonusType.SKILL_BONUS,
                        "special_effect": SetBonusType.SPECIAL_EFFECT,
                        "resistance": SetBonusType.RESISTANCE,
                        "damage_bonus": SetBonusType.DAMAGE_BONUS,
                        "defense_bonus": SetBonusType.DEFENSE_BONUS,
                    }
                    bonus_type = type_map.get(bonus_data["type"], SetBonusType.STAT_BONUS)
                
                bonus = SetBonus(
                    required_pieces=bonus_data["pieces"],
                    bonus_type=bonus_type,
                    stat_name=bonus_data.get("stat", ""),
                    value=bonus_data.get("value", 0),
                    description=bonus_data.get("desc", ""),
                    is_percentage=bonus_data.get("is_pct", False)
                )
                bonuses.append(bonus)
            
            item_set = ItemSet(
                id=set_id,
                name=data["name"],
                item_ids=data["items"],
                bonuses=bonuses,
                description=data.get("description", "")
            )
            self.sets[set_id] = item_set
    
    def get_set_by_item(self, item_id: str) -> Optional[ItemSet]:
        """通过物品ID获取所属套装"""
        for item_set in self.sets.values():
            if item_id in item_set.item_ids:
                return item_set
        return None
    
    def get_set_by_id(self, set_id: str) -> Optional[ItemSet]:
        """通过套装ID获取套装"""
        return self.sets.get(set_id)
    
    def calculate_equipped_pieces(self, equipment: Dict[str, Any], set_id: str) -> int:
        """计算已装备的套装件数"""
        item_set = self.sets.get(set_id)
        if not item_set:
            return 0
        
        count = 0
        equipped_item_ids = set()
        
        for slot, item in equipment.items():
            if item is None:
                continue
            
            # 获取物品的基础ID或套装ID
            item_base_id = getattr(item, 'base_id', None) or getattr(item, 'id', None)
            if item_base_id in item_set.item_ids:
                count += 1
                equipped_item_ids.add(item_base_id)
            
            # 检查套装标记
            item_set_id = getattr(item, 'set_id', None)
            if item_set_id == set_id:
                count += 1
        
        return count
    
    def get_active_bonuses(self, equipment: Dict[str, Any]) -> Dict[str, Tuple[int, List[SetBonus]]]:
        """获取所有激活的套装奖励"""
        active_sets = {}
        
        # 找出所有装备中的套装
        equipped_sets = set()
        for slot, item in equipment.items():
            if item is None:
                continue
            
            item_set = self.get_set_by_item(getattr(item, 'base_id', getattr(item, 'id', '')))
            if item_set:
                equipped_sets.add(item_set.id)
            
            # 检查套装标记
            set_id = getattr(item, 'set_id', None)
            if set_id:
                equipped_sets.add(set_id)
        
        # 计算每个套装的激活奖励
        for set_id in equipped_sets:
            piece_count = self.calculate_equipped_pieces(equipment, set_id)
            if piece_count > 0:
                item_set = self.sets.get(set_id)
                if item_set:
                    bonuses = item_set.get_bonus_for_pieces(piece_count)
                    if bonuses:
                        active_sets[set_id] = (piece_count, bonuses)
        
        return active_sets
    
    def apply_set_bonuses(self, character: Any, equipment: Dict[str, Any]):
        """应用套装奖励到角色"""
        active_sets = self.get_active_bonuses(equipment)
        
        for set_id, (piece_count, bonuses) in active_sets.items():
            for bonus in bonuses:
                self._apply_bonus(character, bonus)
    
    def _apply_bonus(self, character: Any, bonus: SetBonus):
        """应用单个奖励"""
        if bonus.bonus_type == SetBonusType.STAT_BONUS:
            if hasattr(character, 'attributes'):
                from entities.character.attributes import AttributeType
                
                stat_map = {
                    "力量": AttributeType.STRENGTH,
                    "敏捷": AttributeType.DEXTERITY,
                    "智力": AttributeType.INTELLIGENCE,
                    "体质": AttributeType.VITALITY,
                    "生命值": AttributeType.MAX_HEALTH,
                    "法力值": AttributeType.MAX_RESOURCE,
                    "暴击率": AttributeType.CRITICAL_CHANCE,
                    "暴击伤害": AttributeType.CRITICAL_DAMAGE,
                }
                
                attr_type = stat_map.get(bonus.stat_name)
                if attr_type:
                    character.attributes.add_temporary_bonus(
                        attr_type, 
                        bonus.value, 
                        bonus.is_percentage
                    )
        
        elif bonus.bonus_type == SetBonusType.DAMAGE_BONUS:
            if hasattr(character, 'damage_bonus'):
                character.damage_bonus = getattr(character, 'damage_bonus', 0) + bonus.value
        
        elif bonus.bonus_type == SetBonusType.DEFENSE_BONUS:
            if hasattr(character, 'defense_bonus'):
                character.defense_bonus = getattr(character, 'defense_bonus', 0) + bonus.value
        
        elif bonus.bonus_type == SetBonusType.RESISTANCE:
            if hasattr(character, 'resistances'):
                resistance_map = {
                    "火焰": "fire",
                    "冰霜": "cold",
                    "闪电": "lightning",
                    "毒素": "poison",
                    "物理": "physical",
                    "全部": "all",
                }
                res_type = resistance_map.get(bonus.stat_name, "all")
                if res_type == "all":
                    for res in ["fire", "cold", "lightning", "poison", "physical"]:
                        current = getattr(character.resistances, res, 0)
                        setattr(character.resistances, res, current + bonus.value)
                else:
                    current = getattr(character.resistances, res_type, 0)
                    setattr(character.resistances, res_type, current + bonus.value)


# 全局套装管理器实例
_set_manager: Optional[SetManager] = None


def get_set_manager() -> SetManager:
    """获取套装管理器实例"""
    global _set_manager
    if _set_manager is None:
        _set_manager = SetManager()
    return _set_manager
