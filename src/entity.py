from __future__ import annotations

import copy
from typing import Optional, Tuple, Type, TypeVar, TYPE_CHECKING

from render_order import RenderOrder

if TYPE_CHECKING:
    from components.ai import BaseAI
    from components.fighter import Fighter
    from game_map import GameMap

T = TypeVar('T', bound='Entity')


class Entity:
    """
    A generic object to represent players, enemies, items, etc.
    """

    gamemap: GameMap

    def __init__(self,
                 gamemap: Optional[GameMap] = None,
                 x: int = 0, y: int = 0,
                 char: str = '?',
                 color: Tuple[int, int, int] = (255, 255, 255),
                 name: str = '<Unnamed>',
                 blocks_movement: bool = False,
                 render_order: RenderOrder = RenderOrder.CORPSE):
        self.x: int = x
        self.y: int = y
        self.char: str = char
        self.color: Tuple[int, int, int] = color
        self.name: str = name
        self.blocks_movement: bool = blocks_movement
        self.render_order: RenderOrder = render_order
        if gamemap:
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def spawn(self: T, gamemap: GameMap, x: int, y: int) -> T:
        """Spawn a copy of this instance at the given location.
        """
        clone = copy.deepcopy(self)
        clone.x = x
        clone.y = y
        clone.gamemap = gamemap
        gamemap.entities.add(clone)
        return clone

    def place(self, x: int, y: int, gamemap: Optional[GameMap] = None) -> None:
        """Place this entity at a new location. Handles moving across GameMaps.
        """
        self.x = x
        self.y = y
        if gamemap:
            if hasattr(self, "gamemap"):
                self.gamemap.entities.remove(self)
            self.gamemap = gamemap
            gamemap.entities.add(self)

    def move(self, dx: int, dy: int) -> None:
        """Move the entity the specified amount.
        """
        self.x += dx
        self.y += dy


class Actor(Entity):
    """
    Entity that can has AI-based movement.
    """

    def __init__(self,
                 *,
                 x: int = 0, y: int = 0,
                 char: str = '?',
                 color: Tuple[int, int, int] = (255, 255, 255),
                 name: str = '<Unnamed>',
                 ai_cls: Type[BaseAI],
                 fighter: Fighter):
        super().__init__(
            x=x, y=y,
            char=char,
            color=color,
            name=name,
            blocks_movement=True,
            render_order=RenderOrder.ACTOR,
        )

        self.ai: Optional[BaseAI] = ai_cls(self)

        self.fighter = fighter
        self.fighter.entity = self

    @property
    def is_alive(self) -> bool:
        """Returns True as long as this actor can perform actions
        """
        return bool(self.ai)
