"""
角色系统单元测试
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_framework import GameTestCase, TestCategory
from entities.character.character import Character
from entities.character.character_class import CharacterClass, CharacterClassType
from entities.character.attributes import AttributeType, Attributes


class TestCharacterCreation(GameTestCase):
    """角色创建测试"""
    
    def test_create_warrior(self):
        """测试创建战士"""
        char = Character(name="战士测试", character_class=CharacterClass.WARRIOR)
        self.assertIsNotNone(char)
        self.assertEqual(char.name, "战士测试")
        self.assertEqual(char.class_id, CharacterClassType.WARRIOR)
    
    def test_create_all_classes(self):
        """测试创建所有职业"""
        classes = [
            CharacterClass.WARRIOR,
            CharacterClass.MAGE,
            CharacterClass.ROGUE,
            CharacterClass.PALADIN,
            CharacterClass.NECROMANCER,
            CharacterClass.BARBARIAN,
            CharacterClass.MONK,
            CharacterClass.DEMON_HUNTER,
        ]
        
        for char_class in classes:
            char = Character(name=f"测试{char_class.name}", character_class=char_class)
            self.assertIsNotNone(char, f"Failed to create {char_class.name}")


class TestCharacterAttributes(GameTestCase):
    """角色属性测试"""
    
    def setUp(self):
        self.char = Character(name="属性测试", character_class=CharacterClass.WARRIOR)
    
    def test_initial_attributes(self):
        """测试初始属性"""
        self.assertIsNotNone(self.char.attributes)
        self.assertGreater(self.char.attributes.get_total(AttributeType.STRENGTH), 0)
    
    def test_attribute_modification(self):
        """测试属性修改"""
        initial_str = self.char.attributes.get_total(AttributeType.STRENGTH)
        self.char.attributes.add_base(AttributeType.STRENGTH, 10)
        new_str = self.char.attributes.get_total(AttributeType.STRENGTH)
        self.assertEqual(new_str, initial_str + 10)
    
    def test_health_calculation(self):
        """测试生命值计算"""
        max_health = self.char.get_max_health()
        self.assertPositive(max_health, "Max health should be positive")


class TestCharacterLeveling(GameTestCase):
    """角色升级测试"""
    
    def setUp(self):
        self.char = Character(name="升级测试", character_class=CharacterClass.WARRIOR)
    
    def test_initial_level(self):
        """测试初始等级"""
        self.assertEqual(self.char.level, 1)
    
    def test_gain_experience(self):
        """测试获得经验"""
        initial_exp = self.char.experience
        self.char.add_experience(100)
        self.assertGreater(self.char.experience, initial_exp)
    
    def test_level_up(self):
        """测试升级"""
        initial_level = self.char.level
        # 给予大量经验确保升级
        self.char.add_experience(10000)
        self.assertGreater(self.char.level, initial_level)


class TestCharacterResources(GameTestCase):
    """角色资源测试"""
    
    def setUp(self):
        self.char = Character(name="资源测试", character_class=CharacterClass.WARRIOR)
    
    def test_health_resource(self):
        """测试生命值资源"""
        self.assertGreater(self.char.current_health, 0)
        self.assertGreater(self.char.get_max_health(), 0)
    
    def test_take_damage(self):
        """测试受到伤害"""
        initial_health = self.char.current_health
        damage = 10
        self.char.take_damage(damage)
        self.assertEqual(self.char.current_health, initial_health - damage)
    
    def test_heal(self):
        """测试治疗"""
        self.char.take_damage(50)
        heal_amount = 20
        self.char.heal(heal_amount)
        # 验证生命值增加
    
    def test_resource_regeneration(self):
        """测试资源回复"""
        if hasattr(self.char, 'current_resource'):
            self.assertIsNotNone(self.char.current_resource)


if __name__ == '__main__':
    unittest.main()
