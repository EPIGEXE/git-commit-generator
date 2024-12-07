from git import Repo
from typing import Optional

class GitRepo:
    def __init__(self, repo_path: str = "."):
        self.repo = Repo(repo_path)
    
    def get_staged_diff(self) -> Optional[str]:
        """스테이징된 변경사항 가져오기"""
        try:
            return self.repo.git.diff("--staged")
        except Exception as e:
            print(f"Error getting staged diff: {e}")
            return None
    
    def get_staged_files(self) -> list[str]:
        """스테이징된 파일 목록 가져오기"""
        return [item.a_path for item in self.repo.index.diff("HEAD")]