#!/usr/bin/env python3
"""
Setup and installation script for the Adobe Hackathon Document Intelligence System.
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        raise RuntimeError("Python 3.8 or higher is required")
    logger.info(f"✓ Python {version.major}.{version.minor}.{version.micro} detected")

def install_requirements():
    """Install required packages."""
    logger.info("Installing required packages...")
    
    # Core requirements
    packages = [
        "PyPDF2==3.0.1",
        "scikit-learn==1.3.0",
        "numpy==1.24.3",
        "nltk==3.8.1"
    ]
    
    # Optional packages for better performance
    optional_packages = [
        "sentence-transformers==2.2.2",
        "torch==2.0.1+cpu",
        "transformers==4.32.1",
        "pandas==2.0.3"
    ]
    
    # Install core packages
    for package in packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"✓ Installed {package}")
        except subprocess.CalledProcessError as e:
            logger.error(f"✗ Failed to install {package}: {e}")
            raise
    
    # Install optional packages (best effort)
    for package in optional_packages:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            logger.info(f"✓ Installed {package}")
        except subprocess.CalledProcessError:
            logger.warning(f"⚠ Could not install optional package {package}")

def download_nltk_data():
    """Download required NLTK data."""
    logger.info("Downloading NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        logger.info("✓ NLTK data downloaded")
    except Exception as e:
        logger.warning(f"⚠ Could not download NLTK data: {e}")

def download_sentence_model():
    """Download sentence transformer model."""
    logger.info("Downloading sentence transformer model...")
    try:
        from sentence_transformers import SentenceTransformer
        # Download small, efficient model (~90MB)
        model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✓ Sentence transformer model downloaded")
    except Exception as e:
        logger.warning(f"⚠ Could not download sentence transformer model: {e}")

def create_directories():
    """Create necessary directories."""
    directories = [
        "app/input",
        "app/output",
        "models",
        "logs"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✓ Created directory: {directory}")

def main():
    """Main setup function."""
    logger.info("Setting up Adobe Hackathon Document Intelligence System")
    logger.info("=" * 60)
    
    try:
        check_python_version()
        create_directories()
        install_requirements()
        download_nltk_data()
        download_sentence_model()
        
        logger.info("\n" + "=" * 60)
        logger.info("✓ Setup completed successfully!")
        logger.info("\nNext steps:")
        logger.info("1. Place your PDF files in the app/input/ directory")
        logger.info("2. Modify app/persona.json with your persona and job description")
        logger.info("3. Run: python main.py")
        logger.info("4. Check results in app/output/analysis.json")
        
    except Exception as e:
        logger.error(f"✗ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
