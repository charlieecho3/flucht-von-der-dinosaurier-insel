# entities/base_entity.py

class Entity:
    """
    Base entity with x, y coordinates.
    """
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y
