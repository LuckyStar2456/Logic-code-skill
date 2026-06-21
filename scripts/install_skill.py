#!/usr/bin/env python3
"""
Skill Installation Script

Installs this skill into a Logic Code project.
"""

import os
import shutil
import json
import argparse

def install_skill(target_project_path: str):
    """
    Install the skill into the target Logic Code project.
    
    Args:
        target_project_path: Path to the Logic Code project
    """
    skill_name = "code-complexity-analyzer"
    source_skill_dir = os.path.join(os.path.dirname(__file__), '..', 'skill')
    target_skills_dir = os.path.join(target_project_path, '.logic_code', 'skills')
    target_skill_dir = os.path.join(target_skills_dir, skill_name)
    
    try:
        os.makedirs(target_skills_dir, exist_ok=True)
        
        for item in os.listdir(source_skill_dir):
            source_path = os.path.join(source_skill_dir, item)
            target_path = os.path.join(target_skill_dir, item)
            
            if os.path.isdir(source_path):
                shutil.copytree(source_path, target_path, dirs_exist_ok=True)
            else:
                shutil.copy2(source_path, target_path)
        
        registry_path = os.path.join(target_skills_dir, 'registry.json')
        update_registry(registry_path, skill_name)
        
        print(f"✅ Skill '{skill_name}' installed successfully!")
        print(f"Location: {target_skill_dir}")
        
    except Exception as e:
        print(f"❌ Error installing skill: {e}")
        raise

def update_registry(registry_path: str, skill_name: str):
    """Update the skills registry."""
    if os.path.exists(registry_path):
        with open(registry_path, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    else:
        registry = {
            'version': '1.0',
            'skills': [],
            'enabled_skills': []
        }
    
    skill_config_path = os.path.join(
        os.path.dirname(registry_path),
        skill_name,
        'skill.json'
    )
    
    if os.path.exists(skill_config_path):
        with open(skill_config_path, 'r', encoding='utf-8') as f:
            skill_config = json.load(f)
        
        existing_skills = [s.get('name') for s in registry.get('skills', [])]
        if skill_name not in existing_skills:
            registry['skills'].append(skill_config)
        
        if skill_name not in registry.get('enabled_skills', []):
            registry['enabled_skills'].append(skill_name)
        
        with open(registry_path, 'w', encoding='utf-8') as f:
            json.dump(registry, f, indent=2)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Install skill into Logic Code project')
    parser.add_argument('project_path', help='Path to the Logic Code project')
    args = parser.parse_args()
    
    install_skill(args.project_path)