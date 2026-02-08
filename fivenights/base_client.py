# *I* am the Scout here! (Kyle Holter Vogel's NDSU Byte-le 2026 Submission)
# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright (c): 2026, ~~The Scout from Team Fortress 2~~ Kyle Holter Vogel and NDSU ACM

# Despite the fact I probably won't win the alumni category like I wanted,
# (I'm struggling to come up with a strategy), I learned a lot about myself today.
# Sorry guys, no second UND sweep :(
# (unless I lock in and learn all about A* today lmao).

# This is the culumination of the past few months of self-discovery since I 
# graduated UND really.

# Let's just say I've learned I'm almost certainly not "normal".
# And soon, I'll take the psychological tests (and more therapy) to prove it.
# It's so obvious in hindsight.
# Who else would get nearly a 4.0 GPA and then dress up like the Scout?
# Have an insane, undying thirst for knowledge?

# At yet despite all that knowledge, I still need to-do lists and documentation
# in clear, unambigious language?

# I've learned today that I can do a lot on my own, but I can't do *everything*.
# At least not alone.
# I could spend more time on this, but I already won.
# Look at this year's theme ffs. I did that (although not alone obviously).
# Thank you all. For everything.

'''
POSIX-Compliant Shell Scripts

```sh
#!/bin/sh
# NDSU Byte-le 2026 Submission Script
# SPDX-License-Identifier: MIT
# Copyright (c): 2026, The Scout from Team Fortress 2

PROJECT_FOLDER="fivenights"

main() {
    cd "$PROJECT_FOLDER"
    clear
    set -e
    python launcher.pyz client leaderboard -include_alumni && printf "\n"
    # python launcher.pyz --help && printf "\n" # Li'l help pushin' the cart?
    python launcher.pyz grv || exit
    printf "\n"
    python launcher.pyz client submit
}

# shellcheck disable=SC2068
main $@
```

```
#!/bin/sh
# NDSU Byte-le 2026 Installation Script
# SPDX-License-Identifier: MIT
# Copyright (c): 2026, The Scout from Team Fortress 2
# Based on the official documentation: https://ndacm.org/Byte-le-Engine-v2-2026/getting_started.html
# Meant for Debian-based distros only

PYTHON_VERSION="3.13"
PROJECT_FOLDER="fivenights"
PREVIOUS_PROJECT_FOLDER="${PROJECT_FOLDER}-prev"
URL="https://github.com/acm-ndsu/Byte-le-2026-Client-Package/archive/refs/heads/main.zip"

dep() {
    if ! command -v "$1" 2>/dev/null 1>/dev/null; then
        echo "Error: $1 does not exist" 1>&2
        exit 127
    fi
}

main() {
    set -ex

    dep apt
    dep sudo
    sudo apt install -y curl make pipx python3 sudo tar unzip
    pipx install uv # uv is way better than pip

    [ -d "$PREVIOUS_PROJECT_FOLDER" ] && rm -rf "$PREVIOUS_PROJECT_FOLDER"
    [ -d "$PROJECT_FOLDER" ] && mv -v "$PROJECT_FOLDER" "$PREVIOUS_PROJECT_FOLDER"

    # Download Byte-le Client
    curl "$URL" -L -o tmp.zip
    unzip tmp.zip && rm tmp.zip
    mv "Byte-le-2026-Client-Package-main" "$PROJECT_FOLDER"
    [ -f "vID" ] && cp -v "vID" "${PROJECT_FOLDER}/vID"
    [ -f "$PREVIOUS_PROJECT_FOLDER/base_client.py" ] && cp -v "$PREVIOUS_PROJECT_FOLDER/base_client.py" "$PROJECT_FOLDER/base_client.py"
    cd "$PROJECT_FOLDER"

    # Set up Python environment
    [ -f "pyproject.toml" ] || uv init .
    uv python install "$PYTHON_VERSION"
    uv venv --python "$PYTHON_VERSION" --clear
    # shellcheck disable=SC1091
    . ./.venv/bin/activate
    uv python pin "$PYTHON_VERSION"
    uv add -r requirements.txt

    set +x
    printf "\n"
    echo "Run '. ${PROJECT_FOLDER}/.venv/bin/activate' to activate the virtual environment" 
    echo "Run 'python launcher.pyz --help' for help"
    if ! [ -f "vID" ]; then
		echo "Run 'python launcher.pyz client register' to register"
		echo "DO NOT SHARE YOUR vID. THE ANIMATRONICS WILL GET YOU." # and they are known to get a little quirky at night...
	fi
}

# shellcheck disable=SC2068
main $@
```
'''

