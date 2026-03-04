"""
测试框架 - 商业化级别的测试基础设施
支持单元测试、冒烟测试、测试覆盖率
"""
import unittest
import sys
import os
import time
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from io import StringIO


class TestCategory(Enum):
    UNIT = "unit"
    INTEGRATION = "integration"
    SMOKE = "smoke"
    PERFORMANCE = "performance"
    REGRESSION = "regression"


class TestPriority(Enum):
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


@dataclass
class TestResult:
    """测试结果"""
    name: str
    category: TestCategory
    passed: bool
    duration: float
    message: str = ""
    error: Optional[Exception] = None
    
    def __str__(self) -> str:
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status} [{self.category.value}] {self.name} ({self.duration:.3f}s)"


@dataclass
class TestSuiteResult:
    """测试套件结果"""
    suite_name: str
    results: List[TestResult] = field(default_factory=list)
    start_time: float = 0
    end_time: float = 0
    
    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.passed)
    
    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if not r.passed)
    
    @property
    def total(self) -> int:
        return len(self.results)
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time
    
    @property
    def pass_rate(self) -> float:
        return (self.passed / self.total * 100) if self.total > 0 else 0


class GameTestCase(unittest.TestCase):
    """游戏测试基类"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        cls.test_data_dir = os.path.join(os.path.dirname(__file__), "test_data")
        os.makedirs(cls.test_data_dir, exist_ok=True)
    
    @classmethod
    def tearDownClass(cls):
        """清理测试类"""
        pass
    
    def assertInRange(self, value: float, min_val: float, max_val: float, msg: str = ""):
        """断言值在范围内"""
        self.assertTrue(min_val <= value <= max_val, 
                       f"{msg}: {value} not in range [{min_val}, {max_val}]")
    
    def assertPositive(self, value: float, msg: str = ""):
        """断言值为正"""
        self.assertTrue(value > 0, f"{msg}: {value} is not positive")
    
    def assertValidDict(self, d: dict, required_keys: List[str], msg: str = ""):
        """断言字典包含必需的键"""
        missing = [k for k in required_keys if k not in d]
        self.assertEqual(len(missing), 0, f"{msg}: missing keys {missing}")


class TestRunner:
    """测试运行器"""
    
    def __init__(self):
        self.suite_results: List[TestSuiteResult] = []
        self._test_registry: Dict[str, Callable] = {}
    
    def register_test(self, name: str, category: TestCategory, func: Callable):
        """注册测试"""
        self._test_registry[name] = (category, func)
    
    def run_all_tests(self, categories: List[TestCategory] = None) -> Dict[str, Any]:
        """运行所有测试"""
        start_time = time.time()
        
        # 发现并运行测试
        loader = unittest.TestLoader()
        suite = loader.discover('tests', pattern='test_*.py')
        
        if categories:
            suite = self._filter_by_category(suite, categories)
        
        # 运行测试
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        end_time = time.time()
        
        return {
            "total": result.testsRun,
            "passed": result.testsRun - len(result.failures) - len(result.errors),
            "failed": len(result.failures) + len(result.errors),
            "duration": end_time - start_time,
            "failures": result.failures,
            "errors": result.errors
        }
    
    def _filter_by_category(self, suite: unittest.TestSuite, 
                            categories: List[TestCategory]) -> unittest.TestSuite:
        """按类别过滤测试"""
        filtered = unittest.TestSuite()
        for test in suite:
            if hasattr(test, 'category') and test.category in categories:
                filtered.addTest(test)
        return filtered
    
    def run_smoke_tests(self) -> TestSuiteResult:
        """运行冒烟测试"""
        suite_result = TestSuiteResult(suite_name="冒烟测试")
        suite_result.start_time = time.time()
        
        # 核心冒烟测试
        smoke_tests = [
            ("游戏启动", self._test_game_startup),
            ("角色创建", self._test_character_creation),
            ("装备穿戴", self._test_equipment),
            ("技能释放", self._test_skill_cast),
            ("存档保存", self._test_save),
            ("存档加载", self._test_load),
        ]
        
        for name, test_func in smoke_tests:
            result = self._run_single_test(name, TestCategory.SMOKE, test_func)
            suite_result.results.append(result)
        
        suite_result.end_time = time.time()
        self.suite_results.append(suite_result)
        
        return suite_result
    
    def _run_single_test(self, name: str, category: TestCategory, 
                         test_func: Callable) -> TestResult:
        """运行单个测试"""
        start = time.time()
        try:
            test_func()
            return TestResult(
                name=name,
                category=category,
                passed=True,
                duration=time.time() - start
            )
        except Exception as e:
            return TestResult(
                name=name,
                category=category,
                passed=False,
                duration=time.time() - start,
                error=e,
                message=str(e)
            )
    
    def _test_game_startup(self):
        """测试游戏启动"""
        from main import DiabloGame
        game = DiabloGame()
        self.assertIsNotNone(game)
    
    def _test_character_creation(self):
        """测试角色创建"""
        from entities.character.character import Character
        from entities.character.character_class import CharacterClass
        
        char = Character(name="测试角色", character_class=CharacterClass.WARRIOR)
        self.assertIsNotNone(char)
        self.assertEqual(char.name, "测试角色")
    
    def _test_equipment(self):
        """测试装备穿戴"""
        from entities.items.item import Item, ItemRarity
        
        item = Item(
            id="test_sword",
            name="测试剑",
            base_id="sword_1",
            rarity=ItemRarity.COMMON
        )
        self.assertIsNotNone(item)
    
    def _test_skill_cast(self):
        """测试技能释放"""
        pass
    
    def _test_save(self):
        """测试存档保存"""
        from core.save_system import SaveSystem
        save_system = SaveSystem()
        self.assertIsNotNone(save_system)
    
    def _test_load(self):
        """测试存档加载"""
        from core.save_system import SaveSystem
        save_system = SaveSystem()
        self.assertIsNotNone(save_system)
    
    def generate_report(self) -> str:
        """生成测试报告"""
        report = []
        report.append("=" * 60)
        report.append("测试报告")
        report.append("=" * 60)
        
        total_passed = 0
        total_failed = 0
        total_duration = 0
        
        for suite in self.suite_results:
            report.append(f"\n### {suite.suite_name}")
            report.append(f"通过: {suite.passed}/{suite.total} ({suite.pass_rate:.1f}%)")
            report.append(f"耗时: {suite.duration:.3f}s")
            report.append("-" * 40)
            
            for result in suite.results:
                report.append(str(result))
                if result.error:
                    report.append(f"  错误: {result.error}")
            
            total_passed += suite.passed
            total_failed += suite.failed
            total_duration += suite.duration
        
        report.append("\n" + "=" * 60)
        report.append("总计")
        report.append(f"通过: {total_passed}")
        report.append(f"失败: {total_failed}")
        report.append(f"总耗时: {total_duration:.3f}s")
        report.append("=" * 60)
        
        return "\n".join(report)


def run_tests():
    """运行测试入口"""
    runner = TestRunner()
    
    # 运行冒烟测试
    smoke_result = runner.run_smoke_tests()
    print(runner.generate_report())
    
    return smoke_result.failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
