"""
合成系统 - 类似赫拉迪姆魔盒
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random


class RecipeType(Enum):
    UPGRADE = "upgrade"
    REROLL = "reroll"
    CONVERT = "convert"
    CRAFT = "craft"
    SOCKET = "socket"
    UNSOCKET = "unsocket"
    GEM_COMBINE = "gem_combine"
    RUNE_WORD = "rune_word"


@dataclass
class CraftingRecipe:
    id: str
    name: str
    description: str
    recipe_type: RecipeType
    
    ingredients: List[Dict[str, Any]] = field(default_factory=list)
    
    result: Dict[str, Any] = field(default_factory=dict)
    
    required_level: int = 1
    required_gold: int = 0
    
    success_chance: float = 1.0
    
    def matches(self, items: List[Any]) -> bool:
        remaining_items = list(items)
        grouped_matches: Dict[int, List[Any]] = {}
        
        for index, ingredient in enumerate(self.ingredients):
            required_count = ingredient.get("count", 1)
            matched_items = []
            
            for item in list(remaining_items):
                if self._matches_ingredient(item, ingredient):
                    matched_items.append(item)
                    if len(matched_items) == required_count:
                        break
            
            if len(matched_items) < required_count:
                return False
            
            grouped_matches[index] = matched_items
            for item in matched_items:
                remaining_items.remove(item)
        
        if remaining_items:
            return False
        
        for index, ingredient in enumerate(self.ingredients):
            matched_items = grouped_matches.get(index, [])
            if ingredient.get("same_type") and len(matched_items) > 1:
                markers = {self._get_same_type_marker(item) for item in matched_items}
                if None in markers or len(markers) != 1:
                    return False
            if ingredient.get("same_quality") and len(matched_items) > 1:
                qualities = {self._get_quality_marker(item) for item in matched_items}
                if None in qualities or len(qualities) != 1:
                    return False
        
        return True
    
    def _get_item_type(self, item: Any) -> str:
        if hasattr(item, 'item_type'):
            return item.item_type.value
        elif hasattr(item, 'gem_type'):
            return f"gem_{item.gem_type.value}"
        elif hasattr(item, 'rune_type'):
            return f"rune_{item.rune_type.value}"
        return "unknown"

    def _matches_ingredient(self, item: Any, ingredient: Dict[str, Any]) -> bool:
        ingredient_type = ingredient.get("type", "any")
        item_type = self._get_item_type(item)

        if ingredient_type != "any":
            if ingredient_type == "gem":
                if not hasattr(item, "gem_type"):
                    return False
            elif ingredient_type == "rune":
                if not hasattr(item, "rune_type"):
                    return False
            elif ingredient_type.startswith("gem_"):
                if not hasattr(item, "gem_type"):
                    return False
                gem_id = ingredient_type.split("_", 1)[1]
                if item.gem_type.value != gem_id:
                    return False
            elif ingredient_type.startswith("rune_"):
                if not hasattr(item, "rune_type"):
                    return False
                rune_id = ingredient_type.split("_", 1)[1]
                if rune_id.isdigit():
                    if item.rune_type.value != int(rune_id):
                        return False
                elif item.rune_type.name.lower() != rune_id.lower():
                    return False
            elif item_type != ingredient_type:
                return False

        if "id" in ingredient and getattr(item, "base_id", None) != ingredient["id"]:
            return False

        if "rarity" in ingredient:
            item_rarity = getattr(getattr(item, "rarity", None), "value", None)
            if item_rarity != ingredient["rarity"]:
                return False

        if "quality_min" in ingredient:
            quality = getattr(getattr(item, "quality", None), "value", None)
            if quality is None or quality < ingredient["quality_min"]:
                return False

        if "quality_max" in ingredient:
            quality = getattr(getattr(item, "quality", None), "value", None)
            if quality is None or quality > ingredient["quality_max"]:
                return False

        if "sockets_max" in ingredient:
            sockets = getattr(item, "sockets", None)
            if sockets is None or sockets > ingredient["sockets_max"]:
                return False

        if "sockets_min" in ingredient:
            sockets = getattr(item, "sockets", None)
            if sockets is None or sockets < ingredient["sockets_min"]:
                return False

        return True

    def _get_same_type_marker(self, item: Any) -> Optional[str]:
        if hasattr(item, "gem_type"):
            return f"gem:{item.gem_type.value}"
        if hasattr(item, "rune_type"):
            return f"rune:{item.rune_type.value}"
        if hasattr(item, "base_id"):
            return f"base:{item.base_id}"
        if hasattr(item, "item_type"):
            return f"type:{item.item_type.value}"
        return None

    def _get_quality_marker(self, item: Any) -> Optional[int]:
        if hasattr(item, "quality"):
            return item.quality.value
        if hasattr(item, "rarity"):
            return item.rarity.value
        return None


class CraftingSystem:
    def __init__(self):
        self.recipes: Dict[str, CraftingRecipe] = {}
        self._create_default_recipes()
    
    def _create_default_recipes(self):
        self.recipes["upgrade_rare"] = CraftingRecipe(
            id="upgrade_rare",
            name="升级稀有装备",
            description="将稀有装备升级为传奇装备",
            recipe_type=RecipeType.UPGRADE,
            ingredients=[
                {"type": "armor", "rarity": 2},
                {"type": "gem_diamond", "quality_min": 3}
            ],
            result={"rarity_upgrade": 1},
            required_level=30,
            required_gold=10000,
            success_chance=0.5
        )
        
        self.recipes["reroll_stats"] = CraftingRecipe(
            id="reroll_stats",
            name="重铸属性",
            description="重新随机装备属性",
            recipe_type=RecipeType.REROLL,
            ingredients=[
                {"type": "armor"},
                {"type": "gem_amethyst", "quality_min": 2}
            ],
            result={"reroll_affixes": True},
            required_level=10,
            required_gold=1000
        )
        
        self.recipes["add_socket"] = CraftingRecipe(
            id="add_socket",
            name="添加镶孔",
            description="为装备添加一个镶孔",
            recipe_type=RecipeType.SOCKET,
            ingredients=[
                {"type": "armor", "sockets_max": 5},
                {"type": "rune_15"}
            ],
            result={"add_socket": 1},
            required_level=20,
            required_gold=5000
        )
        
        self.recipes["combine_gems"] = CraftingRecipe(
            id="combine_gems",
            name="合成宝石",
            description="将三颗同级宝石合成为一颗更高级宝石",
            recipe_type=RecipeType.GEM_COMBINE,
            ingredients=[
                {"type": "gem", "count": 3, "same_type": True, "same_quality": True}
            ],
            result={"gem_upgrade": 1},
            required_gold=500
        )
        
        self.recipes["craft_legendary"] = CraftingRecipe(
            id="craft_legendary",
            name="打造传奇装备",
            description="使用材料打造传奇装备",
            recipe_type=RecipeType.CRAFT,
            ingredients=[
                {"type": "material", "id": "legendary_essence", "count": 5},
                {"type": "material", "id": "forgotten_soul", "count": 1}
            ],
            result={"create_legendary": True},
            required_level=50,
            required_gold=50000
        )

        self.recipes["combine_runes"] = CraftingRecipe(
            id="combine_runes",
            name="符文进阶",
            description="三枚同阶符文合成为下一阶符文",
            recipe_type=RecipeType.CONVERT,
            ingredients=[
                {"type": "rune", "count": 3, "same_type": True}
            ],
            result={"rune_upgrade": 1},
            required_level=10,
            required_gold=1200
        )

        self.recipes["combine_high_gems"] = CraftingRecipe(
            id="combine_high_gems",
            name="高阶宝石融合",
            description="三颗同类高品质宝石融合为更高品质",
            recipe_type=RecipeType.GEM_COMBINE,
            ingredients=[
                {"type": "gem", "count": 3, "same_type": True, "same_quality": True, "quality_min": 4}
            ],
            result={"gem_upgrade": 1},
            required_level=35,
            required_gold=2500
        )

        self.recipes["refine_weapon"] = CraftingRecipe(
            id="refine_weapon",
            name="淬炼武器",
            description="重铸武器词缀并保留品质",
            recipe_type=RecipeType.REROLL,
            ingredients=[
                {"type": "weapon"},
                {"type": "gem_emerald", "quality_min": 3}
            ],
            result={"reroll_affixes": True},
            required_level=20,
            required_gold=3000
        )

        self.recipes["refine_armor"] = CraftingRecipe(
            id="refine_armor",
            name="锻铸护甲",
            description="重铸护甲词缀并提升防护潜力",
            recipe_type=RecipeType.REROLL,
            ingredients=[
                {"type": "armor"},
                {"type": "gem_diamond", "quality_min": 3}
            ],
            result={"reroll_affixes": True},
            required_level=20,
            required_gold=3000
        )

        self.recipes["socket_weapon"] = CraftingRecipe(
            id="socket_weapon",
            name="武器开孔",
            description="为武器添加一个镶孔",
            recipe_type=RecipeType.SOCKET,
            ingredients=[
                {"type": "weapon", "sockets_max": 5},
                {"type": "rune_15"}
            ],
            result={"add_socket": 1},
            required_level=25,
            required_gold=7000
        )

        self.recipes["upgrade_weapon_rare"] = CraftingRecipe(
            id="upgrade_weapon_rare",
            name="稀有武器升格",
            description="将稀有武器升格为传奇",
            recipe_type=RecipeType.UPGRADE,
            ingredients=[
                {"type": "weapon", "rarity": 2},
                {"type": "gem_ruby", "quality_min": 4},
                {"type": "rune_20"}
            ],
            result={"rarity_upgrade": 1},
            required_level=45,
            required_gold=18000,
            success_chance=0.45
        )

        self.recipes["upgrade_armor_rare"] = CraftingRecipe(
            id="upgrade_armor_rare",
            name="稀有护甲升格",
            description="将稀有护甲升格为传奇",
            recipe_type=RecipeType.UPGRADE,
            ingredients=[
                {"type": "armor", "rarity": 2},
                {"type": "gem_amethyst", "quality_min": 4},
                {"type": "rune_20"}
            ],
            result={"rarity_upgrade": 1},
            required_level=45,
            required_gold=18000,
            success_chance=0.45
        )
    
    def get_recipe(self, recipe_id: str) -> Optional[CraftingRecipe]:
        return self.recipes.get(recipe_id)
    
    def get_available_recipes(self, player_level: int) -> List[CraftingRecipe]:
        return [
            recipe for recipe in self.recipes.values()
            if recipe.required_level <= player_level
        ]
    
    def find_matching_recipe(self, items: List[Any]) -> Optional[CraftingRecipe]:
        for recipe in self.recipes.values():
            if recipe.matches(items):
                return recipe
        return None
    
    def craft(self, recipe: CraftingRecipe, items: List[Any], 
              player_gold: int) -> Tuple[bool, List[Any], str]:
        if player_gold < recipe.required_gold:
            return False, items, f"金币不足，需要 {recipe.required_gold} 金币"
        
        if random.random() > recipe.success_chance:
            return False, [], "合成失败，材料已消耗"
        
        results = self._apply_recipe(recipe, items)
        
        return True, results, "合成成功！"
    
    def _apply_recipe(self, recipe: CraftingRecipe, 
                       items: List[Any]) -> List[Any]:
        results = []
        
        if recipe.recipe_type == RecipeType.GEM_COMBINE:
            if items and len(items) >= 3:
                gem = items[0]
                if hasattr(gem, 'upgrade'):
                    gem.upgrade()
                    results.append(gem)
        
        elif recipe.recipe_type == RecipeType.REROLL:
            for item in items:
                if hasattr(item, 'reforge'):
                    item.reforge()
                    results.append(item)
                    break
        
        elif recipe.recipe_type == RecipeType.UPGRADE:
            for item in items:
                if hasattr(item, 'rarity'):
                    from entities.items.item import ItemRarity
                    if item.rarity.value < ItemRarity.LEGENDARY.value:
                        item.rarity = ItemRarity(item.rarity.value + 1)
                        results.append(item)
                        break
        
        elif recipe.recipe_type == RecipeType.SOCKET:
            for item in items:
                if hasattr(item, 'sockets'):
                    item.sockets += 1
                    results.append(item)
                    break

        elif recipe.recipe_type == RecipeType.CONVERT:
            if recipe.result.get("rune_upgrade"):
                runes = [item for item in items if hasattr(item, "rune_type")]
                if runes:
                    from entities.items.rune import Rune, RuneType
                    rune_value = runes[0].rune_type.value
                    if rune_value < max(r.value for r in RuneType):
                        upgraded = Rune(RuneType(rune_value + 1))
                        results.append(upgraded)

        elif recipe.recipe_type == RecipeType.CRAFT:
            if recipe.result.get("create_legendary"):
                from entities.items.item import ItemFactory, ItemRarity
                base_ids = ItemFactory.get_base_item_ids()
                if base_ids:
                    target_id = random.choice(base_ids)
                    crafted = ItemFactory.create_item(target_id, level=50, rarity=ItemRarity.LEGENDARY)
                    if crafted:
                        results.append(crafted)
        
        return results
    
    def register_recipe(self, recipe: CraftingRecipe):
        self.recipes[recipe.id] = recipe
