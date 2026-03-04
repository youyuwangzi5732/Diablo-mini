"""
商人交易系统
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import random

from entities.items import ItemFactory, ItemRarity


class TransactionType(Enum):
    BUY = "buy"
    SELL = "sell"
    REPAIR = "repair"
    REPAIR_ALL = "repair_all"
    IDENTIFY = "identify"
    SOCKET = "socket"


@dataclass
class ShopSlot:
    item: Any
    price: int
    currency: str = "gold"
    quantity: int = -1
    original_quantity: int = -1
    
    is_sold_out: bool = False


@dataclass
class Transaction:
    type: TransactionType
    items: List[Any] = field(default_factory=list)
    total_cost: int = 0
    currency: str = "gold"
    
    success: bool = False
    message: str = ""


class Vendor:
    def __init__(self, vendor_id: str, name: str, vendor_type: str):
        self.id = vendor_id
        self.name = name
        self.vendor_type = vendor_type
        
        self.shop_slots: List[ShopSlot] = []
        self.buy_multiplier = 0.5
        self.sell_multiplier = 1.0
        
        self.repair_base_cost = 10
        self.identify_cost = 100
        
        self.inventory_refresh_time = 300.0
        self.last_refresh = 0.0
        
        self._generate_inventory()
    
    def _generate_inventory(self):
        self.shop_slots.clear()
        
        if self.vendor_type == "merchant":
            self._generate_merchant_inventory()
        elif self.vendor_type == "blacksmith":
            self._generate_blacksmith_inventory()
        elif self.vendor_type == "jeweler":
            self._generate_jeweler_inventory()
    
    def _generate_merchant_inventory(self):
        items = [
            ("health_potion_small", 50, 10),
            ("health_potion_large", 200, 5),
            ("health_potion_super", 500, 3),
            ("mana_potion_small", 50, 10),
            ("mana_potion_large", 200, 5),
            ("town_portal", 100, 10),
            ("identify_scroll", 50, 10),
        ]
        
        for item_id, price, quantity in items:
            item = ItemFactory.create_item(item_id, 1, ItemRarity.COMMON)
            if item:
                self.shop_slots.append(ShopSlot(
                    item=item,
                    price=price,
                    quantity=quantity,
                    original_quantity=quantity
                ))
    
    def _generate_blacksmith_inventory(self):
        pass
    
    def _generate_jeweler_inventory(self):
        from entities.items.gem import Gem, GemType, GemQuality
        
        gems = [
            (GemType.RUBY, GemQuality.STANDARD, 500),
            (GemType.SAPPHIRE, GemQuality.STANDARD, 500),
            (GemType.EMERALD, GemQuality.STANDARD, 500),
            (GemType.TOPAZ, GemQuality.STANDARD, 500),
            (GemType.AMETHYST, GemQuality.STANDARD, 500),
            (GemType.DIAMOND, GemQuality.STANDARD, 1000),
        ]
        
        for gem_type, quality, price in gems:
            gem = Gem(gem_type, quality)
            self.shop_slots.append(ShopSlot(
                item=gem,
                price=price,
                quantity=5,
                original_quantity=5
            ))
    
    def get_item_price(self, item: Any, is_selling: bool = False) -> int:
        base_value = item.get_sell_value() if hasattr(item, 'get_sell_value') else 10
        
        if is_selling:
            return int(base_value * self.buy_multiplier)
        else:
            return int(base_value * self.sell_multiplier)
    
    def can_buy(self, slot_index: int, player_gold: int) -> Tuple[bool, str]:
        if slot_index < 0 or slot_index >= len(self.shop_slots):
            return False, "无效的商品槽位"
        
        slot = self.shop_slots[slot_index]
        
        if slot.is_sold_out:
            return False, "商品已售罄"
        
        if player_gold < slot.price:
            return False, f"金币不足，需要 {slot.price} 金币"
        
        return True, ""
    
    def buy_item(self, slot_index: int) -> Tuple[Optional[Any], int, str]:
        if slot_index < 0 or slot_index >= len(self.shop_slots):
            return None, 0, "无效的商品槽位"
        
        slot = self.shop_slots[slot_index]
        
        if slot.is_sold_out:
            return None, 0, "商品已售罄"
        
        item = slot.item
        
        if slot.quantity > 0:
            slot.quantity -= 1
            if slot.quantity <= 0:
                slot.is_sold_out = True
        
        return item, slot.price, f"购买了 {item.name}"
    
    def sell_item(self, item: Any) -> Tuple[int, str]:
        price = self.get_item_price(item, is_selling=True)
        return price, f"出售了 {item.name}，获得 {price} 金币"
    
    def get_repair_cost(self, item: Any) -> int:
        if not hasattr(item, 'durability') or not hasattr(item, 'max_durability'):
            return 0
        
        damage = item.max_durability - item.durability
        return int(damage * self.repair_base_cost)
    
    def repair_item(self, item: Any, player_gold: int) -> Tuple[bool, int, str]:
        cost = self.get_repair_cost(item)
        
        if cost <= 0:
            return True, 0, "装备无需修理"
        
        if player_gold < cost:
            return False, 0, f"金币不足，需要 {cost} 金币"
        
        if hasattr(item, 'repair'):
            item.repair()
        
        return True, cost, f"修理完成，花费 {cost} 金币"
    
    def refresh_inventory(self, current_time: float):
        if current_time - self.last_refresh >= self.inventory_refresh_time:
            self._generate_inventory()
            self.last_refresh = current_time


class TradingSystem:
    def __init__(self):
        self.vendors: Dict[str, Vendor] = {}
        self._create_default_vendors()
    
    def _create_default_vendors(self):
        self.vendors["merchant"] = Vendor("merchant", "商人", "merchant")
        self.vendors["blacksmith"] = Vendor("blacksmith", "铁匠", "blacksmith")
        self.vendors["jeweler"] = Vendor("jeweler", "珠宝匠", "jeweler")
    
    def get_vendor(self, vendor_id: str) -> Optional[Vendor]:
        return self.vendors.get(vendor_id)
    
    def process_transaction(self, transaction: Transaction, 
                            player_gold: int, player_inventory: List[Any]) -> Transaction:
        if transaction.type == TransactionType.BUY:
            return self._process_buy(transaction, player_gold, player_inventory)
        
        elif transaction.type == TransactionType.SELL:
            return self._process_sell(transaction, player_gold, player_inventory)
        
        elif transaction.type == TransactionType.REPAIR:
            return self._process_repair(transaction, player_gold)
        
        elif transaction.type == TransactionType.REPAIR_ALL:
            return self._process_repair_all(transaction, player_gold, player_inventory)
        
        return transaction
    
    def _process_buy(self, transaction: Transaction, 
                     player_gold: int, player_inventory: List[Any]) -> Transaction:
        total_cost = transaction.total_cost
        
        if player_gold < total_cost:
            transaction.success = False
            transaction.message = f"金币不足，需要 {total_cost} 金币"
            return transaction
        
        for item in transaction.items:
            if item:
                empty_slot = self._find_empty_inventory_slot(player_inventory)
                if empty_slot == -1:
                    transaction.success = False
                    transaction.message = "背包已满"
                    return transaction
                
                player_inventory[empty_slot] = item
        
        transaction.success = True
        transaction.message = f"购买成功，花费 {total_cost} 金币"
        return transaction
    
    def _process_sell(self, transaction: Transaction,
                      player_gold: int, player_inventory: List[Any]) -> Transaction:
        total_value = 0
        
        for item in transaction.items:
            if item:
                value = item.get_sell_value() if hasattr(item, 'get_sell_value') else 10
                total_value += value
                
                if item in player_inventory:
                    index = player_inventory.index(item)
                    player_inventory[index] = None
        
        transaction.total_cost = -total_value
        transaction.success = True
        transaction.message = f"出售成功，获得 {total_value} 金币"
        return transaction
    
    def _process_repair(self, transaction: Transaction, player_gold: int) -> Transaction:
        total_cost = transaction.total_cost
        
        if player_gold < total_cost:
            transaction.success = False
            transaction.message = f"金币不足，需要 {total_cost} 金币"
            return transaction
        
        for item in transaction.items:
            if item and hasattr(item, 'repair'):
                item.repair()
        
        transaction.success = True
        transaction.message = f"修理完成，花费 {total_cost} 金币"
        return transaction
    
    def _process_repair_all(self, transaction: Transaction,
                            player_gold: int, player_inventory: List[Any]) -> Transaction:
        total_cost = 0
        items_to_repair = []
        
        for item in player_inventory:
            if item and hasattr(item, 'durability') and hasattr(item, 'max_durability'):
                if item.durability < item.max_durability:
                    damage = item.max_durability - item.durability
                    cost = int(damage * 10)
                    total_cost += cost
                    items_to_repair.append(item)
        
        if total_cost == 0:
            transaction.success = True
            transaction.message = "没有需要修理的装备"
            return transaction
        
        if player_gold < total_cost:
            transaction.success = False
            transaction.message = f"金币不足，需要 {total_cost} 金币"
            return transaction
        
        for item in items_to_repair:
            if hasattr(item, 'repair'):
                item.repair()
        
        transaction.total_cost = total_cost
        transaction.success = True
        transaction.message = f"全部修理完成，花费 {total_cost} 金币"
        return transaction
    
    def _find_empty_inventory_slot(self, inventory: List[Any]) -> int:
        for i, item in enumerate(inventory):
            if item is None:
                return i
        return -1
