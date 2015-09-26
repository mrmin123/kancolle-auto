Description
===========

[Kantai Collection](http://www.dmm.com/netgame_s/kancolle) (Kancolle) expedition+combat automation tool.

Originally a fork of based off [these](https://github.com/amylase/kancolle-auto) [other](https://github.com/Yukariin/kancolle-auto) [projects/forks](https://github.com/kevin01523/kancolle-auto). Additional ideas based off [another similiar tool](https://github.com/tantinevincent/Onegai-ooyodosan)).

* Automatic expeditions
    * Determines how much time is remaining in an expedition that's been sent out before script start
    * Identifies which expedition fleet has come back
    * Handles already-returned or immediately returning expeditions on cold start
* Automatic sorties
    * Allows for user to specify the map, number of nodes, formation for each node, and whether or not to engage in night battle for each node
    * Allows for user-specified damage threshold - will not sortie and instead repair any ship at or below this threshold
    * Allows for user-specified repair length threshold - will use bucket if repair timer is above this threshold
    * Automatic sorties be turned off in `config.ini`
* Separate `config.ini` that contains all user variables for easier configuration
* Random variations added to certain actions to hopefully make the tool more difficult to detect
    * Uses random menu items to refresh Home screen
    * Wait/sleep timers are pseudo-random
* Console timer indicates when next automated-action will occur - the user can interact with Kancolle during this time (set Quests, do Development/Construction, re-organize fleet, etc)
    * When script starts up again, it can navigate back to the Home screen and continue its automated actions as long as it doesn't find itself in a Sortie when it comes back
* Improved error catching and handling

Disclaimer/Warning
==================
* I make no guarantees that you won't be caught for using this tool! You may be penalized/banned for using this (or any other) automation tool for this game.
* If allowed, this script will send your ships into battle. I've tried to make it as robust as possible in ensuring that your ships won't be sent to the bottom of the ocean, but there are no guarantees! If this concerns you, disable the combat module in `config.ini`.
* If allowed, this script will use your buckets, so make sure you can spare them!

Known Issues
============
* Sikuli, the program this script relies on for button/screen recognition and OCR, can mis-identify portions of the screen or mis-click at times. As a result, the script might crash.
* I tried to make the sleeps and delays as flexible as possible, but if Kancolle takes too long in certain screen transitions (slow internet connection, unresponsive Kancolle servers, etc) the script might crash.
* Sikuli sometimes can't find/doesn't properly click areas of the screen. I've tried to improve the failure catching and handling for the ones I've encountered, but I probably haven't accounted for everything.
* I'm sure there are other edge and corner cases that I haven't accounted for. Script may crash when these scenarios are hit.

If the script crashes, just get back to the Home screen and restart it. It should be able to recover gracefully. If the same issue crashes the script repeatedly, please open an issue ticket.

Dependencies
============
You need the following at a minimum:

* Python 2.7.x
* Sikuli 1.0.x (not 1.1.x!) with options 2 and 5
* Java JRE 8

You may need to install separate programs depending on your environment (covered in next section).

This tool was developed and tested on Windows and Ubuntu, and on Chrome with the KC3 plugin. No guarantee that it will run on other environments, but it should work.

The tool also requires that your fleets have the default names.

Installation and Usage
======================

### Windows
1. Install Python, Java JRE 8, and Sikuli (options 2, 5) as needed
    * Make sure that you have the `tessdata` folder in the `libs` folder of your Sikuli directory. If it's missing, try re-installing Sikuli with options 1 and 5 checked, run the IDE (this should generate the `tessdata` folder), and then move it out of the `libs` folder, then reinstall Sikuli with options 2 and 5 checked
2. Clone this project somewhere
3. Modify `config.ini` to fit your needs
4. Open KanColle in your favorite program (default: Chrome) and go to the Home screen
5. Run kancolle_auto from the command prompt: `java -jar <path_to_sikuli>\sikuli-script.jar -r <path_to_kancolle_auto>\kancolle_auto.sikuli`

### Ubuntu
1. Install Python, Java JRE 8, and Sikuli (options 2, 5) as needed
    * Make sure that you have the `tessdata` folder in the `/usr/local/share/` directory. I actually have no idea how to generate this in Ubuntu. I had to copy over the folder from my Windows install.
2. Install additional packages: `apt-get install wmctrl xdotool`
3. Clone this project somewhere
4. Modify `config.ini` to fit your needs
5. Open KanColle in your favorite program (default: Chrome) and go to the Home screen
6. Run kancolle_auto from the terminal: `java -jar <path_to_sikuli/sikuli-script.jar -r <path_to_kancolle_auto>/kancolle_auto.sikuli`
