/*------------------------------------------------------------------------------
 Generic Class LScript: Render Presets Button
 Version: 1.0
 Author: Johan Steen
 Author URI: http://www.artstorm.net/
 Date: 7 Mar 2010
 Description: Companion to Render Presets, adds a command to LightWave to map
              Render Presets to a menu item or keyboard shortcut.

 Copyright (c) 2010, Johan Steen
 All Rights Reserved.
 Use is subject to license terms.
------------------------------------------------------------------------------*/

@version 2.3
@script generic
@name "JS_RenderPresetsBtn"

releaseMode = true;			// If false, the button closes the plugin when opened and removes it. If false, it reopens the panel

generic
{
	pluginAdded = false;
	stat = Scene().server(SERVER_MASTER_H);

	// Loop through the Master Plugins and see if Render Presets is added
	for(i=1;i<=stat.size();i++)
	{
		if(stat[i] == "JS_RenderPresets")
		{
			pluginAdded = true;
			break;
		}
	}
	
	if (releaseMode == true) {
		// release mode
		// If not added, add it to the master plugins
		if(!pluginAdded)
			CommandInput("ApplyServer MasterHandler JS_RenderPresets");
		// activate it
		activate = string("EditServer MasterHandler ",i);
		CommandInput(activate);
	} else {
		// debug mode
		if(!pluginAdded) {
			// If not added, add it to the master plugins, and activate it
			CommandInput("ApplyServer MasterHandler JS_RenderPresets");
			activate = string("EditServer MasterHandler ",i);
			CommandInput(activate);
		} else {
			// If already added, remove it from the scene.
			deactivate = string("RemoveServer MasterHandler ",i);
			CommandInput(deactivate);
		}
	}
}