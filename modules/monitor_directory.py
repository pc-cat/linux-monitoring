
import os
import time
import csv
import stat
from pathlib import Path

# Linux-specific imports for Owner/Group names
try:
    import pwd
    import grp
except ImportError:
    pwd = None
    grp = None

class DirectoryMonitor:
    def __init__(self, watch_path, log_file):
        self.watch_path = watch_path
        self.log_file = log_file
        self.previous_state = {} 
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        # Initialize CSV Header if file doesn't exist
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Timestamp", "Event", "Filename", "Type", 
                    "Size_Bytes", "Owner", "Permissions"
                ])
        
        # Take initial snapshot so we don't alert on existing files
        self.previous_state = self._scan_directory()

    def _get_file_details(self, filepath):
        """Extracts mandatory metadata as per Assignment Section 2.A.iv"""
        try:
            path_obj = Path(filepath)
            stats = os.stat(filepath)
            
            # 1. File Type [cite: 36]
            if path_obj.is_dir(): f_type = "Directory"
            elif path_obj.is_symlink(): f_type = "SymLink"
            else: f_type = "File"
            
            # 2. Owner & Group [cite: 38]
            if pwd:
                owner = pwd.getpwuid(stats.st_uid).pw_name
                group = grp.getgrgid(stats.st_gid).gr_name
            else:
                owner = str(stats.st_uid)
                group = str(stats.st_gid)

            # 3. Permissions (e.g., -rwxr-xr-x)
            perms = stat.filemode(stats.st_mode)

            return {
                "size": stats.st_size,
                "mtime": stats.st_mtime,
                "type": f_type,
                "owner": f"{owner}:{group}",
                "perms": perms
            }
        except FileNotFoundError:
            return None

    def _scan_directory(self):
        """Returns a dict of current files and their metadata."""
        current_state = {}
        if not os.path.exists(self.watch_path):
            print(f"[ERROR] Directory not found: {self.watch_path}")
            return {}

        try:
            for f in os.listdir(self.watch_path):
                full_path = os.path.join(self.watch_path, f)
                details = self._get_file_details(full_path)
                if details:
                    current_state[f] = details
        except PermissionError:
            print(f"[ERROR] Permission denied accessing {self.watch_path}")
        
        return current_state

    def check_updates(self):
        """Compares current state vs previous state and logs changes."""
        current_state = self._scan_directory()
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        updates_found = False

        # 1. Check for DELETED files [cite: 23]
        deleted_files = set(self.previous_state.keys()) - set(current_state.keys())
        for f in deleted_files:
            self._log_to_csv(timestamp, "DELETED", f, "N/A", 0, "N/A", "N/A")
            print(f"[FILE] Deleted: {f}")
            updates_found = True

        # 2. Check for CREATED files [cite: 20]
        new_files = set(current_state.keys()) - set(self.previous_state.keys())
        for f in new_files:
            meta = current_state[f]
            self._log_to_csv(timestamp, "CREATED", f, meta['type'], meta['size'], meta['owner'], meta['perms'])
            print(f"[FILE] Created: {f}")
            updates_found = True

        # 3. Check for MODIFIED files [cite: 26]
        common_files = set(current_state.keys()) & set(self.previous_state.keys())
        for f in common_files:
            old_meta = self.previous_state[f]
            new_meta = current_state[f]
            
            # Detect change in Size or Modification Time
            if new_meta['mtime'] != old_meta['mtime'] or new_meta['size'] != old_meta['size']:
                self._log_to_csv(timestamp, "MODIFIED", f, new_meta['type'], new_meta['size'], new_meta['owner'], new_meta['perms'])
                print(f"[FILE] Modified: {f}")
                updates_found = True

        self.previous_state = current_state
        return updates_found

    def _log_to_csv(self, timestamp, event, filename, ftype, size, owner, perms):
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, event, filename, ftype, size, owner, perms])
