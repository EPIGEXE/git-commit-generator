#!/usr/bin/env python3
import os
import stat
from pathlib import Path

def find_git_root() -> Path:
    """현재 디렉토리에서 .git 디렉토리를 찾을 때까지 상위로 올라감"""
    current = Path.cwd()
    while current != current.parent:
        if (current / '.git').is_dir():
            return current
        current = current.parent
    raise ValueError("Not a git repository (or any parent directory)")

def ensure_hooks_dir(repo_path: Path) -> Path:
    """hooks 디렉토리가 없으면 생성"""
    hooks_dir = repo_path / '.git' / 'hooks'
    if not hooks_dir.exists():
        hooks_dir.mkdir(parents=True)
    return hooks_dir

def install_hook(hooks_dir: Path, hook_name: str, content: str):
    """특정 hook 설치"""
    hook_path = hooks_dir / hook_name
    
    # 기존 hook 백업
    if hook_path.exists():
        backup_path = hook_path.with_suffix('.backup')
        hook_path.rename(backup_path)
        print(f"Existing {hook_name} backed up to {backup_path}")
    
    # 새 hook 작성
    with open(hook_path, 'w') as f:
        f.write(content)
    
    # 실행 권한 부여
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
    
    print(f"Installed {hook_name} hook")

def main():
    """메인 설치 프로세스"""
    try:
        # 현재 Git 저장소 찾기
        repo_path = find_git_root()
        hooks_dir = ensure_hooks_dir(repo_path)
        
        # Hook 스크립트 내용
        prepare_commit_msg_hook = """#!/bin/bash
# Git commit message generator hook
python -m git_commit_generator.generator "$1" || exit 1
"""
        
        install_hook(hooks_dir, 'prepare-commit-msg', prepare_commit_msg_hook)
        print(f"Git hooks installed successfully in {repo_path}")
        
    except Exception as e:
        print(f"Error installing git hooks: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()