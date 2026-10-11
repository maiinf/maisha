"""Las ilustraciones de la historia ya no se dibujan aquí: ahora se pintan con mucho más detalle
en herramientas/cinematicas.py (con herramientas/pintor.py). Este archivo solo la llama, por si acaso.

    python3 herramientas/dibujar_historia.py   (es lo mismo que python3 herramientas/cinematicas.py)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cinematicas  # noqa: E402

if __name__ == "__main__":
    cinematicas.main()
