import tkinter as tk
from tkinter import ttk, messagebox, font
import threading
import time
import random
import subprocess
import os
import sys
import json
import urllib.request
import urllib.error
from pynput import keyboard
from pynput.keyboard import Key, Listener
from datetime import datetime
import webbrowser

# Try to import psutil, fallback to subprocess if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("Warning: psutil not available. Game detection will use subprocess fallback.")

class RedMPanning:
    def __init__(self):
        self.VERSION = "1.001"
        self.INFO_URL = "https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/info.txt"
        self.PYTHON_SRC_URL = "https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/"
        self.repo_url = "https://github.com/DRAGEno01/RedM-Auto-Panning/releases"
        
        # State variables
        self.running = False
        self.script_thread = None
        self.hotkey_listener = None
        self.game_detection_active = False
        self.redm_detected = False
        self.start_hotkey = Key.f6
        self.stop_hotkey = Key.f7
        
        # Load settings
        self.load_settings()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("DRAGEno01's RedM Auto Panning")
        self.root.geometry("700x550")
        self.root.resizable(False, False)
        self.root.configure(bg='#1c2026')
        
        # Center window
        self.center_window()
        
        # Create GUI
        self.create_gui()
        
        # Setup hotkey listener
        self.setup_hotkey_listener()
        
        # Setup game detection
        self.setup_game_detection()
        
        # Check for updates
        self.check_version()
        
        # Check application integrity
        self.check_integrity()
        
        # Ensure requirements.txt exists
        self.ensure_requirements_file()
        
        # Start fade-in animation
        self.fade_in_animation()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_gui(self):
        """Create the main GUI"""
        # Main frame with gradient background
        main_frame = tk.Frame(self.root, bg='#1c2026')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=35, pady=35)
        
        # Header panel
        header_frame = tk.Frame(main_frame, bg='#2d333b', relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title and version
        title_frame = tk.Frame(header_frame, bg='#2d333b')
        title_frame.pack(side=tk.LEFT, padx=20, pady=15)
        
        title_label = tk.Label(title_frame, text="RedM Auto Panning", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg='#e0e0e0', bg='#2d333b')
        title_label.pack(side=tk.LEFT)
        
        # Version label
        version_label = tk.Label(header_frame, text=f"v{self.VERSION}", 
                               font=('Segoe UI', 12, 'bold'), 
                               fg='#8b949e', bg='#2d333b')
        version_label.pack(side=tk.RIGHT, padx=20, pady=15)
        
        # Status panel
        status_frame = tk.Frame(main_frame, bg='#000000', relief=tk.FLAT, bd=0)
        status_frame.pack(fill=tk.X, pady=(0, 30))
        
        self.status_label = tk.Label(status_frame, text="Status: Idle", 
                                   font=('Segoe UI', 16, 'bold'), 
                                   fg='#8df18a', bg='#000000')
        self.status_label.pack(pady=20)
        
        # Button panel
        button_frame = tk.Frame(main_frame, bg='#1c2026')
        button_frame.pack(pady=(0, 30))
        
        self.start_button = self.create_styled_button(button_frame, "START", '#28a745', self.start_script)
        self.start_button.pack(side=tk.LEFT, padx=20)
        
        self.stop_button = self.create_styled_button(button_frame, "STOP", '#dc3545', self.stop_script)
        self.stop_button.pack(side=tk.LEFT, padx=20)
        self.stop_button.config(state=tk.DISABLED)
        
        # Game status panel
        game_status_frame = tk.Frame(main_frame, bg='#2d333b', relief=tk.FLAT, bd=0)
        game_status_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.game_status_label = tk.Label(game_status_frame, text="Game Status: Not Detected", 
                                        font=('Segoe UI', 12, 'bold'), 
                                        fg='#c8c8c8', bg='#2d333b')
        self.game_status_label.pack(pady=10)
        
        # Footer panel
        footer_frame = tk.Frame(main_frame, bg='#1c2026')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        # GitHub button
        github_button = self.create_styled_button(footer_frame, "View on GitHub", '#333333', self.open_github)
        github_button.pack(side=tk.LEFT)
        
        # Settings button
        settings_button = self.create_styled_button(footer_frame, "Settings", '#404040', self.show_settings)
        settings_button.pack(side=tk.RIGHT)
    
    def create_styled_button(self, parent, text, color, command):
        """Create a styled button"""
        button = tk.Button(parent, text=text, command=command,
                          font=('Segoe UI', 14, 'bold'),
                          fg='white', bg=color, relief=tk.FLAT, bd=0,
                          padx=20, pady=10, cursor='hand2')
        
        # Add hover effects
        def on_enter(e):
            if color == '#28a745':
                button.config(bg='#2eb84f')
            elif color == '#dc3545':
                button.config(bg='#e74c3c')
            elif color == '#333333':
                button.config(bg='#404040')
            elif color == '#404040':
                button.config(bg='#505050')
        
        def on_leave(e):
            button.config(bg=color)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button
    
    def start_script(self):
        """Start the auto-panning script"""
        if not self.running:
            self.running = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            
            self.script_thread = threading.Thread(target=self.run_script, daemon=True)
            self.script_thread.start()
        else:
            messagebox.showinfo("Info", "Script is already running.")
    
    def stop_script(self):
        """Stop the auto-panning script"""
        if self.running:
            self.running = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.status_label.config(text="Status: Stopped")
    
    def run_script(self):
        """Main script loop"""
        while self.running:
            # Calculate wait time between 17 and 20 seconds
            wait_time = 17.0 + random.random() * 3.0
            wait_time = max(17.0, wait_time)
            
            # Update status with countdown
            self.update_status_with_countdown(wait_time)
            
            if self.running:
                self.perform_action()
    
    def update_status_with_countdown(self, total_seconds):
        """Update status with countdown timer"""
        start_time = time.time()
        while self.running and (time.time() - start_time) < total_seconds:
            remaining = total_seconds - (time.time() - start_time)
            if remaining > 0:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"Waiting: {remaining:.1f} seconds"
                ))
            time.sleep(0.1)
    
    def perform_action(self):
        """Perform the panning action"""
        if not self.running:
            return
            
        # Update status
        self.root.after(0, lambda: self.status_label.config(text="Performing Action"))
        
        # Calculate hold time with randomization
        hold_time = 0.9 + random.random() * 0.2
        hold_time += (random.random() - 0.5) * 0.05
        hold_time = round(hold_time, 5)
        
        # Introduce occasional "normal" behavior
        if random.random() < 0.05:
            hold_time = 1.0
        
        # Simulate key press (using pynput)
        try:
            # Press and hold Enter
            keyboard.Controller().press(Key.enter)
            time.sleep(hold_time)
            keyboard.Controller().release(Key.enter)
        except Exception as e:
            print(f"Error performing action: {e}")
    
    def setup_hotkey_listener(self):
        """Setup global hotkey listener"""
        def on_press(key):
            try:
                if key == self.start_hotkey and not self.running:
                    self.root.after(0, self.start_script)
                elif key == self.stop_hotkey and self.running:
                    self.root.after(0, self.stop_script)
            except AttributeError:
                pass
        
        def on_release(key):
            pass
        
        self.hotkey_listener = Listener(on_press=on_press, on_release=on_release)
        self.hotkey_listener.start()
    
    def setup_game_detection(self):
        """Setup RedM game detection"""
        self.game_detection_active = True
        self.detect_game()
    
    def detect_game(self):
        """Detect if RedM is running"""
        if not self.game_detection_active:
            return
            
        was_detected = self.redm_detected
        self.redm_detected = self.is_redm_running()
        
        if self.redm_detected != was_detected:
            if self.redm_detected:
                self.game_status_label.config(text="Game Status: Running", fg='#8df18a')
            else:
                self.game_status_label.config(text="Game Status: Not Detected", fg='#ff8080')
                if self.running:
                    self.stop_script()
        
        # Schedule next detection
        self.root.after(2000, self.detect_game)
    
    def is_redm_running(self):
        """Check if RedM process is running"""
        if PSUTIL_AVAILABLE:
            try:
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    try:
                        if proc.info['name'] and 'RedM' in proc.info['name']:
                            return True
                        if proc.info['cmdline']:
                            cmdline = ' '.join(proc.info['cmdline'])
                            if 'RedM' in cmdline:
                                return True
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
            except Exception as e:
                print(f"Error checking RedM process with psutil: {e}")
        else:
            # Fallback using subprocess and tasklist
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq RedM.exe'], 
                                      capture_output=True, text=True, timeout=5)
                return 'RedM.exe' in result.stdout
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
                print(f"Error checking RedM process with tasklist: {e}")
        return False
    
    def check_version(self):
        """Check for application updates"""
        def check():
            try:
                with urllib.request.urlopen(self.INFO_URL, timeout=5) as response:
                    info_content = response.read().decode('utf-8').strip()
                
                # Parse the info.py content
                supported = None
                latest_version = None
                
                for line in info_content.split('\n'):
                    line = line.strip()
                    if line.startswith('supported'):
                        supported = line.split('=')[1].strip()
                    elif line.startswith('version'):
                        latest_version = line.split('=')[1].strip()
                
                print(f"Remote info - Supported: {supported}, Version: {latest_version}")
                print(f"Local version: {self.VERSION}")
                
                # Check if supported and version scenarios
                if supported and supported.lower() == 'false':
                    if latest_version and latest_version != self.VERSION:
                        # Not supported AND different version - must update
                        self.root.after(0, lambda: self.show_must_update_dialog(latest_version))
                    else:
                        # Not supported but same version - can continue with warning
                        self.root.after(0, lambda: self.show_unsupported_warning_dialog())
                    return
                
                # Check if version is different (and supported)
                if latest_version and latest_version != self.VERSION:
                    self.root.after(0, lambda: self.show_update_dialog(latest_version))
                    
            except Exception as e:
                print(f"Version check failed: {e}")
                # Show connection warning
                self.root.after(0, self.show_connection_warning)
        
        threading.Thread(target=check, daemon=True).start()
    
    def check_integrity(self):
        """Check application integrity to detect tampering"""
        def integrity_check():
            try:
                # Extract author from GitHub URL
                author = self.extract_author_from_url(self.repo_url)
                if not author:
                    return  # Skip check if can't extract author
                
                # Check if title contains the correct author
                if author not in self.root.title():
                    self.root.after(0, self.show_tampering_warning)
                    return
                
                # Read the current file to check for tampering
                try:
                    with open(__file__, 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Check if author appears in the code (more subtle)
                    if author not in file_content:
                        self.root.after(0, self.show_tampering_warning)
                        return
                        
                except Exception as e:
                    print(f"Error reading file for integrity check: {e}")
                    self.root.after(0, self.show_tampering_warning)
                    return
                    
            except Exception as e:
                print(f"Integrity check failed: {e}")
                self.root.after(0, self.show_tampering_warning)
        
        threading.Thread(target=integrity_check, daemon=True).start()
    
    def ensure_requirements_file(self):
        """Create requirements.txt if it doesn't exist"""
        try:
            requirements_path = os.path.join(self.get_script_dir(), 'requirements.txt')
            if not os.path.exists(requirements_path):
                requirements_content = """pynput>=1.7.6
psutil>=5.9.0"""
                with open(requirements_path, 'w') as f:
                    f.write(requirements_content)
                print(f"Created requirements.txt at: {requirements_path}")
        except Exception as e:
            print(f"Error creating requirements.txt: {e}")
    
    def extract_author_from_url(self, url):
        """Extract author name from GitHub URL"""
        try:
            # Parse GitHub URL to extract author
            if 'github.com' in url:
                parts = url.split('/')
                for i, part in enumerate(parts):
                    if part == 'github.com' and i + 1 < len(parts):
                        return parts[i + 1]  # Return the username after github.com
            return None
        except Exception as e:
            print(f"Error extracting author from URL: {e}")
            return None
    
    def show_tampering_warning(self):
        """Show tampering warning dialog"""
        tampering_window = tk.Toplevel(self.root)
        tampering_window.title("Security Warning")
        tampering_window.geometry("600x500")
        tampering_window.resizable(False, False)
        tampering_window.configure(bg='#1c2026')
        tampering_window.grab_set()
        
        # Center the dialog
        tampering_window.transient(self.root)
        tampering_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Content
        content_frame = tk.Frame(tampering_window, bg='#1c2026')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(content_frame, text="Security Warning", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg='#ff4444', bg='#1c2026')
        title_label.pack(pady=(0, 25))
        
        # Message
        message_text = """WARNING: This application appears to have been modified from the official version.

The code has been changed from the official version. This could be a security risk.

For your safety, please download a new secure copy from the official GitHub repository to ensure you have the authentic, unmodified version."""
        
        # Create a text widget for better text wrapping
        text_widget = tk.Text(content_frame, 
                             font=('Segoe UI', 12), 
                             fg='#b0b0b0', bg='#1c2026',
                             wrap=tk.WORD, 
                             height=8, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=10, 
                             pady=10)
        text_widget.pack(pady=(0, 25), fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#1c2026')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        github_button = tk.Button(button_frame, text="Download Official Version", 
                                 command=lambda: [webbrowser.open(self.repo_url), tampering_window.destroy()],
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg='#28a745', relief=tk.FLAT, bd=0,
                                 padx=20, pady=12, cursor='hand2')
        github_button.pack(side=tk.LEFT, padx=(0, 15))
        
        exit_button = tk.Button(button_frame, text="Exit", 
                               command=self.root.quit,
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#dc3545', relief=tk.FLAT, bd=0,
                               padx=20, pady=12, cursor='hand2')
        exit_button.pack(side=tk.RIGHT)
    
    def show_update_dialog(self, latest_version):
        """Show update dialog"""
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Required")
        update_window.geometry("600x500")
        update_window.resizable(False, False)
        update_window.configure(bg='#1c2026')
        update_window.grab_set()
        
        # Center the dialog
        update_window.transient(self.root)
        update_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Content
        content_frame = tk.Frame(update_window, bg='#1c2026')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(content_frame, text="Update Required", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg='#ff6b6b', bg='#1c2026')
        title_label.pack(pady=(0, 25))
        
        # Message with proper wrapping
        message_text = f"""Your version is outdated and no longer supported.

Current version: {self.VERSION}
Latest version: {latest_version}

Please download and install the latest version to ensure optimal performance and security."""
        
        # Create a text widget for better text wrapping
        text_widget = tk.Text(content_frame, 
                             font=('Segoe UI', 12), 
                             fg='#b0b0b0', bg='#1c2026',
                             wrap=tk.WORD, 
                             height=8, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=10, 
                             pady=10)
        text_widget.pack(pady=(0, 25), fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#1c2026')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        download_button = tk.Button(button_frame, text="Download", 
                                   command=lambda: self.download_update(latest_version, update_window),
                                   font=('Segoe UI', 12, 'bold'),
                                   fg='white', bg='#28a745', relief=tk.FLAT, bd=0,
                                   padx=25, pady=12, cursor='hand2')
        download_button.pack(side=tk.LEFT, padx=(0, 15))
        
        exit_button = tk.Button(button_frame, text="Exit", 
                               command=self.root.quit,
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#dc3545', relief=tk.FLAT, bd=0,
                               padx=25, pady=12, cursor='hand2')
        exit_button.pack(side=tk.RIGHT)
    
    def show_connection_warning(self):
        """Show connection warning dialog"""
        warning_window = tk.Toplevel(self.root)
        warning_window.title("Connection Warning")
        warning_window.geometry("500x400")
        warning_window.resizable(False, False)
        warning_window.configure(bg='#1c2026')
        warning_window.grab_set()
        
        # Center the dialog
        warning_window.transient(self.root)
        warning_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Content
        content_frame = tk.Frame(warning_window, bg='#1c2026')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(content_frame, text="Connection Warning", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg='#ffa500', bg='#1c2026')
        title_label.pack(pady=(0, 25))
        
        # Message with proper wrapping
        message_text = f"""Unable to check for updates. Please verify your internet connection.

Current version: {self.VERSION}

You can continue using the application, but updates may be available."""
        
        # Create a text widget for better text wrapping
        text_widget = tk.Text(content_frame, 
                             font=('Segoe UI', 12), 
                             fg='#b0b0b0', bg='#1c2026',
                             wrap=tk.WORD, 
                             height=6, 
                             width=50,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=10, 
                             pady=10)
        text_widget.pack(pady=(0, 25), fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#1c2026')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        continue_button = tk.Button(button_frame, text="Continue", 
                                   command=warning_window.destroy,
                                   font=('Segoe UI', 12, 'bold'),
                                   fg='white', bg='#6c757d', relief=tk.FLAT, bd=0,
                                   padx=25, pady=12, cursor='hand2')
        continue_button.pack(side=tk.LEFT, padx=(0, 15))
        
        github_button = tk.Button(button_frame, text="Check GitHub", 
                                 command=lambda: [webbrowser.open(self.repo_url), warning_window.destroy()],
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg='#007bff', relief=tk.FLAT, bd=0,
                                 padx=25, pady=12, cursor='hand2')
        github_button.pack(side=tk.RIGHT)
    
    def show_unsupported_warning_dialog(self):
        """Show unsupported version warning (can continue)"""
        warning_window = tk.Toplevel(self.root)
        warning_window.title("Version Warning")
        warning_window.geometry("550x450")
        warning_window.resizable(False, False)
        warning_window.configure(bg='#1c2026')
        warning_window.grab_set()
        
        # Center the dialog
        warning_window.transient(self.root)
        warning_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Content
        content_frame = tk.Frame(warning_window, bg='#1c2026')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(content_frame, text="Version Warning", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg='#ffa500', bg='#1c2026')
        title_label.pack(pady=(0, 25))
        
        # Message
        message_text = f"""This version is no longer officially supported.

Current version: {self.VERSION}

You can still continue to use the current version, but it may never be updated again. We recommend switching to the Java version or downloading the latest Python version from GitHub for continued support and updates."""
        
        # Create a text widget for better text wrapping
        text_widget = tk.Text(content_frame, 
                             font=('Segoe UI', 12), 
                             fg='#b0b0b0', bg='#1c2026',
                             wrap=tk.WORD, 
                             height=8, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=10, 
                             pady=10)
        text_widget.pack(pady=(0, 25), fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#1c2026')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        continue_button = tk.Button(button_frame, text="Continue Anyway", 
                                   command=warning_window.destroy,
                                   font=('Segoe UI', 12, 'bold'),
                                   fg='white', bg='#6c757d', relief=tk.FLAT, bd=0,
                                   padx=20, pady=12, cursor='hand2')
        continue_button.pack(side=tk.LEFT, padx=(0, 10))
        
        github_button = tk.Button(button_frame, text="Go to GitHub", 
                                 command=lambda: [webbrowser.open(self.repo_url), warning_window.destroy()],
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg='#007bff', relief=tk.FLAT, bd=0,
                                 padx=20, pady=12, cursor='hand2')
        github_button.pack(side=tk.RIGHT)
    
    def show_must_update_dialog(self, latest_version):
        """Show must update dialog (cannot continue)"""
        must_update_window = tk.Toplevel(self.root)
        must_update_window.title("Update Required")
        must_update_window.geometry("600x500")
        must_update_window.resizable(False, False)
        must_update_window.configure(bg='#1c2026')
        must_update_window.grab_set()
        
        # Center the dialog
        must_update_window.transient(self.root)
        must_update_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Content
        content_frame = tk.Frame(must_update_window, bg='#1c2026')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(content_frame, text="Update Required", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg='#ff4444', bg='#1c2026')
        title_label.pack(pady=(0, 25))
        
        # Message
        message_text = f"""This version is no longer supported and cannot be used.

Current version: {self.VERSION}
Latest version: {latest_version}

You cannot use this version of the application. Please visit GitHub to download a supported version (Python or Java)."""
        
        # Create a text widget for better text wrapping
        text_widget = tk.Text(content_frame, 
                             font=('Segoe UI', 12), 
                             fg='#b0b0b0', bg='#1c2026',
                             wrap=tk.WORD, 
                             height=8, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=10, 
                             pady=10)
        text_widget.pack(pady=(0, 25), fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#1c2026')
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        github_button = tk.Button(button_frame, text="Visit GitHub", 
                                 command=lambda: [webbrowser.open(self.repo_url), must_update_window.destroy()],
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg='#007bff', relief=tk.FLAT, bd=0,
                                 padx=25, pady=12, cursor='hand2')
        github_button.pack(side=tk.LEFT, padx=(0, 15))
        
        exit_button = tk.Button(button_frame, text="Exit", 
                               command=self.root.quit,
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#dc3545', relief=tk.FLAT, bd=0,
                               padx=25, pady=12, cursor='hand2')
        exit_button.pack(side=tk.RIGHT)
    
    def download_update(self, latest_version, parent_window):
        """Download the latest update"""
        try:
            # Construct URL for the new version
            url = f"{self.PYTHON_SRC_URL}V{latest_version}/RedMPanning.py"
            print(f"Downloading from: {url}")
            
            # Download to script directory
            script_dir = self.get_script_dir()
            new_file_path = os.path.join(script_dir, "RedMPanning_new.py")
            urllib.request.urlretrieve(url, new_file_path)
            
            # Show progress dialog
            self.show_update_progress(latest_version, parent_window)
            
        except Exception as e:
            print(f"Download error: {e}")
            messagebox.showerror("Update Failed", f"Error downloading update: {e}")
    
    def show_update_progress(self, latest_version, parent_window):
        """Show update progress and perform the update"""
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Updating Application")
        progress_window.geometry("500x300")
        progress_window.resizable(False, False)
        progress_window.configure(bg='#1c2026')
        progress_window.grab_set()
        
        # Center the dialog
        progress_window.transient(self.root)
        progress_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Content
        content_frame = tk.Frame(progress_window, bg='#1c2026')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Title
        title_label = tk.Label(content_frame, text="Updating Application", 
                              font=('Segoe UI', 16, 'bold'), 
                              fg='#28a745', bg='#1c2026')
        title_label.pack(pady=(0, 20))
        
        # Status label
        status_label = tk.Label(content_frame, text="Preparing update...", 
                              font=('Segoe UI', 12), 
                              fg='#b0b0b0', bg='#1c2026')
        status_label.pack(pady=(0, 20))
        
        # Progress bar
        progress_bar = ttk.Progressbar(content_frame, mode='indeterminate')
        progress_bar.pack(fill=tk.X, pady=(0, 20))
        progress_bar.start()
        
        def perform_update():
            try:
                # Update status
                status_label.config(text="Installing update...")
                progress_window.update()
                
                script_dir = self.get_script_dir()
                current_file = os.path.join(script_dir, "RedMPanning.py")
                backup_file = os.path.join(script_dir, "RedMPanning_backup.py")
                new_file = os.path.join(script_dir, "RedMPanning_new.py")
                
                # Backup current file
                if os.path.exists(current_file):
                    os.rename(current_file, backup_file)
                
                # Replace with new version
                if os.path.exists(new_file):
                    os.rename(new_file, current_file)
                
                # Update status
                status_label.config(text="Update complete! Restarting...")
                progress_window.update()
                
                # Wait a moment then restart
                time.sleep(2)
                
                # Close current application
                parent_window.destroy()
                progress_window.destroy()
                self.root.quit()
                
                # Restart the application from script directory
                import subprocess
                subprocess.Popen([sys.executable, current_file])
                
            except Exception as e:
                print(f"Update error: {e}")
                status_label.config(text=f"Update failed: {e}")
                messagebox.showerror("Update Failed", f"Error during update: {e}")
        
        # Start update in background
        threading.Thread(target=perform_update, daemon=True).start()
    
    def show_settings(self):
        """Show settings dialog"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Settings")
        settings_window.geometry("450x350")
        settings_window.resizable(False, False)
        settings_window.configure(bg='#1c2026')
        settings_window.grab_set()
        
        # Center the dialog
        settings_window.transient(self.root)
        settings_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Content
        content_frame = tk.Frame(settings_window, bg='#1c2026')
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(content_frame, text="Hotkey Settings", 
                              font=('Segoe UI', 16, 'bold'), 
                              fg='white', bg='#1c2026')
        title_label.pack(pady=(0, 30))
        
        # Start hotkey
        start_frame = tk.Frame(content_frame, bg='#2d333b', relief=tk.FLAT, bd=0)
        start_frame.pack(fill=tk.X, pady=(0, 15))
        
        start_label = tk.Label(start_frame, text="Start Hotkey:", 
                              font=('Segoe UI', 12), 
                              fg='white', bg='#2d333b')
        start_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        start_combo = ttk.Combobox(start_frame, values=[f"F{i}" for i in range(1, 13)], 
                                 state="readonly", width=10)
        start_combo.set(f"F{self.start_hotkey.value.vk - 111}")  # Convert to F1-F12
        start_combo.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Stop hotkey
        stop_frame = tk.Frame(content_frame, bg='#2d333b', relief=tk.FLAT, bd=0)
        stop_frame.pack(fill=tk.X, pady=(0, 30))
        
        stop_label = tk.Label(stop_frame, text="Stop Hotkey:", 
                             font=('Segoe UI', 12), 
                             fg='white', bg='#2d333b')
        stop_label.pack(side=tk.LEFT, padx=15, pady=10)
        
        stop_combo = ttk.Combobox(stop_frame, values=[f"F{i}" for i in range(1, 13)], 
                                state="readonly", width=10)
        stop_combo.set(f"F{self.stop_hotkey.value.vk - 111}")  # Convert to F1-F12
        stop_combo.pack(side=tk.RIGHT, padx=15, pady=10)
        
        # Buttons
        button_frame = tk.Frame(content_frame, bg='#1c2026')
        button_frame.pack(fill=tk.X)
        
        def save_settings():
            # Update hotkeys based on selection
            start_f_num = int(start_combo.get()[1:])
            stop_f_num = int(stop_combo.get()[1:])
            
            self.start_hotkey = getattr(Key, f'f{start_f_num}')
            self.stop_hotkey = getattr(Key, f'f{stop_f_num}')
            
            self.save_settings()
            settings_window.destroy()
        
        save_button = tk.Button(button_frame, text="Save Changes", 
                               command=save_settings,
                               font=('Segoe UI', 12, 'bold'),
                               fg='white', bg='#28a745', relief=tk.FLAT, bd=0,
                               padx=20, pady=10, cursor='hand2')
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = tk.Button(button_frame, text="Cancel", 
                                 command=settings_window.destroy,
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg='#6c757d', relief=tk.FLAT, bd=0,
                                 padx=20, pady=10, cursor='hand2')
        cancel_button.pack(side=tk.RIGHT)
    
    def open_github(self):
        """Open GitHub repository"""
        webbrowser.open(self.repo_url)
    
    def get_script_dir(self):
        """Get the directory where the script is located"""
        return os.path.dirname(os.path.abspath(__file__))
    
    def load_settings(self):
        """Load settings from file"""
        try:
            settings_path = os.path.join(self.get_script_dir(), 'settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                    start_f = settings.get('start_hotkey', 6)
                    stop_f = settings.get('stop_hotkey', 7)
                    self.start_hotkey = getattr(Key, f'f{start_f}')
                    self.stop_hotkey = getattr(Key, f'f{stop_f}')
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'start_hotkey': int(self.start_hotkey.value.vk - 111),
                'stop_hotkey': int(self.stop_hotkey.value.vk - 111)
            }
            settings_path = os.path.join(self.get_script_dir(), 'settings.json')
            with open(settings_path, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def fade_in_animation(self):
        """Fade-in animation for the window"""
        self.root.attributes('-alpha', 0.0)
        
        def fade_in():
            alpha = self.root.attributes('-alpha')
            if alpha < 1.0:
                alpha += 0.05
                self.root.attributes('-alpha', alpha)
                self.root.after(50, fade_in)
        
        self.root.after(200, fade_in)
    
    def run(self):
        """Run the application"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            pass
        finally:
            # Cleanup
            if self.hotkey_listener:
                self.hotkey_listener.stop()
            self.game_detection_active = False

if __name__ == "__main__":
    try:
        app = RedMPanning()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")
