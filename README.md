<p align="center">
    <h3 align="center">Mogru</h3>
    <p align="center">
        A text-based roguelike game written in Python 3 using TCOD.
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
Gameplay is rudimentary at the moment. Use the arrow keys to move your character (the `@`) 
on the map and press `Esc` to quit.

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
