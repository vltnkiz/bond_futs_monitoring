from typing import Callable

from src.core.models.tick import Tick

TickHandler = Callable[[Tick], None]