import heapq
import random
from game.client.user_client import UserClient
from game.common.avatar import Avatar
from game.common.enums import ActionType, ObjectType
from game.common.enums import ObjectType, ActionType
from game.common.game_object import GameObject
from game.common.map.game_board import GameBoard
from game.common.map.occupiable import Occupiable
from game.constants import *
from game.constants import DIRECTION_TO_MOVE
from game.utils.vector import Vector
from typing import Dict, List, Tuple, Optional

DIRECTIONS = [(1,0), (-1,0), (0,1), (0,-1)]
Position = Tuple[int, int]

def a_star_move(start: Vector, goal: Vector, world, allow_vents: bool = True, game_object: GameObject | None = None) -> ActionType | None:
    path = a_star_path(
        start=start,
        goal=goal,
        world=world,
        allow_vents=allow_vents,
        game_object=game_object
    )

    if not path or len(path) < 2:
        return None

    next_step: Vector = path[1]
    direction = next_step - start
    action = DIRECTION_TO_MOVE.get(direction)
    return action

def a_star_path(start: Vector, goal: Vector, world, allow_vents = True, game_object: GameObject | None = None) -> Optional[List[Vector]]:
    start_p = (start.x, start.y)
    goal_p = (goal.x, goal.y)

    frontier = [(0, start_p)]
    came_from = {start_p: None}
    cost = {start_p: 0}

    while frontier:
        _, current = heapq.heappop(frontier)

        if current == goal_p:
            path = []
            while current is not None:
                x, y = current
                path.insert(0, Vector(x, y))
                current = came_from[current]
            return path

        for dx, dy in DIRECTIONS:
            nxt = (current[0] + dx, current[1] + dy)
            vec = Vector(nxt[0], nxt[1])

            if game_object is not None and not world.can_object_occupy(vec, game_object):
                continue

            if not world.is_valid_coords(vec):
                continue

            top = world.get_top(vec)
            if top and top.object_type != ObjectType.AVATAR:
                # walls block
                if top.object_type == ObjectType.WALL:
                    continue

                # vents block unless allowed
                if top.object_type == ObjectType.VENT and not allow_vents:
                    continue

                # can't pass through non-occupiable
                if not isinstance(top, Occupiable):
                    continue

            new_cost = cost[current] + 1
            if nxt not in cost or new_cost < cost[nxt]:
                cost[nxt] = new_cost
                priority = new_cost + vec.distance(goal)
                heapq.heappush(frontier, (priority, nxt))
                came_from[nxt] = current

    return None

class Client(UserClient):
    turnCounter = 0
    luigi = False

    def __init__(self):
        super().__init__()
        

    def team_name(self) -> str:
        """
        Allows the team to set a team name.
        :return: Your team name
        """
        return "Frickin' Unbelievable!"

    # Note that only the FIRST TWO actions will be actually be used by the engine.
    # An "infinite loop" for the duration of the game. Treat the return value second action as a "hold".
    def take_turn(self, turn: int, world: GameBoard, avatar: Avatar) -> list[ActionType]:
        """
        This is where your AI will decide what to do.
        :param turn:        The current turn of the game.
        :param actions:     This is the actions object that you will add effort allocations or decrees to.
        :param world:       Generic world information
        """

        # Luigi wins by doing nothing
        if self.luigi == True:
            return []
        else:
            mikeSchmidt = [] # First Night

        # See Enums: https://ndacm.org/Byte-le-Engine-v2-2026/enums.html
        allOptions = [
            None, # Do nothing
            ActionType.MOVE_UP,         # Move up one tile
            ActionType.MOVE_DOWN,       # Move down one tile
            ActionType.MOVE_LEFT,       # Move left one tile
            ActionType.MOVE_RIGHT,      # Move right one tile
            ActionType.INTERACT_UP,     # Interact with the tile above you
            ActionType.INTERACT_DOWN,   # Interact with the tile below you
            ActionType.INTERACT_LEFT,   # Interact with the tile to your left
            ActionType.INTERACT_RIGHT,  # Interact with the tile to your right
            ActionType.INTERACT_CENTER, # Interact with the tile you are standing on
        ]
        movementOptions = allOptions[1:4]
        interactOptions = allOptions[5:9]

        randomMove = random.choice(movementOptions)
        randomInteract = random.choice(interactOptions)
        
        nextMove = randomMove
        nextInteract = randomInteract

        mikeSchmidt.append(nextMove)
        mikeSchmidt.append(nextInteract)

        self.turnCounter += 1
        print(f"\n{self.turnCounter} - [{mikeSchmidt[0].name}, {mikeSchmidt[1].name}]")

        # Your Client.take_turn() method must return a list of ActionTypes.
        return mikeSchmidt
