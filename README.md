Render Presets
--------------

Render Presets lets you manage a library of different common rendering related
settings to quickly organize, apply or switch between them.

Website:      http://www.artstorm.net/plugins/render-presets/  
Project:      https://github.com/artstorm/render-presets  
Support:      https://github.com/artstorm/render-presets/issues  
 
Contents:
 
* Installation
* Usage
* Source Code
* Changelog
* Credits


Installation
============
 
General installation steps:
 
* Copy js_render_presets.py, js_render_presets_button.py and 
  js_render_presets.def to LightWave's plug-in folder.
* "Autoscan Plugins" in LightWave 3D 11.0 doesn't seem to pickup Python scripts
   so you will have to tell LightWave manually of their existence.
* locate the "Add Plugins" button in LightWave and manually add the two .py
  files.

After the plugin is added to LightWave, I'd recommend placing it in a convenient
spot in LightWave’s menu, so all you have to do is press the Render Presets 
button when you need to use it. 

 
Usage
=====

See http://www.artstorm.net/plugins/render-presets/ for usage instructions.


Source Code
===========
 
Download the source code:
 
https://github.com/artstorm/render-presets

You can get the latest development branch or any previous tagged version via git
clone or by exploring the repository directly in your browser.
 
 
Changelog
=========

* v2.0.1 - 15 Dec 2012
  * Fixed bug with presets being referenced instead of copied when duplicating.
* v2.0 - 23 Apr 2012
  * Rewrote the plugin in Python and deprecated the LScript version.
  * Added new settings introduced with LightWave 3D 11.0: Shading Samples, Light
    Samples, Camera Min/Max Samples.
  * Default values updated to reflect defaults in LightWave 3D 11.0.
* v1.3 - 28 Jun 2011
  * Fixed Issue 1: Line 430, attempt to access undeclared array selectedPreset.
    when running under LightWave 10.0 and 10.1.
  * Implemted Issue 2: Duplicate presets button.
  * Minor fixes for running the script uncompiled.
* v1.2 - 1 Jun 2010:
  * Added a [Grab] button on the Global Illum Panel to copy the current GI
    settings from the scene.
* v1.1 - 27 May 2010:
  * Fixed a bug that could cause a preset to be cleared when closing/opening
    the window.
  * Added a preset option for Camera Resolution Multiplier.
* v1.0 - 7 Mar 2010:
  * Release of version 1.0, first public release.

Credits
=======

* Johan Steen, http://www.artstorm.net/
  * Original author
