from __future__ import annotations

import os

from typing import Callable, Optional, Tuple, TYPE_CHECKING, Union

import tcod.event

import actions
from actions import (
    Action,
    BumpAction,
    PickupAction,
    WaitAction,
)
import color
import exceptions


MOVE_KEYS = {
    # Arrow keys
    tcod.event.KeySym.UP: (0, -1),
    tcod.event.KeySym.DOWN: (0, 1),
    tcod.event.KeySym.LEFT: (-1, 0),
    tcod.event.KeySym.RIGHT: (1, 0),
    tcod.event.KeySym.HOME: (-1, -1),
    tcod.event.KeySym.END: (-1, 1),
    tcod.event.KeySym.PAGEUP: (1, -1),
    tcod.event.KeySym.PAGEDOWN: (1, 1),
    # Numpad keys
    tcod.event.KeySym.KP_1: (-1, 1),
    tcod.event.KeySym.KP_2: (0, 1),
    tcod.event.KeySym.KP_3: (1, 1),
    tcod.event.KeySym.KP_4: (-1, 0),
    tcod.event.KeySym.KP_6: (1, 0),
    tcod.event.KeySym.KP_7: (-1, -1),
    tcod.event.KeySym.KP_8: (0, -1),
    tcod.event.KeySym.KP_9: (1, -1),
    # Vi keys
    tcod.event.KeySym.h: (-1, 0),
    tcod.event.KeySym.j: (0, 1),
    tcod.event.KeySym.k: (0, -1),
    tcod.event.KeySym.l: (1, 0),
    tcod.event.KeySym.y: (-1, -1),
    tcod.event.KeySym.u: (1, -1),
    tcod.event.KeySym.b: (-1, 1),
    tcod.event.KeySym.n: (1, 1),
}

WAIT_KEYS = {tcod.event.KeySym.PERIOD, tcod.event.KeySym.KP_5, tcod.event.KeySym.CLEAR}

CONFIRM_KEYS = {
    tcod.event.KeySym.RETURN,
    tcod.event.KeySym.KP_ENTER,
}

CURSOR_Y_KEYS = {
    tcod.event.KeySym.UP: -1,
    tcod.event.KeySym.DOWN: 1,
    tcod.event.KeySym.PAGEUP: -10,
    tcod.event.KeySym.PAGEDOWN: 10,
}

ActionOrHandler = Union[Action, "BaseEventHandler"]
"""An event handler return value which can trigger an action or switch event handlers.

If a handler is returned then it will become the active handler for future events.
If an action is returned it will be attempted and if it's valid then
MainGameEventHandler will become the active handler.
"""

if TYPE_CHECKING:
    from engine import Engine
    from entity import Actor, Item


