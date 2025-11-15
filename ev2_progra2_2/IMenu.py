# IMenu.py
from typing import Protocol, List, Optional, runtime_checkable
from Ingrediente import Ingrediente
from Stock import Stock


@runtime_checkable
class IMenu(Protocol):
    def esta_disponible(self, stock) -> bool:
        ...
