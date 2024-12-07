import unittest
from unittest.mock import patch, MagicMock
from git_commit_generator.generator import CommitMessageGenerator

class TestCommitMessageGenerator(unittest.TestCase):
    def setUp(self):
        # GitRepo 클래스 전체를 Mock으로 대체
        self.git_repo_patcher = patch('git_commit_generator.generator.GitRepo')
        self.MockGitRepo = self.git_repo_patcher.start()
        self.mock_repo_instance = MagicMock()
        self.MockGitRepo.return_value = self.mock_repo_instance

        # CommitMessageModel 클래스도 Mock으로 대체
        self.model_patcher = patch('git_commit_generator.generator.CommitMessageModel')
        self.MockModel = self.model_patcher.start()
        self.mock_model_instance = MagicMock()
        self.MockModel.return_value = self.mock_model_instance

    def tearDown(self):
        self.git_repo_patcher.stop()
        self.model_patcher.stop()

    def test_generate_message_success(self):
        # Mock 설정
        self.mock_repo_instance.get_staged_diff.return_value = "diff --git a/file.txt b/file.txt\n+new line"
        self.mock_model_instance.generate_message.return_value = "feat: Add new line to file.txt"
        
        generator = CommitMessageGenerator()
        result = generator.generate_message()
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['message'], "feat: Add new line to file.txt")
    
    def test_generate_message_no_staged_changes(self):
        # Mock 설정
        self.mock_repo_instance.get_staged_diff.return_value = ""
        
        generator = CommitMessageGenerator()
        result = generator.generate_message()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('No staged changes found', result['message'])

    def test_generate_message_error(self):
        # Mock 설정
        self.mock_repo_instance.get_staged_diff.return_value = "diff --git a/file.txt b/file.txt\n+new line"
        self.mock_model_instance.generate_message.side_effect = Exception("Model error")
        
        generator = CommitMessageGenerator()
        result = generator.generate_message()
        
        self.assertEqual(result['status'], 'error')
        self.assertIn('Error generating commit message', result['message'])

if __name__ == '__main__':
    unittest.main()