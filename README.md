kancolle-auto
=============

Automation tool for Kantai Collection (http://www.dmm.com/netgame/feature/kancolle.html)

Dependency
==========

You need to install tools listed below.

* Python 2.x
* Sikuli

This tool is developed on Ubuntu. This tool might not run on the other environment.

Usage
=====

1. Go to Kantai Collection Home Port in your browser.
2. Run this script.
 * $ ./processwatch.py sikuli kancolle_auto.sikuli
  * just doing "$ sikuli kancolle_auto.sikuli" is still ok, but latest Sikuli engine has memory leak problem and sometimes it aborts.
  * processwatch.py executes specified command, and it re-execute the command if it ends. 
 
