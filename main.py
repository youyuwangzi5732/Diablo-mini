"""
暗黑迷你 - Diablo Mini
主游戏入口（完整版）
"""
import pygame
import sys
import os
from typing import Optional, List, Dict, Any, Tuple

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core import GameEngine, EventSystem, ResourceManager, SaveSystem, AudioManager
from core.event_system import EventType
from ui import (UIManager, UIState, MainMenu, HUD, InventoryUI, CharacterPanel, SkillTreeUI,
               PauseMenu, SettingsMenu, VendorUI, DialogueUI, QuestTrackerUI, QuestLogUI)
from ui.main_menu import CharacterSelectMenu, CharacterCreateMenu
from entities.character import Character, ClassFactory
from entities.items import ItemFactory, AffixGenerator
from systems.skills import SkillFactory, SkillExecutor, SkillExecutionContext
from systems.combat import CombatSystem, MonsterFactory, ProjectileManager
from systems.world import World, NPCManager, QuestManager
from systems.world.town_renderer import TownRenderer
from systems.world.terrain_renderer import TerrainRenderer, EnvironmentEffects
from systems.world.building_sprites import BuildingSpriteRenderer
from systems.world.npc_animator import TownNPCManager, NPCAnimationState
from systems.particles import ParticleSystem
from systems.input_manager import InputManager, PlayerController
from systems.loot import LootManager
from systems.trading import TradingSystem
from systems.enhancement import EnhancementSystem
from systems.game_state import GameStateMachine, GameStateType
from systems.animation import AnimationManager
from systems.environment import EnvironmentManager
from systems.sound_manager import SoundManager
from systems.consumables import PotionFactory, PotionBelt
from systems.crafting import CraftingSystem
from systems.combat_effects import CombatEffectsManager, EffectType
from systems.analytics import get_analytics, AnalyticsManager, EventType as AnalyticsEventType
from systems.leaderboard import get_leaderboard, LeaderboardManager
from systems.season_system import get_season_manager, SeasonManager
from systems.security_system import get_security_manager, SecurityManager
from ui.font_manager import get_font
from config.game_config import GameConfig, ColorConfig


class GameData:
    def __init__(self):
        self.player: Optional[Character] = None
        self.world: Optional[World] = None
        self.npc_manager: Optional[NPCManager] = None
        self.quest_manager: Optional[QuestManager] = None
        self.combat_system: Optional[CombatSystem] = None
        self.particle_system: Optional[ParticleSystem] = None
        self.input_manager: Optional[InputManager] = None
        self.player_controller: Optional[PlayerController] = None
        self.loot_manager: Optional[LootManager] = None
        self.trading_system: Optional[TradingSystem] = None
        self.enhancement_system: Optional[EnhancementSystem] = None
        self.state_machine: Optional[GameStateMachine] = None
        self.animation_manager: Optional[AnimationManager] = None
        self.environment_manager: Optional[EnvironmentManager] = None
        self.sound_manager: Optional[SoundManager] = None
        self.crafting_system: Optional[CraftingSystem] = None
        self.projectile_manager: Optional[ProjectileManager] = None
        self.skill_executor: Optional[SkillExecutor] = None
        self.town_renderer: Optional[TownRenderer] = None
        self.terrain_renderer: Optional[TerrainRenderer] = None
        self.building_renderer: Optional[BuildingSpriteRenderer] = None
        self.town_npc_manager: Optional[TownNPCManager] = None
        self.environment_effects: Optional[EnvironmentEffects] = None
        self.combat_effects: Optional[CombatEffectsManager] = None
        
        self.analytics_manager: Optional[AnalyticsManager] = None
        self.leaderboard_manager: Optional[LeaderboardManager] = None
        self.season_manager: Optional[SeasonManager] = None
        self.security_manager: Optional[SecurityManager] = None
        
        self.potion_belt: Optional[PotionBelt] = None
        
        self.monsters: List = []
        self.camera_offset: Tuple[float, float] = (0.0, 0.0)
        
        self.current_save_slot: str = "default"
        self.play_time: float = 0.0
        
        self.settings: Dict[str, Any] = {
            "master_volume": 100,
            "music_volume": 80,
            "sfx_volume": 100,
            "fullscreen": False,
            "vsync": True,
            "show_damage_numbers": True,
            "show_health_bars": True,
        }


