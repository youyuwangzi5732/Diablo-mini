"""
NPC对话和交易界面
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
import pygame

from .font_manager import get_font

from .ui_element import UIElement, UIButton, UILabel, UIPanel
from .ui_manager import UIManager
from config.game_config import ColorConfig
from .ui_theme import draw_panel, font as ui_font, line_height, ui, PALETTE


@dataclass
class VendorItem:
    item: Any
    price: int
    stock: int = -1
    currency: str = "gold"


class VendorUI:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = False
        
        self.base_panel_width = 800
        self.base_panel_height = 500
        self.panel_width = self.base_panel_width
        self.panel_height = self.base_panel_height
        
        self.vendor: Optional[Any] = None
        self.player: Optional[Any] = None
        
        self.vendor_items: List[VendorItem] = []
        self.player_items: List[Any] = []
        
        self.selected_vendor_item: Optional[int] = None
        self.selected_player_item: Optional[int] = None
        
        self.scroll_offset_vendor = 0
        self.scroll_offset_player = 0
        
        self.tab = "buy"
    
    def toggle(self):
        self.visible = not self.visible
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def set_vendor(self, vendor: Any, player: Any):
        self.vendor = vendor
        self.player = player
        
        if vendor and hasattr(vendor, 'items'):
            self.vendor_items = [
                VendorItem(item=item, price=getattr(item, 'value', 100))
                for item in vendor.items
            ]
        
        if player and hasattr(player, 'inventory'):
            self.player_items = [item for item in player.inventory if item is not None]
    
    def get_panel_position(self) -> tuple:
        x = (self.screen_width - self.panel_width) // 2
        y = (self.screen_height - self.panel_height) // 2
        return (x, y)

    def _apply_ui_scale(self):
        self.panel_width = ui(self.base_panel_width)
        self.panel_height = ui(self.base_panel_height)
    
    def update(self, delta_time: float):
        pass
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        self._apply_ui_scale()
        
        panel_x, panel_y = self.get_panel_position()
        
        panel_surface = pygame.Surface(
            (self.panel_width, self.panel_height),
            pygame.SRCALPHA
        )
        draw_panel(panel_surface, self.panel_width, self.panel_height, "交易", "圆角一体化商店")
        
        self._render_header(panel_surface)
        self._render_tabs(panel_surface)
        
        if self.tab == "buy":
            self._render_vendor_items(panel_surface)
        else:
            self._render_player_items(panel_surface)
        
        self._render_player_gold(panel_surface)
        self._render_buttons(panel_surface)
        
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def _render_header(self, surface: pygame.Surface):
        font = ui_font("section", bold=True)
        
        vendor_name = getattr(self.vendor, 'name', '商人') if self.vendor else '商人'
        title = font.render(f"{vendor_name} 的商店", True, PALETTE["title_text"][:3])
        surface.blit(title, (ui(20), ui(14)))
    
    def _render_tabs(self, surface: pygame.Surface):
        font = ui_font("body", bold=True)
        
        tab_buy_color = (80, 80, 80) if self.tab == "buy" else (50, 50, 50)
        tab_sell_color = (80, 80, 80) if self.tab == "sell" else (50, 50, 50)
        
        pygame.draw.rect(surface, tab_buy_color, (ui(20), ui(58), ui(100), ui(35)), border_radius=ui(10))
        pygame.draw.rect(surface, PALETTE["panel_border"][:3], (ui(20), ui(58), ui(100), ui(35)), 1, border_radius=ui(10))
        
        buy_text = font.render("购买", True, (255, 255, 255))
        surface.blit(buy_text, (ui(55), ui(65)))
        
        pygame.draw.rect(surface, tab_sell_color, (ui(130), ui(58), ui(100), ui(35)), border_radius=ui(10))
        pygame.draw.rect(surface, PALETTE["panel_border"][:3], (ui(130), ui(58), ui(100), ui(35)), 1, border_radius=ui(10))
        
        sell_text = font.render("出售", True, (255, 255, 255))
        surface.blit(sell_text, (ui(160), ui(65)))
    
    def _render_vendor_items(self, surface: pygame.Surface):
        font = ui_font("body")
        font_small = ui_font("small")
        
        start_y = ui(104)
        item_height = ui(54)
        visible_items = 7
        
        for i, vendor_item in enumerate(self.vendor_items[self.scroll_offset_vendor:self.scroll_offset_vendor + visible_items]):
            actual_index = i + self.scroll_offset_vendor
            y = start_y + i * item_height
            
            is_selected = self.selected_vendor_item == actual_index
            bg_color = (60, 50, 40) if is_selected else (40, 35, 30)
            
            pygame.draw.rect(surface, bg_color, (ui(20), y, self.panel_width - ui(40), item_height - ui(6)), border_radius=ui(9))
            
            if is_selected:
                pygame.draw.rect(surface, PALETTE["accent"][:3], (ui(20), y, self.panel_width - ui(40), item_height - ui(6)), 2, border_radius=ui(9))
            
            item = vendor_item.item
            item_name = getattr(item, 'name', '未知物品')
            rarity = getattr(item, 'rarity', None)
            
            rarity_colors = {
                0: ColorConfig.RARITY_COMMON,
                1: ColorConfig.RARITY_MAGIC,
                2: ColorConfig.RARITY_RARE,
                3: ColorConfig.RARITY_LEGENDARY,
                4: ColorConfig.RARITY_SET,
            }
            
            text_color = rarity_colors.get(
                rarity.value if hasattr(rarity, 'value') else rarity,
                (200, 200, 200)
            )
            
            name_text = font.render(item_name, True, text_color)
            surface.blit(name_text, (ui(30), y + ui(8)))
            
            level = getattr(item, 'required_level', 1)
            level_text = font_small.render(f"等级: {level}", True, (150, 150, 150))
            surface.blit(level_text, (ui(30), y + ui(30)))
            
            price_text = font.render(f"{vendor_item.price} 金币", True, (255, 215, 0))
            surface.blit(price_text, (self.panel_width - ui(180), y + ui(15)))
    
    def _render_player_items(self, surface: pygame.Surface):
        font = get_font(16)
        font_small = get_font(14)
        
        start_y = 100
        item_height = 50
        visible_items = 7
        
        for i, item in enumerate(self.player_items[self.scroll_offset_player:self.scroll_offset_player + visible_items]):
            if item is None:
                continue
                
            actual_index = i + self.scroll_offset_player
            y = start_y + i * item_height
            
            is_selected = self.selected_player_item == actual_index
            bg_color = (60, 50, 40) if is_selected else (40, 35, 30)
            
            pygame.draw.rect(surface, bg_color, (20, y, self.panel_width - 40, item_height - 5))
            
            if is_selected:
                pygame.draw.rect(surface, (200, 180, 100), (20, y, self.panel_width - 40, item_height - 5), 2)
            
            item_name = getattr(item, 'name', '未知物品')
            rarity = getattr(item, 'rarity', None)
            
            rarity_colors = {
                0: ColorConfig.RARITY_COMMON,
                1: ColorConfig.RARITY_MAGIC,
                2: ColorConfig.RARITY_RARE,
                3: ColorConfig.RARITY_LEGENDARY,
                4: ColorConfig.RARITY_SET,
            }
            
            text_color = rarity_colors.get(
                rarity.value if hasattr(rarity, 'value') else rarity,
                (200, 200, 200)
            )
            
            name_text = font.render(item_name, True, text_color)
            surface.blit(name_text, (30, y + 8))
            
            sell_price = int(getattr(item, 'value', 100) * 0.25)
            price_text = font.render(f"{sell_price} 金币", True, (255, 215, 0))
            surface.blit(price_text, (self.panel_width - 150, y + 15))
    
    def _render_player_gold(self, surface: pygame.Surface):
        font = get_font(18)
        
        gold = getattr(self.player, 'gold', 0) if self.player else 0
        
        gold_text = font.render(f"金币: {gold}", True, (255, 215, 0))
        surface.blit(gold_text, (20, self.panel_height - 50))
    
    def _render_buttons(self, surface: pygame.Surface):
        font = get_font(16)
        
        btn_buy_x = self.panel_width - 220
        btn_y = self.panel_height - 50
        
        btn_color = (60, 100, 60) if self.tab == "buy" and self.selected_vendor_item is not None else (50, 50, 50)
        pygame.draw.rect(surface, btn_color, (btn_buy_x, btn_y, 100, 35))
        pygame.draw.rect(surface, (100, 100, 100), (btn_buy_x, btn_y, 100, 35), 1)
        
        btn_text = font.render("购买", True, (255, 255, 255))
        surface.blit(btn_text, (btn_buy_x + 30, btn_y + 8))
        
        btn_close_x = btn_buy_x + 110
        pygame.draw.rect(surface, (80, 50, 50), (btn_close_x, btn_y, 100, 35))
        pygame.draw.rect(surface, (100, 100, 100), (btn_close_x, btn_y, 100, 35), 1)
        
        close_text = font.render("关闭", True, (255, 255, 255))
        surface.blit(close_text, (btn_close_x + 30, btn_y + 8))
    
    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        
        panel_x, panel_y = self.get_panel_position()
        local_pos = (pos[0] - panel_x, pos[1] - panel_y)
        
        if 20 <= local_pos[0] <= 120 and 55 <= local_pos[1] <= 90:
            self.tab = "buy"
            return True
        
        if 130 <= local_pos[0] <= 230 and 55 <= local_pos[1] <= 90:
            self.tab = "sell"
            return True
        
        if self.tab == "buy":
            self._handle_vendor_item_click(local_pos)
        else:
            self._handle_player_item_click(local_pos)
        
        btn_buy_x = self.panel_width - 220
        btn_y = self.panel_height - 50
        
        if btn_buy_x <= local_pos[0] <= btn_buy_x + 100 and btn_y <= local_pos[1] <= btn_y + 35:
            self._on_buy_click()
            return True
        
        btn_close_x = btn_buy_x + 110
        if btn_close_x <= local_pos[0] <= btn_close_x + 100 and btn_y <= local_pos[1] <= btn_y + 35:
            self.hide()
            return True
        
        return True
    
    def _handle_vendor_item_click(self, local_pos: tuple):
        start_y = 100
        item_height = 50
        
        for i in range(7):
            y = start_y + i * item_height
            if 20 <= local_pos[0] <= self.panel_width - 20 and y <= local_pos[1] <= y + item_height - 5:
                self.selected_vendor_item = i + self.scroll_offset_vendor
                return
    
    def _handle_player_item_click(self, local_pos: tuple):
        start_y = 100
        item_height = 50
        
        for i in range(7):
            y = start_y + i * item_height
            if 20 <= local_pos[0] <= self.panel_width - 20 and y <= local_pos[1] <= y + item_height - 5:
                self.selected_player_item = i + self.scroll_offset_player
                return
    
    def _on_buy_click(self):
        if self.tab == "buy" and self.selected_vendor_item is not None:
            if self.selected_vendor_item < len(self.vendor_items):
                vendor_item = self.vendor_items[self.selected_vendor_item]
                
                if self.player and hasattr(self.player, 'gold'):
                    if self.player.gold >= vendor_item.price:
                        self.player.gold -= vendor_item.price
                        
                        empty_slot = self._find_empty_inventory_slot()
                        if empty_slot >= 0:
                            self.player.inventory[empty_slot] = vendor_item.item
                            self.ui_manager.add_notification(
                                f"购买了 {vendor_item.item.name}",
                                (100, 255, 100)
                            )
                            
                            self.player_items = [item for item in self.player.inventory if item is not None]
                        else:
                            self.player.gold += vendor_item.price
                            self.ui_manager.add_notification("背包已满!", (255, 100, 100))
                    else:
                        self.ui_manager.add_notification("金币不足!", (255, 100, 100))
        
        elif self.tab == "sell" and self.selected_player_item is not None:
            if self.selected_player_item < len(self.player_items):
                item = self.player_items[self.selected_player_item]
                
                if item and self.player:
                    sell_price = int(getattr(item, 'value', 100) * 0.25)
                    self.player.gold += sell_price
                    
                    inv_index = self.player.inventory.index(item)
                    self.player.inventory[inv_index] = None
                    
                    self.ui_manager.add_notification(
                        f"出售了 {item.name} 获得 {sell_price} 金币",
                        (255, 215, 0)
                    )
                    
                    self.player_items = [i for i in self.player.inventory if i is not None]
                    self.selected_player_item = None
    
    def _find_empty_inventory_slot(self) -> int:
        if not self.player:
            return -1
        
        for i, item in enumerate(self.player.inventory):
            if item is None:
                return i
        return -1
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height


class DialogueUI:
    def __init__(self, ui_manager: UIManager):
        self.ui_manager = ui_manager
        self.screen_width = ui_manager.screen_width
        self.screen_height = ui_manager.screen_height
        
        self.visible = False
        
        self.panel_width = 600
        self.panel_height = 300
        
        self.npc: Optional[Any] = None
        self.player: Optional[Any] = None
        
        self.current_dialogue: str = ""
        self.dialogue_options: List[Dict[str, Any]] = []
        self.selected_option: int = 0
        
        self.dialogue_history: List[str] = []
    
    def toggle(self):
        self.visible = not self.visible
    
    def show(self):
        self.visible = True
    
    def hide(self):
        self.visible = False
    
    def set_npc(self, npc: Any, player: Any):
        self.npc = npc
        self.player = player
        
        if npc:
            if hasattr(npc, "get_greeting"):
                self.current_dialogue = npc.get_greeting()
            else:
                self.current_dialogue = getattr(npc, 'greeting', "你好，冒险者！")
            self._load_dialogue_options()
    
    def _load_dialogue_options(self):
        self.dialogue_options = []
        
        if not self.npc:
            return
        
        npc_type = getattr(self.npc, 'npc_type', None)
        if hasattr(npc_type, 'value'):
            npc_type = npc_type.value
        
        if npc_type == "merchant":
            self.dialogue_options = [
                {"id": "trade", "text": "我想买东西", "action": "open_trade"},
                {"id": "sell", "text": "我想卖东西", "action": "open_sell"},
                {"id": "gossip", "text": "最近有什么消息吗？", "action": "gossip"},
                {"id": "bye", "text": "再见", "action": "close"},
            ]
        elif npc_type == "blacksmith":
            self.dialogue_options = [
                {"id": "repair", "text": "修理装备", "action": "open_repair"},
                {"id": "craft", "text": "锻造物品", "action": "open_craft"},
                {"id": "bye", "text": "再见", "action": "close"},
            ]
        elif npc_type == "jeweler":
            self.dialogue_options = [
                {"id": "gem_combine", "text": "合成宝石", "action": "open_gem_combine"},
                {"id": "add_socket", "text": "为装备开孔", "action": "open_socket"},
                {"id": "bye", "text": "再见", "action": "close"},
            ]
        elif npc_type == "quest_giver":
            self.dialogue_options = [
                {"id": "quest", "text": "有什么任务吗？", "action": "show_quests"},
                {"id": "ending_review", "text": "查看章节结局回顾", "action": "open_progression"},
                {"id": "branch_merchant", "text": "支持商会补给线", "action": "choose_branch_merchant"},
                {"id": "branch_guard", "text": "支持镇卫强攻线", "action": "choose_branch_guard"},
                {"id": "bye", "text": "再见", "action": "close"},
            ]
        elif npc_type == "teleporter":
            self.dialogue_options = [
                {"id": "waypoint", "text": "打开传送地图", "action": "open_waypoint"},
                {"id": "rift", "text": "进入秘境", "action": "open_rift"},
                {"id": "bye", "text": "再见", "action": "close"},
            ]
        else:
            self.dialogue_options = [
                {"id": "talk", "text": "聊聊吧", "action": "gossip"},
                {"id": "bye", "text": "再见", "action": "close"},
            ]
    
    def get_panel_position(self) -> tuple:
        x = (self.screen_width - self.panel_width) // 2
        y = self.screen_height - self.panel_height - 50
        return (x, y)
    
    def update(self, delta_time: float):
        pass
    
    def render(self, surface: pygame.Surface):
        if not self.visible:
            return
        
        panel_x, panel_y = self.get_panel_position()
        
        panel_surface = pygame.Surface(
            (self.panel_width, self.panel_height),
            pygame.SRCALPHA
        )
        panel_surface.fill((20, 20, 20, 230))
        pygame.draw.rect(panel_surface, (100, 100, 100),
                         (0, 0, self.panel_width, self.panel_height), 2)
        
        self._render_npc_portrait(panel_surface)
        self._render_dialogue_text(panel_surface)
        self._render_options(panel_surface)
        
        surface.blit(panel_surface, (panel_x, panel_y))
    
    def _render_npc_portrait(self, surface: pygame.Surface):
        portrait_rect = pygame.Rect(15, 15, 80, 80)
        pygame.draw.rect(surface, (50, 50, 50), portrait_rect)
        pygame.draw.rect(surface, (100, 100, 100), portrait_rect, 2)
        
        npc_name = getattr(self.npc, 'name', 'NPC') if self.npc else 'NPC'
        font = get_font(14)
        name_text = font.render(npc_name, True, (200, 200, 200))
        surface.blit(name_text, (15, 100))
    
    def _render_dialogue_text(self, surface: pygame.Surface):
        font = get_font(16)
        
        text_area = pygame.Rect(110, 15, self.panel_width - 130, 100)
        
        words = self.current_dialogue.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] < text_area.width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word + " "
        lines.append(current_line)
        
        for i, line in enumerate(lines[:5]):
            text = font.render(line, True, (255, 255, 255))
            surface.blit(text, (text_area.x, text_area.y + i * 22))
    
    def _render_options(self, surface: pygame.Surface):
        font = get_font(16)
        
        start_y = 130
        
        pygame.draw.line(surface, (80, 80, 80), (10, start_y - 5), (self.panel_width - 10, start_y - 5), 1)
        
        for i, option in enumerate(self.dialogue_options):
            y = start_y + i * 35
            
            is_selected = self.selected_option == i
            bg_color = (60, 50, 40) if is_selected else (40, 35, 30)
            
            option_rect = pygame.Rect(20, y, self.panel_width - 40, 30)
            pygame.draw.rect(surface, bg_color, option_rect)
            
            if is_selected:
                pygame.draw.rect(surface, (200, 180, 100), option_rect, 2)
            
            text = font.render(option["text"], True, (255, 255, 255))
            surface.blit(text, (30, y + 7))
    
    def handle_click(self, pos: tuple) -> bool:
        if not self.visible:
            return False
        
        panel_x, panel_y = self.get_panel_position()
        local_pos = (pos[0] - panel_x, pos[1] - panel_y)
        
        start_y = 130
        
        for i, option in enumerate(self.dialogue_options):
            y = start_y + i * 35
            
            if 20 <= local_pos[0] <= self.panel_width - 20 and y <= local_pos[1] <= y + 30:
                self.selected_option = i
                self._execute_option(option)
                return True
        
        return True
    
    def _execute_option(self, option: Dict[str, Any]):
        action = option.get("action", "")
        
        if action == "close":
            self.hide()
        elif action == "open_trade" or action == "open_sell":
            self.ui_manager.trigger_callback("open_vendor", self.npc)
        elif action == "open_repair":
            self.ui_manager.trigger_callback("open_repair", self.npc)
        elif action == "open_craft":
            self.ui_manager.trigger_callback("open_craft", self.npc, "craft")
        elif action == "open_gem_combine":
            self.ui_manager.trigger_callback("open_craft", self.npc, "gem_combine")
        elif action == "open_socket":
            self.ui_manager.trigger_callback("open_craft", self.npc, "socket")
        elif action == "show_quests":
            self.ui_manager.trigger_callback("show_quests", self.npc)
        elif action == "open_progression":
            self.ui_manager.trigger_callback("open_progression", self.npc)
        elif action == "open_waypoint":
            self.ui_manager.trigger_callback("open_waypoint", self.npc)
        elif action == "open_rift":
            self.ui_manager.trigger_callback("open_rift", self.npc)
        elif action == "choose_branch_merchant":
            self.ui_manager.trigger_callback("select_story_branch", self.npc, "merchant")
        elif action == "choose_branch_guard":
            self.ui_manager.trigger_callback("select_story_branch", self.npc, "guard")
        elif action == "gossip":
            self._show_gossip()
    
    def _show_gossip(self):
        gossips = [
            "最近听说北边的森林里出现了不少怪物，你要小心啊。",
            "商队说地狱的裂隙越来越大了，不知道会发生什么。",
            "有个冒险者在遗迹里发现了一件传说中的装备！",
            "天气越来越冷了，感觉有什么不祥的事情要发生。",
        ]
        
        import random
        self.current_dialogue = random.choice(gossips)
    
    def handle_key(self, key: int):
        if not self.visible:
            return
        
        if key == pygame.K_UP:
            self.selected_option = max(0, self.selected_option - 1)
        elif key == pygame.K_DOWN:
            self.selected_option = min(len(self.dialogue_options) - 1, self.selected_option + 1)
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            if self.dialogue_options:
                self._execute_option(self.dialogue_options[self.selected_option])
        elif key == pygame.K_ESCAPE:
            self.hide()
    
    def resize(self, width: int, height: int):
        self.screen_width = width
        self.screen_height = height
