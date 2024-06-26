# Change Log

## v0.1.7 Bug-Fix missing dependency in v0.1.16
* added dependency `esp2_gateway_adapter`

## v0.1.16 Improved send message and program devices (DELETED)
* Support for programming different baseId for HA sender into devices on bus.
* Enabled FMZ14 and FAE14SSR to be programmed. 
* Added template list for messages to be sent
* Added lib for ESP3 (USB300) support. (https://github.com/grimmpp/esp2_gateway_adapter)

## v0.1.15 Fixed Send Message
* Send Message Window improved and fixed.
* Added button in toolbar for send message window.

## v0.1.13 Send Message Window Improved
* Improved send messages tool.
* fixed log rotation
* Improved ESP3. Sending is working but not for gateway commands like A5-38-08 which is needed to control lights.

## v0.1.12 Send Message Window added
* Small tool to send messages added.

## v0.1.11 EEP Checker added
* Small tool added to check EEP values of a data set.

## v0.1.10 Logs are sent into file
* Logs are now written to log file in application folder.
* Added Flag to see values from incomming telegrams.

## v0.1.9 Read Support for USB300 + Multi-Gateway Support for HA Config Export
* Fixed compatibility of loading old application configs
* Icons added
* Remove Smart Home addresses as real buttons from HA export
* Serial port detection for FAM-USB and USB300 improved.
* TODO: Cleanup of ESP3 communication, move function into lib

## v0.1.8 Wireless Tranceiver Support
* Reset suggested HA settings added
* Support for FAM-USB. Is now detected as gateway and contained in HA config 
* **Experimental** Support for USB300. CODE CLEANUP HEAVILY NEEDED!!!

## v0.1.7 F2SR14 Support
* Support for F4SR14 added
* Update Button added

## v0.1.6 Sensor Values are evaluated
* Sensor values are displayed in command line
* Sponsor button added
* Docs updated with system requirements
* Added links to documentation
* Improved look and feel
* About window improved
* Icons to menu added
* Unmapped devices are moved to FAM14 after connection.
* Error handling added for serial connection.

## v0.1.5 Refactoring + Basic Features (GOAL: Stability)
* Improved imports incl. homeassistant mock
* Changed application output format to yaml. **=> Braking Change**
* Refactored Home Assistant Configuration Exporter
* Created start file for windows (eo-man.bat) which can be used to create a shortcut for e.g. the taskbar.
* Changed folder structure (renamed 'eo-man' to 'eo_man' which allows using package name.)  **=> Braking Change**
* Introduced tests
* Introduced cli commands
* Added possibility to only use command line to generate Home Assistant Configuration
* Application info added
* Application info and description added to auto-generated Home Assistant configuration.
* python pre-commits added to ensure unittests are executed successfully before every commit. 

## v0.1.4 Bug fixed in python package
* Bug in python package fixed

## v0.1.1 Bug Fix and values in log view
* 🐞 Missing function added from refactoring 🐞
* 💎 Added values for incoming messages which are displayed in log view.