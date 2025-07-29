"""Initialize live and historical databases."""

import os
import sys

# Ensure project root is in path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from storage import live, historical


def main() -> None:
    print("Inicializando bases de datos...")
    live.init_db()
    historical.init_db()
    print("Listo.")


if __name__ == "__main__":
    main()