class Game:
    def __init__(self):
        self.engine = GameEngine()
        self.ui_manager = UIManager(self.engine.screen)
        self.save_system = SaveSystem()
        self.resource_manager = ResourceManager()
        self.audio_manager = AudioManager()
        self.event_system = EventSystem()
        
        self.data = GameData()
        
        self.main_menu: Optional[MainMenu] = None
        self.character_select: Optional[CharacterSelectMenu] = None
        self.character_create: Optional[CharacterCreateMenu] = None
        self.hud: Optional[HUD] = None
        self.inventory_ui: Optional[InventoryUI] = None
        self.character_panel: Optional[CharacterPanel] = None
        self.skill_tree_ui: Optional[SkillTreeUI] = None
        self.pause_menu: Optional[PauseMenu] = None
        self.settings_menu: Optional[SettingsMenu] = None
        self.vendor_ui: Optional[VendorUI] = None
        self.dialogue_ui: Optional[DialogueUI] = None
        self.quest_tracker: Optional[QuestTrackerUI] = None
        self.quest_log: Optional[QuestLogUI] = None
        
        self._initialize_systems()
        self._initialize_ui()
        self._register_callbacks()
    
    def _initialize_systems(self):
        ClassFactory.initialize()
        ItemFactory.initialize()
        AffixGenerator.initialize()
        SkillFactory.initialize()
        MonsterFactory.initialize()
        
        self.data.world = World()
        self.data.npc_manager = NPCManager()
        self.data.quest_manager = QuestManager()
        self.data.combat_system = CombatSystem()
        self.data.particle_system = ParticleSystem()
        self.data.input_manager = InputManager()
        self.data.loot_manager = LootManager()
        self.data.trading_system = TradingSystem()
        self.data.enhancement_system = EnhancementSystem()
        self.data.state_machine = GameStateMachine(GameStateType.MAIN_MENU)
        self.data.animation_manager = AnimationManager()
        self.data.environment_manager = EnvironmentManager()
        self.data.sound_manager = SoundManager()
        self.data.crafting_system = CraftingSystem()
        self.data.projectile_manager = ProjectileManager()
        self.data.town_renderer = TownRenderer()
        self.data.terrain_renderer = TerrainRenderer()
        self.data.building_renderer = BuildingSpriteRenderer()
        self.data.town_npc_manager = TownNPCManager()
        self.data.environment_effects = EnvironmentEffects()
        self.data.combat_effects = CombatEffectsManager()
        
        self.data.analytics_manager = get_analytics()
        self.data.leaderboard_manager = get_leaderboard()
        self.data.season_manager = get_season_manager()
        self.data.security_manager = get_security_manager()
        
        self.data.skill_executor = SkillExecutor(
            self.data.combat_system,
            self.data.particle_system
        )
        
        self.data.potion_belt = PotionBelt(4)
    
    def _initialize_ui(self):
        self.main_menu = MainMenu(self.ui_manager)
        self.character_select = CharacterSelectMenu(self.ui_manager)
        self.character_create = CharacterCreateMenu(self.ui_manager)
        
        self.hud = HUD(self.ui_manager)
        self.inventory_ui = InventoryUI(self.ui_manager)
        self.character_panel = CharacterPanel(self.ui_manager)
        self.skill_tree_ui = SkillTreeUI(self.ui_manager)
        
        self.pause_menu = PauseMenu(self.ui_manager)
        self.settings_menu = SettingsMenu(self.ui_manager)
        self.vendor_ui = VendorUI(self.ui_manager)
        self.dialogue_ui = DialogueUI(self.ui_manager)
        self.quest_tracker = QuestTrackerUI(self.ui_manager)
        self.quest_log = QuestLogUI(self.ui_manager)
    
    def _register_callbacks(self):
        self.ui_manager.register_callback("new_game", self._on_new_game)
        self.ui_manager.register_callback("continue_game", self._on_continue_game)
        self.ui_manager.register_callback("quit_game", self._on_quit_game)
        self.ui_manager.register_callback("create_character", self._on_create_character)
        self.ui_manager.register_callback("start_game", self._on_start_game)
        self.ui_manager.register_callback("use_item", self._on_use_item)
        self.ui_manager.register_callback("resume_game", self._on_resume_game)
        self.ui_manager.register_callback("return_to_main_menu", self._on_return_to_main_menu)
        self.ui_manager.register_callback("open_settings", self._on_open_settings)
        self.ui_manager.register_callback("close_settings", self._on_close_settings)
        self.ui_manager.register_callback("setting_changed", self._on_setting_changed)
        self.ui_manager.register_callback("open_vendor", self._on_open_vendor)
    
    def _on_new_game(self):
        self.ui_manager.change_state(UIState.CHARACTER_CREATE)
    
    def _on_continue_game(self):
        characters = self.save_system.get_characters_in_slot(self.data.current_save_slot)
        self.character_select.set_characters(characters)
    
    def _on_quit_game(self):
        self.engine.running = False
    
    def _on_create_character(self, name: str, class_id: str):
        print(f"[DEBUG] _on_create_character called: name='{name}', class_id='{class_id}'")
        try:
            print(f"[DEBUG] Creating Character...")
            character = Character(class_id, name)
            print(f"[DEBUG] Character created: {character.name}")
            
            print(f"[DEBUG] Granting initial skills...")
            self._grant_initial_skills(character)
            
            print(f"[DEBUG] Granting initial equipment...")
            self._grant_initial_equipment(character)
            
            print(f"[DEBUG] Saving character...")
            self.save_system.save_character(self.data.current_save_slot, character.to_dict())
            self.data.player = character
            
            print(f"[DEBUG] Tracking analytics...")
            self.data.analytics_manager.track_event(
                AnalyticsEventType.CHARACTER_CREATE,
                {"class": class_id, "name": name}
            )
            
            print(f"[DEBUG] Starting game...")
            self._start_game()
            print(f"[DEBUG] Game started successfully!")
        except Exception as e:
            print(f"Error creating character: {e}")
            import traceback
            traceback.print_exc()
    
    def _grant_initial_skills(self, character: Character):
        from systems.skills import register_all_skills
        register_all_skills()
        
        class_skills = {
            "barbarian": ["bash", "cleave"],
            "wizard": ["magic_missile", "electrocute"],
            "demon_hunter": ["hungering_arrow", "impale"],
            "monk": ["fists_of_thunder", "deadly_reach"],
            "necromancer": ["raise_skeleton", "bone_spear"],
            "crusader": ["punish", "shield_bash"],
            "druid": ["werewolf", "earth_spike"],
            "assassin": ["tiger_strike", "claw_mastery"],
        }
        
        initial_skills = class_skills.get(character.character_class.id, [])
        
        for i, skill_id in enumerate(initial_skills[:2]):
            character.learn_skill(skill_id)
            if i < 6:
                character.skill_bar[i] = skill_id
    
    def _grant_initial_equipment(self, character: Character):
        from entities.items import ItemFactory, PotionFactory
        
        starting_gear = {
            "barbarian": {"main_hand": "sword_1h", "chest": "chest_heavy"},
            "monk": {"main_hand": "dagger", "chest": "chest_light"},
            "wizard": {"main_hand": "staff", "chest": "chest_light"},
            "demon_hunter": {"main_hand": "bow", "chest": "chest_light"},
            "necromancer": {"main_hand": "staff", "chest": "chest_light"},
            "crusader": {"main_hand": "sword_1h", "chest": "chest_heavy"},
            "druid": {"main_hand": "staff", "chest": "chest_light"},
            "assassin": {"main_hand": "dagger", "chest": "chest_light"},
        }
        
        class_id = character.character_class.id
        gear = starting_gear.get(class_id, {})
        
        for slot, item_id in gear.items():
            item = ItemFactory.create_item(item_id, level=1)
            if item and slot in character.equipment:
                character.equipment[slot] = item
        
        for i in range(3):
            potion = PotionFactory.get_potion("health_potion_small")
            if potion and i < len(character.inventory):
                character.inventory[i] = potion
    
    def _on_start_game(self, character_data: dict):
        self.data.player = Character.from_dict(character_data)
        self._start_game()
    
    def _on_use_item(self, item, slot_index: int):
        if not item or not self.data.player:
            return
        
        from entities.items.item import ItemType
        
        if hasattr(item, 'item_type'):
            if item.item_type == ItemType.POTION:
                self._use_potion(item, slot_index)
            elif item.item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.ACCESSORY]:
                self._equip_item(item, slot_index)
            elif item.item_type == ItemType.MATERIAL:
                pass
            elif item.item_type == ItemType.GEM:
                pass
    
    def _use_potion(self, potion, slot_index: int):
        if not self.data.player:
            return
        
        from systems.consumables import PotionFactory
        
        result = potion.use(self.data.player)
        if result.get("success"):
            self.data.player.inventory[slot_index] = None
            heal_amount = result.get("heal", 0)
            self.ui_manager.add_notification(
                f"恢复了 {heal_amount} 点生命值",
                (100, 255, 100)
            )
            self._update_ui_with_player()
        else:
            self.ui_manager.add_notification(
                result.get("message", "无法使用"),
                (255, 100, 100)
            )
    
    def _equip_item(self, item, slot_index: int):
        if not self.data.player or not hasattr(self.data.player, 'equipment'):
            return
        
        result = self.data.player.equipment.equip_from_inventory(slot_index)
        if result.get("success"):
            self._update_ui_with_player()
            self.ui_manager.add_notification(
                f"装备了 {item.name}",
                (100, 200, 255)
            )
        else:
            self.ui_manager.add_notification(
                result.get("message", "无法装备"),
                (255, 100, 100)
            )
    
    def _on_resume_game(self):
        self.data.state_machine.pop_state()
        self.pause_menu.hide()
    
    def _on_return_to_main_menu(self):
        self._save_game()
        self.data.state_machine.change_state(GameStateType.MAIN_MENU)
        self.ui_manager.change_state(UIState.MAIN_MENU)
        self.pause_menu.hide()
    
    def _on_open_settings(self):
        self.settings_menu.show()
    
    def _on_close_settings(self):
        self.settings_menu.hide()
    
    def _on_setting_changed(self, setting_id: str, value: Any):
        self.data.settings[setting_id] = value
        
        if setting_id == "music_volume":
            self.audio_manager.set_music_volume(value / 100)
        elif setting_id == "fullscreen":
            self._toggle_fullscreen(value)
    
    def _on_open_vendor(self, npc: Any):
        self.vendor_ui.set_vendor(npc, self.data.player)
        self.vendor_ui.show()
        self.dialogue_ui.hide()
    
    def _toggle_fullscreen(self, enabled: bool):
        if enabled:
            self.engine.screen = pygame.display.set_mode(
                (0, 0), pygame.FULLSCREEN | pygame.HWSURFACE | pygame.DOUBLEBUF
            )
        else:
            self.engine.screen = pygame.display.set_mode(
                (GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT),
                pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.RESIZABLE
            )
    
    def _start_game(self):
        self.data.state_machine.change_state(GameStateType.PLAYING)
        self.ui_manager.change_state(UIState.GAME)
        
        if self.data.player:
            # 确保玩家从主城开始
            self.data.world.current_area_id = "tristram"
            town = self.data.world.get_area("tristram")
            if town:
                # 将玩家放置在主城中心位置
                self.data.player.position = (town.width // 2, town.height // 2)
            
            self.data.player_controller = PlayerController(
                self.data.player, 
                self.data.input_manager
            )
            
            self._update_ui_with_player()
            # 主城不生成怪物
            # self._spawn_initial_monsters()
            self._load_initial_quests()
            
            # 显示欢迎消息
            self.ui_manager.add_notification(
                f"欢迎来到 {town.name if town else '新崔斯特姆'}",
                (255, 220, 100)
            )
    
    def _update_ui_with_player(self):
        if not self.data.player:
            return
        
        self.inventory_ui.set_items(self.data.player.inventory)
        self.inventory_ui.set_equipment(self.data.player.equipment)
        self.character_panel.set_character(self.data.player)
    
    def _spawn_initial_monsters(self):
        area = self.data.world.get_current_area()
        if not area:
            return
        
        for spawn_data in area.monster_spawns:
            monster_id = spawn_data.get("monster_id")
            count = spawn_data.get("count", 1)
            level = spawn_data.get("level", 1)
            
            for _ in range(count):
                pos = area.get_random_spawn_point()
                monster = MonsterFactory.create_monster(
                    monster_id, level, 
                    position=pos
                )
                if monster:
                    self.data.monsters.append(monster)
    
    def _load_initial_quests(self):
        if self.data.quest_manager:
            quests = self.data.quest_manager.get_active_quests()
            self.quest_tracker.set_quests(quests)
    
    def _save_game(self):
        save_data = {}
        
        if self.data.player:
            save_data["character"] = self.data.player.to_dict()
        
        if self.data.world:
            save_data["world"] = {
                "current_area_id": self.data.world.current_area_id,
            }
        
        if self.data.quest_manager:
            save_data["quests"] = self.data.quest_manager.to_dict()
        
        save_data["play_time"] = self.data.play_time
        
        save_data["settings"] = self.data.settings
        
        self.save_system.save_game(self.data.current_save_slot, save_data)
    
    def _load_game(self, save_slot: str) -> bool:
        save_data = self.save_system.load_game(save_slot)
        
        if not save_data:
            return False
        
        if "character" in save_data:
            self.data.player = Character.from_dict(save_data["character"])
        
        if "world" in save_data:
            if self.data.world:
                self.data.world.current_area_id = save_data["world"].get("current_area_id", "tristram")
        
        if "quests" in save_data:
            if self.data.quest_manager:
                self.data.quest_manager = QuestManager.from_dict(save_data["quests"])
        
        self.data.play_time = save_data.get("play_time", 0)
        
        if "settings" in save_data:
            self.data.settings.update(save_data["settings"])
        
        return True
    
    def handle_event(self, event: pygame.event.Event):
        if self.data.animation_manager.is_cutscene_playing():
            self.data.animation_manager.handle_event(event)
            return
        
        if self.settings_menu.visible:
            self._handle_settings_event(event)
            return
        
        if self.pause_menu.visible:
            self._handle_pause_event(event)
            return
        
        if self.vendor_ui.visible:
            self._handle_vendor_event(event)
            return
        
        if self.dialogue_ui.visible:
            self._handle_dialogue_event(event)
            return
        
        if self.quest_log.visible:
            self._handle_quest_log_event(event)
            return
        
        current_state = self.data.state_machine.get_current_state_type()
        
        if current_state == GameStateType.MAIN_MENU:
            self._handle_main_menu_event(event)
        elif current_state == GameStateType.PLAYING:
            self._handle_game_event(event)
    
    def _handle_main_menu_event(self, event: pygame.event.Event):
        ui_state = self.ui_manager.current_state
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if ui_state == UIState.MAIN_MENU:
                for element in self.main_menu.elements.values():
                    if hasattr(element, 'contains_point') and element.contains_point(event.pos):
                        if hasattr(element, 'on_click'):
                            element.on_click(event.pos)
                        break
            elif ui_state == UIState.CHARACTER_SELECT:
                self.character_select.handle_click(event.pos)
            elif ui_state == UIState.CHARACTER_CREATE:
                self.character_create.handle_click(event.pos)
        
        elif event.type == pygame.KEYDOWN:
            if ui_state == UIState.CHARACTER_CREATE:
                self.character_create.handle_key(event.key, event.unicode)
    
    def _handle_game_event(self, event: pygame.event.Event):
        self.data.input_manager.handle_event(event)
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.inventory_ui.toggle()
            elif event.key == pygame.K_c:
                self.character_panel.toggle()
            elif event.key == pygame.K_k:
                self.skill_tree_ui.toggle()
            elif event.key == pygame.K_j:
                self.quest_log.toggle()
            elif event.key == pygame.K_ESCAPE:
                self._handle_escape()
            elif event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]:
                slot = event.key - pygame.K_1
                self._use_skill_slot(slot)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self._handle_left_click(event.pos)
            elif event.button == 3:
                self._handle_right_click(event.pos)
            
            if self.inventory_ui.visible:
                self.inventory_ui.handle_click(event.pos, event.button)
            elif self.skill_tree_ui.visible:
                self.skill_tree_ui.handle_click(event.pos)
        
        elif event.type == pygame.MOUSEMOTION:
            self.inventory_ui.handle_motion(event.pos)
            self.skill_tree_ui.handle_motion(event.pos)
    
    def _handle_pause_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self._on_resume_game()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.pause_menu.handle_click(event.pos)
    
    def _handle_settings_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.settings_menu.hide()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.settings_menu.handle_click(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            self.settings_menu.handle_motion(event.pos)
    
    def _handle_vendor_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.vendor_ui.hide()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.vendor_ui.handle_click(event.pos)
    
    def _handle_dialogue_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.dialogue_ui.handle_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.dialogue_ui.handle_click(event.pos)
    
    def _handle_quest_log_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            self.quest_log.handle_key(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.quest_log.handle_click(event.pos)
    
    def _handle_escape(self):
        if self.inventory_ui.visible:
            self.inventory_ui.toggle()
        elif self.character_panel.visible:
            self.character_panel.toggle()
        elif self.skill_tree_ui.visible:
            self.skill_tree_ui.toggle()
        elif self.quest_log.visible:
            self.quest_log.toggle()
        else:
            self.data.state_machine.push_state(GameStateType.PAUSED)
            self.pause_menu.show()
    
    def _handle_left_click(self, pos: tuple):
        if not self.data.player:
            return
        
        world_x = (pos[0] + self.data.camera_offset[0]) / 64
        world_y = (pos[1] + self.data.camera_offset[1]) / 64
        
        for monster in self.data.monsters:
            if not monster.is_alive:
                continue
            
            dx = world_x - monster.position[0]
            dy = world_y - monster.position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < 1.0:
                self._attack_monster(monster)
                break
    
    def _attack_monster(self, monster):
        if not self.data.player or not self.data.combat_system:
            return
        
        skill_id = self.data.player.skill_bar[0] if self.data.player.skill_bar else None
        if skill_id:
            self._use_skill_on_target(skill_id, monster)
        else:
            damage_result = self.data.combat_system.calculate_player_attack(
                self.data.player, monster
            )
            
            if damage_result:
                monster.take_damage(damage_result["final_damage"])
                
                if damage_result["is_crit"]:
                    self.ui_manager.add_notification("暴击!", (255, 255, 0))
                
                self.data.combat_system.add_damage_number(
                    monster.position[0], monster.position[1],
                    damage_result["final_damage"],
                    damage_result["is_crit"]
                )
    
    def _use_skill_on_target(self, skill_id: str, target):
        if not self.data.player or not self.data.skill_executor:
            return
        
        skill_instance = self.data.player.skills.get(skill_id)
        if not skill_instance:
            return
        
        from systems.skills import SkillFactory, SkillExecutionContext
        
        skill = SkillFactory.get_skill(skill_id)
        if not skill:
            return
        
        if skill_instance.cooldown_remaining > 0:
            return
        
        context = SkillExecutionContext(
            caster=self.data.player,
            skill=skill,
            level=skill_instance.level,
            selected_branch=skill_instance.selected_branch,
            target=target
        )
        
        result = self.data.skill_executor.execute_skill(context, self.data.monsters)
        
        if result.success:
            cooldown = skill.get_cooldown(skill_instance.level, skill_instance.selected_branch)
            skill_instance.cooldown_remaining = cooldown
    
    def _handle_right_click(self, pos: tuple):
        if not self.data.player:
            return
        
        world_x = (pos[0] + self.data.camera_offset[0]) / 64
        world_y = (pos[1] + self.data.camera_offset[1]) / 64
        
        self._check_npc_interaction((world_x, world_y))
        self._check_transition_point((world_x, world_y))
    
    def _check_npc_interaction(self, world_pos: tuple):
        if not self.data.npc_manager:
            return
        
        for npc in self.data.npc_manager.npcs.values():
            dx = world_pos[0] - npc.position[0]
            dy = world_pos[1] - npc.position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < 2.0:
                self._interact_with_npc(npc)
                break
    
    def _interact_with_npc(self, npc):
        from systems.world.npc import NPCType
        
        self.dialogue_ui.set_npc(npc)
        self.dialogue_ui.show()
        
        if npc.npc_type == NPCType.MERCHANT:
            self.vendor_ui.set_vendor(npc, self.data.player)
        elif npc.npc_type == NPCType.TELEPORTER:
            self._open_waypoint_ui()
        elif npc.npc_type == NPCType.HEALER:
            self._heal_player()
    
    def _open_waypoint_ui(self):
        pass
    
    def _heal_player(self):
        if self.data.player:
            max_health = self.data.player.attributes.get_total('max_health') if hasattr(self.data.player.attributes, 'get_total') else 100
            self.data.player.current_health = max_health
            self.ui_manager.add_notification("已完全恢复生命值", (100, 255, 100))
    
    def _check_transition_point(self, world_pos: tuple):
        if not self.data.world:
            return
        
        current_area = self.data.world.get_current_area()
        if not current_area:
            return
        
        for conn in current_area.connections:
            dx = world_pos[0] - conn.position[0]
            dy = world_pos[1] - conn.position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance < 2.0:
                self._transition_to_area(conn.target_area_id)
                break
    
    def _transition_to_area(self, area_id: str):
        if not self.data.world:
            return
        
        target_area = self.data.world.get_area(area_id)
        if not target_area:
            return
        
        self.data.world.change_area(area_id)
        self.data.monsters.clear()
        
        self._spawn_monsters_for_area(target_area)
        
        if self.data.player:
            spawn_pos = self._get_spawn_position(area_id)
            self.data.player.position = spawn_pos
        
        self.ui_manager.add_notification(f"进入了 {target_area.name}", (255, 255, 255))
    
    def _spawn_monsters_for_area(self, area):
        from systems.combat import MonsterFactory
        
        for spawn_data in area.monster_spawns:
            monster_id = spawn_data.get("monster_id")
            count = spawn_data.get("count", 1)
            level = spawn_data.get("level", 1)
            
            for _ in range(count):
                import random
                spawn_x = random.uniform(5, area.width - 5)
                spawn_y = random.uniform(5, area.height - 5)
                
                monster = MonsterFactory.create_monster(
                    monster_id, level,
                    position=(spawn_x, spawn_y)
                )
                if monster:
                    self.data.monsters.append(monster)
    
    def _get_spawn_position(self, area_id: str) -> tuple:
        area = self.data.world.get_area(area_id)
        if not area:
            return (0, 0)
        
        if area.is_safe_zone:
            return (area.width // 2, area.height // 2)
        
        return (area.width // 2, area.height // 2)
    
    def _use_skill_slot(self, slot: int):
        if not self.data.player or not self.data.skill_executor:
            return
        
        skill_id = self.data.player.skill_bar[slot] if slot < len(self.data.player.skill_bar) else None
        if not skill_id:
            return
        
        skill_instance = self.data.player.skills.get(skill_id)
        if not skill_instance:
            return
        
        skill = SkillFactory.get_skill(skill_id)
        if not skill:
            return
        
        if skill_instance.cooldown_remaining > 0:
            self.ui_manager.add_notification("技能冷却中!", (255, 100, 100))
            return
        
        context = SkillExecutionContext(
            caster=self.data.player,
            skill=skill,
            level=skill_instance.level,
            selected_branch=skill_instance.selected_branch
        )
        
        result = self.data.skill_executor.execute_skill(context, self.data.monsters)
        
        if result.success:
            cooldown = skill.get_cooldown(skill_instance.level, skill_instance.selected_branch)
            skill_instance.cooldown_remaining = cooldown
            
            if result.targets_hit:
                self.ui_manager.add_notification(
                    f"命中 {len(result.targets_hit)} 个目标!",
                    (255, 200, 100)
                )
        else:
            if result.message:
                self.ui_manager.add_notification(result.message, (255, 100, 100))
    
    def update(self, delta_time: float):
        self.data.play_time += delta_time
        
        current_state = self.data.state_machine.get_current_state_type()
        
        if current_state == GameStateType.MAIN_MENU:
            self._update_main_menu(delta_time)
        elif current_state == GameStateType.PLAYING:
            self._update_game(delta_time)
        elif current_state == GameStateType.PAUSED:
            self._update_paused(delta_time)
    
    def _update_main_menu(self, delta_time: float):
        ui_state = self.ui_manager.current_state
        
        if ui_state == UIState.MAIN_MENU:
            self.main_menu.update(delta_time)
        elif ui_state == UIState.CHARACTER_SELECT:
            self.character_select.update(delta_time)
        elif ui_state == UIState.CHARACTER_CREATE:
            self.character_create.update(delta_time)
    
    def _update_game(self, delta_time: float):
        self.data.input_manager.update(delta_time)
        
        if self.data.player:
            self.data.player.update(delta_time)
            self.hud.update_character(self.data.player)
            
            if self.data.player_controller:
                self.data.player_controller.update(delta_time)
            
            self._update_camera()
        
        self.data.combat_system.update(delta_time)
        
        for monster in self.data.monsters[:]:
            monster.update(delta_time, 
                          self.data.player.position if self.data.player else None)
            
            self._process_monster_attack(monster, delta_time)
            
            if not monster.is_alive:
                self._on_monster_death(monster)
        
        self.data.monsters = [m for m in self.data.monsters if m.is_alive]
        
        if self.data.player and self.data.player.current_health <= 0:
            self._on_player_death()
        
        collected = self.data.loot_manager.update(
            delta_time, 
            self.data.player.position if self.data.player else None
        )
        
        for dropped in collected:
            self._collect_loot(dropped)
        
        self.data.projectile_manager.update(delta_time, self.data.monsters)
        
        if self.data.skill_executor:
            self.data.skill_executor.update(delta_time, self.data.monsters)
        
        self.data.particle_system.update(delta_time)
        
        self.data.environment_manager.update(
            delta_time,
            self.data.player.position if self.data.player else None
        )
        
        self.data.animation_manager.update(delta_time)
        
        # 更新增强渲染系统
        if self.data.terrain_renderer:
            self.data.terrain_renderer.update(delta_time)
        
        if self.data.building_renderer:
            self.data.building_renderer.update(delta_time)
        
        if self.data.town_npc_manager:
            self.data.town_npc_manager.update(delta_time)
        
        if self.data.environment_effects:
            self.data.environment_effects.update(delta_time)
        
        if self.data.combat_effects:
            self.data.combat_effects.update(delta_time)
        
        self.data.potion_belt.update(delta_time)
        
        self.hud.update(delta_time)
        self.inventory_ui.update(delta_time)
        self.character_panel.update(delta_time)
        self.skill_tree_ui.update(delta_time)
        self.quest_tracker.update(delta_time)
        
        self.ui_manager.update(delta_time)
    
    def _process_monster_attack(self, monster, delta_time: float):
        if not self.data.player or not monster.is_alive:
            return
        
        if not hasattr(monster, 'attack_cooldown') or monster.attack_cooldown > 0:
            return
        
        player_pos = self.data.player.position
        monster_pos = monster.position
        
        dx = player_pos[0] - monster_pos[0]
        dy = player_pos[1] - monster_pos[1]
        distance = (dx * dx + dy * dy) ** 0.5
        
        attack_range = getattr(monster.stats, 'attack_range', 1.5)
        
        if distance <= attack_range:
            damage_result = self.data.combat_system.calculate_monster_attack(
                monster, self.data.player
            )
            
            if damage_result:
                actual_damage = damage_result.get("final_damage", 0)
                self.data.player.current_health -= actual_damage
                
                self.data.combat_system.add_damage_number(
                    player_pos[0], player_pos[1],
                    actual_damage,
                    damage_result.get("is_crit", False),
                    is_player=True
                )
                
                if damage_result.get("is_crit"):
                    self.ui_manager.add_notification("被暴击!", (255, 50, 50))
                
                monster.attack_cooldown = 1.0 / monster.stats.attack_speed
    
    def _on_player_death(self):
        self.ui_manager.add_notification("你死了!", (255, 0, 0))
        
        gold_loss = int(self.data.player.gold * 0.1)
        self.data.player.gold -= gold_loss
        
        self.data.player.current_health = self.data.player.attributes.get_total('max_health') * 0.5
        
        self._transition_to_area("tristram")
        
        self.ui_manager.add_notification(f"损失了 {gold_loss} 金币", (255, 200, 100))
    
    def _update_paused(self, delta_time: float):
        self.pause_menu.update(delta_time)
        self.settings_menu.update(delta_time)
    
    def _update_camera(self):
        if not self.data.player:
            return
        
        target_x = self.data.player.position[0] * 64 - self.engine.screen.get_width() // 2
        target_y = self.data.player.position[1] * 64 - self.engine.screen.get_height() // 2
        
        self.data.camera_offset = (
            self.data.camera_offset[0] + (target_x - self.data.camera_offset[0]) * 0.1,
            self.data.camera_offset[1] + (target_y - self.data.camera_offset[1]) * 0.1
        )
    
    def _on_monster_death(self, monster):
        # 触发死亡特效
        if self.data.combat_effects:
            self.data.combat_effects.create_hit_effect(
                monster.position[0] * 64 + 32,
                monster.position[1] * 64 + 32,
                EffectType.DEATH
            )
        
        loot = self.data.loot_manager.generate_loot(
            source=self._get_drop_source(monster.monster_type),
            level=monster.level,
            position=monster.position,
            magic_find=self._get_player_magic_find()
        )
        
        self.data.loot_manager.add_dropped_items(loot)
        
        if self.data.player:
            exp = monster.get_experience()
            gold = monster.get_gold()
            
            self.data.player.add_experience(exp)
            self.data.player.gold += gold
            
            self.ui_manager.add_notification(
                f"+{exp} 经验, +{gold} 金币",
                (255, 220, 100)
            )
        
        self._spawn_death_particles(monster)
    
    def _get_drop_source(self, monster_type):
        from systems.loot import DropSource
        type_mapping = {
            "normal": DropSource.MONSTER,
            "champion": DropSource.ELITE,
            "rare": DropSource.ELITE,
            "unique": DropSource.ELITE,
            "boss": DropSource.BOSS,
        }
        return type_mapping.get(monster_type.value if hasattr(monster_type, 'value') else "normal",
                                DropSource.MONSTER)
    
    def _get_player_magic_find(self) -> float:
        if self.data.player and hasattr(self.data.player, 'attributes'):
            from entities.character.attributes import AttributeType
            return self.data.player.attributes.get_total(AttributeType.MAGIC_FIND)
        return 0.0
    
    def _collect_loot(self, dropped):
        if dropped.is_gold:
            if self.data.player:
                self.data.player.gold += dropped.gold_amount
                self.ui_manager.add_notification(
                    f"+{dropped.gold_amount} 金币",
                    (255, 215, 0)
                )
        else:
            item = dropped.item
            if self.data.player and hasattr(self.data.player, 'inventory'):
                empty_slot = self._find_empty_inventory_slot()
                if empty_slot >= 0:
                    self.data.player.inventory[empty_slot] = item
                    self.ui_manager.add_notification(
                        f"获得: {item.name}",
                        (100, 200, 255)
                    )
    
    def _find_empty_inventory_slot(self) -> int:
        if not self.data.player:
            return -1
        
        for i, item in enumerate(self.data.player.inventory):
            if item is None:
                return i
        return -1
    
    def _spawn_death_particles(self, monster):
        config = self.data.particle_system.create_blood_effect(
            monster.position[0] * 64,
            monster.position[1] * 64
        )
        
        self.data.particle_system.create_emitter(config)
    
    def render(self, surface: pygame.Surface):
        current_state = self.data.state_machine.get_current_state_type()
        
        if current_state == GameStateType.MAIN_MENU:
            self._render_main_menu(surface)
        elif current_state == GameStateType.PLAYING:
            self._render_game(surface)
        elif current_state == GameStateType.PAUSED:
            self._render_game(surface)
            self._render_pause(surface)
    
    def _render_main_menu(self, surface: pygame.Surface):
        ui_state = self.ui_manager.current_state
        
        if ui_state == UIState.MAIN_MENU:
            self.main_menu.render(surface)
        elif ui_state == UIState.CHARACTER_SELECT:
            self.character_select.render(surface)
        elif ui_state == UIState.CHARACTER_CREATE:
            self.character_create.render(surface)
    
    def _render_game(self, surface: pygame.Surface):
        surface.fill((30, 25, 20))
        
        self._render_world(surface)
        
        # 渲染主城建筑和NPC
        area = self.data.world.get_current_area()
        if area and area.area_type.value == "town":
            self._render_town(surface)
        else:
            self._render_environment(surface)
            self._render_monsters(surface)
        
        self._render_loot(surface)
        self._render_projectiles(surface)
        self._render_skill_projectiles(surface)
        self._render_player(surface)
        
        self.data.particle_system.render(surface, self.data.camera_offset)
        
        # 渲染战斗特效
        if self.data.combat_effects:
            self.data.combat_effects.render(surface, self.data.camera_offset)
        
        self.hud.render(surface)
        
        # 渲染当前区域名称
        if area:
            self.hud.render_area_name(surface, area.name, area.is_safe_zone)
        
        self.inventory_ui.render(surface)
        self.character_panel.render(surface)
        self.skill_tree_ui.render(surface)
        self.quest_tracker.render(surface)
        self.quest_log.render(surface)
        
        self._render_damage_numbers(surface)
        
        self.ui_manager.render()
        
        self.data.animation_manager.render(surface)
    
    def _render_town(self, surface: pygame.Surface):
        """渲染主城场景"""
        cam_x, cam_y = self.data.camera_offset
        tile_size = 64
        
        # 渲染建筑（使用新的建筑精灵渲染器）
        if self.data.building_renderer:
            building_positions = {
                "merchant": (15, 15),
                "blacksmith": (35, 18),
                "jeweler": (22, 32),
                "quest_hall": (12, 28),
                "healer": (8, 18),
                "stash": (38, 32),
                "waypoint": (25, 8),
                "trainer": (42, 25),
                "tavern": (18, 38),
            }
            
            for building_id, (bx, by) in building_positions.items():
                screen_x = int(bx * tile_size - cam_x)
                screen_y = int(by * tile_size - cam_y)
                self.data.building_renderer.render_building_animated(
                    surface, building_id, screen_x, screen_y, scale=1.0
                )
        
        # 渲染中心广场
        center_x = int(25 * tile_size - cam_x)
        center_y = int(25 * tile_size - cam_y)
        
        # 广场地面
        pygame.draw.circle(surface, (70, 65, 60), (center_x, center_y), int(3 * tile_size))
        pygame.draw.circle(surface, (90, 85, 80), (center_x, center_y), int(3 * tile_size), 3)
        
        # 中心喷泉
        pygame.draw.circle(surface, (100, 120, 140), (center_x, center_y), tile_size)
        pygame.draw.circle(surface, (150, 170, 190), (center_x, center_y), tile_size, 3)
        pygame.draw.circle(surface, (80, 100, 120), (center_x, center_y), tile_size - 10)
        
        # 渲染NPC（使用新的NPC动画系统）
        if self.data.town_npc_manager:
            self.data.town_npc_manager.render(surface, self.data.camera_offset, tile_size)
        else:
            self._render_npcs(surface)
        
        # 渲染环境粒子效果
        if self.data.environment_effects:
            self.data.environment_effects.render(surface)
    
    def _render_pause(self, surface: pygame.Surface):
        self.pause_menu.render(surface)
        self.settings_menu.render(surface)
    
    def _render_world(self, surface: pygame.Surface):
        area = self.data.world.get_current_area()
        if not area:
            return
        
        tile_size = 64
        cam_x, cam_y = self.data.camera_offset
        area_type = area.area_type.value if hasattr(area.area_type, 'value') else str(area.area_type)
        
        # 使用增强地形渲染器
        if self.data.terrain_renderer:
            if area_type == "town":
                self.data.terrain_renderer.render_town_ground(
                    surface, self.data.camera_offset, area.width, area.height, tile_size
                )
            else:
                self.data.terrain_renderer.render_area(
                    surface, area_type, self.data.camera_offset, area.width, area.height, tile_size
                )
        else:
            # 回退到简单渲染
            start_x = max(0, int(cam_x // tile_size))
            start_y = max(0, int(cam_y // tile_size))
            end_x = min(area.width, start_x + surface.get_width() // tile_size + 2)
            end_y = min(area.height, start_y + surface.get_height() // tile_size + 2)
            
            for y in range(start_y, end_y):
                for x in range(start_x, end_x):
                    color = (40, 35, 30)
                    if area_type == "town":
                        color = (50, 45, 40)
                    elif area_type == "forest":
                        color = (30, 50, 30)
                    elif area_type == "dungeon":
                        color = (25, 25, 35)
                    elif area_type == "desert":
                        color = (70, 60, 40)
                    elif area_type == "snow":
                        color = (60, 65, 70)
                    elif area_type == "hell":
                        color = (50, 25, 25)
                    
                    screen_x = x * tile_size - int(cam_x)
                    screen_y = y * tile_size - int(cam_y)
                    pygame.draw.rect(surface, color, (screen_x, screen_y, tile_size, tile_size))
    
    def _render_environment(self, surface: pygame.Surface):
        cam_x, cam_y = self.data.camera_offset
        
        for obj in self.data.environment_manager.objects.values():
            if obj.is_hidden:
                continue
            
            x = int(obj.position[0] * 64 - cam_x) + 32
            y = int(obj.position[1] * 64 - cam_y) + 32
            
            colors = {
                "chest": (139, 90, 43),
                "breakable": (100, 80, 60),
                "door": (101, 67, 33),
                "shrine": (200, 180, 100),
                "waypoint": (100, 150, 255),
                "portal": (150, 100, 255),
            }
            
            obj_type = obj.object_type.value if hasattr(obj.object_type, 'value') else str(obj.object_type)
            color = colors.get(obj_type, (100, 100, 100))
            
            pygame.draw.rect(surface, color, (x - 20, y - 20, 40, 40))
    
    def _render_npcs(self, surface: pygame.Surface):
        """渲染NPC"""
        cam_x, cam_y = self.data.camera_offset
        
        # NPC类型颜色映射
        npc_colors = {
            "merchant": (100, 200, 100),      # 绿色 - 商人
            "blacksmith": (150, 150, 150),    # 灰色 - 铁匠
            "jeweler": (200, 100, 200),       # 紫色 - 珠宝匠
            "quest_giver": (255, 200, 100),   # 金色 - 任务发布者
            "healer": (200, 200, 255),        # 淡蓝 - 治疗师
            "stash": (150, 120, 80),          # 土黄 - 仓库
            "teleporter": (100, 100, 255),    # 蓝色 - 传送使者
            "trainer": (200, 150, 50),        # 金色 - 训练师
        }
        
        font = get_font(12)
        
        for npc in self.data.npc_manager.npcs.values():
            x = int(npc.position[0] * 64 - cam_x) + 32
            y = int(npc.position[1] * 64 - cam_y) + 32
            
            # 检查是否在屏幕范围内
            if x < -50 or x > surface.get_width() + 50 or y < -50 or y > surface.get_height() + 50:
                continue
            
            # 获取NPC颜色
            npc_type = npc.npc_type.value if hasattr(npc.npc_type, 'value') else str(npc.npc_type)
            color = npc_colors.get(npc_type, (200, 200, 200))
            
            # 绘制NPC（人形）
            # 身体
            pygame.draw.circle(surface, color, (x, y), 15)
            # 头部
            pygame.draw.circle(surface, tuple(min(255, c + 30) for c in color), (x, y - 20), 10)
            # 边框
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 15, 2)
            
            # 绘制NPC名称
            name_text = font.render(npc.name, True, (255, 255, 255))
            name_x = x - name_text.get_width() // 2
            name_y = y - 45
            
            # 文字背景
            bg_padding = 2
            bg_rect = (name_x - bg_padding, name_y - bg_padding,
                      name_text.get_width() + bg_padding * 2,
                      name_text.get_height() + bg_padding * 2)
            pygame.draw.rect(surface, (30, 30, 30, 200), bg_rect)
            surface.blit(name_text, (name_x, name_y))
            
            # 如果是任务发布者且有可接任务，显示感叹号
            if npc_type == "quest_giver":
                exclamation = font.render("!", True, (255, 255, 0))
                surface.blit(exclamation, (x + 10, y - 40))
    
    def _render_loot(self, surface: pygame.Surface):
        cam_x, cam_y = self.data.camera_offset
        
        for dropped in self.data.loot_manager.get_dropped_items():
            x = int(dropped.position[0] * 64 - cam_x) + 32
            y = int(dropped.position[1] * 64 - cam_y) + 32
            
            if dropped.is_gold:
                color = (255, 215, 0)
                pygame.draw.circle(surface, color, (x, y), 8)
            else:
                item = dropped.item
                rarity = getattr(item, 'rarity', None)
                rarity_value = rarity.value if hasattr(rarity, 'value') else 0
                
                rarity_colors = {
                    0: ColorConfig.RARITY_COMMON,
                    1: ColorConfig.RARITY_MAGIC,
                    2: ColorConfig.RARITY_RARE,
                    3: ColorConfig.RARITY_LEGENDARY,
                    4: ColorConfig.RARITY_SET,
                    5: ColorConfig.RARITY_CRAFTED
                }
                color = rarity_colors.get(rarity_value, (200, 200, 200))
                
                pygame.draw.rect(surface, color, (x - 10, y - 10, 20, 20))
    
    def _render_monsters(self, surface: pygame.Surface):
        cam_x, cam_y = self.data.camera_offset
        
        for monster in self.data.monsters:
            if not monster.is_alive:
                continue
            
            x = int(monster.position[0] * 64 - cam_x) + 32
            y = int(monster.position[1] * 64 - cam_y) + 32
            
            if x < -50 or x > surface.get_width() + 50 or y < -50 or y > surface.get_height() + 50:
                continue
            
            monster_type = monster.monster_type.value if hasattr(monster.monster_type, 'value') else "normal"
            
            colors = {
                "normal": (200, 50, 50),
                "champion": (200, 150, 50),
                "rare": (200, 100, 200),
                "unique": (150, 100, 200),
                "boss": (255, 100, 50),
            }
            color = colors.get(monster_type, (200, 50, 50))
            
            size = 15
            if monster_type == "champion":
                size = 18
            elif monster_type == "rare":
                size = 20
            elif monster_type == "boss":
                size = 30
            
            pygame.draw.circle(surface, color, (x, y), size)
            
            if self.data.settings.get("show_health_bars", True):
                bar_width = 40
                bar_height = 4
                health_percent = monster.current_health / monster.stats.health
                
                pygame.draw.rect(surface, (50, 50, 50),
                                 (x - bar_width // 2, y - size - 10, bar_width, bar_height))
                pygame.draw.rect(surface, (200, 50, 50),
                                 (x - bar_width // 2, y - size - 10, 
                                  int(bar_width * health_percent), bar_height))
    
    def _render_projectiles(self, surface: pygame.Surface):
        cam_x, cam_y = self.data.camera_offset
        
        for proj in self.data.projectile_manager.get_projectiles():
            x = int(proj.position[0] * 64 - cam_x) + 32
            y = int(proj.position[1] * 64 - cam_y) + 32
            
            pygame.draw.circle(surface, (200, 200, 255), (x, y), 5)
    
    def _render_skill_projectiles(self, surface: pygame.Surface):
        if not self.data.skill_executor:
            return
        
        cam_x, cam_y = self.data.camera_offset
        
        for proj in self.data.skill_executor.get_projectiles():
            x = int(proj["position"][0] * 64 - cam_x) + 32
            y = int(proj["position"][1] * 64 - cam_y) + 32
            
            damage_type = proj.get("damage_type")
            colors = {
                "fire": (255, 100, 50),
                "cold": (100, 200, 255),
                "lightning": (255, 255, 100),
                "poison": (100, 255, 100),
                "arcane": (200, 100, 255),
                "physical": (200, 200, 200),
            }
            color = colors.get(damage_type.value if hasattr(damage_type, 'value') else str(damage_type), (200, 200, 255))
            
            pygame.draw.circle(surface, color, (x, y), 6)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), 6, 1)
    
    def _render_player(self, surface: pygame.Surface):
        if not self.data.player:
            return
        
        cam_x, cam_y = self.data.camera_offset
        
        x, y = self.data.player.position
        x = int(x * 64 - cam_x) + 32
        y = int(y * 64 - cam_y) + 32
        
        pygame.draw.circle(surface, (100, 150, 255), (x, y), 20)
        pygame.draw.circle(surface, (150, 200, 255), (x, y), 20, 2)
        
        font = get_font(12)
        name_text = font.render(self.data.player.name, True, (255, 255, 255))
        surface.blit(name_text, (x - name_text.get_width() // 2, y - 35))
    
    def _render_damage_numbers(self, surface: pygame.Surface):
        if not self.data.settings.get("show_damage_numbers", True):
            return
        
        font = get_font(16)
        cam_x, cam_y = self.data.camera_offset
        
        for dmg_num in self.data.combat_system.get_damage_numbers():
            x = int(dmg_num["x"] * 64 - cam_x) + 32
            y = int(dmg_num["y"] * 64 - cam_y) + 32 - int((1.5 - dmg_num["lifetime"]) * 30)
            
            text = str(int(abs(dmg_num["damage"])))
            if dmg_num["is_crit"]:
                text = f"!{text}!"
            
            text_surface = font.render(text, True, dmg_num["color"])
            surface.blit(text_surface, (x - text_surface.get_width() // 2, y))
    
    def run(self):
        self.engine.register_state("main_menu", self)
        self.engine.register_state("game", self)
        
        self.engine.run()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
