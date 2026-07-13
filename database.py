import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class Database:
    def __init__(self, db_path='users.json'):
        self.db_path = db_path
        self.data = self.load()
    
    def load(self):
        try:
            with open(self.db_path, 'r') as f:
                return json.load(f)
        except:
            return {
                'users': {},
                'inbounds': {},
                'settings': {},
                'traffic_logs': []
            }
    
    def save(self):
        with open(self.db_path, 'w') as f:
            json.dump(self.data, f, indent=2)
    
    def create_user(self, name: str, traffic_limit: int, expiry_days: int) -> Dict:
        """ایجاد کاربر جدید"""
        user_id = str(uuid.uuid4())[:8]
        expiry = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        user = {
            'id': user_id,
            'name': name,
            'traffic_limit': traffic_limit * 1024 * 1024 * 1024,  # GB to bytes
            'traffic_used': 0,
            'expiry': expiry,
            'status': 'active',
            'created': datetime.now().isoformat(),
            'uuid': str(uuid.uuid4()),
            'vless_link': ''
        }
        
        self.data['users'][user_id] = user
        self.save()
        return user
    
    def delete_user(self, user_id: str) -> bool:
        if user_id in self.data['users']:
            del self.data['users'][user_id]
            self.save()
            return True
        return False
    
    def get_user(self, user_id: str) -> Optional[Dict]:
        return self.data['users'].get(user_id)
    
    def get_all_users(self) -> List[Dict]:
        return list(self.data['users'].values())
    
    def update_traffic(self, user_id: str, bytes_used: int):
        user = self.get_user(user_id)
        if user:
            user['traffic_used'] += bytes_used
            self.save()
    
    def check_expiry(self):
        """بررسی و غیرفعال‌سازی کاربران منقضی شده"""
        now = datetime.now().isoformat()
        for user_id, user in self.data['users'].items():
            if user['expiry'] < now and user['status'] == 'active':
                user['status'] = 'expired'
        self.save()
    
    def get_stats(self) -> Dict:
        users = self.get_all_users()
        total_users = len(users)
        active_users = len([u for u in users if u['status'] == 'active'])
        total_traffic = sum(u['traffic_used'] for u in users)
        
        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_traffic': total_traffic,
            'inbounds_count': len(self.data['inbounds'])
        }

db = Database()
