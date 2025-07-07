#!/usr/bin/env python3
"""
GitHub Project Uploader
A desktop GUI application for uploading local projects to GitHub repositories
with username/password authentication.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import logging
from pathlib import Path

# Import our custom modules
from gui_components import MainWindow
from utils import setup_logging

def main():
    """Main entry point for the application."""
    try:
        # Setup logging
        setup_logging()
        logging.info("Starting GitHub Project Uploader")
        
        # Create the main window
        root = tk.Tk()
        app = MainWindow(root)
        
        # Start the GUI event loop
        root.mainloop()
        
    except Exception as e:
        logging.error(f"Fatal error in main application: {e}")
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
