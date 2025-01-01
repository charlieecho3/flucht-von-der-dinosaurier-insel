# main.py

import logging
from game import Game

def setup_logging() -> None:
    """
    Configure logging for the entire application.
    """
    logging.basicConfig(
        level=logging.INFO,  # Adjust level to DEBUG if you want more verbosity
        format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
    )

if __name__ == "__main__":
    setup_logging()
    g = Game()
    g.run()
