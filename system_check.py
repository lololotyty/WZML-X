#!/usr/bin/env python3
import os
import sys
import subprocess
import importlib
from importlib.metadata import version, PackageNotFoundError
import logging

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("system_check.log"), logging.StreamHandler()],
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

def check_python_version():
    logger.info(f"Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        logger.error("Python version below 3.8. Please upgrade your Python version.")
        return False
    return True

def check_package_exists(package_name, required_version=None):
    try:
        importlib.import_module(package_name)
        try:
            installed_version = version(package_name)
            logger.info(f"{package_name}: {installed_version}")
            if required_version and installed_version < required_version:
                logger.warning(f"{package_name} version {installed_version} is below required {required_version}")
                return False
        except PackageNotFoundError:
            logger.info(f"{package_name}: Installed (version unknown)")
        return True
    except ImportError:
        logger.error(f"{package_name}: Not installed")
        return False

def install_package(package_name):
    logger.info(f"Installing {package_name}...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package_name])

def check_mega_sdk():
    try:
        from mega import MegaApi
        logger.info("Mega SDK: Installed")
        
        # Test basic functionality
        api = MegaApi(None, None, None, "WZML-X-Test")
        logger.info(f"Mega SDK Version: {api.getVersion()}")
        return True
    except ImportError:
        logger.error("Mega SDK not installed correctly")
        
        # Try to fix it
        logger.info("Attempting to install Mega SDK...")
        try:
            install_package("mega.py>=1.0.8")
            from mega import MegaApi
            logger.info("Mega SDK: Successfully installed")
            return True
        except Exception as e:
            logger.error(f"Failed to install Mega SDK: {str(e)}")
            return False

def check_heroku_environment():
    """Check if running on Heroku and if all required environment variables are set"""
    is_heroku = "DYNO" in os.environ
    logger.info(f"Running on Heroku: {is_heroku}")
    
    if is_heroku:
        required_vars = ["BOT_TOKEN", "OWNER_ID", "TELEGRAM_API", "TELEGRAM_HASH"]
        missing_vars = []
        
        for var in required_vars:
            if not os.environ.get(var):
                missing_vars.append(var)
        
        if missing_vars:
            logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
            return False
            
        # Check Mega credentials if provided
        if os.environ.get("MEGA_EMAIL") and not os.environ.get("MEGA_PASSWORD"):
            logger.warning("MEGA_EMAIL is set but MEGA_PASSWORD is missing")
            
        logger.info("Heroku environment looks good")
        return True
    
    return True  # Not on Heroku, so this check passes

def main():
    logger.info("Starting system check...")
    
    all_checks_passed = True
    
    # Basic system checks
    if not check_python_version():
        all_checks_passed = False
    
    # Check required packages
    required_packages = [
        "aiohttp", 
        "aiofiles", 
        "psutil", 
        "pyrogram", 
        "pyrofork", 
        "qbittorrent-api", 
        "yt-dlp"
    ]
    
    for package in required_packages:
        if not check_package_exists(package):
            try:
                install_package(package)
            except Exception as e:
                logger.error(f"Failed to install {package}: {str(e)}")
                all_checks_passed = False
    
    # Check Mega SDK specifically
    if not check_mega_sdk():
        all_checks_passed = False
    
    # Check Heroku environment
    if not check_heroku_environment():
        all_checks_passed = False
        
    # Final verdict
    if all_checks_passed:
        logger.info("All system checks passed! The bot should work correctly.")
    else:
        logger.warning("Some checks failed. Please fix the issues mentioned above.")
    
    return all_checks_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 
