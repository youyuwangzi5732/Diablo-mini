"""
装备系统单元测试
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_framework import GameTestCase
from entities.items.item import Item, ItemRarity, ItemType
from entities.items.affix_pool import AffixPoolManager, AffixType, AffixTier


class TestItemCreation(GameTestCase):
    """物品创建测试"""
    
    def test_create_common_item(self):
        """测试创建普通物品"""
        item = Item(
            id="test_sword",
            name="测试剑",
            base_id="sword_1",
            rarity=ItemRarity.COMMON
        )
        self.assertIsNotNone(item)
        self.assertEqual(item.rarity, ItemRarity.COMMON)
    
    def test_create_all_rarities(self):
        """测试创建所有稀有度物品"""
        rarities = [
            ItemRarity.COMMON,
            ItemRarity.MAGIC,
            ItemRarity.RARE,
            ItemRarity.LEGENDARY,
            ItemRarity.SET,
        ]
        
        for rarity in rarities:
            item = Item(
                id=f"test_{rarity.value}",
                name=f"测试{rarity.name}",
                base_id="sword_1",
                rarity=rarity
            )
            self.assertEqual(item.rarity, rarity)


class TestAffixPool(GameTestCase):
    """词缀池测试"""
    
    def setUp(self):
        AffixPoolManager.initialize()
    
    def test_affix_definitions_loaded(self):
        """测试词缀定义加载"""
        self.assertGreater(len(AffixPoolManager.AFFIX_DEFINITIONS), 0)
    
    def test_get_affix_by_id(self):
        """测试通过ID获取词缀"""
        affix = AffixPoolManager.get_affix_by_id("prefix_strength")
        self.assertIsNotNone(affix)
        self.assertEqual(affix.name, "力量")
    
    def test_affix_value_generation(self):
        """测试词缀数值生成"""
        affix = AffixPoolManager.get_affix_by_id("prefix_strength")
        if affix:
            value = affix.generate_value(AffixTier.TIER_3)
            self.assertInRange(value, affix.value_range.min_value * 0.5, 
                              affix.value_range.max_value * 1.5)
    
    def test_affix_pool_creation(self):
        """测试词缀池创建"""
        pools = AffixPoolManager.AFFIX_POOLS
        self.assertGreater(len(pools), 0)
    
    def test_generate_affixes_for_item(self):
        """测试为物品生成词缀"""
        affixes = AffixPoolManager.generate_affixes_for_item(
            item_type="weapon",
            rarity="rare",
            item_level=50,
            character_level=50
        )
        self.assertGreater(len(affixes), 0)


class TestItemAttributes(GameTestCase):
    """物品属性测试"""
    
    def test_item_level_requirement(self):
        """测试物品等级需求"""
        item = Item(
            id="test_item",
            name="测试物品",
            base_id="sword_1",
            rarity=ItemRarity.RARE,
            required_level=20
        )
        self.assertEqual(item.required_level, 20)
    
    def test_item_value(self):
        """测试物品价值"""
        item = Item(
            id="test_item",
            name="测试物品",
            base_id="sword_1",
            rarity=ItemRarity.RARE,
            value=1000
        )
        self.assertEqual(item.value, 1000)


class TestEquipmentSlots(GameTestCase):
    """装备槽位测试"""
    
    def test_weapon_slot(self):
        """测试武器槽位"""
        item = Item(
            id="test_sword",
            name="测试剑",
            base_id="sword_1",
            rarity=ItemRarity.COMMON,
            item_type=ItemType.WEAPON
        )
        self.assertEqual(item.item_type, ItemType.WEAPON)
    
    def test_armor_slot(self):
        """测试护甲槽位"""
        item = Item(
            id="test_helm",
            name="测试头盔",
            base_id="helm_1",
            rarity=ItemRarity.COMMON,
            item_type=ItemType.ARMOR
        )
        self.assertEqual(item.item_type, ItemType.ARMOR)


class TestSetSystem(GameTestCase):
    """套装系统测试"""
    
    def test_set_manager_initialization(self):
        """测试套装管理器初始化"""
        from entities.items.set_system import get_set_manager
        manager = get_set_manager()
        self.assertIsNotNone(manager)
        self.assertGreater(len(manager.sets), 0)
    
    def test_get_set_by_id(self):
        """测试通过ID获取套装"""
        from entities.items.set_system import get_set_manager
        manager = get_set_manager()
        item_set = manager.get_set_by_id("immortal_king")
        self.assertIsNotNone(item_set)
        self.assertEqual(item_set.name, "不朽之王")
    
    def test_set_bonus_calculation(self):
        """测试套装奖励计算"""
        from entities.items.set_system import get_set_manager
        manager = get_set_manager()
        
        # 模拟装备
        equipment = {
            "main_hand": type('obj', (object,), {'base_id': 'immortal_king_weapon'})(),
            "head": type('obj', (object,), {'base_id': 'immortal_king_helm'})(),
        }
        
        active_sets = manager.get_active_bonuses(equipment)
        self.assertIsInstance(active_sets, dict)


if __name__ == '__main__':
    unittest.main()
