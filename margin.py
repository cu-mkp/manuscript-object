from typing import Optional

class Margin:
  def __init__(self, entry: str, folio: str, position: str, text: str, render: Optional[str] = '') -> None:
    self.entry = entry
    self.folio = folio
    self.position = position
    self.text = text
    self.render = render