class BaseEventHandler(tcod.event.EventDispatch[ActionOrHandler]):
    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle an event and return the next active event handler."""
        state = self.dispatch(event)
        if isinstance(state, BaseEventHandler):
            return state
        assert not isinstance(state, Action), f"{self!r} can not handle actions."
        return self

    def on_render(self, console: tcod.Console) -> None:
        raise NotImplementedError()

    def ev_quit(self, event: "tcod.event.Quit") -> Optional[Action]:
        raise SystemExit()


class PopupMessage(BaseEventHandler):
    """Display a popup text window."""

    def __init__(self,  parent_handler: BaseEventHandler, text: str):
        self.parent = parent_handler
        self.text = text

    def on_render(self, console: tcod.Console) -> None:
        """Render the parent and dim the result, then print the message on top."""
        self.parent.on_render(console)
        console.tiles_rgb["fg"] //= 8
        console.tiles_rgb["bg"] //= 8

        console.print(
            console.width // 2,
            console.height // 2,
            self.text,
            fg=color.white,
            bg=color.black,
            alignment=tcod.CENTER,
        )

    def ev_keydown(self, event: "tcod.event.KeyDown") -> Optional[BaseEventHandler]:
        """Any key returns to the parent handler."""
        return self.parent


class EventHandler(BaseEventHandler):
    """
    Base class for event handlers.
    """

    def __init__(self, engine: Engine):
        self.engine = engine

    def handle_events(self, event: tcod.event.Event) -> BaseEventHandler:
        """Handle events for input handlers with an engine."""
        action_or_state = self.dispatch(event)
        if isinstance(action_or_state, BaseEventHandler):
            return action_or_state
        if self.handle_action(action_or_state):
            if not self.engine.player.is_alive:
                return GameOverEventHandler(self.engine)
            elif self.engine.player.level.requires_level_up:
                return LevelUpEventHandler(self.engine)
            return MainGameEventHandler(self.engine)
        return self

    def handle_action(self, action: Optional[Action]) -> bool:
        """Handle actions returned from event methods.

        Returns True if the action will advance a turn.
        """
        if action is None:
            return False

        try:
            action.perform()
        except exceptions.Impossible as exc:
            self.engine.message_log.add_message(exc.args[0], color.impossible)
            return False

        self.engine.handle_enemy_turns()

        self.engine.update_fov()
        return True

    def ev_mousemotion(self, event: tcod.event.MouseMotion) -> None:
        if self.engine.game_map.in_bounds(event.tile.x, event.tile.y):
            self.engine.mouse_location = event.tile.x, event.tile.y

    def on_render(self, console: tcod.Console) -> None:
        self.engine.render(console)


class MainGameEventHandler(EventHandler):
    """
    Handles events from TCOD.
    """

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        action: Optional[Action] = None

        key = event.sym
        modifier = event.mod

        player: Actor = self.engine.player

        if key == tcod.event.KeySym.PERIOD and modifier & (
            tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT
        ):
            return actions.TakeStairsAction(player)

        if key in MOVE_KEYS:
            dx, dy = MOVE_KEYS[key]
            action = BumpAction(player, dx, dy)
        elif key in WAIT_KEYS:
            action = WaitAction(player)
        elif key == tcod.event.KeySym.ESCAPE:
            raise SystemExit()
        elif key == tcod.event.KeySym.v:
            return HistoryViewer(self.engine)
        elif key == tcod.event.KeySym.g:
            action = PickupAction(player)
        elif key == tcod.event.KeySym.i:
            return InventoryActivateHandler(self.engine)
        elif key == tcod.event.KeySym.d:
            return InventoryDropHandler(self.engine)
        elif key == tcod.event.KeySym.c:
            return CharacterScreenEventHandler(self.engine)
        elif key == tcod.event.KeySym.SLASH:
            return LookHandler(self.engine)

        return action


class GameOverEventHandler(EventHandler):
    """
    Handles events when the game is over.
    """

    def on_quit(self) -> None:
        """Handle exiting out of a finished game."""
        if os.path.exists("savegame.sav"):
            os.remove("savegame.sav")
        raise exceptions.QuitWithoutSaving()

    def ev_quit(self, event: "tcod.event.Quit") -> None:
        self.on_quit()

    def ev_keydown(self, event: tcod.event.KeyDown) -> None:
        if event.sym == tcod.event.KeySym.ESCAPE:
            self.on_quit()


class HistoryViewer(EventHandler):
    """
    Prints the history on a larger window which can be navigated.
    """

    def __init__(self, engine: Engine):
        super().__init__(engine)
        self.log_length: int = len(engine.message_log.messages)
        self.cursor: int = self.log_length - 1

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        log_console = tcod.Console(console.width - 6, console.height - 6)

        log_console.draw_frame(0, 0, log_console.width, log_console.height)
        log_console.print_box(
            0, 0, log_console.width, 1, "┤Message history├", alignment=tcod.CENTER
        )

        self.engine.message_log.render_messages(
            log_console,
            1,
            1,
            log_console.width - 2,
            log_console.height - 2,
            self.engine.message_log.messages[: self.cursor + 1],
        )
        log_console.blit(console, 3, 3)

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[MainGameEventHandler]:
        if event.sym in CURSOR_Y_KEYS:
            adjust = CURSOR_Y_KEYS[event.sym]
            if adjust < 0 and self.cursor == 0:
                self.cursor = self.log_length - 1
            elif adjust > 0 and self.cursor == self.log_length - 1:
                self.cursor = 0
            else:
                self.cursor = max(0, min(self.cursor + adjust, self.log_length - 1))

        elif event.sym == tcod.event.KeySym.HOME:
            self.cursor = 0
        elif event.sym == tcod.event.KeySym.END:
            self.cursor = self.log_length - 1
        else:
            return MainGameEventHandler(self.engine)
        return None


class AskUserEventHandler(EventHandler):
    """
    Handles user input for actions which require special input.
    """

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """By default any key exits this input handler."""
        if event.sym in {
            tcod.event.KeySym.LSHIFT,
            tcod.event.KeySym.RSHIFT,
            tcod.event.KeySym.LCTRL,
            tcod.event.KeySym.RCTRL,
            tcod.event.KeySym.LALT,
            tcod.event.KeySym.RALT,
        }:
            return None
        return self.on_exit()

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """By default any mouse click exits this input handler."""
        return self.on_exit()

    def on_exit(self) -> Optional[Action]:
        """Called when the user is trying to exit or cancel an action.

        By default this returns to the main event handler.
        """
        self.engine.event_handler = MainGameEventHandler(self.engine)
        return MainGameEventHandler(self.engine)


class CharacterScreenEventHandler(AskUserEventHandler):
    TITLE = "Character Information"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        y = 0

        width = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=7,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(
            x=x + 1, y=y + 1, string=f"Level: {self.engine.player.level.current_level}",
        )
        console.print(
            x=x + 1, y=y + 2, string=f"XP: {self.engine.player.level.current_xp}",
        )
        console.print(
            x=x + 1,
            y=y + 3,
            string=f"XP for next level: {self.engine.player.level.experience_to_next_level}",
        )
        console.print(
            x=x + 1, y=y + 4, string=f"Attack: {self.engine.player.fighter.power}",
        )
        console.print(
            x=x + 1, y=y + 5, string=f"Defense: {self.engine.player.fighter.defense}",
        )


class LevelUpEventHandler(AskUserEventHandler):
    TITLE = "Level Up"

    def on_render(self, console: tcod.Console) -> None:
        super().on_render(console)

        if self.engine.player.x <= 30:
            x = 40
        else:
            x = 0

        console.draw_frame(
            x=x,
            y=0,
            width=35,
            height=8,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        console.print(x=x + 1, y=1, string="Congratulations! You leveled up!")
        console.print(x=x + 1, y=2, string="Select an attribute to increase.")

        console.print(
            x=x + 1,
            y=4,
            string=f"a) Constitution (+20 HP, from {self.engine.player.fighter.max_hp})",
        )
        console.print(
            x=x + 1,
            y=5,
            string=f"b) Strength (+1 attack, from {self.engine.player.fighter.power})",
        )
        console.print(
            x=x + 1,
            y=6,
            string=f"c) Agility (+1 defense, from {self.engine.player.fighter.defense})",
        )

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 2:
            if index == 0:
                player.level.increase_max_hp()
            elif index == 1:
                player.level.increase_power()
            else:
                player.level.increase_defense()
        else:
            self.engine.message_log.add_message("Invalid entry.", color.invalid)

            return None

        return super().ev_keydown(event)

    def ev_mousebuttondown(
            self, event: tcod.event.MouseButtonDown
    ) -> Optional[ActionOrHandler]:
        """Don't allow the player to click to exit the menu, like normal."""
        return None


