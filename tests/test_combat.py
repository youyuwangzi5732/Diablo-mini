"""
战斗系统单元测试
"""
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_framework import GameTestCase
from systems.combat.damage_calculator import (
    DamageCalculator, DamageSnapshot, DamageType, DamageSource
)


class TestDamageCalculator(GameTestCase):
    """伤害计算器测试"""
    
    def test_create_snapshot(self):
        """测试创建伤害快照"""
        snapshot = DamageSnapshot(
            attacker_id="test",
            attacker_level=1,
            base_damage_min=10,
            base_damage_max=20
        )
        self.assertIsNotNone(snapshot)
        self.assertEqual(snapshot.base_damage_min, 10)
    
    def test_calculate_base_damage(self):
        """测试基础伤害计算"""
        snapshot = DamageSnapshot(
            attacker_id="test",
            attacker_level=1,
            base_damage_min=100,
            base_damage_max=100,
            critical_chance=0,
            damage_percent=0
        )
        
        result = DamageCalculator.calculate_damage(
            snapshot=snapshot,
            target=None,
            damage_type=DamageType.PHYSICAL
        )
        
        self.assertIsNotNone(result)
        self.assertGreater(result.final_damage, 0)
    
    def test_critical_hit(self):
        """测试暴击"""
        snapshot = DamageSnapshot(
            attacker_id="test",
            attacker_level=1,
            base_damage_min=100,
            base_damage_max=100,
            critical_chance=1.0,
            critical_damage=2.0,
            damage_percent=0
        )
        
        result = DamageCalculator.calculate_damage(
            snapshot=snapshot,
            target=None,
            damage_type=DamageType.PHYSICAL
        )
        
        self.assertTrue(result.is_critical)
    
    def test_damage_types(self):
        """测试伤害类型"""
        snapshot = DamageSnapshot(
            attacker_id="test",
            attacker_level=1,
            base_damage_min=50,
            base_damage_max=50
        )
        
        for damage_type in [DamageType.PHYSICAL, DamageType.FIRE, DamageType.COLD]:
            result = DamageCalculator.calculate_damage(
                snapshot=snapshot,
                target=None,
                damage_type=damage_type
            )
            self.assertEqual(result.damage_type, damage_type)
    
    def test_armor_reduction(self):
        """测试护甲减伤"""
        snapshot = DamageSnapshot(
            attacker_id="test",
            attacker_level=70,
            base_damage_min=100,
            base_damage_max=100,
            critical_chance=0
        )
        
        target = type('obj', (object,), {
            'armor': 1000,
            'armor_percent': 0,
            'dodge_chance': 0,
            'block_chance': 0
        })()
        
        result = DamageCalculator.calculate_damage(
            snapshot=snapshot,
            target=target,
            damage_type=DamageType.PHYSICAL
        )
        
        self.assertGreater(result.armor_mitigation, 0)
        self.assertLess(result.final_damage, 100)
    
    def test_resistance_reduction(self):
        """测试抗性减伤"""
        snapshot = DamageSnapshot(
            attacker_id="test",
            attacker_level=70,
            base_damage_min=100,
            base_damage_max=100,
            critical_chance=0
        )
        
        target = type('obj', (object,), {
            'fire_resistance': 50,
            'all_resistance': 0,
            'dodge_chance': 0,
            'block_chance': 0
        })()
        
        result = DamageCalculator.calculate_damage(
            snapshot=snapshot,
            target=target,
            damage_type=DamageType.FIRE
        )
        
        self.assertGreater(result.resistance_mitigation, 0)
    
    def test_attribute_bonus(self):
        """测试属性加成"""
        snapshot_no_str = DamageSnapshot(
            attacker_id="test",
            attacker_level=1,
            base_damage_min=100,
            base_damage_max=100,
            strength=0
        )
        
        snapshot_with_str = DamageSnapshot(
            attacker_id="test",
            attacker_level=1,
            base_damage_min=100,
            base_damage_max=100,
            strength=100
        )
        
        result_no_str = DamageCalculator.calculate_damage(
            snapshot=snapshot_no_str,
            target=None,
            damage_type=DamageType.PHYSICAL
        )
        
        result_with_str = DamageCalculator.calculate_damage(
            snapshot=snapshot_with_str,
            target=None,
            damage_type=DamageType.PHYSICAL
        )
        
        self.assertGreater(result_with_str.final_damage, result_no_str.final_damage)
    
    def test_dps_calculation(self):
        """测试DPS计算"""
        snapshot = DamageSnapshot(
            attacker_id="test",
            attacker_level=1,
            base_damage_min=100,
            base_damage_max=200,
            attack_speed=1.0,
            critical_chance=0.1,
            critical_damage=1.5
        )
        
        dps = DamageCalculator.calculate_dps(snapshot)
        self.assertPositive(dps, "DPS should be positive")


class TestDamageTypes(GameTestCase):
    """伤害类型测试"""
    
    def test_true_damage_ignores_resistance(self):
        """测试真实伤害无视抗性"""
        snapshot = DamageSnapshot(
            attacker_id="test",
            attacker_level=70,
            base_damage_min=100,
            base_damage_max=100,
            critical_chance=0
        )
        
        target = type('obj', (object,), {
            'all_resistance': 100,
            'dodge_chance': 0,
            'block_chance': 0
        })()
        
        result_true = DamageCalculator.calculate_damage(
            snapshot=snapshot,
            target=target,
            damage_type=DamageType.TRUE
        )
        
        result_fire = DamageCalculator.calculate_damage(
            snapshot=snapshot,
            target=target,
            damage_type=DamageType.FIRE
        )
        
        self.assertGreater(result_true.final_damage, result_fire.final_damage)


if __name__ == '__main__':
    unittest.main()
