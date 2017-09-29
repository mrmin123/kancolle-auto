#### 2017-09-29 ([Release 10.1](https://github.com/mrmin123/kancolle-auto/releases/tag/10.1))
* Restore accidentally-removed combat assets

#### 2017-09-22
* Archive 2017 Summer Event assets

#### 2017-09-04
* Add support for 2017 Summer Event (thanks to @muromachi, @waicool20, @yhn147, @perryhuynh)
* Add support for Luigi Torelli in the submarine switcher module (thanks to @waicool20)

#### 2017-06-07 ([Release 10](https://github.com/mrmin123/kancolle-auto/releases/tag/10))
* Update PvP and Submarine Switch assets to support the June 6th 2017 update to Kantai Collection (thanks to everyone for reporting changes and providing assets)

#### 2017-05-31
* Actually archive 2017 Spring Event assets
* Change `FleetComp` option to `FleetComps` to support fleet cycling for sorties (thanks to @waicool20)
* Add `UseBuckets` option to Submarine Switch module to specify whether or not submarines should be bucketed (thanks to @R-Jimenez)
* Update readme

#### 2017-05-22
* Archive 2017 Spring Event assets

#### 2017-05-13
* Add additional assets for 2017 Spring Event (thanks to @frosty5689)

#### 2017-05-12
* Add support for 2017 Spring Event (thanks to @AppleBoi86, @waicool20, @twisting2017, @perryhuynh, and @frosty5689)

#### 2017-05-07
* Update asset for port checking for Events

#### 2017-04-03
* Bugfix to repair module (thanks to @Aripracc)

#### 2017-04-02
* Updates to sortie-related assets (thanks to @waicool20)

#### 2017-03-29 ([Release 9.1](https://github.com/mrmin123/kancolle-auto/releases/tag/9.1))
* Create wrapper for streamlining calls to Sikuli's `findAll` functionality

#### 2017-03-26
* Fix fleetcomp switcher and assets
* Update readme and configs

#### 2017-03-17 ([Release 9](https://github.com/mrmin123/kancolle-auto/releases/tag/9))
* Update assets to support the March 17th 2017 upgrade to Kantai Collection (thanks to everyone for reporting changes and providing assets)

#### 2017-03-15 ([Release 8.3](https://github.com/mrmin123/kancolle-auto/releases/tag/8.3))
* Bugfixes to PvP module

#### 2017-03-13 ([Release 8.2](https://github.com/mrmin123/kancolle-auto/releases/tag/8.2))
* Bugfixes to submarine switch module

#### 2017-03-12 ([Release 8.1](https://github.com/mrmin123/kancolle-auto/releases/tag/8.1))
* Impovements to PvP module so it selects diamond or line abreast vs sub-heavy opponents, as well as declining night battle against all-sub fleets
* Improvements to submarine switch module to use less clicks
* `EnabledSubs` option of submarine switch module now supports 'ss' and 'ssv' as valid group values
* Bugfix to `ScheduledStop` feature (thanks to @waicool20)
* Minor code updates

#### 2017-02-28 ([Release 8](https://github.com/mrmin123/kancolle-auto/releases/tag/8))
* Archive 2017 Winter Event assets
* Implement `FatigueSwitch` feature, which lets you specify whether or not kancolle-auto should attempt to switch out fatigued submarines with its submarine switcher module
* Optimized the submarine switch module's performance when `EnabledSubs` is set to 'all'
* Bugfix to fix non-detection of quest bw7
* Minor code updates

#### 2017-02-25
* Critical bugfix to `LastNodePush` feature. Please upgrade if you are using this, otherwise you are at risk of losing ships

#### 2017-02-24
* Bugfix with config reader not working when `ReplaceLimit` was set to blank value

#### 2017-02-23
* Implement `ReplaceLimit`, which lets you specify what up to what level of damaged subs should be swapped out by the submarine switch module
* Revise timings to fix bugs caused by optimizing default Sikuli wait times
* Bugfix on 2017 Winter Event asset (E-3 panel)

#### 2017-02-20
* Optimized default Sikuli and combat loop wait times
* Bugfix and updates to config files
* Revise some expedition assets

#### 2017-02-19
* Update 2017 Winter Event assets
* Add SSV support to submarine switch module (thanks to @waicool20)
* Revise submarine switch assets
* Improve `debug_find` function
* Add CONTRIBUTING.md
* Update config and config_detailed (may cause many merge conflicts)
* Update code to follow PEP8 spacing
* Copy 2017 Winter Event assets into archive folder for use in wiki documentation

#### 2017-02-18
* Bugfix to LBAS assignment method
* Bugfix to repair module's setting of next sortie time

