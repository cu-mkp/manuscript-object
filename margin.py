from typing import Optional
import re

class Margin:
  def __init__(self, entry: str, position: str, text: str, render: Optional[str] = '') -> None:
    self.entry = entry
    self.position = position
    self.render = render
    self.text = text
    self.length = self.find_length(text)
  
  def find_length(self, text: str) -> int:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'<.*?>', '', text)
    return len(text)
