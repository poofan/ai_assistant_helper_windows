#!/usr/bin/env python3
"""
AI Chat Messenger - Main Application
A Python-based AI chat application with screenshot analysis capabilities.
"""

import sys
import os
import logging
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window_modern import ModernMainWindow
from utils.config import Config

def setup_logging():
    """Setup logging configuration"""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "ai_chat_messenger.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def main():
    """Main application entry point"""
    logger = setup_logging()
    logger.info("Starting Modern AI Chat Messenger...")
    
    try:
        # Load configuration
        config = Config()
        
        # Create and run the modern main window
        app = ModernMainWindow(config)
        app.run()
        
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        sys.exit(1)
    
    logger.info("Application closed")

if __name__ == "__main__":
    main()