#### 2017-02-17
* Expand support for 2017 Winter Event

#### 2017-02-16
* Expand support for 2017 Winter Event

#### 2017-02-15
* Expand support for 2017 Winter Event (thanks to @waicool20)
* Improve Event expedition support (thanks to @waicool20)

#### 2017-02-14
* Expand support for 2017 Winter Event (thanks to @AppleBoi86 and @Danielosama)

#### 2017-02-12
* Expand support for 2017 Winter Event
* Revise submarine switch module logic

#### 2017-02-11
* Begin adding support for 2017 Winter Event
* Bugfix to LBAS panel switch image so it works with low-morale planes

#### 2017-02-07 ([Release 7.1](https://github.com/mrmin123/kancolle-auto/releases/tag/7.1))
* Improvements to repair and submarine switch modules (thanks to @waicool20)
* Further modifications to combat module
* Minor updates and code cleanup

#### 2017-01-28
* Bugfix for crash when kancolle-auto's repair module encounters a completely filled repair screen (thanks to @waicool20)

#### 2017-01-23
* Bugfix for crash when kancolle-auto is started only with PvP module enabled (thanks to @waicool20)

#### 2017-01-22 ([Release 7](https://github.com/mrmin123/kancolle-auto/releases/tag/7))
* Upgrade to use Sikuli 1.1.1/SikuliX
  * WARNING: Future versions of kancolle-auto will no longer be compatible with Sikuli 1.0.x! Please upgrade Sikuli following the [Quick Start](https://github.com/mrmin123/kancolle-auto#quick-start) directions
* Update README

#### 2017-1-1 ([Release 6.1](https://github.com/mrmin123/kancolle-auto/releases/tag/6.1))
* Happy New Year
* Add CHANGELOG to repo
* Update README and ISSUE_TEMPLATE

#### 2016-12-22
* Add support for LBAS on normal non-event maps
* Add better support for LBAS when all groups are not assigned any nodes
* Add 6-4 map assets
* Remove 2016 Winter Event assets

#### 2016-12-05 ([Release 6](https://github.com/mrmin123/kancolle-auto/releases/tag/6))
* Revise submarine switch module to support more granular choice of submarines
* Revise FCF logic to better support ship drops before FCF screen check

#### 2016-12-03
* Add additional images for 2016 Winter Event

#### 2016-11-27
* Update Event expedition icon for 2016 Winter Event
* Update LBAS resupply logic to use the new one-click resupply button

#### 2016-11-26
* Revise and add images for 2016 Winter Event

#### 2016-11-20
* Revise images for 2016 Winter Event (thanks to @diceman112)

#### 2016-11-19
* Add support for 2016 Winter Event (thanks to @diceman112)

#### 2016-10-13
* Re-structure Quest module, `QuestNode` object, and Quest trees
* Add extra Quest item to catch erroneous bw4 OCR readings

#### 2016-09-07
* Replace 4-4 panel image (thanks to @diceman112)

#### 2016-09-05
* Separate out config file descriptions into `config_detailed.ini`
* Separate out submarine switcher in config into its own section
* Bugfix in OCR function

#### 2016-08-24
* Restructured to handle viewer popups

#### 2016-08-21
* Add additional 2016 Summer Event E-4 assets
* Made Event pre-boss and boss node support expeditions more future proof. They are defined as expeditions 9998 and 9999, respectively
* Minor changes to README and config file
* Other minor changes

#### 2016-08-18 ([Release 5](https://github.com/mrmin123/kancolle-auto/releases/tag/5))
* Add support for 2016 Summer Event
  * Panel images for all maps
  * Node select images for E-4
  * LBAS node select images for E-2, E-3, E-4
* Add LBAS resupply and sortie support for event maps
* Add pre-boss support and boss support expedition support
* Add additional check to improve fleet status checking mid-sortie
* Update README, config file, and ISSUE_TEMPLATE
* Other minor tweaks and improvements
* Add debug method for rudimentary image match checking

#### 2016-07-17
* Re-work Quests module to be more flexible (see [#198](https://github.com/mrmin123/kancolle-auto/issues/198))
* Changes to OCR functions in `util` to support changes related to above item
* Add support for `ScheduledStop`
* Organized and moved code around

#### 2016-07-05 ([Release 4.3](https://github.com/mrmin123/kancolle-auto/releases/tag/4.3))
* Update Submarine Switch images (thanks to @diceman112)
* Update bw6, bw7, bw10, c8 quest images. All quest images now updated

#### 2016-06-22
* Update bd4 and bd6 quest images

#### 2016-06-21
* Update sub switch image
* Update quest image

#### 2016-06-15
* Re-support Quests after the June 10th 2016 Quests UI update to Kantai Collection
* Remove unnecessary last crash timer check from catbomb recovery routine
* Improve catbomb recovery routine

#### 2016-06-09 ([release 4.2](https://github.com/mrmin123/kancolle-auto/releases/tag/4.2))
* Implement `LastNodePush`, which makes kancolle-auto 'push' past the last specified combat node, regardless of fleet damage states. Useful for maps where the last node is a resource/non-combat node like 1-6 (please be careful when using this feature!!!!)
* Improve tracking of completed sorties
* Bugfix in PvP module
* Bugfix in Quests module
* Remove 2016 Spring event elements
* Implement additional catbomb check post-expedition

#### 2016-05-30
* Add node D image for 2016 Spring E-4
* Revise home refresh action pre-sortie to avoid some crash scenarios
* Add/modify rejiggers in combat module
* Update readme and config

#### 2016-05-28
* Add node D and E images for 2016 Spring E-2
* Slight modification to expedition and sortie counting mechanism

#### 2016-05-25 ([release 4.1](https://github.com/mrmin123/kancolle-auto/releases/tag/r4.1))
* Critical bugfix to combat module

#### 2016-05-21 ([release r4](https://github.com/mrmin123/kancolle-auto/releases/tag/r4))
* Implement global regions for each formation
* Fix formation input validator in config loader
* Workaround to `wait_and_click()`

#### 2016-05-13
* Add node D and F images for 2016 Spring E-7
* Implement formation input validation in config loader
* Fix automatic formation fill for combined fleets
* Tweak `rnavigation()`

#### 2016-05-11
* Add/revise images for 2016 Spring event (page switch arrows are in)
* Revise resupply to better support failed switches due to damage ship smoke
* Add home refresh before sortieing to refresh ships under repair
* Add support for multiple rewards/unlocks after sorties
* Bugfix to PvP module

#### 2016-05-05
* Add panel images for 2016 Spring event (no page switch arrows yet)
* Tighten up expand areas in repair module to hopefully avoid crashes
* Revise certain mouse rejigger areas so that mouse does not rest on certain buttons
* Bugfix to submarine switcher
* Revise `display_timers` text

#### 2016-04-03
* Update config defaults and readme
* Force homescreen refresh before combat sortieing to update ships under repair
* Add expanded click areas for fleet flags and ship selection in repair screen

#### 2016-03-21
* Bugfix to Quests module where quests not started due to the queue being full would be tracked incorrectly

#### 2016-03-16
* Bugfix to Combat module where SubmarineSwitch would not work if the submarines had low morale

#### 2016-03-14
* Implement `MedalStop` into Combat module - stops automatic sorties once a medal has been obtained (for automating monthly medal grinding)
* Fix Quests module
  * Better tracking of number of active quests
  * Fix ability to switch quests from PvP to Sortie quests
* Optimize expeditions module
* Move 2016-Winter assets, add node selection images for map 4-5
* Other minor bugfixes

#### 2016-03-12
* Improved performance of image matching by specifying specific search regions for many commonly-used images, as well as specifying the global search region to the Kantai Collection game, not the viewer/browser window
* Sped up certain actions by incorporating `sleep_fast()` (0.2 - 0.5ms sleep) and tightening up or removing other `sleep()`s
* Changes to how Schedule Sleep and PvP timers are set
* Fix submarine switcher not sorting immediately after successful submarine switch
* Fix issues with cold starting expeditions
* Incorporate more informative next action timer message at end of main loop
* Numerous changes to main kancolle_auto loop
* Add ISSUE_TEMPLATE
* Minor changes to navigation
* Few other bugfixes

#### 2016-02-20 ([release r3](https://github.com/mrmin123/kancolle-auto/releases/tag/r3))
* Finalize Combined Fleet support
* Finalize Event support
* Revise Expeditions module and the way it tracks expeditions
* Improvements to `rejigger_mouse`
* Updated README, config, and wiki
* Other minor bugfixes and improvements

#### 2016-02-18
* Add Combined Fleet support
* Add support for FCF (automatically retreats via FCF if only one ship is critically damaged)
* Bugfix in Combat module where sortieing to non-Event maps were bugged
* Bugfix in Quests module

#### 2016-02-16
* Expand support for sortieing to Event maps
* Implement node select ability
* Revise the Combat module's pre-combat loop

#### 2016-02-15
* Add basic support for sortieing to Event maps

#### 2016-02-12
* Bugfixes on `pattern_generator` and other speed improvement changes
* Optimized Quest module
* Added quest filtering system - quest selection and deselection based on PvP or Sortie quests
* Re-generated quest images

#### 2016-02-11
* Improve speed and performance of kancolle-auto overall by reducing number of image matching kancolle-auto has to do
  * Revamped random click - `rclick` function has been removed and replaced with `pattern_generator`, which can reduce the number of image matching actions by up to 50%, while retaining random click locations
  * Optimized use of `findAll` - code that is dependent on `findAll` no longer requires redundant image matching
* Expeditions received during PvP are not forgotten anymore and are properly re-dispatched
* Taigei is no longer a valid submarine replacement for the `switch_sub` method

#### 2016-02-09
* Improve quest identification in Quests module

#### 2016-02-06
* Implement submarine switching capability for Combat module - if enabled, kancolle-auto will switch out submarines being repaired to continue sorties
* Change `RepairTimeLimit` setting in `config.ini` to format `HHMM` from `HH` for more granular setting of the repair time limit

#### 2016-01-22
* Implement fleet composition switcher for when both PvP and Combat are enabled
* Update retreat images in Combat module

#### 2016-01-18 ([release r2.1](https://github.com/mrmin123/kancolle-auto/releases/tag/r2.1))
* Fix KC3 recovery method

#### 2016-01-09 ([release r2](https://github.com/mrmin123/kancolle-auto/releases/tag/r2))
* Revise quest images
* Bugfixes to Quest module
* Revise builtin-expedition timers

#### 2016-01-04
* Implement random mouse rest locations (thanks to @minh6a)
* Implement config option to modify script cycle timer
* Implement force recheck of expected fleets
* Minor changes to Quests module
* Tweak expanded click areas
* Fix bug that caused repeated checks for PvP
* Other minor bugfixes

#### 2015-12-26
* Bugfix on PvP expanded click areas

#### 2015-12-23
* Implement expanded click areas for quests and PvP screens
* Shorten timers on hard-coded expedition timers
* Implement ability to turn off Quests module via config

#### 2015-12-19
* Revise images used for PvP
* Incorporate Enabled config option for Quests
* Bugfixes to Quests module

#### 2015-12-17
* Rudimentary implementation of PvP module (automated PvP)
* Rudimentary implementation of schedule sleep (kancolle-auto automatically pauses/sleeps at specified time for specified length of time)
* Expand and bugfixes on quests module
* Expand OCR and allow for attempt limit on timer reads

#### 2015-11-15
* Implement quests module (automated quests)
* Other minor improvements and bugfixes

#### 2015-11-08 ([release r1](https://github.com/mrmin123/kancolle-auto/releases/tag/r1))
* Incorporate destination checks to `rnavigation`
* Other minor changes

#### 2015-11-06
* Expand repair functionality
  * Read timers on ships already under repairs
  * Continue repair process if fleet is still damages and a repair dock opens up
* Optimize actions on script start
* Other minor improvements and bugfixes

#### 2015-10-27
* Make `check_timer` more crash-resistant
* Skip OCR check when set to always use buckets on repair
* Expand OCR
* Other minor improvements and bugfixes

#### 2015-10-27
* Implement expanded click area for `expedition_finish.png`
* Revise combat_panel images
* Expand OCR

#### 2015-10-26
* Implement expanded click area for `compass.png`, `next.png`, and `next_alt.png` (expansion of bot-detection evasion features; see discussion in [#52](https://github.com/mrmin123/kancolle-auto/issues/52))
* Revise combat_panel images to account for above change
* Other minor improvements and bugfixes

#### 2015-10-25
* Implement random walk through menus (expansion of bot-detection evasion features; see discussion in [#52](https://github.com/mrmin123/kancolle-auto/issues/52))
* Refactor expedition module so expedition-only related commands lives only in `expedition.py`
* Improve the `check_timer` method so that it does not crash the script when it encounters completely bizarre OCR results
* Tighten up images
* Other minor improvements and bugfixes

#### 2015-10-20
* Tweak some sleep timers
* Tweak fatigue/morale image check thresholds
* Revise sortie world selection images

#### 2015-10-19
* Update KCT recovery method to use the 'Get API Link' option
* Minor bugfixes

#### 2015-10-18
* Incorporate mouse click location randomization (see discussion in [#52](https://github.com/mrmin123/kancolle-auto/issues/52))
* Update readme

#### 2015-10-16
* Add support for catbomb recovery

#### 2015-10-13
* Expand OCR character checking

#### 2015-10-12
* Incorporate retreat and repair thresholds so the two can be differentiated
* Add ability to choose whether or not to sortie if port is full (ship slots maxed out)

#### Previous
* A bunch of stuff
