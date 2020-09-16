<p align="center">
    <h3 align="center">Mogru</h3>
    <p align="center">
        A text-based roguelike game written in Python 3 using <a href="https://github.com/libtcod/python-tcod">python-tcod</a>.
        <br />
        <a href="https://github.com/bigangryguy/mogru"><strong>Explore the docs »</strong></a>
        <br />
        <br />
        <a href="https://github.com/bigangryguy/mogru/issues">Report Bug</a>
        ·
        <a href="https://github.com/bigangryguy/mogru/issues">Request Feature</a>
    </p>
</p>

<!-- TABLE OF CONTENTS -->
## Table of Contents

* [About the Project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)

<!-- ABOUT THE PROJECT -->
## About The Project

A text-based roguelike game written in Python 3 using TCOD. Starting from a simple initial framework, it will
be the basis for experiments in procedural generation of game elements and artificial intelligence.

### Built With

* [python-tcod](https://github.com/libtcod/python-tcod)
* [SDL2](https://www.libsdl.org/)
* [numpy](https://numpy.org/)



<!-- GETTING STARTED -->
## Getting Started

To get a local copy up and running follow these simple steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.
* SDL2: Install per your OS instructions. For most Linux distros, SDL2 is available as a package.

* python-tcod
```shell script
pip install --user tcod
```

* numpy
```shell script
pip install --user numpy
```

The project also includes a `requirements.txt` file to install all Python dependencies. To use that instead, run
from the root of the repo:
```shell script
pip install -r requirements.txt
```

### Installation

There is no installation process at the moment. Clone the repo using the command below. 
```sh
git clone https://github.com/bigangryguy/mogru.git
```

<!-- USAGE EXAMPLES -->
## Usage

Mogru can be run from a command line. In the `src` folder of the repo, run:
```shell script
python main.py
```

## Playing
As with most text-based roguelikes, the player is represented as `@` on the dungeon map.

Navigation of the map uses these keys:
* `Left arrow`, `H`, `numpad 4`: move left
* `Right arrow`, `L`, `numpad 6`: move right
* `Up arrow`, `K`, `numpad 8`: move up
* `Down arrow`, `J`, `numpad 2`: move down
* `Home`, `Y`, `numpad 7`: move up/left
* `Page Up`, `U`, `numpad 9`: move up/right
* `End`, `B`, `numpad 1`: move down/left
* `Page Down`, `N`, `numpad 3`: move down/right

Pressing `.` or `numpad 5` skips your turn.

Pressing `g` picks up an item. Press `i` to open your inventory to use an item and press `d` to open your inventory
to drop an item. While in your inventory, press the `a` to `z` keys to use the corresponding item or press any other 
key (or mouse click) to exit the inventory.

Pressing `Esc` quits the game immediately.

Moving into enemies attacks them. They will attack you. The message log will display the results of your attacks and 
the enemy's attacks. To see a larger view of the message log, press `V`. You can use the `up arrow`, `down arrow`, 
`page up`, and `page down` keys to navigate the larger message log view. Press any other key to return to the main 
game screen.

Hovering your mouse pointer over something will display the name of that thing above your message log.

<!-- ROADMAP -->
## Roadmap

* Expand beyond the initial [tutorial project](http://rogueliketutorials.com/tutorials/tcod/v2/)
* Add custom tilesets
* Improve the map generator
* Add more items, monsters, etc.

See the [open issues](https://github.com/bigangryguy/mogru/issues) for a list of proposed features (and known issues).

<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to be learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<!-- LICENSE -->
## License

Distributed under the GNU General Public License V3.0. See `COPYING` for more information.

<!-- CONTACT -->
## Contact

David Wilcox - [@davidtwilcox](https://twitter.com/davidtwilcox) - david@dtwil.co

Project Link: [https://github.com/bigangryguy/mogru](https://github.com/bigangryguy/mogru)

<!-- ACKNOWLEDGEMENTS -->
## Acknowledgements

* [Yet Another Roguelike Tutorial - Written in Python 3 and TCOD](http://rogueliketutorials.com/tutorials/tcod/v2/)
