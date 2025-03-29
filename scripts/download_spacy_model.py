#!/usr/bin/env python
"""
Utility script to download the required SpaCy language model
"""
import sys
import subprocess
import spacy
from pathlib import Path

def download_model(model_name="en_core_web_sm"):
    """Download a SpaCy language model if not already installed"""
    try:
        # Try to load the model to check if it's installed
        spacy.load(model_name)
        print(f"✅ Model '{model_name}' is already installed")
        return True
    except OSError:
        print(f"⬇️ Downloading model '{model_name}'...")
        
        # Download the model
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
            print(f"✅ Successfully downloaded model '{model_name}'")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Error downloading model: {e}")
            return False

def main():
    """Main entry point for the script"""
    model_name = "en_core_web_sm"
    
    if len(sys.argv) > 1:
        model_name = sys.argv[1]
    
    print("🦙 LlamaGraph SpaCy Model Download Utility")
    print("-----------------------------------------")
    
    if download_model(model_name):
        print("\n🎉 All done! You can now use LlamaGraph.")
    else:
        print("\n⚠️ There was an error downloading the model.")
        print("You can try downloading it manually with:")
        print(f"  python -m spacy download {model_name}")

if __name__ == "__main__":
    main() 