class InventoryEventHandler(AskUserEventHandler):
    """This handler lets the user select an item.

    What happens then depends on the subclass.
    """

    TITLE: str = "<missing title>"

    def on_render(self, console: tcod.Console) -> None:
        """Render an inventory menu, which displays the items in the inventory
        and the letter to select them.
        Will move to a different position based on where the player is located
        so the player can always see where they are.
        """
        super().on_render(console)
        number_of_items_in_inventory: int = len(self.engine.player.inventory.items)

        height: int = number_of_items_in_inventory + 2

        if height <= 3:
            height = 3

        x: int = 0
        if self.engine.player.x <= 30:
            x = 40

        y: int = 0

        width: int = len(self.TITLE) + 4

        console.draw_frame(
            x=x,
            y=y,
            width=width,
            height=height,
            title=self.TITLE,
            clear=True,
            fg=(255, 255, 255),
            bg=(0, 0, 0),
        )

        if number_of_items_in_inventory > 0:
            for i, item in enumerate(self.engine.player.inventory.items):
                item_key = chr(ord("a") + i)
                console.print(x + 1, y + i + 1, f"({item_key}) {item.name}")
        else:
            console.print(x + 1, y + 1, "(Empty)")

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        player = self.engine.player
        key = event.sym
        index = key - tcod.event.KeySym.a

        if 0 <= index <= 26:
            try:
                selected_item = player.inventory.items[index]
            except IndexError:
                self.engine.message_log.add_message("Invalid entry.", color.invalid)
                return None
            return self.on_item_selected(selected_item)
        return super().ev_keydown(event)

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Called when the user selects a valid item."""
        raise NotImplementedError


class InventoryActivateHandler(InventoryEventHandler):
    """
    Handle using an inventory item.
    """

    TITLE: str = "Select an item to use"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Return the action for the selected item."""
        return item.consumable.get_action(self.engine.player)


