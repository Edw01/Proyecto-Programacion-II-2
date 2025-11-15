from dataclasses import dataclass, field
from typing import List, Optional
from Ingrediente import Ingrediente
from Stock import Stock
from IMenu import IMenu


@dataclass
class CrearMenu():
    nombre: str
    ingredientes: List[Ingrediente]
    precio: float = 0.0
    icono_path: Optional[str] = None
    cantidad: int = field(default=0, compare=False)

    def esta_disponible(self, stock: Stock) -> bool:
        for req in self.ingredientes:
            ok = False
            for ing in stock.lista_ingredientes:
                if ing.nombre.upper() == req.nombre.upper() and (req.unidad is None or ing.unidad == req.unidad):
                    if int(ing.cantidad) >= int(req.cantidad):
                        ok = True
                        break
            if not ok:
                return False
        return True
