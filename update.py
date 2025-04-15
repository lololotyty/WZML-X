#!/usr/bin/env python3
import logging
import os
import sys
from logging import (
    INFO,
    getLogger,
    basicConfig,
    error as log_error,
)
import subprocess
from importlib.metadata import distributions
from requests import get as rget
from dotenv import load_dotenv, dotenv_values
from pymongo import MongoClient

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=INFO,
)

def getConfig(name: str):
    return os.environ.get(name, None)

def install_requirements():
    for line in open('requirements.txt'):
        try:
            package = line.strip()
            if not len(package) or package.startswith('#'):
                continue
            if subprocess.check_call([sys.executable, "-m", "pip", "install", package]) != 0:
                print(f"Error installing {package}")
        except Exception as e:
            print(f"Failed to install {package}: {e}")

def is_heroku():
    return 'DYNO' in os.environ

if os.path.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

if os.path.exists('.git'):
    try:
        subprocess.check_call(
            ['git', 'pull'],
            stderr=subprocess.STDOUT,
            stdout=subprocess.DEVNULL
        )
    except Exception as e:
        log_error(f"Git pull error: {e}")

UPSTREAM_REPO = getConfig('UPSTREAM_REPO')
UPSTREAM_BRANCH = getConfig('UPSTREAM_BRANCH')

if UPSTREAM_REPO:
    if os.path.exists('.git'):
        subprocess.run(['rm', '-rf', '.git'])

    subprocess.run([
        'git', 'init'
    ])
    subprocess.run([
        'git', 'remote', 'add', 'origin', UPSTREAM_REPO
    ])
    subprocess.run([
        'git', 'fetch', 'origin', UPSTREAM_BRANCH
    ])
    subprocess.run([
        'git', 'checkout', '-f', f'origin/{UPSTREAM_BRANCH}'
    ])

# Install mega.py specifically for better Mega support
try:
    import mega
    print("mega.py is already installed")
except ImportError:
    print("Installing mega.py...")
    subprocess.call([sys.executable, "-m", "pip", "install", "mega.py>=1.0.8"])

# Check environment and install requirements
try:
    # Run the system check script 
    if os.path.exists('system_check.py'):
        subprocess.call([sys.executable, 'system_check.py'])
    
    # Ensure config file exists for Heroku
    config_file = os.path.exists('config.env')
    sample_config = os.path.exists('config_sample.env')
    
    if not config_file and sample_config:
        print("Creating config.env from sample...")
        with open('config_sample.env', 'r') as sample:
            with open('config.env', 'w') as config:
                config.write(sample.read())
    
    print("Ready to start the bot!")

except Exception as e:
    log_error(f"Something went wrong! Retry or ask support! Error: {e}")
    exit(1)
