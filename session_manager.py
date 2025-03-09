import json
from pathlib import Path
import hashlib
from typing import Optional, Dict
from config import USERS_XLSX

class SessionManager:
    def __init__(self):
        self.users_file = Path(USERS_XLSX)
        self._init_files()

    def _init_files(self):
        if not self.users_file.exists():
            default_users = {
                "admin": {
                    "password": hashlib.sha256("password123".encode()).hexdigest(),
                    "role": "admin"
                }
            }
            self.users_file.parent.mkdir(exist_ok=True)
            self.users_file.write_text(json.dumps(default_users))

    def validate_user(self, username: str, password: str) -> bool:
        users = json.loads(self.users_file.read_text())
        if username in users:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            return users[username]["password"] == hashed_password
        return False
    
    def reset_password(self, username: str, old_password: str, new_password: str, confirm_password: str) -> Dict[str, str]:
        if not self.validate_user(username, old_password):
            return {"status": "error", "message": "現在のパスワードが無効です。"}
        if new_password != confirm_password:
            return {"status": "error", "message": "新しいパスワードと確認用パスワードが一致しません。"}
            
        users = json.loads(self.users_file.read_text())
        users[username]["password"] = hashlib.sha256(new_password.encode()).hexdigest()
        self.users_file.write_text(json.dumps(users))
        return {"status": "success", "message": "パスワードが正常に更新されました。"}