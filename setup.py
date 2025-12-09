"""
Quick Setup Script
Installs dependencies and creates necessary directories
"""

import os
import subprocess
import sys
from pathlib import Path


def create_directories():
    """Create necessary directories"""
    directories = [
        'logs',
        'data',
        'backtest_results',
        'trade_history'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def install_dependencies():
    """Install Python dependencies"""
    print("\nInstalling dependencies...")
    print("=" * 50)
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("\n✓ All dependencies installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error installing dependencies: {e}")
        print("You may need to install some packages manually.")
        return False
    
    return True


def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path('.env')
    
    if not env_file.exists():
        example_file = Path('.env.example')
        if example_file.exists():
            env_file.write_text(example_file.read_text())
            print("✓ Created .env file from .env.example")
            print("  → Please edit .env and add your API keys")
        else:
            print("✗ .env.example not found")
    else:
        print("✓ .env file already exists")


def main():
    """Main setup function"""
    print("=" * 50)
    print("  Intraday Trading Bot - Setup")
    print("=" * 50)
    
    # Create directories
    print("\n1. Creating directories...")
    create_directories()
    
    # Create .env file
    print("\n2. Setting up environment file...")
    create_env_file()
    
    # Install dependencies
    print("\n3. Installing dependencies...")
    if install_dependencies():
        print("\n" + "=" * 50)
        print("  Setup Complete!")
        print("=" * 50)
        print("\nNext steps:")
        print("1. Edit config.yaml to customize settings")
        print("2. Edit .env to add your API keys (if using live data)")
        print("3. Run the bot: python main.py")
        print("4. Or run the dashboard: streamlit run dashboard/app.py")
    else:
        print("\n" + "=" * 50)
        print("  Setup Incomplete")
        print("=" * 50)
        print("\nPlease fix the errors above and run setup again.")


if __name__ == "__main__":
    main()
