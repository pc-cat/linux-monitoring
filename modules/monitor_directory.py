import os
import time
import csv
import stat
from pathlib import Path
from datetime import datetime

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
        
        # Initialize CSV Header
        # STRICTLY following Requirement A.iv (Metadata Extraction)
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    "Event_Timestamp", "Event_Type", 
                    "Filename", "File_Type", "Size_Bytes", 
                    "Owner_Group", "Permissions",
                    "Access_Time", "Mod_Time", "Create_Time", # Added these 3
                    "Change_Details" # Stores "Old -> New"
                ])
        
        # Take initial snapshot
        self.previous_state = self._scan_directory()

    def _get_file_details(self, filepath):
        """
        Extracts ALL mandatory metadata [cite: 34-39]
        """
        try:
            path_obj = Path(filepath)
            stats = os.stat(filepath)
            
            # 1. File Type (Requirement A.iv.2)
            if path_obj.is_symlink(): f_type = "Symbolic Link"
            elif path_obj.is_dir(): f_type = "Directory"
            else: f_type = "Regular File"
            
            # 2. Owner & Group (Requirement A.iv.4)
            if pwd and grp:
                try:
                    owner = pwd.getpwuid(stats.st_uid).pw_name
                    group = grp.getgrgid(stats.st_gid).gr_name
                    owner_group = f"{owner}:{group}"
                except KeyError:
                    owner_group = f"{stats.st_uid}:{stats.st_gid}"
            else:
                owner_group = f"{stats.st_uid}:{stats.st_gid}"

            # 3. Permissions
            perms = stat.filemode(stats.st_mode)

            # 4. Timestamps (Requirement A.iv.5)
            # Convert float timestamps to readable strings
            atime_str = datetime.fromtimestamp(stats.st_atime).strftime('%Y-%m-%d %H:%M:%S')
            mtime_str = datetime.fromtimestamp(stats.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
            ctime_str = datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d %H:%M:%S')

            return {
                "size": stats.st_size,
                "mtime_raw": stats.st_mtime, # Kept for comparison logic
                "perms_raw": perms,          # Kept for comparison logic
                
                # Data for Logging
                "type": f_type,
                "owner_group": owner_group,
                "perms": perms,
                "atime": atime_str,
                "mtime": mtime_str,
                "ctime": ctime_str
            }
        except FileNotFoundError:
            return None

    def _scan_directory(self):
        current_state = {}
        if not os.path.exists(self.watch_path):
            return {}

        try:
            for f in os.listdir(self.watch_path):
                full_path = os.path.join(self.watch_path, f)
                details = self._get_file_details(full_path)
                if details:
                    current_state[f] = details
        except PermissionError:
            pass
        return current_state

    def check_updates(self):
        current_state = self._scan_directory()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updates_found = False

        # --- 1. Check DELETED [cite: 23-25] ---
        deleted_files = set(self.previous_state.keys()) - set(current_state.keys())
        for f in deleted_files:
            # "Record filename and timestamp of detection"
            self._write_row(timestamp, "DELETED", f, "N/A", "0", "N/A", "N/A", "N/A", "N/A", "N/A", "File Removed")
            print(f"[FILE] Deleted: {f}")
            updates_found = True

        # --- 2. Check CREATED [cite: 20-22] ---
        new_files = set(current_state.keys()) - set(self.previous_state.keys())
        for f in new_files:
            meta = current_state[f]
            self._write_row(timestamp, "CREATED", f, meta['type'], meta['size'], 
                          meta['owner_group'], meta['perms'], 
                          meta['atime'], meta['mtime'], meta['ctime'], 
                          "New File Added")
            print(f"[FILE] Created: {f}")
            updates_found = True

        # --- 3. Check MODIFIED [cite: 27-32] ---
        common_files = set(current_state.keys()) & set(self.previous_state.keys())
        for f in common_files:
            old_meta = self.previous_state[f]
            new_meta = current_state[f]
            changes = []

            # Check Size Change
            if new_meta['size'] != old_meta['size']:
                changes.append(f"Size: {old_meta['size']} -> {new_meta['size']}")
            
            # Check Permission Change
            if new_meta['perms_raw'] != old_meta['perms_raw']:
                changes.append(f"Perms: {old_meta['perms_raw']} -> {new_meta['perms_raw']}")
            
            # Check Content Modification (Timestamp)
            if new_meta['mtime_raw'] != old_meta['mtime_raw']:
                changes.append("Content Modified")

            if changes:
                change_str = " | ".join(changes)
                self._write_row(timestamp, "MODIFIED", f, new_meta['type'], new_meta['size'], 
                              new_meta['owner_group'], new_meta['perms'], 
                              new_meta['atime'], new_meta['mtime'], new_meta['ctime'], 
                              change_str)
                print(f"[FILE] Modified: {f} -> {change_str}")
                updates_found = True

        self.previous_state = current_state
        return updates_found

    def _write_row(self, ts, event, fname, ftype, size, owner, perms, atime, mtime, ctime, details):
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([ts, event, fname, ftype, size, owner, perms, atime, mtime, ctime, details])
