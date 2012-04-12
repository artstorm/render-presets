--------------------------------------------------------------------------------
 Render Presets - README

 Render Presets lets you manage a library of different common
 rendering related settings to quickly organize, apply or switch
 between them.

 Website:      http://www.artstorm.net/plugins/render-presets/
 Project:      http://code.google.com/p/js-lscripts/
 Feeds:        http://code.google.com/p/js-lscripts/feeds
 
 Contents:
 
 * Installation
 * Usage
 * Source Code
 * Changelog
 * Credits

--------------------------------------------------------------------------------
 Installation
 
 General installation steps:
 
 * Copy JS_RenderPresets.lsc and JS_RenderPresetsBtn.lsc to LightWave's
   plug-in folder.
 * If "Autoscan Plugins" is enabled, just restart LightWave and it's installed.
 * Else, locate the “Add Plugins” button in LightWave and add them manually.

 I’d recommend to add the plugin to a convenient spot in LightWave’s menu,
 so all you have to do is press the Render Presets button when you need to
 use it. 
 
--------------------------------------------------------------------------------
 Usage

 See http://www.artstorm.net/plugins/render-presets/ for usage instructions.

--------------------------------------------------------------------------------
 Source Code
 
 Download the source code:
 
   http://code.google.com/p/js-lightwave-lscripts/source/checkout

 You can check out the latest trunk or any previous tagged version via svn
 or explore the repository directly in your browser.
 
 Note that the default checkout path includes all my available LScripts, you
 might want to browse the repository first to get the path to the specific
 script's trunk or tag to download if you don't want to get them all.
 
--------------------------------------------------------------------------------

## Changelog

- v2.0 - xx XXX 2012
  - Rewrote the plugin in Python and deprecated the LScript version.
  - Added new settings introduced with LightWave 3D 11.0: Shading Samples, Light
    Samples, Camera Min/Max Samples.
  - Default values updated to reflect defaults in LightWave 3D 11.0.
- v1.3 - 28 Jun 2011
  - Fixed Issue 1: Line 430, attempt to access undeclared array selectedPreset.
    when running under LightWave 10.0 and 10.1.
  - Implemted Issue 2: Duplicate presets button.
  - Minor fixes for running the script uncompiled.
- v1.2 - 1 Jun 2010:
  - Added a [Grab] button on the Global Illum Panel to copy the current GI
    settings from the scene.
- v1.1 - 27 May 2010:
  - Fixed a bug that could cause a preset to be cleared when closing/opening
    the window.
  - Added a preset option for Camera Resolution Multiplier.
- v1.0 - 7 Mar 2010:
  - Release of version 1.0, first public release.

--------------------------------------------------------------------------------
 Credits

 Johan Steen, http://www.artstorm.net/
 * Original author
