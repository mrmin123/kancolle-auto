# kancolle-auto

**kancolle-auto** is a robust Kantai Collection automation tool.

***

>**WARNINGS/DISCLAIMERS**

> kancolle-auto is meant for educational purposes only. Actual and prolonged use of kancolle-auto may result in your account being banned. Remember that botting is against the rules!

> I make no guarantees that you will not be caught and penalized using kancolle-auto, so be smart about it. Don't spam expeditions and sorties nonstop 24/7. Try to mimic a human as much as possible with your use of this tool! Relevant discussion can be found [here](https://github.com/mrmin123/kancolle-auto/issues/130).

> In addition, if you let kancolle-auto sortie you might lose ships! It is highly unlikely (multiple checks occur to prevent this from happening) but I make no guarantees! Also, if you let kancolle-auto use buckets, make sure you can spare them!

***

>**NOTE**

> kancolle-auto is **not** designed to be the **fastest** automation tool. It is designed to be **robust** and **highly customizable**. kancolle-auto is meant to free up your time, energy, and attention, not to net you the most resources or XP in the shortest time possible. It can automate almost every major feature in the game, including combat, and it can run for days on end with minimal to no user intervention.

***

**Please refer to the [releases page](https://github.com/mrmin123/kancolle-auto/releases) for stable releases, or the master branch for bleeding-edge (potentially untested and/or buggy in exchange for additional features).**

Please read the [**kancolle-auto wiki**](https://github.com/mrmin123/kancolle-auto/wiki) for more details:

* The [**Changelog**](http://github.com/mrmin123/kancolle-auto/wiki/Changelog) will have information on the differences between the releases and master branch
* Please refer to the [**Setup**](https://github.com/mrmin123/kancolle-auto/wiki/Setup) page for instructions on setting up kancolle-auto
* Examples of the config can be found [**here**](https://github.com/mrmin123/kancolle-auto/wiki/Example-configs), while Event-specific config examples can be found [**here**](https://github.com/mrmin123/kancolle-auto/wiki/Example-Event-configs)


#### Features

* Expedition module &mdash; automate expeditions
* PvP module &mdash; automate PvP
* Combat module &mdash; automate sorties, node selections, repairs, and submarine switching
  * Supports Event maps, Combined Fleet maps, and LBAS maps
* Quests module &mdash; automate quests
* Individual toggles for each of the above modules
* Scheduled sleeping/pausing of script
* Rudimentary catbomb recovery
* Separate `config.ini` file for easier configuration and backup of configurations
* Random variations to help avoid bot detection
* Helpful timers and other messages in console (when using sikuli-script)

For a more in-depth list of features, as well as installation/usage directions, please refer to the [kancolle-auto wiki](http://github.com/mrmin123/kancolle-auto/wiki).

kancolle-auto was originally a fork of [these](https://github.com/amylase/kancolle-auto) [other](https://github.com/Yukariin/kancolle-auto) [projects/forks](https://github.com/kevin01523/kancolle-auto), but has since outgrown on them in scope and function. Some ideas were inspired by [another similiar tool](https://github.com/tantinevincent/Onegai-ooyodosan).

#### Quick Start

1. Install [Java JRE 7](http://www.oracle.com/technetwork/java/javase/downloads/jre7-downloads-1880261.html)
2. Install [Sikuli 1.0.x](https://launchpad.net/sikuli/sikulix/1.0.1) (not 1.1.x!) with options 2 and 5
3. Install kancolle-auto
4. [Setup kancolle-auto's config file](https://github.com/mrmin123/kancolle-auto/wiki/Setup-config.ini) ([examples](https://github.com/mrmin123/kancolle-auto/wiki/Example-configs))
5. Run Kantai Collection
6. Run kancolle-auto using command `java -jar <path_to_sikuli>/sikuli-script.jar -r <path_to_kancolle_auto>/kancolle_auto.sikuli` (replacing `<path_to_sikuli>` and `<path_to_kancolle_auto>` with the correct directories for your installs)

#### FAQ/Commonly asked questions

**Q: Can I do other stuff on the machine or play Kantai Collection while kancolle-auto is running?**

A: Kinda. kancolle-auto takes control of the mouse as it runs so it will be difficult to do anything meaningful while kancolle-auto is actively running. During scheduled pauses, however, you have full control of the machine. Just make sure that Kantai Collection is not in the middle of a PvP or Sortie when the schedule pause ends. The script will crash and you will have to restart the script.

**Q: kancolle-auto periodically crashes! (FindFailed errors)**

A: This is 99% not a bug in the program so please do not make a ticket. Instead, try raising the `SleepModifier` field in the config to 1 or 2 or 3. If this does not reduce the number of crashes, then please create a detailed ticket.

**Q: I started getting catbombed frequently after I started using kancolle-auto!**

A: You're probably botting too much. Use the ScheduledSleep functionality and let the program pause itself for a few hours every day.
