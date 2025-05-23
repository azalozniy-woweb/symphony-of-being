import os
import time
import pickle
import shutil
MAX_BACKUPS = 5
AUTOSAVE_BACKUPS = 352

class MemoryBackupManager:
    def __init__(self, db_file):
        self.db_file = db_file
        os.makedirs("backup", exist_ok=True)

    def safe_save_to_backup(self):
        """Создаёт стабильную резервную копию, которую ничего не трогает."""
        try:
            if os.path.exists(self.db_file) and os.stat(self.db_file).st_size > 100:
                safe_copy = self.db_file.replace(".pkl", ".safe.pkl")
                shutil.copy(self.db_file, safe_copy)
                print("[SAFE] Сделана безопасная копия памяти.")
        except Exception as e:
            print(f"[SAFE ERROR] Ошибка при создании безопасной копии: {e}")

    def create_backup(self):
        backup_file = f"backup/memory_backup_{int(time.time())}.db"
        if not os.path.exists(self.db_file):
            return
        backup_files = [f for f in os.listdir("backup") if f.endswith(".db")]
        if len(backup_files) >= MAX_BACKUPS:
            oldest = min(backup_files, key=lambda x: os.path.getctime(os.path.join("backup", x)))
            os.remove(os.path.join("backup", oldest))
        try:
            shutil.copy(self.db_file, backup_file)
        except:
            pass

    def restore_from_backup(self):
        files = [f for f in os.listdir("backup") if f.endswith(".db")]
        if files:
            latest = max(files, key=lambda x: os.path.getctime(os.path.join("backup", x)))
            try:
                with open(os.path.join("backup", latest), 'rb') as f:
                    return pickle.loads(f.read())
            except Exception as e:
                print(f"[RESTORE] Ошибка при загрузке backup: {e}")
        return {}, {}  # <-- Вставь это, если ничего не найдено или ошибка


    def restore_from_safe_copy(self):
        safe_copy = self.db_file.replace(".pkl", ".safe.pkl")
        if os.path.exists(safe_copy):
            try:
                with open(safe_copy, 'rb') as f:
                    return pickle.loads(f.read())
            except Exception as e:
                print(f"[RESTORE] Не удалось загрузить safe copy: {e}")
        return None