class InventoryDropHandler(InventoryEventHandler):
    """
    Handle dropping an inventory item.
    """

    TITLE: str = "Select an item to drop"

    def on_item_selected(self, item: Item) -> Optional[ActionOrHandler]:
        """Drop this item."""
        return actions.DropItem(self.engine.player, item)


class SelectIndexHandler(AskUserEventHandler):
    """
    Handles asking the user for an index on the map.
    """

    def __init__(self, engine: Engine):
        """Sets the cursor to the player when this handler is constructed."""
        super().__init__(engine)
        player = self.engine.player
        engine.mouse_location = player.x, player.y

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)
        x, y = self.engine.mouse_location
        console.tiles_rgb["bg"][x, y] = color.white
        console.tiles_rgb["fg"][x, y] = color.black

    def ev_keydown(self, event: tcod.event.KeyDown) -> Optional[ActionOrHandler]:
        """Check for key movement or confirmation keys."""
        key = event.sym
        if key in MOVE_KEYS:
            modifier = 1
            if event.mod & (tcod.event.KMOD_LSHIFT | tcod.event.KMOD_RSHIFT):
                modifier *= 5
            if event.mod & (tcod.event.KMOD_LCTRL | tcod.event.KMOD_RCTRL):
                modifier *= 10
            if event.mod & (tcod.event.KMOD_LALT | tcod.event.KMOD_RALT):
                modifier *= 20

            x, y = self.engine.mouse_location
            dx, dy = MOVE_KEYS[key]
            x += dx * modifier
            y += dy * modifier
            x = max(0, min(x, self.engine.game_map.width - 1))
            y = max(0, min(y, self.engine.game_map.height - 1))
            self.engine.mouse_location = x, y
            return None
        elif key in CONFIRM_KEYS:
            return self.on_index_selected(*self.engine.mouse_location)
        return super().ev_keydown(event)

    def ev_mousebuttondown(self, event: tcod.event.MouseButtonDown) -> Optional[ActionOrHandler]:
        """Left click confirms a selection."""
        if self.engine.game_map.in_bounds(*event.tile):
            if event.button == 1:
                return self.on_index_selected(*event.tile)
        return super().ev_mousebuttondown(event)

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        """Called when an index is selected."""
        raise NotImplementedError


class LookHandler(SelectIndexHandler):
    """
    Lets the player look around using the keyboard.
    """

    def on_index_selected(self, x: int, y: int) -> Optional[ActionOrHandler]:
        """Return to main handler."""
        return MainGameEventHandler(self.engine)


class SingleRangedAttackHandler(SelectIndexHandler):
    """
    Handles targeting a single enemy. Only the enemy selected will be affected.
    """

    def __init__(
        self, engine: Engine, callback: Callable[[Tuple[int, int]], Optional[Action]]
    ):
        super().__init__(engine)

        self.callback = callback

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))


class AreaRangedAttackHandler(SelectIndexHandler):
    """
    Handles targeting an area within a given radius. Any entity within the area will
    will be affected.
    """

    def __init__(
        self,
        engine: Engine,
        radius: int,
        callback: Callable[[Tuple[int, int]], Optional[Action]],
    ):
        super().__init__(engine)

        self.radius: int = radius
        self.callback: Callable[[Tuple[int, int]], Optional[Action]] = callback

    def on_render(self, console: tcod.Console) -> None:
        """Highlight the tile under the cursor."""
        super().on_render(console)

        x, y = self.engine.mouse_location

        console.draw_frame(
            x=x - self.radius - 1,
            y=y - self.radius - 1,
            width=self.radius ** 2,
            height=self.radius ** 2,
            fg=color.red,
            clear=False,
        )

    def on_index_selected(self, x: int, y: int) -> Optional[Action]:
        return self.callback((x, y))
