Description
=============

Automation tool for [Kantai Collection](http://www.dmm.com/netgame_s/kancolle)

Dependency
==========

You need to install tools listed below.

* Python 2.x
* Sikuli (strongly recommended use 1.0.x instead 1.1.x)
* java jre(latest)

This tool is developed and successfully tested on Ubuntu, Archlinux, Gentoo and Windows. But it should run on the other environment too.

Usage
=====

1. Open KanColle viewer from [KanColle Tools](https://github.com/KanColleTool/KanColleTool) (if you use other viewers or play in browser - just focus necessary window after see yellow Sikuli splash) and go to port (main screen).
2. Run this script.

 for windows first cd to your current sikuli dir
 
 * open cmd

 * type cd %sikuli dir%\folder name\

 * press enter

 * type runScript -r %script dir%\kancolle_auto.sikuli

 * then focus on your kancolle viewer or gui where you play kancolle

 * just doing "$ runScript -r kancolle_auto.sikuli".
