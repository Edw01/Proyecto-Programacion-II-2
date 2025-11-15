# menu_catalog.py
from typing import List
from ElementoMenu import CrearMenu
from Ingrediente import Ingrediente
from IMenu import IMenu


def get_default_menus() -> List[IMenu]:
    listaMenus = [
        CrearMenu(
            "Papas fritas",
            [Ingrediente("papas", "unid", 5)],
            precio=500,
            icono_path="IMG/icono_papas_fritas_64x64.png",
        ),
        CrearMenu(
            "Pepsi",
            [Ingrediente("Pepsi", "unid", 1)],
            precio=1100,
            icono_path="IMG/icono_cola_64x64.png",
        ),
        CrearMenu(
            "Completo",
            [
                Ingrediente("vienesa", "unid", 1),
                Ingrediente("pan de completo", "unid", 1),
                Ingrediente("tomate", "unid", 1),
                Ingrediente("palta", "unid", 1),
            ],
            precio=1800,
            icono_path="IMG/icono_hotdog_sin_texto_64x64.png",
        ),
        CrearMenu(
            "Hamburguesa",
            [
                Ingrediente("pan de hamburguesa", "unid", 1),
                Ingrediente("lamina de queso", "unid", 1),
                Ingrediente("churrasco de carne", "unid", 1),
            ],
            precio=3500,
            icono_path="IMG/icono_hamburguesa_negra_64x64.png",
        ),
        CrearMenu(
            "Panqueques",
            [
                Ingrediente("panqueques", "unid", 2),
                Ingrediente("manjar", "unid", 1),
                Ingrediente("azucar flor", "unid", 1),
            ],
            precio=2000,
            icono_path="IMG/icono_panqueques_64x64.png",
        ),
        CrearMenu(
            "Pollo frito",
            [
                Ingrediente("presa de pollo", "unid", 1),
                Ingrediente("porcion de harina", "unid", 1),
                Ingrediente("porcion de aceite", "unid", 1),
            ],
            precio=2800,
            icono_path="IMG/icono_pollo_frito_64x64.png",
        ),
        CrearMenu(
            "Ensalada mixta",
            [
                Ingrediente("lechuga", "unid", 1),
                Ingrediente("tomate", "unid", 1),
                Ingrediente("zanahoria rallada", "unid", 1),
            ],
            precio=1500,
            icono_path="IMG/icono_ensalada_mixta_64x64.png",
        ),
        CrearMenu(
            "Coca-cola",
            [Ingrediente("coca cola", "unid", 1),],
            precio=1000,
            icono_path="IMG/icono_cola_lata_64x64.png"
        )
    ]
    for menu in listaMenus:
        if isinstance(menu, IMenu) == False:
            raise TypeError(
                f"La clase de menú no implementa la interfaz diseñada.")
        else:
            return listaMenus
