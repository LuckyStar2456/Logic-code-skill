#!/usr/bin/env python3
"""
Skill Packaging Script

Packages the skill into a distributable format.
"""

import os
import zipfile
import shutil
import json
from datetime import datetime

def package_skill(output_dir: str = None):
    """
    Package the skill into a ZIP file.
    
    Args:
        output_dir: Directory to save the package (default: dist/)
    """
    skill_name = "code-complexity-analyzer"
    
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'dist')
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    package_name = f"{skill_name}_{timestamp}.zip"
    package_path = os.path.join(output_dir, package_name)
    
    skill_dir = os.path.join(os.path.dirname(__file__), '..', 'skill')
    
    try:
        with zipfile.ZipFile(package_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(skill_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, skill_dir)
                    zipf.write(file_path, arcname)
        
        print(f"✅ Skill packaged successfully!")
        print(f"Location: {package_path}")
        print(f"Size: {os.path.getsize(package_path) / 1024:.2f} KB")
        
        return package_path
        
    except Exception as e:
        print(f"❌ Error packaging skill: {e}")
        raise

def create_version_file():
    """Create a version file for the skill."""
    version_info = {
        'name': 'code-complexity-analyzer',
        'version': '1.0.0',
        'created_at': datetime.now().isoformat(),
        'compatible_with': ['Logic Code >= 2.0.0']
    }
    
    version_path = os.path.join(
        os.path.dirname(__file__),
        '..',
        'skill',
        'version.json'
    )
    
    with open(version_path, 'w', encoding='utf-8') as f:
        json.dump(version_info, f, indent=2)

if __name__ == '__main__':
    create_version_file()
    package_skill()