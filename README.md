# kancolle-auto

**kancolle-auto** is a Kantai Collection automation tool.

**Please refer to the [releases page](https://github.com/mrmin123/kancolle-auto/releases) for stable releases, or the master branch for bleeding-edge (potentially unstable and buggy).** The [Changelog](http://github.com/mrmin123/kancolle-auto/wiki/Changelog) will have information on what's different.  Please refer to the [Setup page](https://github.com/mrmin123/kancolle-auto/wiki/Setup) for instructions on setting up kancolle-auto.

kancolle-auto is meant for educational purposes only. Actual and prolonged use of kancolle-auto may result in your account being banned. Remember that botting is against the rules!

kancolle-auto was originally a fork of [these](https://github.com/amylase/kancolle-auto) [other](https://github.com/Yukariin/kancolle-auto) [projects/forks](https://github.com/kevin01523/kancolle-auto), but has since outgrown on them in scope and function. Some ideas were inspired by [another similiar tool](https://github.com/tantinevincent/Onegai-ooyodosan).

#### Features

* Expedition module &mdash; automate expeditions
* PvP module &mdash; automate PvP
* Combat module &mdash; automate sorties (including Event maps), node selections, repairs, and submarine switching
* Quests module &mdash; automate quests
* Individual toggles for each of the above modules
* Scheduled sleeping/pausing of script
* Rudimentary catbomb recovery
* Separate `config.ini` file for easier configuration and backup of configurations
* Random variations to help avoid bot detection
* Helpful timers and other messages in console (when using sikuli-script)

For a more in-depth list of features, as well as installation/usage directions, please refer to the [kancolle-auto wiki](http://github.com/mrmin123/kancolle-auto/wiki).

#### Quick Start

1. Install Python 2.7.x
2. Install Java JRE 8
3. Install Sikuli 1.0.x
4. Install kancolle-auto
5. Setup kancolle-auto's config file
6. Run Kantai Collection
7. Run kancolle-auto using command `java -jar <path_to_sikuli>/sikuli-script.jar -r <path_to_kancolle_auto>/kancolle_auto.sikuli` (replacing `<path_to_sikuli>` and `<path_to_kancolle_auto>` with the correct directories for your install)
