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
import importlib.util
import glob

# psutil is no longer needed since game detection has been removed

class RedMPanning:
    def __init__(self):
        self.VERSION = "1.004"
        self.INFO_URL = "https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/info.txt"
        self.PYTHON_SRC_URL = "https://raw.githubusercontent.com/DRAGEno01/RedM-Auto-Panning/refs/heads/main/src/Python/"
        self.repo_url = "https://github.com/DRAGEno01/RedM-Auto-Panning/releases"
        
        # State variables
        self.running = False
        self.script_thread = None
        self.hotkey_listener = None
        self.start_hotkey = Key.f6
        self.stop_hotkey = Key.f7
        
        # Theme system
        self.current_theme = 'Default'
        self.previous_theme = 'Default'  # Track previous theme for restart detection
        self.available_themes = {}
        self.theme_colors = {}
        
        # Load settings
        self.load_settings()
        
        # Load available themes
        self.load_themes()
        
        # Create main window
        self.root = tk.Tk()
        self.root.title("DRAGEno01's RedM Auto Panning")
        self.root.geometry("800x650")
        self.root.resizable(False, False)
        self.root.configure(bg='#1a1a1a')
        
        # Center window
        self.center_window()
        
        # Create GUI
        self.create_gui()
        
        # Apply the loaded theme
        self.apply_theme(self.current_theme)
        
        # Setup hotkey listener
        self.setup_hotkey_listener()
        
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
        """Create a beautiful, modern GUI"""
        # Main container with modern dark background
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True)
        
        # Top section with title and version - modern dark styling
        top_section = tk.Frame(main_container, bg='#2d2d2d', height=80)
        top_section.pack(fill=tk.X, padx=0, pady=0)
        top_section.pack_propagate(False)
        
        # Title with modern styling
        title_label = tk.Label(top_section, text="RedM Auto Panning", 
                              font=('Segoe UI', 28, 'bold'), 
                              fg='#ffffff', bg='#2d2d2d')
        title_label.pack(side=tk.LEFT, padx=30, pady=20)
        
        # Version badge - modern dark styling
        version_frame = tk.Frame(top_section, bg='#404040', relief=tk.FLAT, bd=0)
        version_frame.pack(side=tk.RIGHT, padx=30, pady=20)
        
        version_label = tk.Label(version_frame, text=f"v{self.VERSION}", 
                               font=('Segoe UI', 12, 'bold'), 
                               fg='#a78bfa', bg='#404040',
                               padx=12, pady=6)
        version_label.pack()
        
        # Main content area - balanced spacing
        content_area = tk.Frame(main_container, bg='#1a1a1a')
        content_area.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Status card with modern dark design - balanced spacing
        status_card = tk.Frame(content_area, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        status_card.pack(fill=tk.X, pady=(0, 20))
        
        # Status indicator with icon-like design - balanced spacing
        status_container = tk.Frame(status_card, bg='#2d2d2d')
        status_container.pack(pady=18)
        
        # Status dot (visual indicator) - modern green
        status_dot = tk.Frame(status_container, bg='#4ade80', width=12, height=12, relief=tk.FLAT, bd=0)
        status_dot.pack(side=tk.LEFT, padx=(0, 15))
        status_dot.pack_propagate(False)
        
        self.status_label = tk.Label(status_container, text="Ready to Start", 
                                   font=('Segoe UI', 20, 'bold'), 
                                   fg='#ffffff', bg='#2d2d2d')
        self.status_label.pack(side=tk.LEFT)
        
        # Control buttons with modern dark card design - balanced spacing
        control_card = tk.Frame(content_area, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        control_card.pack(fill=tk.X, pady=(0, 20))
        
        # Button container - balanced spacing
        button_container = tk.Frame(control_card, bg='#2d2d2d')
        button_container.pack(pady=18)
        
        # Start button with compact settings-style
        self.start_button = tk.Button(button_container, text="▶ START", 
                                     command=self.start_script,
                                     font=('Segoe UI', 11, 'bold'),
                                     fg='white', bg='#22c55e', relief=tk.FLAT, bd=0,
                                     padx=15, pady=8, cursor='hand2')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Stop button with compact settings-style
        self.stop_button = tk.Button(button_container, text="⏹ STOP", 
                                    command=self.stop_script,
                                    font=('Segoe UI', 11, 'bold'),
                                    fg='white', bg='#f87171', relief=tk.FLAT, bd=0,
                                    padx=15, pady=8, cursor='hand2')
        self.stop_button.pack(side=tk.LEFT)
        self.stop_button.config(state=tk.DISABLED)
        
        # Info section with hotkeys - modern dark card, balanced spacing
        info_card = tk.Frame(content_area, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        info_card.pack(fill=tk.X, pady=(0, 20))
        
        # Store reference to hotkey label for dynamic updates - balanced spacing
        self.hotkey_label = tk.Label(info_card, text="", 
                                    font=('Segoe UI', 12, 'bold'), 
                                    fg='#94a3b8', bg='#2d2d2d')
        self.hotkey_label.pack(pady=15)
        
        # Update hotkey display with current settings
        self.update_hotkey_display()
        
        # Footer with modern buttons - balanced spacing
        footer = tk.Frame(content_area, bg='#1a1a1a')
        footer.pack(side=tk.BOTTOM, fill=tk.X, pady=(20, 0))
        
        # Footer buttons with compact settings-style - closer together
        github_btn = tk.Button(footer, text="🔗 GitHub", 
                              command=self.open_github,
                              font=('Segoe UI', 11, 'bold'),
                              fg='white', bg='#6b7280', relief=tk.FLAT, bd=0,
                              padx=15, pady=8, cursor='hand2')
        github_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        donate_btn = tk.Button(footer, text="💖 Donate", 
                              command=self.open_donate,
                              font=('Segoe UI', 11, 'bold'),
                              fg='white', bg='#e91e63', relief=tk.FLAT, bd=0,
                              padx=15, pady=8, cursor='hand2')
        donate_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        themes_btn = tk.Button(footer, text="🎨 Themes", 
                              command=self.open_theme_browser,
                              font=('Segoe UI', 11, 'bold'),
                              fg='white', bg='#8b5cf6', relief=tk.FLAT, bd=0,
                              padx=15, pady=8, cursor='hand2')
        themes_btn.pack(side=tk.LEFT, padx=(0, 5))
        
        settings_btn = tk.Button(footer, text="⚙️ Settings", 
                                command=self.show_settings,
                                font=('Segoe UI', 11, 'bold'),
                                fg='white', bg='#6b7280', relief=tk.FLAT, bd=0,
                                padx=15, pady=8, cursor='hand2')
        settings_btn.pack(side=tk.LEFT, padx=(5, 0))
    
    def update_hotkey_display(self):
        """Update the hotkey display in the UI with current settings"""
        if hasattr(self, 'hotkey_label'):
            start_key = self.get_key_name(self.start_hotkey)
            stop_key = self.get_key_name(self.stop_hotkey)
            self.hotkey_label.config(text=f"⌨️  {start_key} to Start  •  {stop_key} to Stop")
    
    def get_key_name(self, key):
        """Convert key object to display name"""
        if hasattr(key, 'name'):
            return key.name.upper()
        return str(key).upper()
    
    def create_modern_button(self, parent, text, color, command):
        """Create a modern, beautiful button with glassmorphism effect"""
        button = tk.Button(parent, text=text, command=command,
                          font=('Segoe UI', 18, 'bold'),
                          fg='white', bg=color, relief=tk.FLAT, bd=0,
                          padx=40, pady=20, cursor='hand2',
                          activebackground=color, activeforeground='white')
        
        # Modern hover effects
        def on_enter(e):
            if color == '#10b981':  # Start button
                button.config(bg='#059669')
            elif color == '#ef4444':  # Stop button
                button.config(bg='#dc2626')
        
        def on_leave(e):
            button.config(bg=color)
        
        button.bind('<Enter>', on_enter)
        button.bind('<Leave>', on_leave)
        
        return button
    
    def create_footer_button(self, parent, text, command):
        """Create a modern footer button with subtle styling"""
        button = tk.Button(parent, text=text, command=command,
                          font=('Segoe UI', 12, 'bold'),
                          fg='#94a3b8', bg='#1a1a2e', relief=tk.FLAT, bd=0,
                          padx=20, pady=12, cursor='hand2',
                          activebackground='#16213e', activeforeground='#ffffff')
        
        # Subtle hover effects
        def on_enter(e):
            button.config(bg='#16213e', fg='#ffffff')
        
        def on_leave(e):
            button.config(bg='#1a1a2e', fg='#94a3b8')
        
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
            self.status_label.config(text="Stopped", fg='#ef4444')
    
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
                    text=f"Waiting {remaining:.1f}s", fg='#fbbf24'
                ))
            time.sleep(0.1)
    
    def perform_action(self):
        """Perform the panning action"""
        if not self.running:
            return
            
        # Update status
        self.root.after(0, lambda: self.status_label.config(text="Performing Action", fg='#8b5cf6'))
        
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
        tampering_window.configure(bg='#1a1a1a')
        tampering_window.grab_set()
        
        # Center the dialog
        tampering_window.transient(self.root)
        tampering_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Main container with modern dark styling
        main_container = tk.Frame(tampering_window, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Header section with modern dark styling
        header_frame = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with modern styling
        title_label = tk.Label(header_frame, text="🚨 Security Warning", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg='#ef4444', bg='#2d2d2d')
        title_label.pack(pady=15)
        
        # Content area with modern dark card
        content_card = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        content_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Message
        message_text = """WARNING: This application appears to have been modified from the official version.

The code has been changed from the official version. This could be a security risk.

For your safety, please download a new secure copy from the official GitHub repository to ensure you have the authentic, unmodified version."""
        
        # Create a text widget for better text wrapping with modern styling
        text_widget = tk.Text(content_card, 
                             font=('Segoe UI', 12), 
                             fg='#ffffff', bg='#2d2d2d',
                             wrap=tk.WORD, 
                             height=8, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=20, 
                             pady=20)
        text_widget.pack(pady=20, fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Modern button container
        button_container = tk.Frame(main_container, bg='#1a1a1a')
        button_container.pack(fill=tk.X, pady=(0, 0))
        
        github_button = tk.Button(button_container, text="📥 Download Official Version", 
                                 command=lambda: [webbrowser.open(self.repo_url), tampering_window.destroy()],
                                 font=('Segoe UI', 11, 'bold'),
                                 fg='white', bg='#22c55e', relief=tk.FLAT, bd=0,
                                 padx=20, pady=10, cursor='hand2')
        github_button.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_button = tk.Button(button_container, text="❌ Exit", 
                               command=self.root.quit,
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', bg='#6b7280', relief=tk.FLAT, bd=0,
                               padx=20, pady=10, cursor='hand2')
        exit_button.pack(side=tk.LEFT)
        
        # Apply current theme to the popup
        self.apply_theme_to_popup(tampering_window)
    
    def show_update_dialog(self, latest_version):
        """Show update dialog"""
        update_window = tk.Toplevel(self.root)
        update_window.title("Update Required - RedM Auto Panning")
        update_window.geometry("600x500")
        update_window.resizable(False, False)
        update_window.configure(bg='#1a1a1a')
        update_window.grab_set()
        
        # Center the dialog
        update_window.transient(self.root)
        update_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Handle window close (X button) - exit the app
        update_window.protocol("WM_DELETE_WINDOW", self.root.quit)
        
        # Main container with modern dark styling
        main_container = tk.Frame(update_window, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Header section with modern dark styling
        header_frame = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with modern styling
        title_label = tk.Label(header_frame, text="⚠️ Update Required", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg='#f87171', bg='#2d2d2d')
        title_label.pack(pady=15)
        
        # Content area with modern dark card
        content_card = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        content_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Message with proper wrapping
        message_text = f"""Your version is outdated and no longer supported.

Current version: {self.VERSION}
Latest version: {latest_version}

Please download and install the latest version to ensure optimal performance and security."""
        
        # Create a text widget for better text wrapping with modern styling
        text_widget = tk.Text(content_card, 
                             font=('Segoe UI', 12), 
                             fg='#ffffff', bg='#2d2d2d',
                             wrap=tk.WORD, 
                             height=8, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=20, 
                             pady=20)
        text_widget.pack(pady=20, fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Modern button container
        button_container = tk.Frame(main_container, bg='#1a1a1a')
        button_container.pack(fill=tk.X, pady=(0, 0))
        
        download_button = tk.Button(button_container, text="📥 Download Update", 
                                   command=lambda: self.download_update(latest_version, update_window),
                                   font=('Segoe UI', 11, 'bold'),
                                   fg='white', bg='#22c55e', relief=tk.FLAT, bd=0,
                                   padx=20, pady=10, cursor='hand2')
        download_button.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_button = tk.Button(button_container, text="❌ Exit", 
                               command=self.root.quit,
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', bg='#6b7280', relief=tk.FLAT, bd=0,
                               padx=20, pady=10, cursor='hand2')
        exit_button.pack(side=tk.LEFT)
        
        # Apply current theme to the popup
        self.apply_theme_to_popup(update_window)
    
    def show_connection_warning(self):
        """Show connection warning dialog"""
        warning_window = tk.Toplevel(self.root)
        warning_window.title("Connection Warning")
        warning_window.geometry("550x450")
        warning_window.resizable(False, False)
        warning_window.configure(bg='#1a1a1a')
        warning_window.grab_set()
        
        # Center the dialog
        warning_window.transient(self.root)
        warning_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Main container with modern dark styling
        main_container = tk.Frame(warning_window, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Header section with modern dark styling
        header_frame = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with modern styling
        title_label = tk.Label(header_frame, text="⚠️ Connection Warning", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg='#f59e0b', bg='#2d2d2d')
        title_label.pack(pady=15)
        
        # Content area with modern dark card
        content_card = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        content_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Message with proper wrapping
        message_text = f"""Unable to check for updates. Please verify your internet connection.

Current version: {self.VERSION}

You can continue using the application, but updates may be available."""
        
        # Create a text widget for better text wrapping with modern styling
        text_widget = tk.Text(content_card, 
                             font=('Segoe UI', 12), 
                             fg='#ffffff', bg='#2d2d2d',
                             wrap=tk.WORD, 
                             height=6, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=20, 
                             pady=20)
        text_widget.pack(pady=20, fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Modern button container
        button_container = tk.Frame(main_container, bg='#1a1a1a')
        button_container.pack(fill=tk.X, pady=(0, 0))
        
        continue_button = tk.Button(button_container, text="✅ Continue", 
                                   command=warning_window.destroy,
                                   font=('Segoe UI', 11, 'bold'),
                                   fg='white', bg='#6b7280', relief=tk.FLAT, bd=0,
                                   padx=20, pady=10, cursor='hand2')
        continue_button.pack(side=tk.LEFT, padx=(0, 10))
        
        github_button = tk.Button(button_container, text="🔗 Check GitHub", 
                               command=lambda: [webbrowser.open(self.repo_url), warning_window.destroy()],
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', bg='#22c55e', relief=tk.FLAT, bd=0,
                               padx=20, pady=10, cursor='hand2')
        github_button.pack(side=tk.LEFT)
        
        # Apply current theme to the popup
        self.apply_theme_to_popup(warning_window)
    
    def show_unsupported_warning_dialog(self):
        """Show unsupported version warning (can continue)"""
        warning_window = tk.Toplevel(self.root)
        warning_window.title("Version Warning - RedM Auto Panning")
        warning_window.geometry("550x450")
        warning_window.resizable(False, False)
        warning_window.configure(bg='#1a1a1a')
        warning_window.grab_set()
        
        # Center the dialog
        warning_window.transient(self.root)
        warning_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Main container with modern dark styling
        main_container = tk.Frame(warning_window, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Header section with modern dark styling
        header_frame = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with modern styling
        title_label = tk.Label(header_frame, text="⚠️ Version Warning", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg='#f59e0b', bg='#2d2d2d')
        title_label.pack(pady=15)
        
        # Content area with modern dark card
        content_card = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        content_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Message
        message_text = f"""This version is no longer officially supported.

Current version: {self.VERSION}

You can still continue to use the current version, but it may never be updated again. We recommend switching to the Java version or downloading the latest Python version from GitHub for continued support and updates."""
        
        # Create a text widget for better text wrapping with modern styling
        text_widget = tk.Text(content_card, 
                             font=('Segoe UI', 12), 
                             fg='#ffffff', bg='#2d2d2d',
                             wrap=tk.WORD, 
                             height=8, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=20, 
                             pady=20)
        text_widget.pack(pady=20, fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Modern button container
        button_container = tk.Frame(main_container, bg='#1a1a1a')
        button_container.pack(fill=tk.X, pady=(0, 0))
        
        continue_button = tk.Button(button_container, text="✅ Continue Anyway", 
                                   command=warning_window.destroy,
                                   font=('Segoe UI', 11, 'bold'),
                                   fg='white', bg='#6b7280', relief=tk.FLAT, bd=0,
                                   padx=20, pady=10, cursor='hand2')
        continue_button.pack(side=tk.LEFT, padx=(0, 10))
        
        github_button = tk.Button(button_container, text="🔗 Go to GitHub", 
                                 command=lambda: [webbrowser.open(self.repo_url), warning_window.destroy()],
                                 font=('Segoe UI', 11, 'bold'),
                                 fg='white', bg='#22c55e', relief=tk.FLAT, bd=0,
                                 padx=20, pady=10, cursor='hand2')
        github_button.pack(side=tk.LEFT)
        
        # Apply current theme to the popup
        self.apply_theme_to_popup(warning_window)
    
    def show_must_update_dialog(self, latest_version):
        """Show must update dialog (cannot continue)"""
        must_update_window = tk.Toplevel(self.root)
        must_update_window.title("Update Required - RedM Auto Panning")
        must_update_window.geometry("600x500")
        must_update_window.resizable(False, False)
        must_update_window.configure(bg='#1a1a1a')
        must_update_window.grab_set()
        
        # Center the dialog
        must_update_window.transient(self.root)
        must_update_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Handle window close (X button) - exit the app
        must_update_window.protocol("WM_DELETE_WINDOW", self.root.quit)
        
        # Main container with modern dark styling
        main_container = tk.Frame(must_update_window, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Header section with modern dark styling
        header_frame = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with modern styling
        title_label = tk.Label(header_frame, text="🚫 Update Required", 
                              font=('Segoe UI', 20, 'bold'), 
                              fg='#ef4444', bg='#2d2d2d')
        title_label.pack(pady=15)
        
        # Content area with modern dark card
        content_card = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        content_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Message
        message_text = f"""This version is no longer supported and cannot be used.

Current version: {self.VERSION}
Latest version: {latest_version}

You cannot use this version of the application. Please visit GitHub to download a supported version (Python or Java)."""
        
        # Create a text widget for better text wrapping with modern styling
        text_widget = tk.Text(content_card, 
                             font=('Segoe UI', 12), 
                             fg='#ffffff', bg='#2d2d2d',
                             wrap=tk.WORD, 
                             height=8, 
                             width=60,
                             relief=tk.FLAT, 
                             bd=0,
                             padx=20, 
                             pady=20)
        text_widget.pack(pady=20, fill=tk.BOTH, expand=True)
        text_widget.insert(tk.END, message_text)
        text_widget.config(state=tk.DISABLED)  # Make it read-only
        
        # Modern button container
        button_container = tk.Frame(main_container, bg='#1a1a1a')
        button_container.pack(fill=tk.X, pady=(0, 0))
        
        github_button = tk.Button(button_container, text="🔗 Visit GitHub", 
                                 command=lambda: [webbrowser.open(self.repo_url), must_update_window.destroy()],
                                 font=('Segoe UI', 11, 'bold'),
                                 fg='white', bg='#22c55e', relief=tk.FLAT, bd=0,
                                 padx=20, pady=10, cursor='hand2')
        github_button.pack(side=tk.LEFT, padx=(0, 10))
        
        exit_button = tk.Button(button_container, text="❌ Exit", 
                               command=self.root.quit,
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', bg='#6b7280', relief=tk.FLAT, bd=0,
                               padx=20, pady=10, cursor='hand2')
        exit_button.pack(side=tk.LEFT)
        
        # Apply current theme to the popup
        self.apply_theme_to_popup(must_update_window)
    
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
                
                # Clean up any existing backup or new files from previous failed updates
                if os.path.exists(backup_file):
                    os.remove(backup_file)
                    print(f"[INFO] Removed existing backup file: {backup_file}")
                
                if os.path.exists(new_file):
                    os.remove(new_file)
                    print(f"[INFO] Removed existing new file: {new_file}")
                
                # Backup current file
                if os.path.exists(current_file):
                    os.rename(current_file, backup_file)
                    print(f"[INFO] Created backup: {backup_file}")
                
                # Replace with new version
                if os.path.exists(new_file):
                    os.rename(new_file, current_file)
                    print(f"[INFO] Installed new version: {current_file}")
                else:
                    raise Exception("New file not found after download")
                
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
        settings_window.title("Settings - RedM Auto Panning")
        settings_window.geometry("450x400")
        settings_window.resizable(False, False)
        settings_window.configure(bg='#1a1a1a')
        settings_window.grab_set()
        
        # Center the dialog
        settings_window.transient(self.root)
        settings_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 50, self.root.winfo_rooty() + 50))
        
        # Main container with modern dark styling
        main_container = tk.Frame(settings_window, bg='#1a1a1a')
        main_container.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Modern header section with subtle gradient effect
        header_frame = tk.Frame(main_container, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Modern title with better spacing
        title_label = tk.Label(header_frame, text="⚙️ Settings", 
                              font=('Segoe UI', 18, 'bold'), 
                              fg='#ffffff', bg='#2d2d2d')
        title_label.pack(pady=15)
        
        # Content area with subtle background
        content_frame = tk.Frame(main_container, bg='#1a1a1a')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Modern settings cards with dark styling and proper padding
        settings_card = tk.Frame(content_frame, bg='#2d2d2d', relief=tk.FLAT, bd=0)
        settings_card.pack(fill=tk.X, pady=(0, 20), padx=10)
        
        # Add subtle inner border
        inner_border = tk.Frame(settings_card, bg='#404040', height=1)
        inner_border.pack(fill=tk.X, pady=(0, 15))
        
        # Start hotkey - modern layout with proper padding
        start_frame = tk.Frame(settings_card, bg='#2d2d2d')
        start_frame.pack(fill=tk.X, pady=(0, 12), padx=15)
        
        start_label = tk.Label(start_frame, text="🎯 Start Hotkey:", 
                              font=('Segoe UI', 12, 'bold'), 
                              fg='#4ade80', bg='#2d2d2d')
        start_label.pack(side=tk.LEFT)
        
        # Create modern styled combobox for start hotkey
        start_combo = tk.StringVar()
        start_combo.set(f"F{self.start_hotkey.value.vk - 111}")
        
        start_dropdown = tk.OptionMenu(start_frame, start_combo, *[f"F{i}" for i in range(1, 13)])
        start_dropdown.config(font=('Segoe UI', 11), bg='#404040', fg='white', 
                            activebackground='#525252', activeforeground='white',
                            relief=tk.FLAT, bd=0, padx=10, pady=5, width=8)
        start_dropdown.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Stop hotkey - modern layout with proper padding
        stop_frame = tk.Frame(settings_card, bg='#2d2d2d')
        stop_frame.pack(fill=tk.X, pady=(0, 12), padx=15)
        
        stop_label = tk.Label(stop_frame, text="⏹ Stop Hotkey:", 
                             font=('Segoe UI', 12, 'bold'), 
                             fg='#f87171', bg='#2d2d2d')
        stop_label.pack(side=tk.LEFT)
        
        # Create modern styled combobox for stop hotkey
        stop_combo = tk.StringVar()
        stop_combo.set(f"F{self.stop_hotkey.value.vk - 111}")
        
        stop_dropdown = tk.OptionMenu(stop_frame, stop_combo, *[f"F{i}" for i in range(1, 13)])
        stop_dropdown.config(font=('Segoe UI', 11), bg='#404040', fg='white', 
                           activebackground='#525252', activeforeground='white',
                           relief=tk.FLAT, bd=0, padx=10, pady=5, width=8)
        stop_dropdown.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Theme selection - modern layout with proper padding
        theme_frame = tk.Frame(settings_card, bg='#2d2d2d')
        theme_frame.pack(fill=tk.X, pady=(0, 15), padx=15)
        
        theme_label = tk.Label(theme_frame, text="🎨 Theme:", 
                              font=('Segoe UI', 12, 'bold'), 
                              fg='#a78bfa', bg='#2d2d2d')
        theme_label.pack(side=tk.LEFT)
        
        # Create modern theme selection with available themes
        theme_var = tk.StringVar()
        theme_var.set(self.current_theme)  # Set current theme
        
        # Get available theme names
        theme_options = ['Default'] + list(self.available_themes.keys())
        
        theme_dropdown = tk.OptionMenu(theme_frame, theme_var, *theme_options)
        theme_dropdown.config(font=('Segoe UI', 11), bg='#404040', fg='white', 
                           activebackground='#525252', activeforeground='white',
                           relief=tk.FLAT, bd=0, padx=10, pady=5, width=8)
        theme_dropdown.pack(side=tk.RIGHT, padx=(0, 5))
        
        # Modern button container
        button_container = tk.Frame(content_frame, bg='#1a1a1a')
        button_container.pack(fill=tk.X, pady=(25, 0))
        
        def save_settings():
            # Update hotkeys based on selection
            start_f_num = int(start_combo.get()[1:])
            stop_f_num = int(stop_combo.get()[1:])
            
            self.start_hotkey = getattr(Key, f'f{start_f_num}')
            self.stop_hotkey = getattr(Key, f'f{stop_f_num}')
            
            # Update theme
            selected_theme = theme_var.get()
            
            # Check if theme changed BEFORE updating current_theme
            theme_changed = selected_theme != self.current_theme
            
            # Update current theme
            self.current_theme = selected_theme
            
            # Save settings to file first
            self.save_settings()
            
            # Update the UI display with new hotkeys
            self.update_hotkey_display()
            
            # Close settings window
            settings_window.destroy()
            
            # Check if theme changed and restart if needed
            if theme_changed:
                print(f"[INFO] Theme changed from {self.previous_theme} to {selected_theme}")
                self.restart_with_theme(selected_theme)
            else:
                print(f"[INFO] Theme unchanged ({selected_theme}), no restart needed")
        
        # Create compact dark buttons that fit properly
        save_button = tk.Button(button_container, text="💾 Save", 
                               command=save_settings,
                               font=('Segoe UI', 11, 'bold'),
                               fg='white', bg='#22c55e', relief=tk.FLAT, bd=0,
                               padx=15, pady=8, cursor='hand2')
        save_button.pack(side=tk.LEFT, padx=(0, 10))
        
        theme_folder_button = tk.Button(button_container, text="📁 Theme Folder", 
                                       command=self.create_theme_folder,
                                       font=('Segoe UI', 11, 'bold'),
                                       fg='white', bg='#8b5cf6', relief=tk.FLAT, bd=0,
                                       padx=15, pady=8, cursor='hand2')
        theme_folder_button.pack(side=tk.LEFT, padx=(0, 10))
        
        cancel_button = tk.Button(button_container, text="❌ Cancel", 
                                 command=settings_window.destroy,
                                 font=('Segoe UI', 11, 'bold'),
                                 fg='white', bg='#6b7280', relief=tk.FLAT, bd=0,
                                 padx=15, pady=8, cursor='hand2')
        cancel_button.pack(side=tk.LEFT)
        
        # Apply current theme to the settings dialog
        self.apply_theme_to_popup(settings_window)
    
    def open_github(self):
        """Open GitHub repository"""
        webbrowser.open(self.repo_url)
    
    def open_donate(self):
        """Open Patreon donation page"""
        webbrowser.open("https://www.patreon.com/DRAGEno01")
    
    def open_theme_browser(self):
        """Open theme browser website"""
        webbrowser.open("https://drageno01.web.app/projects/redm-ap/")
    
    def create_theme_folder(self):
        """Create themes folder if it doesn't exist and open it"""
        try:
            script_dir = self.get_script_dir()
            themes_folder = os.path.join(script_dir, "themes")
            
            if not os.path.exists(themes_folder):
                os.makedirs(themes_folder)
                print(f"[SUCCESS] Created themes folder at: {themes_folder}")
            
            # Open the themes folder in file explorer
            import subprocess
            import platform
            
            system = platform.system()
            try:
                if system == "Windows":
                    subprocess.run(["explorer", themes_folder], check=False)
                elif system == "Darwin":  # macOS
                    subprocess.run(["open", themes_folder], check=False)
                else:  # Linux and others
                    subprocess.run(["xdg-open", themes_folder], check=False)
                    
                print(f"[SUCCESS] Opened themes folder: {themes_folder}")
            except Exception as open_error:
                print(f"[WARNING] Could not open file explorer: {open_error}")
                # Don't show error dialog for file explorer issues
                
        except Exception as e:
            print(f"[ERROR] Failed to create themes folder: {e}")
            # Show error message to user only for folder creation failures
            import tkinter.messagebox as msgbox
            msgbox.showerror("Theme Folder Error", f"Failed to create themes folder:\n\n{str(e)}")
    
    def get_script_dir(self):
        """Get the directory where the script is located"""
        return os.path.dirname(os.path.abspath(__file__))
    
    def load_themes(self):
        """Load available themes from the themes folder"""
        try:
            themes_dir = os.path.join(self.get_script_dir(), "themes")
            if not os.path.exists(themes_dir):
                print("[INFO] Themes directory does not exist")
                return
            
            # Find all .py files in themes directory
            theme_files = glob.glob(os.path.join(themes_dir, "*.py"))
            
            for theme_file in theme_files:
                try:
                    # Extract theme name from filename
                    theme_name = os.path.splitext(os.path.basename(theme_file))[0]
                    
                    # Load the theme module
                    spec = importlib.util.spec_from_file_location(theme_name, theme_file)
                    theme_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(theme_module)
                    
                    # Get theme configuration
                    if hasattr(theme_module, 'get_theme'):
                        theme_config = theme_module.get_theme()
                        self.available_themes[theme_name] = theme_config
                        print(f"[SUCCESS] Loaded theme: {theme_name}")
                    else:
                        print(f"[WARNING] Theme {theme_name} does not have get_theme() function")
                        
                except Exception as e:
                    print(f"[ERROR] Failed to load theme {theme_file}: {e}")
            
            print(f"[INFO] Loaded {len(self.available_themes)} themes")
            
        except Exception as e:
            print(f"[ERROR] Failed to load themes: {e}")
    
    def apply_theme(self, theme_name):
        """Apply a theme to the application"""
        try:
            if theme_name == 'Default':
                # Use default dark theme - matching exact UI colors
                self.theme_colors = {
                    'bg_primary': '#1a1a1a',        # Main background
                    'bg_secondary': '#2d2d2d',      # Card backgrounds
                    'bg_card': '#2d2d2d',           # Card backgrounds
                    'bg_header': '#2d2d2d',         # Header background
                    'bg_version': '#404040',        # Version badge background
                    'text_primary': '#ffffff',      # Primary text
                    'text_secondary': '#94a3b8',   # Secondary text
                    'text_accent': '#a78bfa',       # Accent text (version)
                    'text_success': '#4ade80',      # Success text
                    'text_warning': '#fbbf24',      # Warning text
                    'text_danger': '#ef4444',       # Danger text
                    'btn_primary': '#22c55e',       # Start button
                    'btn_success': '#22c55e',       # Success button
                    'btn_danger': '#f87171',        # Stop button
                    'btn_secondary': '#6b7280',     # GitHub/Settings buttons
                    'btn_warning': '#f59e0b',       # Warning button
                    'btn_info': '#e91e63',          # Donate button
                    'status_ready': '#4ade80',      # Ready status
                    'status_running': '#8b5cf6',    # Running status
                    'status_stopped': '#ef4444',    # Stopped status
                    'status_waiting': '#fbbf24',    # Waiting status
                    'border_light': '#404040',      # Light border
                    'border_medium': '#525252',     # Medium border
                    'border_dark': '#6b7280',       # Dark border
                    'accent_primary': '#8b5cf6',    # Primary accent
                    'accent_secondary': '#6b7280',  # Secondary accent
                    'highlight': '#2d2d2d',        # Highlight background
                    'status_dot': '#4ade80',        # Status dot color
                }
            elif theme_name in self.available_themes:
                self.theme_colors = self.available_themes[theme_name]
            else:
                print(f"[WARNING] Theme '{theme_name}' not found, using default")
                self.apply_theme('Default')
                return
            
            # Apply theme to current UI
            self.apply_theme_to_ui()
            print(f"[SUCCESS] Applied theme: {theme_name}")
            
        except Exception as e:
            print(f"[ERROR] Failed to apply theme {theme_name}: {e}")
    
    def apply_theme_to_ui(self):
        """Apply current theme colors to the UI"""
        try:
            if not hasattr(self, 'root') or not self.theme_colors:
                return
            
            # Apply to main window
            self.root.configure(bg=self.theme_colors.get('bg_primary', '#1a1a1a'))
            
            # Apply to all widgets recursively
            self.apply_theme_to_widget(self.root)
            
            # Force UI refresh to ensure changes are visible
            self.root.update_idletasks()
            self.root.update()
            
        except Exception as e:
            print(f"[ERROR] Failed to apply theme to UI: {e}")
    
    def apply_theme_to_widget(self, widget):
        """Recursively apply theme to widget and its children"""
        try:
            # Apply theme based on widget type and configuration
            if isinstance(widget, tk.Frame):
                if hasattr(widget, 'cget'):
                    try:
                        current_bg = widget.cget('bg')
                        # Map specific background colors to theme colors
                        if current_bg == '#1a1a1a':
                            widget.configure(bg=self.theme_colors.get('bg_primary', current_bg))
                        elif current_bg == '#2d2d2d':
                            widget.configure(bg=self.theme_colors.get('bg_secondary', current_bg))
                        elif current_bg == '#404040':
                            # Inner borders and version badges use this color
                            widget.configure(bg=self.theme_colors.get('border_light', self.theme_colors.get('bg_version', current_bg)))
                    except:
                        pass
            elif isinstance(widget, tk.Label):
                if hasattr(widget, 'cget'):
                    try:
                        current_fg = widget.cget('fg')
                        current_bg = widget.cget('bg')
                        
                        # Map text colors
                        if current_fg == '#ffffff':
                            widget.configure(fg=self.theme_colors.get('text_primary', current_fg))
                        elif current_fg == '#94a3b8':
                            widget.configure(fg=self.theme_colors.get('text_secondary', current_fg))
                        elif current_fg == '#a78bfa':
                            widget.configure(fg=self.theme_colors.get('text_accent', current_fg))
                        elif current_fg == '#4ade80':
                            widget.configure(fg=self.theme_colors.get('text_success', current_fg))
                        elif current_fg == '#f87171':
                            widget.configure(fg=self.theme_colors.get('text_danger', current_fg))
                        elif current_fg == '#fbbf24':
                            widget.configure(fg=self.theme_colors.get('text_warning', current_fg))
                        
                        # Map background colors for labels
                        if current_bg == '#1a1a1a':
                            widget.configure(bg=self.theme_colors.get('bg_primary', current_bg))
                        elif current_bg == '#2d2d2d':
                            widget.configure(bg=self.theme_colors.get('bg_secondary', current_bg))
                        elif current_bg == '#404040':
                            widget.configure(bg=self.theme_colors.get('bg_version', current_bg))
                    except:
                        pass
            elif isinstance(widget, tk.Button):
                if hasattr(widget, 'cget'):
                    try:
                        current_bg = widget.cget('bg')
                        # Map button colors
                        if current_bg == '#22c55e':
                            widget.configure(bg=self.theme_colors.get('btn_success', current_bg))
                        elif current_bg == '#f87171':
                            widget.configure(bg=self.theme_colors.get('btn_danger', current_bg))
                        elif current_bg == '#6b7280':
                            widget.configure(bg=self.theme_colors.get('btn_secondary', current_bg))
                        elif current_bg == '#8b5cf6':
                            widget.configure(bg=self.theme_colors.get('accent_primary', current_bg))
                        elif current_bg == '#e91e63':
                            widget.configure(bg=self.theme_colors.get('btn_info', current_bg))
                    except:
                        pass
            elif isinstance(widget, tk.Text):
                if hasattr(widget, 'cget'):
                    try:
                        current_fg = widget.cget('fg')
                        current_bg = widget.cget('bg')
                        
                        # Map text widget colors
                        if current_fg == '#ffffff':
                            widget.configure(fg=self.theme_colors.get('text_primary', current_fg))
                        elif current_fg == '#b0b0b0':
                            widget.configure(fg=self.theme_colors.get('text_secondary', current_fg))
                        
                        if current_bg == '#1a1a1a':
                            widget.configure(bg=self.theme_colors.get('bg_primary', current_bg))
                        elif current_bg == '#2d2d2d':
                            widget.configure(bg=self.theme_colors.get('bg_secondary', current_bg))
                        elif current_bg == '#1c2026':
                            widget.configure(bg=self.theme_colors.get('bg_primary', current_bg))
                    except:
                        pass
            elif isinstance(widget, tk.OptionMenu) or isinstance(widget, tk.Menubutton):
                # OptionMenu is actually a Menubutton
                if hasattr(widget, 'cget'):
                    try:
                        current_bg = widget.cget('bg')
                        current_fg = widget.cget('fg')
                        
                        # Map OptionMenu colors
                        if current_bg == '#404040':
                            widget.configure(bg=self.theme_colors.get('border_light', self.theme_colors.get('bg_version', current_bg)))
                        elif current_bg == '#2d2d2d':
                            widget.configure(bg=self.theme_colors.get('bg_secondary', current_bg))
                        
                        if current_fg == 'white' or current_fg == '#ffffff':
                            widget.configure(fg=self.theme_colors.get('text_primary', '#ffffff'))
                        
                        # Try to set activebackground if it exists
                        try:
                            current_abg = widget.cget('activebackground')
                            if current_abg == '#525252':
                                widget.configure(activebackground=self.theme_colors.get('border_medium', current_abg))
                        except:
                            # Set default activebackground if not set
                            widget.configure(activebackground=self.theme_colors.get('border_medium', '#525252'))
                        
                        # Set activeforeground
                        try:
                            widget.configure(activeforeground=self.theme_colors.get('text_primary', '#ffffff'))
                        except:
                            pass
                    except:
                        pass
            
            # Apply to children
            for child in widget.winfo_children():
                self.apply_theme_to_widget(child)
                
        except Exception as e:
            print(f"[ERROR] Failed to apply theme to widget: {e}")
    
    def apply_theme_to_popup(self, popup_window):
        """Apply current theme to a popup dialog window"""
        try:
            if not hasattr(self, 'theme_colors') or not self.theme_colors:
                return
            
            # Apply theme to the popup window
            popup_window.configure(bg=self.theme_colors.get('bg_primary', '#1a1a1a'))
            
            # Apply theme to all widgets in the popup
            self.apply_theme_to_widget(popup_window)
            
            # Force update to ensure changes are visible
            popup_window.update_idletasks()
            popup_window.update()
            
        except Exception as e:
            print(f"[ERROR] Failed to apply theme to popup: {e}")
    
    def refresh_ui_theme(self):
        """Force a complete UI theme refresh"""
        try:
            # Apply theme to all widgets
            self.apply_theme_to_ui()
            
            # Force multiple UI updates to ensure changes are visible
            self.root.update_idletasks()
            self.root.update()
            
            # Additional refresh for stubborn widgets
            self.root.after(100, lambda: self.root.update_idletasks())
            
            print(f"[SUCCESS] UI theme refreshed for: {self.current_theme}")
            
        except Exception as e:
            print(f"[ERROR] Failed to refresh UI theme: {e}")
    
    def restart_with_theme(self, theme_name):
        """Restart the application with the new theme"""
        try:
            print(f"[INFO] Restarting application with theme: {theme_name}")
            
            # Show restart message
            self.show_restart_message(theme_name)
            
            # Get current script path
            script_path = os.path.abspath(__file__)
            
            # Close current application
            self.root.quit()
            
            # Start new instance with the same script
            import subprocess
            subprocess.Popen([sys.executable, script_path])
            
            # Exit current instance
            sys.exit(0)
            
        except Exception as e:
            print(f"[ERROR] Failed to restart application: {e}")
            # Fallback to regular theme application
            self.apply_theme(theme_name)
    
    def show_restart_message(self, theme_name):
        """Show a brief message about theme restart"""
        try:
            # Create a simple message window
            restart_window = tk.Toplevel(self.root)
            restart_window.title("Applying Theme")
            restart_window.geometry("400x200")
            restart_window.resizable(False, False)
            restart_window.configure(bg='#1a1a1a')
            restart_window.grab_set()
            
            # Center the message
            restart_window.transient(self.root)
            restart_window.geometry("+%d+%d" % (self.root.winfo_rootx() + 100, self.root.winfo_rooty() + 100))
            
            # Content
            content_frame = tk.Frame(restart_window, bg='#1a1a1a')
            content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
            
            # Message
            message_label = tk.Label(content_frame, 
                                   text=f"🎨 Applying {theme_name} theme...\n\nRestarting application...", 
                                   font=('Segoe UI', 14, 'bold'), 
                                   fg='#ffffff', bg='#1a1a1a',
                                   justify=tk.CENTER)
            message_label.pack(expand=True)
            
            # Auto-close after 2 seconds
            restart_window.after(2000, restart_window.destroy)
            
        except Exception as e:
            print(f"[ERROR] Failed to show restart message: {e}")
    
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
                    # Load theme from settings
                    self.current_theme = settings.get('theme', 'Default')
                    self.previous_theme = self.current_theme  # Set initial previous theme
            else:
                self.current_theme = 'Default'
                self.previous_theme = 'Default'
        except Exception as e:
            print(f"Error loading settings: {e}")
            self.current_theme = 'Default'  # Default theme
    
    def save_settings(self):
        """Save settings to file"""
        try:
            settings = {
                'start_hotkey': int(self.start_hotkey.value.vk - 111),
                'stop_hotkey': int(self.stop_hotkey.value.vk - 111),
                'theme': getattr(self, 'current_theme', 'Default')
            }
            settings_path = os.path.join(self.get_script_dir(), 'settings.json')
            with open(settings_path, 'w') as f:
                json.dump(settings, f)
            
            # Update previous theme for next comparison
            self.previous_theme = self.current_theme
            
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

if __name__ == "__main__":
    try:
        app = RedMPanning()
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        messagebox.showerror("Error", f"Failed to start application: {e}")
