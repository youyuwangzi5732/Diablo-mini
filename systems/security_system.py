"""
风控与安全系统
支持数据校验、防篡改、异常检测、安全审计
"""
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import hashlib
import json
import os
import secrets
import hmac
import base64
from collections import defaultdict


class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertType(Enum):
    INVALID_DATA = "invalid_data"
    TAMPERING_DETECTED = "tampering_detected"
    ABNORMAL_BEHAVIOR = "abnormal_behavior"
    SPEED_HACK = "speed_hack"
    RESOURCE_EXPLOIT = "resource_exploit"
    DUPLICATE_ITEM = "duplicate_item"
    INVALID_TRANSACTION = "invalid_transaction"
    SUSPICIOUS_PATTERN = "suspicious_pattern"


@dataclass
class SecurityAlert:
    alert_id: str
    alert_type: AlertType
    severity: SecurityLevel
    timestamp: float
    character_id: str
    details: Dict[str, Any]
    resolved: bool = False
    resolved_by: str = ""
    resolved_at: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "alert_id": self.alert_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "character_id": self.character_id,
            "details": self.details,
            "resolved": self.resolved,
            "resolved_by": self.resolved_by,
            "resolved_at": self.resolved_at
        }


@dataclass
class AuditLog:
    log_id: str
    timestamp: float
    action: str
    character_id: str
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    checksum: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "log_id": self.log_id,
            "timestamp": self.timestamp,
            "action": self.action,
            "character_id": self.character_id,
            "before_state": self.before_state,
            "after_state": self.after_state,
            "checksum": self.checksum
        }


@dataclass
class BehaviorProfile:
    character_id: str
    average_gold_per_hour: float = 0
    average_exp_per_hour: float = 0
    average_items_per_hour: float = 0
    average_kill_speed: float = 0
    typical_play_hours: List[int] = field(default_factory=list)
    typical_session_duration: float = 0
    last_updated: float = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "character_id": self.character_id,
            "average_gold_per_hour": self.average_gold_per_hour,
            "average_exp_per_hour": self.average_exp_per_hour,
            "average_items_per_hour": self.average_items_per_hour,
            "average_kill_speed": self.average_kill_speed,
            "typical_play_hours": self.typical_play_hours,
            "typical_session_duration": self.typical_session_duration,
            "last_updated": self.last_updated
        }


