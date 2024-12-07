from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
from .config import Config

class CommitMessageModel:
    def __init__(self):
        self.config = Config()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        
        model_name = self.config.get('model.name')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        self.model.to(self.device)
    
    def generate_message(self, diff_text: str) -> str:
        """변경사항으로부터 커밋 메시지 생성"""
        inputs = self.tokenizer(
            diff_text,
            return_tensors="pt",
            truncation=True,
            max_length=self.config.get('model.max_length', 512)
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_length=50,
                num_beams=self.config.get('model.num_beams', 4),
                temperature=self.config.get('model.temperature', 0.7),
                top_k=self.config.get('model.top_k', 50),
                top_p=self.config.get('model.top_p', 0.95)
            )
        
        message = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self._format_message(message)
    
    def _format_message(self, message: str) -> str:
        """커밋 메시지 포맷팅"""
        commit_types = self.config.get('commit_format.types', [])
        template = self.config.get('commit_format.template', '{type}: {message}')
        
        # 메시지에서 타입 추출 또는 기본값 사용
        message_type = 'chore'  # 기본값
        for type_ in commit_types:
            if message.lower().startswith(f"{type_}:"):
                message_type = type_
                message = message[len(type_)+1:].strip()
                break
        
        return template.format(type=message_type, message=message)