import os
import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    def __init__(self):
        self.config_data = {}
        self.load_config()
    
    def load_config(self):
        """설정 파일 로드"""
        # 기본 설정 파일 로드
        default_config_path = Path(__file__).parent / "config" / "default_config.yml"
        self.config_data = self._load_yaml(default_config_path)
        
        # 사용자 설정 파일 로드 (있는 경우)
        user_config_path = Path.home() / ".git-commit-generator.yml"
        if user_config_path.exists():
            user_config = self._load_yaml(user_config_path)
            self._merge_configs(self.config_data, user_config)
        
        # 프로젝트별 설정 파일 로드 (있는 경우)
        project_config_path = Path.cwd() / ".git-commit-generator.yml"
        if project_config_path.exists():
            project_config = self._load_yaml(project_config_path)
            self._merge_configs(self.config_data, project_config)
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """YAML 파일 로드"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config file {path}: {e}")
            return {}
    
    def _merge_configs(self, base: Dict, override: Dict):
        """설정 병합"""
        for key, value in override.items():
            if isinstance(value, dict) and key in base:
                self._merge_configs(base[key], value)
            else:
                base[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """설정값 가져오기"""
        keys = key.split('.')
        value = self.config_data
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default