class DataValidator:
    def __init__(self):
        self._valid_ranges = {
            "level": (1, 100),
            "paragon_level": (0, 10000),
            "gold": (0, 10000000000),
            "experience": (0, 1000000000000),
            "health": (0, 1000000),
            "mana": (0, 100000),
            "damage": (0, 10000000),
            "armor": (0, 100000),
            "resistance": (0, 10000),
            "item_count": (0, 1000),
            "skill_level": (0, 20),
        }
        
        self._required_fields = {
            "character": ["id", "name", "class_type", "level", "gold", "experience"],
            "item": ["id", "name", "type", "rarity", "level_requirement"],
            "skill": ["id", "name", "class_type", "level"],
        }
    
    def validate_value(self, field: str, value: Any) -> Tuple[bool, str]:
        if field not in self._valid_ranges:
            return True, ""
        
        min_val, max_val = self._valid_ranges[field]
        
        if not isinstance(value, (int, float)):
            return False, f"Invalid type for {field}"
        
        if value < min_val or value > max_val:
            return False, f"{field} value {value} out of range [{min_val}, {max_val}]"
        
        return True, ""
    
    def validate_structure(self, data_type: str, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        if data_type not in self._required_fields:
            return True, []
        
        for field in self._required_fields[data_type]:
            if field not in data:
                errors.append(f"Missing required field: {field}")
        
        return len(errors) == 0, errors
    
    def validate_item(self, item_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        valid, errors = self.validate_structure("item", item_data)
        if not valid:
            return False, errors
        
        if "affixes" in item_data:
            for affix in item_data["affixes"]:
                if "type" not in affix or "value" not in affix:
                    errors.append("Invalid affix structure")
        
        return len(errors) == 0, errors


class TamperDetector:
    def __init__(self, secret_key: str = None):
        self._secret_key = secret_key or secrets.token_hex(32)
        self._checksums: Dict[str, str] = {}
        self._modification_history: Dict[str, List[Dict]] = defaultdict(list)
    
    def generate_checksum(self, data: Dict[str, Any]) -> str:
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False)
        return hmac.new(
            self._secret_key.encode(),
            serialized.encode(),
            hashlib.sha256
        ).hexdigest()
    
    def register_checksum(self, data_id: str, data: Dict[str, Any]):
        checksum = self.generate_checksum(data)
        self._checksums[data_id] = checksum
        
        self._modification_history[data_id].append({
            "timestamp": datetime.now().timestamp(),
            "checksum": checksum,
            "action": "register"
        })
    
    def verify_checksum(self, data_id: str, data: Dict[str, Any]) -> bool:
        if data_id not in self._checksums:
            return True
        
        expected = self._checksums[data_id]
        actual = self.generate_checksum(data)
        
        if expected != actual:
            self._modification_history[data_id].append({
                "timestamp": datetime.now().timestamp(),
                "expected": expected,
                "actual": actual,
                "action": "tamper_detected"
            })
            return False
        
        return True
    
    def update_checksum(self, data_id: str, data: Dict[str, Any]):
        checksum = self.generate_checksum(data)
        self._checksums[data_id] = checksum
        
        self._modification_history[data_id].append({
            "timestamp": datetime.now().timestamp(),
            "checksum": checksum,
            "action": "update"
        })
    
    def get_modification_history(self, data_id: str) -> List[Dict]:
        return self._modification_history.get(data_id, [])
    
    def encode_data(self, data: Dict[str, Any]) -> str:
        serialized = json.dumps(data, ensure_ascii=False)
        checksum = self.generate_checksum(data)
        
        payload = {
            "data": data,
            "checksum": checksum,
            "timestamp": datetime.now().timestamp()
        }
        
        encoded = base64.b64encode(json.dumps(payload).encode()).decode()
        return encoded
    
    def decode_data(self, encoded: str) -> Tuple[Optional[Dict[str, Any]], bool]:
        try:
            decoded = base64.b64decode(encoded.encode()).decode()
            payload = json.loads(decoded)
            
            data = payload.get("data", {})
            expected_checksum = payload.get("checksum", "")
            
            actual_checksum = self.generate_checksum(data)
            
            if expected_checksum != actual_checksum:
                return None, False
            
            return data, True
            
        except Exception:
            return None, False


class AnomalyDetector:
    def __init__(self):
        self._profiles: Dict[str, BehaviorProfile] = {}
        self._thresholds = {
            "gold_per_hour_multiplier": 5.0,
            "exp_per_hour_multiplier": 5.0,
            "items_per_hour_multiplier": 10.0,
            "kill_speed_multiplier": 3.0,
            "session_duration_multiplier": 3.0,
            "max_gold_per_hour": 100000000,
            "max_exp_per_hour": 10000000000,
            "max_items_per_hour": 1000,
        }
        
        self._recent_activities: Dict[str, List[Dict]] = defaultdict(list)
        self._max_activities = 1000
    
    def update_profile(self, character_id: str, stats: Dict[str, Any]):
        if character_id not in self._profiles:
            self._profiles[character_id] = BehaviorProfile(character_id=character_id)
        
        profile = self._profiles[character_id]
        
        alpha = 0.1
        if "gold_per_hour" in stats:
            profile.average_gold_per_hour = (
                alpha * stats["gold_per_hour"] + 
                (1 - alpha) * profile.average_gold_per_hour
            )
        
        if "exp_per_hour" in stats:
            profile.average_exp_per_hour = (
                alpha * stats["exp_per_hour"] + 
                (1 - alpha) * profile.average_exp_per_hour
            )
        
        if "items_per_hour" in stats:
            profile.average_items_per_hour = (
                alpha * stats["items_per_hour"] + 
                (1 - alpha) * profile.average_items_per_hour
            )
        
        if "kill_speed" in stats:
            profile.average_kill_speed = (
                alpha * stats["kill_speed"] + 
                (1 - alpha) * profile.average_kill_speed
            )
        
        if "session_duration" in stats:
            profile.typical_session_duration = (
                alpha * stats["session_duration"] + 
                (1 - alpha) * profile.typical_session_duration
            )
        
        profile.last_updated = datetime.now().timestamp()
    
    def record_activity(self, character_id: str, activity: Dict[str, Any]):
        activities = self._recent_activities[character_id]
        activities.append({
            **activity,
            "timestamp": datetime.now().timestamp()
        })
        
        if len(activities) > self._max_activities:
            self._recent_activities[character_id] = activities[-self._max_activities:]
    
    def detect_anomalies(self, character_id: str, current_stats: Dict[str, Any]) -> List[Dict[str, Any]]:
        anomalies = []
        
        if character_id not in self._profiles:
            return anomalies
        
        profile = self._profiles[character_id]
        
        if profile.average_gold_per_hour > 0:
            ratio = current_stats.get("gold_per_hour", 0) / profile.average_gold_per_hour
            if ratio > self._thresholds["gold_per_hour_multiplier"]:
                anomalies.append({
                    "type": "gold_anomaly",
                    "current": current_stats.get("gold_per_hour", 0),
                    "average": profile.average_gold_per_hour,
                    "ratio": ratio
                })
        
        if current_stats.get("gold_per_hour", 0) > self._thresholds["max_gold_per_hour"]:
            anomalies.append({
                "type": "gold_absolute",
                "current": current_stats.get("gold_per_hour", 0),
                "max": self._thresholds["max_gold_per_hour"]
            })
        
        if profile.average_exp_per_hour > 0:
            ratio = current_stats.get("exp_per_hour", 0) / profile.average_exp_per_hour
            if ratio > self._thresholds["exp_per_hour_multiplier"]:
                anomalies.append({
                    "type": "exp_anomaly",
                    "current": current_stats.get("exp_per_hour", 0),
                    "average": profile.average_exp_per_hour,
                    "ratio": ratio
                })
        
        if profile.average_kill_speed > 0:
            ratio = current_stats.get("kill_speed", 0) / profile.average_kill_speed
            if ratio > self._thresholds["kill_speed_multiplier"]:
                anomalies.append({
                    "type": "speed_anomaly",
                    "current": current_stats.get("kill_speed", 0),
                    "average": profile.average_kill_speed,
                    "ratio": ratio
                })
        
        return anomalies
    
    def detect_duplicate_items(self, character_id: str, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        duplicates = []
        seen_ids = set()
        
        for item in items:
            item_id = item.get("id", "")
            if item_id in seen_ids:
                duplicates.append({
                    "type": "duplicate_item_id",
                    "item_id": item_id
                })
            seen_ids.add(item_id)
        
        item_signatures = defaultdict(list)
        for item in items:
            sig = self._generate_item_signature(item)
            item_signatures[sig].append(item)
        
        for sig, items_with_sig in item_signatures.items():
            if len(items_with_sig) > 1:
                duplicates.append({
                    "type": "duplicate_item_signature",
                    "signature": sig,
                    "count": len(items_with_sig)
                })
        
        return duplicates
    
    def _generate_item_signature(self, item: Dict[str, Any]) -> str:
        sig_data = {
            "name": item.get("name", ""),
            "type": item.get("type", ""),
            "rarity": item.get("rarity", ""),
            "level": item.get("level_requirement", 0),
            "affixes": sorted(item.get("affixes", []), key=lambda x: str(x))
        }
        return hashlib.md5(json.dumps(sig_data, sort_keys=True).encode()).hexdigest()


class SecurityManager:
    def __init__(self, data_dir: str = "security"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        self._validator = DataValidator()
        self._tamper_detector = TamperDetector()
        self._anomaly_detector = AnomalyDetector()
        
        self._alerts: List[SecurityAlert] = []
        self._audit_logs: List[AuditLog] = []
        
        self._blocked_characters: set = set()
        self._suspicious_characters: Dict[str, int] = defaultdict(int)
        
        self._alert_callbacks: List[Callable[[SecurityAlert], None]] = []
        
        self._load_data()
    
    def validate_character_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        valid, struct_errors = self._validator.validate_structure("character", data)
        errors.extend(struct_errors)
        
        for field, value in data.items():
            valid, error = self._validator.validate_value(field, value)
            if not valid:
                errors.append(error)
        
        return len(errors) == 0, errors
    
    def validate_item_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        return self._validator.validate_item(data)
    
    def register_save_data(self, save_id: str, data: Dict[str, Any]):
        self._tamper_detector.register_checksum(save_id, data)
    
    def verify_save_data(self, save_id: str, data: Dict[str, Any]) -> bool:
        return self._tamper_detector.verify_checksum(save_id, data)
    
    def update_save_data(self, save_id: str, data: Dict[str, Any]):
        self._tamper_detector.update_checksum(save_id, data)
    
    def encode_secure_data(self, data: Dict[str, Any]) -> str:
        return self._tamper_detector.encode_data(data)
    
    def decode_secure_data(self, encoded: str) -> Tuple[Optional[Dict[str, Any]], bool]:
        return self._tamper_detector.decode_data(encoded)
    
    def record_behavior(self, character_id: str, stats: Dict[str, Any]):
        self._anomaly_detector.update_profile(character_id, stats)
    
    def check_for_anomalies(self, character_id: str, stats: Dict[str, Any]) -> List[SecurityAlert]:
        anomalies = self._anomaly_detector.detect_anomalies(character_id, stats)
        alerts = []
        
        for anomaly in anomalies:
            alert = SecurityAlert(
                alert_id=secrets.token_hex(8),
                alert_type=AlertType.ABNORMAL_BEHAVIOR,
                severity=SecurityLevel.MEDIUM if anomaly.get("ratio", 0) < 10 else SecurityLevel.HIGH,
                timestamp=datetime.now().timestamp(),
                character_id=character_id,
                details=anomaly
            )
            alerts.append(alert)
            self._alerts.append(alert)
            self._suspicious_characters[character_id] += 1
            
            for callback in self._alert_callbacks:
                callback(alert)
        
        return alerts
    
    def check_items(self, character_id: str, items: List[Dict[str, Any]]) -> List[SecurityAlert]:
        duplicates = self._anomaly_detector.detect_duplicate_items(character_id, items)
        alerts = []
        
        for dup in duplicates:
            alert = SecurityAlert(
                alert_id=secrets.token_hex(8),
                alert_type=AlertType.DUPLICATE_ITEM,
                severity=SecurityLevel.HIGH,
                timestamp=datetime.now().timestamp(),
                character_id=character_id,
                details=dup
            )
            alerts.append(alert)
            self._alerts.append(alert)
            
            for callback in self._alert_callbacks:
                callback(alert)
        
        return alerts
    
    def log_action(self, action: str, character_id: str, 
                   before_state: Dict[str, Any], after_state: Dict[str, Any]):
        log_id = secrets.token_hex(8)
        
        checksum = hashlib.sha256(
            json.dumps({
                "action": action,
                "before": before_state,
                "after": after_state,
                "timestamp": datetime.now().timestamp()
            }, sort_keys=True).encode()
        ).hexdigest()
        
        log = AuditLog(
            log_id=log_id,
            timestamp=datetime.now().timestamp(),
            action=action,
            character_id=character_id,
            before_state=before_state,
            after_state=after_state,
            checksum=checksum
        )
        
        self._audit_logs.append(log)
        
        if len(self._audit_logs) > 10000:
            self._audit_logs = self._audit_logs[-10000:]
    
    def create_alert(self, alert_type: AlertType, severity: SecurityLevel,
                     character_id: str, details: Dict[str, Any]) -> SecurityAlert:
        alert = SecurityAlert(
            alert_id=secrets.token_hex(8),
            alert_type=alert_type,
            severity=severity,
            timestamp=datetime.now().timestamp(),
            character_id=character_id,
            details=details
        )
        
        self._alerts.append(alert)
        
        for callback in self._alert_callbacks:
            callback(alert)
        
        self._save_data()
        
        return alert
    
    def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.resolved = True
                alert.resolved_by = resolved_by
                alert.resolved_at = datetime.now().timestamp()
                self._save_data()
                return True
        return False
    
    def get_alerts(self, character_id: str = None, unresolved_only: bool = False) -> List[SecurityAlert]:
        alerts = self._alerts
        
        if character_id:
            alerts = [a for a in alerts if a.character_id == character_id]
        
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        
        return alerts
    
    def get_audit_logs(self, character_id: str = None, action: str = None,
                       limit: int = 100) -> List[AuditLog]:
        logs = self._audit_logs
        
        if character_id:
            logs = [l for l in logs if l.character_id == character_id]
        
        if action:
            logs = [l for l in logs if l.action == action]
        
        return logs[-limit:]
    
    def is_blocked(self, character_id: str) -> bool:
        return character_id in self._blocked_characters
    
    def block_character(self, character_id: str):
        self._blocked_characters.add(character_id)
        self._save_data()
    
    def unblock_character(self, character_id: str):
        self._blocked_characters.discard(character_id)
        self._save_data()
    
    def get_suspicion_level(self, character_id: str) -> int:
        return self._suspicious_characters.get(character_id, 0)
    
    def register_alert_callback(self, callback: Callable[[SecurityAlert], None]):
        self._alert_callbacks.append(callback)
    
    def generate_security_report(self) -> Dict[str, Any]:
        total_alerts = len(self._alerts)
        unresolved = len([a for a in self._alerts if not a.resolved])
        
        by_severity = defaultdict(int)
        for alert in self._alerts:
            by_severity[alert.severity.value] += 1
        
        by_type = defaultdict(int)
        for alert in self._alerts:
            by_type[alert.alert_type.value] += 1
        
        return {
            "total_alerts": total_alerts,
            "unresolved_alerts": unresolved,
            "blocked_characters": len(self._blocked_characters),
            "suspicious_characters": len(self._suspicious_characters),
            "alerts_by_severity": dict(by_severity),
            "alerts_by_type": dict(by_type),
            "total_audit_logs": len(self._audit_logs)
        }
    
    def _save_data(self):
        data = {
            "alerts": [a.to_dict() for a in self._alerts[-1000:]],
            "blocked_characters": list(self._blocked_characters),
            "suspicious_characters": dict(self._suspicious_characters)
        }
        
        filepath = os.path.join(self.data_dir, "security_data.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_data(self):
        filepath = os.path.join(self.data_dir, "security_data.json")
        
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for alert_data in data.get("alerts", []):
                alert = SecurityAlert(
                    alert_id=alert_data.get("alert_id", ""),
                    alert_type=AlertType(alert_data.get("alert_type", "invalid_data")),
                    severity=SecurityLevel(alert_data.get("severity", "low")),
                    timestamp=alert_data.get("timestamp", 0),
                    character_id=alert_data.get("character_id", ""),
                    details=alert_data.get("details", {}),
                    resolved=alert_data.get("resolved", False),
                    resolved_by=alert_data.get("resolved_by", ""),
                    resolved_at=alert_data.get("resolved_at")
                )
                self._alerts.append(alert)
            
            self._blocked_characters = set(data.get("blocked_characters", []))
            self._suspicious_characters = defaultdict(int, data.get("suspicious_characters", {}))
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Error loading security data: {e}")


_security_manager: Optional[SecurityManager] = None


def get_security_manager() -> SecurityManager:
    global _security_manager
    if _security_manager is None:
        _security_manager = SecurityManager()
    return _security_manager
