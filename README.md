Description
===========

Automation tool for [Kantai Collection](http://www.dmm.com/netgame_s/kancolle) because seriously, fuck this game.

Some features added on top of the [other](https://github.com/amylase/kancolle-auto) [project](https://github.com/Yukariin/kancolle-auto) [forks](https://github.com/kevin01523/kancolle-auto) (ideas borrowed from [another similiar tool](https://github.com/tantinevincent/Onegai-ooyodosan)):

* More robust handling of expeditions on cold start
    * Handles already-returned or immediately returning expedition fleets better
    * Determines how much time is remaining in an expedition that's already been sent out
* Identifies which expedition fleet has come back
    * Required fleet names to be the default fleet names
* Automatic 3-2-A grind
    * Allows for user-specified damage threshold - will not sortie and instead repair any ship at or below this threshold
    * Allows for user-specified repair length threshold - will use bucket if repair timer is above this threshold
    * Can be turned off by setting `combat` variable to `False`
* Variability added to actions to hopefully make the tool more difficult to detect
    * Uses random menu items to refresh Home screen
    * Wait/sleep timers are pseudo-random
* Improved error catching and handling

Known Issues
============
* If ships are damaged AND need resupply, the script will NOT properly detect the damage state of your fleet. This might result in your critically damaged ships being sortied! Make sure your Fleet 1 is resupplied before running this script!
    * This is theoretically an easy fix, but I'm too lazy to do it...
* I tried to make the sleeps and delays as flexible as possible, but if Kancolle takes too long in certain screen transitions (slow internet connection, unresponsive Kancolle servers, etc) the script might crash because it can't find the next expected screen in time
* Sikuli sometimes can't find/doesn't properly click areas of the screen. I've tried to improve the failure catching and handling for the ones I've encountered, but I probably haven't accounted for everything
* I'm sure there are other edge and corner cases that I haven't accounted for. Script may crash when these scenarios are hit!

If the script crashes, just get back to the Home screen and restart it. It should be able to recover gracefully.

Dependencies
============

You need the following at a minimum.

* Python 2.7.x
* Sikuli 1.0.x (not 1.1.x!) with options 2 and 5
* Java JRE 8

You may need to install separate programs depending on your environment (covered in next section).

This tool was developed and tested on Windows and Ubuntu, and on Chrome with the KC3 plugin. No guarantee that it will run on other environments, but it should work.

Installation and Usage
======================

1. Install Python, Java JRE 8, and Sikuli (options 2, 5) as needed
    * Make sure that you have the `tessdata` folder in the `libs` folder of your Sikuli directory. If it's missing, try re-installing Sikuli with options 1 and 5 checked, run the IDE (this should generate the `tessdata` folder), and then move it out of the `libs` folder, then reinstall Sikuli with options 2 and 5 checked
2. Clone this project somewhere
3. Modify the `USER VARIABLES` section in `kancolle_auto.py` to fit your expedition needs
4. Open KanColle in your favorite program (default: Chrome) and go to the Home screen
5. Run kancolle_auto from the command prompt: `java -jar <path_to_sikuli>\sikuli-script.jar -r <path_to_kancolle_auto>\kancolle_auto.sikuli`

###Ubuntu
1. Install Python, Java JRE 8, and Sikuli (options 2, 5) as needed
    * Make sure that you have the `tessdata` folder in the `/usr/local/share/` directory. I actually have no idea how to generate this in Ubuntu. I had to copy over the folder from my Windows install.
2. Install additional packages: `apt-get install wmctrl xdotool`
3. Clone this project somewhere
4. Modify the `USER VARIABLES` section in `kancolle_auto.py` to fit your expedition needs
5. Open KanColle in your favorite program (default: Chrome) and go to the Home screen
6. Run kancolle_auto from the terminal: `java -jar <path_to_sikuli/sikuli-script.jar -r <path_to_kancolle_auto>/kancolle_auto.sikuli`
