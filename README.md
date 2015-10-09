# kancolle-auto

## Description

[Kantai Collection](http://www.dmm.com/netgame_s/kancolle) (Kancolle) expedition+combat automation tool. Originally a fork of based off [these](https://github.com/amylase/kancolle-auto) [other](https://github.com/Yukariin/kancolle-auto) [projects/forks](https://github.com/kevin01523/kancolle-auto). Additional ideas based off [another similiar tool](https://github.com/tantinevincent/Onegai-ooyodosan).

* Automatic expeditions
    * Determines how much time is remaining for expeditions sent out before script start
    * Identifies which expedition fleet has come back (see Setup Requirements)
    * Handles already-returned or immediately returning expeditions on cold start
* Combat module (automatic sorties and repair)
    * Allows for user to specify the map, number of nodes, formation for each node, and whether or not to engage in night battle for each node
    * Allows for user-specified damage threshold - will not sortie and instead repair any ship at or below this threshold
    * Allows for user-specified repair length threshold - will use bucket if repair timer is above this threshold
    * Automatic node decisions are NOT supported (although it's entirely possible for the user to choose the desired node even while the script is running)
    * Module can be turned off
* Separate `config.ini` that contains all user variables for easier configuration
* Random variations added to certain actions to hopefully make the tool more difficult to detect
    * Uses random menu items to refresh Home screen
    * Wait/sleep timers are pseudo-random
* Console timer indicates when next automated-action will occur - the user can interact with Kancolle during this time (set Quests, do Development/Construction, re-organize fleet, etc)
    * When script starts up again, it can navigate back to the Home screen and continue its automated actions as long as the game is not mid-Sortie
* Improved error catching and handling

## Setup Requirements

* Make sure your fleets have the default names for the script to be able to identify which expedition fleet has come back.
* If the combat module is enabled, make sure there are no ships NOT in fleet 1 that are in light/moderate/critical damage. You risk sinking ships otherwise!!!

## Disclaimers, Warnings, Caveats...

* kancolle-auto does NOT configure your fleet for you. It is up to the user to ensure that the fleets being deployed are able to complete their expeditions and sorties.
* You might be caught for using this tool! Automation is against the rules and I make no guarantees that you will not be caught and penalized and/or banned.
* If the combat module is enabled...
    * ... this script will send your ships into battle. There is always the risk of something going wrong and a ship sinking. Please disable the combat module if this worries you.
    * ... and bucket usage is enabled, this script will use them. Make sure you can spare them.
* Sikuli DOES take over your mouse so it will be difficult to do anything else while kancolle-auto is running.
* If you have multiple monitors, make sure your Kancolle window is on the main monitor, as Sikuli has issues with multi-monitor setups.


##Dependencies

You need the following at a minimum:

* Python 2.7.x
* Sikuli 1.0.x (not 1.1.x!) with options 2 and 5
* Java JRE 8

You may need to install separate programs depending on your environment (covered in next section).

This tool was developed and tested on Windows and Ubuntu, and on Chrome with the KC3 plugin.

##Installation and Usage

### Windows
1. Install Python, Java JRE 8, and Sikuli (options 2, 5) as needed
    * Make sure that you have the `tessdata` folder in the `libs` folder of your Sikuli directory. If it's missing, try deleting the `libs` folder so Sikuli re-generates the folder with the `tessdata` files. If that still doesn't work, try re-installing Sikuli with options 1 and 5 checked, run the IDE (this should generate the `tessdata` folder), and then move it out of the `libs` folder, then reinstall Sikuli with options 2 and 5 checked
2. Clone this project somewhere
3. Modify `config.ini` to fit your needs
4. Open KanColle in your favorite program (default: Chrome) and go to the Home screen
5. Run kancolle_auto from the command prompt: `java -jar <path_to_sikuli>\sikuli-script.jar -r <path_to_kancolle_auto>\kancolle_auto.sikuli`

### Ubuntu
1. Install Python, Java JRE 8, and Sikuli (options 2, 5) as needed
2. Install additional packages: `apt-get install wmctrl xdotool tesseract-ocr`
    * Make sure that you have the `tessdata` folder in the `/usr/local/share/` directory. For example, if tesseract-ocr installed to `/usr/share/`, move it over to the correct directory using the command `sudo cp -rpf /usr/share/tesseract-ocr/tessdata /usr/local/share/tessdata`
3. Clone this project somewhere
4. Modify `config.ini` to fit your needs
5. Open KanColle in your favorite program (default: Chrome) and go to the Home screen
6. Run kancolle_auto from the terminal: `java -jar <path_to_sikuli/sikuli-script.jar -r <path_to_kancolle_auto>/kancolle_auto.sikuli`

## Known Issues and Troubleshooting

* Sikuli, the program this script relies on for button/screen recognition and OCR, can mis-identify portions of the screen or mis-click at times. The script might fail as a result.
* I tried to make the sleeps and delays as flexible as possible, but if Kancolle takes too long in certain screen transitions (slow internet connection, unresponsive Kancolle servers, etc) the script might fail.
* Sikuli sometimes can't find/doesn't properly click areas of the screen. I've tried to improve the failure catching and handling for the ones I've encountered, but I probably haven't accounted for everything.
* I'm sure there are other edge and corner cases that I haven't accounted for. Script may fail when these scenarios are hit.

Generally, if the script crashes, get out of the sortie if you're in one, and restart the script; it should recover gracefully. If the script fails at a specific point/scenario consistently, please open a ticket.
