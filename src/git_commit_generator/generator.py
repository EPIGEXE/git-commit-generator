import os
from typing import Dict, Optional
from .git_utils import GitRepo
from .models import CommitMessageModel

class CommitMessageGenerator:
    def __init__(self, repo_path: str = "."):
        self.git_repo = GitRepo(repo_path)
        self.model = CommitMessageModel()
        
    def _preprocess_diff(self, diff: str) -> str:
        """diff 텍스트 전처리"""
        # 너무 긴 diff는 잘라내고, 중요한 부분만 추출
        lines = diff.split('\n')
        # 변경된 라인만 추출 (+, - 로 시작하는 라인)
        filtered_lines = [
            line for line in lines 
            if line.startswith('+') or line.startswith('-')
        ]
        return '\n'.join(filtered_lines)[:512]  # 모델 입력 제한
        
    def generate_message(self) -> Dict[str, str]:
        """커밋 메시지 생성"""
        try:
            # 스테이징된 변경사항 가져오기
            diff = self.git_repo.get_staged_diff()
            if not diff:
                return {
                    'status': 'error',
                    'message': 'No staged changes found'
                }
            
            # diff 전처리
            processed_diff = self._preprocess_diff(diff)
            
            # 커밋 메시지 생성
            message = self.model.generate_message(processed_diff)
            
            return {
                'status': 'success',
                'message': message
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Error generating commit message: {str(e)}'
            }

def main():
    """CLI 진입점"""
    import sys
    
    # commit-msg 파일 경로를 인자로 받음
    commit_msg_file = sys.argv[1] if len(sys.argv) > 1 else None
    
    generator = CommitMessageGenerator()
    result = generator.generate_message()
    
    if result['status'] == 'success':
        if commit_msg_file:
            # Git hook에서 호출된 경우
            with open(commit_msg_file, 'w') as f:
                f.write(result['message'])
        else:
            # CLI에서 직접 호출된 경우
            print(result['message'])
    else:
        print(result['message'], file=sys.stderr)
        sys.exit(1)

def install_hooks():
    """Git hooks 설치"""
    try:
        from pathlib import Path
        import stat
        
        def find_git_root() -> Path:
            current = Path.cwd()
            while current != current.parent:
                if (current / '.git').is_dir():
                    return current
                current = current.parent
            raise ValueError("Not a git repository")

        # Git hook 내용 - Python 경로를 동적으로 찾음
        commit_msg_hook = """#!/bin/sh
PYTHON_PATH=$(which python)
SCRIPT_PATH=$(python -c "import git_commit_generator; import os; print(os.path.dirname(git_commit_generator.__file__))")
$PYTHON_PATH $SCRIPT_PATH/generator.py "$1"
"""
        
        repo_path = find_git_root()
        hooks_dir = repo_path / '.git' / 'hooks'
        hooks_dir.mkdir(parents=True, exist_ok=True)
        
        hook_path = hooks_dir / 'commit-msg'
        
        if hook_path.exists():
            backup_path = hook_path.with_suffix('.backup')
            hook_path.rename(backup_path)
            print(f"기존 commit-msg hook을 {backup_path}로 백업했습니다.")
        
        with open(hook_path, 'w') as f:
            f.write(commit_msg_hook)
        
        hook_path.chmod(hook_path.stat().st_mode | stat.S_IEXEC)
        
        print("Git commit-msg hook이 성공적으로 설치되었습니다!")
        return True
        
    except Exception as e:
        print(f"Hook 설치 중 오류 발생: {e}")
        return False

def main():
    """CLI 진입점"""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Git 커밋 메시지 생성기')
    parser.add_argument('--install-hooks', action='store_true', 
                       help='Git hooks 설치')
    parser.add_argument('commit_msg_file', nargs='?', 
                       help='커밋 메시지 파일 경로')
    
    args = parser.parse_args()
    
    if args.install_hooks:
        install_hooks()
        return
    
    # commit-msg 파일 경로를 인자로 받음
    commit_msg_file = args.commit_msg_file
    
    generator = CommitMessageGenerator()
    result = generator.generate_message()
    
    if result['status'] == 'success':
        if commit_msg_file:
            # Git hook에서 호출된 경우
            with open(commit_msg_file, 'w') as f:
                f.write(result['message'])
        else:
            # CLI에서 직접 호출된 경우
            print(result['message'])
    else:
        print(result['message'], file=sys.stderr)
        sys.exit(1)