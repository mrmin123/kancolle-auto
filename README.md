Description
===========

Automation tool for [Kantai Collection](http://www.dmm.com/netgame_s/kancolle) because seriously, fuck this game.

Some additional features:
* Determines how much time is remaining in an expedition that's already been sent out before the script was started
* Knows which expeditions have come back
* Improved error (but not perfect) catching

Dependencies
============

You need the following at a minimum.

* Python 2.7.x
* Sikuli 1.0.x (not 1.1.x!) with options 2 and 5
* Java JRE 8

You may need to install separate programs depending on your environment (covered in next section).

This tool was developed and tested on Windows and Ubuntu. No guarantee that it will run on other environments!

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
