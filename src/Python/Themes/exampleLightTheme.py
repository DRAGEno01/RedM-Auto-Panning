# Light Theme for DRAGEno01's RedM Auto Panning
# This example theme provides a clean, bright interface.

def get_theme():
    """Return theme configuration dictionary"""
    return {
        'name': 'Light',
        'description': 'Clean and bright interface',
        
        # Main colors
        'bg_primary': '#ffffff',      # Main background
        'bg_secondary': '#f8f9fa',    # Card backgrounds
        'bg_card': '#f8f9fa',         # Card backgrounds
        'bg_header': '#e9ecef',       # Header background
        'bg_version': '#dee2e6',      # Version badge background
        
        # Text colors
        'text_primary': '#212529',    # Primary text
        'text_secondary': '#6c757d',  # Secondary text
        'text_accent': '#007bff',      # Accent text (version)
        'text_success': '#28a745',     # Success text
        'text_warning': '#ffc107',    # Warning text
        'text_danger': '#dc3545',      # Danger text
        
        # Button colors
        'btn_primary': '#28a745',      # Start button
        'btn_success': '#28a745',      # Success button
        'btn_danger': '#dc3545',      # Stop button
        'btn_secondary': '#6c757d',    # GitHub/Settings buttons
        'btn_warning': '#ffc107',     # Warning button
        'btn_info': '#e91e63',        # Donate button
        
        # Status colors
        'status_ready': '#28a745',    # Ready status
        'status_running': '#007bff',  # Running status
        'status_stopped': '#dc3545',  # Stopped status
        'status_waiting': '#ffc107',  # Waiting status
        
        # Border colors
        'border_light': '#dee2e6',    # Light border
        'border_medium': '#adb5bd',   # Medium border
        'border_dark': '#6c757d',    # Dark border
        
        # Special colors
        'accent_primary': '#007bff',   # Primary accent
        'accent_secondary': '#6c757d', # Secondary accent
        'highlight': '#e3f2fd',       # Highlight background
        'status_dot': '#28a745',      # Status dot color
    }
