/* ******************************
 * Master Class LScript: Render Presets
 * Version: 1.1
 * Author: Johan Steen
 * Date: 27 May 2010
 * Description: Allow the user to define and apply different presets for render settings.
 *
 * http://www.artstorm.net/
 *
 * REVISIONS
 * Version 1.1 - 27 May 2010
 * - Fixed a bug that could cause a preset to be cleared when closing/opening the window.
 * - Added a preset option for Camera Resolution Multiplier.
 * - Made the script Open Source under the GPL 3.0 License.
 *
 * Version 1.0 - 7 Mar 2010
 * - Initial Release.
 * ****************************** */

@version 2.7
@warnings
@script master
@name "JS_RenderPresets"

// Main Variables
rp_version = "1.1";
rp_date = "27 May 2010";
presetsFile = getdir(SETTINGSDIR) + getsep() + "JS_RenderPresets.cfg";

// Variables for GUI gadgets
// -------------------------
ctlPresetList;
// Global Illum Panel
ctlGIEnabled;
ctlGIEnableRadiosity, ctlGIType, ctlGIInterpolated, ctlGIBlurBackground, ctlGIUseTransparency, ctlGIVolumetricRadiosity, ctlGIAmbientOcclusion, ctlGIDirectionalRays, ctlGIUseGradients, ctlGIUseBehindTest, ctlGIUseBumps;
ctlGIIntensity, ctlGIIndirectBounces, ctlGIRaysPerEvaluation, ctlGISecondaryBounceRays, ctlGIAngularTolerance, ctlGIMinimumPixelSpacing, ctlGIMaximumPixelSpacing, ctlGIMultiplier;
// Render Panel
ctlRNDEnabled;
ctlRNDRaytraceShadows, ctlRNDRaytraceReflection, ctlRNDRaytraceTransp, ctlRNDRaytraceRefraction, ctlRNDRaytraceOcclusion, ctlRNDDepthBufferAA, ctlRNDRenderLines;
ctlRNDRayRecursion, ctlRNDRayPrecision, ctlRNDRayCutoff;
// Backdrop Panel
ctlBDEnabled;
ctlBDBackdropColor, ctlBDGradientBackdrop, ctlBDZenithColor, ctlBDSkyColor, ctlBDSkySqueeze, ctlBDGroundSqueeze, ctlBDGroundColor, ctlBDNadirColor;
// Processing Panel
ctlPROCEnabled;
ctlPROCLimitDynamicRange, ctlPROCDitherIntensity;
// Camera Panel
ctlCAMEnabled;
ctlCAMAntialiasing, ctlCAMReconstruction, ctlCAMSamplingPattern, ctlCAMAdaptiveSampling, ctlCAMTreshold, ctlCAMOversample;
// Resolution Panel
ctlRESEnabled;
ctlRESMultiplier;
// Comment
ctlComment;

// Variables for the Presets and stored data
selPreset = nil;			// the currently selected preset
arrPresetList;				// The list with the Presets
arrPresetData;				// The Array that contains all the data for the presets
arrPresetLinks;				// Array that keeps track of which preset data which is connected to which name. ID = PresetData ID, Value = PresetList Name
arrPresetOptions = @ "Comment",
"GIPanelEnabled",
"EnableRadiosity", "RadiosityType", "RadiosityInterpolation", "BlurBackgroundRadiosity", "RadiosityTransparency", "VolumetricRadiosity", "RadiosityUseAmbient", "RadiosityDirectionalRays", "RadiosityUseGradients", "RadiosityUseBehindTest", "RadiosityUseBumps",
"RadiosityIntensity", "IndirectBounces", "RaysPerEvaluation", "RaysPerEvaluation2", "RadiosityTolerance", "RadiosityMinPixelSpacing", "RadiosityMaxPixelSpacing", "RadiosityMultiplier",
"RenderPanelEnabled",
"RayTraceShadows", "RayTraceReflection", "RayTraceTransparency", "RayTraceRefraction", "RayTraceOcclusion", "DepthBufferAA", "RenderLines",
"RayRecursionLimit", "RayPrecision", "RayCutoff",
"BackdropPanelEnabled",
"BackdropColor", "GradientBackdrop", "ZenithColor", "SkyColor", "SkySqueezeColor", "GroundSqueezeColor", "GroundColor", "NadirColor",
"ProcessingPanelEnabled",
"LimitDynamicRange", "DitherIntensity",
"CameraPanelEnabled",
"Antialiasing", "ReconstructionFilter", "NoiseSampler", "AdaptiveSampling", "AdaptiveThreshold", "Oversampling",
"ResolutionPanelEnabled", "ResolutionMultiplier"@;

//
// FUNCTIONS ALWAYS AVAILABLE IN MASTER CLASS PLUGINS
// ------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------
create
{
	// Loads the presets when the plugin starts
	loadPresets();
}

destroy
{
	// Saves the presets when the plugin exits
	savePresets();
}

flags
{
    // indicates the type of the Master script.  it can
    // be either SCENE or LAYOUT.  SCENE scripts will be
    // removed whenever the current scene is cleared or
    // replaced.  LAYOUT scripts persist until manually
    // removed.

    return(SCENE);
}

process: event, command
{
    // called for each event that occurs within the filter
    // you specified in flags()
}

load: what,io
{
    if(what == SCENEMODE)   // processing an ASCII scene file
    {
    }
}

save: what,io
{
    if(what == SCENEMODE)
    {
    }
}

options
{
    if(reqisopen())
        return;

	// Reset some initialization values
	selPreset = nil;

    reqbegin("Render Presets v" + rp_version);
	reqsize(510,420);
	
    //
    // List and main buttons
    // --------------------------------------------------------------------------------
    ctlPresetList = ctllistbox("Presets", 150,310,"ListSize","ListItem","ListEvent");	// label, width, height, count_udf, name_udf[, event_udf , [select_udf] ]
	
	// Main Buttons
    c1 = ctlbutton("New", 73, "onBtn_NewPreset");			// label, width, udf, arguments to udf:string
    c2 = ctlbutton("Save", 73, "onBtn_Save");
    c3 = ctlbutton("Rename", 73, "onBtn_Rename");
    c4 = ctlbutton("Delete", 73, "onBtn_DelPreset");
	c5 = ctlbutton("Up", 73, "onBtn_Sort", "1");
	c6 = ctlbutton("Down", 73, "onBtn_Sort", "0");
    c7 = ctlbutton("About", 73, "onBtn_About");
    c8 = ctlbutton("Apply", 73, "onBtn_Apply");
	
	ctlgroup(c1,c2,c3,c4,c5,c6,c7,c8);				// Group the buttons
	ctlposition(c2,77,0);							// Position the buttons
	ctlposition(c3,0,24);
	ctlposition(c4,77,24);
	ctlposition(c5,0,48);
	ctlposition(c6,77,48);
	ctlposition(c7,0,72);
	ctlposition(c8,77,72);
	
    //
    // The preset data GUI
    // --------------------------------------------------------------------------------
    ctlPresetTabs = ctltab("Global Illum","Render","Effects","Camera");
    ctlTabSep = ctlsep();
	
	ctlgroup(ctlPresetTabs,ctlTabSep);
	ctlposition(ctlPresetTabs,190,6,250,19);				// x,y,width,height
	ctlposition(ctlTabSep,0,19,320);


	// Global Illum Tab
	// ----------------
	ctlGIEnabled			= ctlcheckbox("Enable in Preset", false);
	ctlGIEnableRadiosity	= ctlcheckbox("Enable Radiosity", false);
    ctlGIType				= ctlpopup("Type", 3, @ "Backdrop Only", "Monte Carlo", "Final Gather" @);  // array or string UDF; the list of items, or a UDF which returns a string or array
	ctlGIInterpolated		= ctlcheckbox("Interpolated", true);
	ctlGIBlurBackground		= ctlcheckbox("Blur Background", true);
	ctlGIUseTransparency	= ctlcheckbox("Use Transparency", false);
	ctlGIVolumetricRadiosity= ctlcheckbox("Volumetric Radiosity", false);
	ctlGIAmbientOcclusion	= ctlcheckbox("Ambient Occlusion", false);
	ctlGIDirectionalRays	= ctlcheckbox("Directional Rays", false);
	ctlGIUseGradients		= ctlcheckbox("Use Gradients", false);
	ctlGIUseBehindTest		= ctlcheckbox("Use Behind Test", true);
	ctlGIUseBumps			= ctlcheckbox("Use Bumps", false);
	//
	ctlGIIntensity			= ctlpercent("Intensity", 1);
	ctlGIIndirectBounces	= ctlminislider("Indirect Bounces", 1, 1, 64);					// label, default, min, max
	ctlGIRaysPerEvaluation	= ctlminislider("Rays Per Evaluation", 64, 1, 2147483647);		// label, default, min, max
	ctlGISecondaryBounceRays= ctlminislider("Secondary Bounce Rays", 16, 0, 2147483647);
	ctlGIAngularTolerance	= ctlangle("Angular Tolerance", 45);
	ctlGIMinimumPixelSpacing= ctlnumber("Minimum Pixel Spacing", 4.0);
	ctlGIMaximumPixelSpacing= ctlnumber("Maximum Pixel Spacing", 100.0);
	ctlGIMultiplier			= ctlpercent("Multiplier", 1);
	
	ctlgroup(ctlGIEnableRadiosity, ctlGIType, ctlGIInterpolated, ctlGIBlurBackground, ctlGIUseTransparency, ctlGIVolumetricRadiosity, ctlGIAmbientOcclusion, ctlGIDirectionalRays, ctlGIUseGradients, ctlGIUseBehindTest, ctlGIUseBumps);
	ctlgroup(ctlGIEnableRadiosity, ctlGIIntensity, ctlGIIndirectBounces, ctlGIRaysPerEvaluation, ctlGISecondaryBounceRays, ctlGIAngularTolerance, ctlGIMinimumPixelSpacing, ctlGIMaximumPixelSpacing, ctlGIMultiplier);
	ctlposition(ctlGIEnabled,				190,	34,		150);
	//
	ctlposition(ctlGIEnableRadiosity,		190,	64,		120);
	ctlposition(ctlGIType,					126,	0);
	ctlposition(ctlGIInterpolated,			0,		22,		150);
	ctlposition(ctlGIBlurBackground,		156,	22,		150);
	ctlposition(ctlGIUseTransparency,		0,		44,		150);
	ctlposition(ctlGIVolumetricRadiosity,	156,	44,		150);
	ctlposition(ctlGIAmbientOcclusion,		0,		66,		150);
	ctlposition(ctlGIDirectionalRays,		156,	66,		150);
	ctlposition(ctlGIUseGradients,			0,		88,		150);
	ctlposition(ctlGIUseBehindTest,			156,	88,		150);
	ctlposition(ctlGIUseBumps,				156,	110,	150);
	//
	ctlposition(ctlGIIntensity,				111,	132,	173);
	ctlposition(ctlGIIndirectBounces,		70,		154,	214);
	ctlposition(ctlGIRaysPerEvaluation,		54,		176,	230);
	ctlposition(ctlGISecondaryBounceRays,	32,		198,	252);
	ctlposition(ctlGIAngularTolerance,		63,		220,	221);
	ctlposition(ctlGIMinimumPixelSpacing,	42,		242,	242);
	ctlposition(ctlGIMaximumPixelSpacing,	39,		264,	245);
	ctlposition(ctlGIMultiplier,			109,	288,	175);
	//
	ctlactive(ctlGIEnabled, "toggleOptions", ctlGIEnableRadiosity, ctlGIType, ctlGIInterpolated, ctlGIBlurBackground, ctlGIUseTransparency, ctlGIVolumetricRadiosity, ctlGIAmbientOcclusion, ctlGIDirectionalRays, ctlGIUseGradients, ctlGIUseBehindTest, ctlGIUseBumps);
	ctlactive(ctlGIEnabled, "toggleOptions", ctlGIIntensity, ctlGIIndirectBounces, ctlGIRaysPerEvaluation, ctlGISecondaryBounceRays, ctlGIAngularTolerance, ctlGIMinimumPixelSpacing, ctlGIMaximumPixelSpacing, ctlGIMultiplier);

	// Render Tab
	// ----------
	ctlRNDEnabled			= ctlcheckbox("Enable in Preset", false);
	ctlRNDRaytraceShadows	= ctlcheckbox("Raytrace Shadows", false);
	ctlRNDRaytraceReflection= ctlcheckbox("Raytrace Reflection", false);
	ctlRNDRaytraceTransp	= ctlcheckbox("Raytrace Transparency", false);
	ctlRNDRaytraceRefraction= ctlcheckbox("Raytrace Refraction", false);
	ctlRNDRaytraceOcclusion	= ctlcheckbox("Raytrace Occlusion", false);
	ctlRNDDepthBufferAA		= ctlcheckbox("Depth Buffer AA", false);
	ctlRNDRenderLines		= ctlcheckbox("Render Lines", true);
	ctlRNDRayRecursion		= ctlinteger("Ray Recursion Limit", 16);
	ctlRNDRayPrecision		= ctlnumber("Ray Precision", 6.0);
	ctlRNDRayCutoff			= ctlnumber("Ray Cutoff", 0.01);

	ctlgroup(ctlRNDRaytraceShadows, ctlRNDRaytraceReflection, ctlRNDRaytraceTransp, ctlRNDRaytraceRefraction, ctlRNDRaytraceOcclusion, ctlRNDDepthBufferAA, ctlRNDRenderLines);
	ctlgroup(ctlRNDRaytraceShadows, ctlRNDRayRecursion, ctlRNDRayPrecision, ctlRNDRayCutoff);
	ctlposition(ctlRNDEnabled,				190,	34,		150);
	//
	ctlposition(ctlRNDRaytraceShadows,		190,	64,		150);
	ctlposition(ctlRNDRaytraceReflection,	156,	0,		150);
	ctlposition(ctlRNDRaytraceTransp,		0,		22,		150);
	ctlposition(ctlRNDRaytraceRefraction,	156,	22,		150);
	ctlposition(ctlRNDRaytraceOcclusion,	0,		44,		150);
	ctlposition(ctlRNDDepthBufferAA,		156,	44,		150);
	ctlposition(ctlRNDRenderLines,			0,		66,		150);
	//
	ctlposition(ctlRNDRayRecursion,			56,		88,		250);
	ctlposition(ctlRNDRayPrecision,			85,		110,	221);
	ctlposition(ctlRNDRayCutoff,			100,	132,	206);
	//
	ctlactive(ctlRNDEnabled, "toggleOptions", ctlRNDRaytraceShadows, ctlRNDRaytraceReflection, ctlRNDRaytraceTransp, ctlRNDRaytraceRefraction, ctlRNDRaytraceOcclusion, ctlRNDDepthBufferAA, ctlRNDRenderLines);
	ctlactive(ctlRNDEnabled, "toggleOptions", ctlRNDRayRecursion, ctlRNDRayPrecision, ctlRNDRayCutoff);
	

	// Effects Tab
	// ------------
	ctlBDEnabled			= ctlcheckbox("Enable in Preset", false);
	ctlBDBackdropColor		= ctlcolor("Backdrop Color", 0);
	ctlBDGradientBackdrop	= ctlcheckbox("Gradient Backdrop", false);
	ctlBDZenithColor		= ctlcolor("Zenith Color", <0,40,80>);
	ctlBDSkyColor			= ctlcolor("Sky Color", <120,180,240>);
	ctlBDSkySqueeze			= ctlnumber("Sky Squeeze", 2.0);
	ctlBDGroundSqueeze		= ctlnumber("Ground Squeeze", 2.0);
	ctlBDGroundColor		= ctlcolor("Ground Color", <50,40,30>);
	ctlBDNadirColor			= ctlcolor("Nadir Color", <100,80,60>);

	ctlgroup(ctlBDBackdropColor, ctlBDGradientBackdrop, ctlBDZenithColor, ctlBDSkyColor, ctlBDSkySqueeze, ctlBDGroundSqueeze, ctlBDGroundColor, ctlBDNadirColor);
	ctlposition(ctlBDEnabled,				190,	34,		150);
	//
	ctlposition(ctlBDBackdropColor,		258,	64,		238);
	ctlposition(ctlBDGradientBackdrop,	-68,	22,		150);
	ctlposition(ctlBDZenithColor,		16,		44,		222);
	ctlposition(ctlBDSkyColor,			28,		66,		210);
	ctlposition(ctlBDSkySqueeze,		19,		88,		219);
	ctlposition(ctlBDGroundSqueeze,		2,		110,	236);
	ctlposition(ctlBDGroundColor,		11,		132,	227);
	ctlposition(ctlBDNadirColor,		21,		154,	217);
	//
	ctlactive(ctlBDEnabled, "toggleOptions", ctlBDBackdropColor, ctlBDGradientBackdrop, ctlBDZenithColor, ctlBDSkyColor, ctlBDSkySqueeze, ctlBDGroundSqueeze, ctlBDGroundColor, ctlBDNadirColor);

	// processing section
	ctlEffectSep = ctlsep();
	ctlPROCEnabled			= ctlcheckbox("Enable in Preset", false);
	ctlPROCLimitDynamicRange= ctlcheckbox("Limit Dynamic Range", false);
    ctlPROCDitherIntensity	= ctlpopup("Dither Intensity", 2, @"Off", "Normal", "2 x Normal", "4 x Normal"@);  //array or string UDF; the list of items, or a UDF which returns a string or array
	
	ctlposition(ctlEffectSep,			190,	250,	320);
	ctlposition(ctlPROCEnabled,			190,	260,	150);
	ctlposition(ctlPROCLimitDynamicRange, 346,	290,	150);
	ctlposition(ctlPROCDitherIntensity,	270,	312,	226);
	//
	ctlactive(ctlPROCEnabled, "toggleOptions", ctlPROCLimitDynamicRange, ctlPROCDitherIntensity);
	

	// Camera Tab
	// ------------
	ctlCAMEnabled			= ctlcheckbox("Enable in Preset", false);
	ctlCAMAntialiasing		= ctlminislider("Antialiasing", 1, 1, 10000);
    ctlCAMReconstruction	= ctlpopup("Reconstruction Filter", 1, @"Classic", "Box", "Box (Sharp)", "Box (Soft)", "Gaussian", "Gaussian (Sharp)", "Gaussian (Soft)", "Mitchell", "Mitchell (Sharp)", "Mitchell (Soft)", "Lanczos", "Lanczos (Sharp)", "Lanczos (Soft)"@);  //array or string UDF; the list of items, or a UDF which returns a string or array
    ctlCAMSamplingPattern	= ctlpopup("Sampling Pattern", 2, @"Blue Noise", "Fixed", "Classic"@);  //array or string UDF; the list of items, or a UDF which returns a string or array
	ctlCAMAdaptiveSampling	= ctlcheckbox("Adaptive Sampling", false);
	ctlCAMTreshold			= ctlnumber("Treshold", 0.1);
	ctlCAMOversample		= ctlnumber("Oversample", 0.0);
	
	ctlposition(ctlCAMEnabled,			190,	34,		150);
	ctlposition(ctlCAMAntialiasing,		287,	64,		187);
	ctlposition(ctlCAMReconstruction,	243,	86,		253);
	ctlposition(ctlCAMSamplingPattern,	260,	108,	236);
	ctlposition(ctlCAMAdaptiveSampling,	346,	130,	150);
	ctlposition(ctlCAMTreshold,			299,	152,	197);
	ctlposition(ctlCAMOversample,		284,	174,	212);
	//
	ctlactive(ctlCAMEnabled, "toggleOptions", ctlCAMAntialiasing, ctlCAMReconstruction, ctlCAMSamplingPattern, ctlCAMAdaptiveSampling, ctlCAMTreshold, ctlCAMOversample);
	
	// resolution section
	ctlRESSep = ctlsep();
	ctlRESEnabled			= ctlcheckbox("Enable in Preset", false);
    ctlRESMultiplier		= ctlpopup("Multiplier", 3, @"25 %", "50 %", "100 %", "200 %", "400 %"@);  //array or string UDF; the list of items, or a UDF which returns a string or array

	ctlposition(ctlRESSep,				190,	206,	320);
	ctlposition(ctlRESEnabled,			190,	216,	150);
	ctlposition(ctlRESMultiplier,		299,	246,	197);
	
	ctlactive(ctlRESEnabled, "toggleOptions", ctlRESMultiplier);
	
	
	// The pages for the tabs
	// ----------------------
	ctlpage(1,ctlGIEnabled, ctlGIEnableRadiosity, ctlGIType, ctlGIInterpolated, ctlGIBlurBackground, ctlGIUseTransparency, ctlGIVolumetricRadiosity, ctlGIAmbientOcclusion, ctlGIDirectionalRays, ctlGIUseGradients, ctlGIUseBehindTest, ctlGIUseBumps);
	ctlpage(1,ctlGIIntensity, ctlGIIndirectBounces, ctlGIRaysPerEvaluation, ctlGISecondaryBounceRays, ctlGIAngularTolerance, ctlGIMinimumPixelSpacing, ctlGIMaximumPixelSpacing, ctlGIMultiplier);
	ctlpage(2,ctlRNDEnabled, ctlRNDRaytraceShadows, ctlRNDRaytraceReflection, ctlRNDRaytraceTransp, ctlRNDRaytraceRefraction, ctlRNDRaytraceOcclusion, ctlRNDDepthBufferAA, ctlRNDRenderLines);
	ctlpage(2,ctlRNDRayRecursion, ctlRNDRayPrecision, ctlRNDRayCutoff);
	ctlpage(3,ctlBDEnabled, ctlBDBackdropColor, ctlBDGradientBackdrop, ctlBDZenithColor, ctlBDSkyColor, ctlBDSkySqueeze, ctlBDGroundSqueeze, ctlBDGroundColor, ctlBDNadirColor);
	ctlpage(3,ctlEffectSep, ctlPROCEnabled, ctlPROCLimitDynamicRange, ctlPROCDitherIntensity);
	ctlpage(4,ctlCAMEnabled, ctlCAMAntialiasing, ctlCAMReconstruction, ctlCAMSamplingPattern, ctlCAMAdaptiveSampling, ctlCAMTreshold, ctlCAMOversample);
	ctlpage(4,ctlRESSep, ctlRESEnabled, ctlRESMultiplier);
	
	// Comment Field
    ctlCommSep = ctlsep();
	ctlComment = ctlstring("Comment", "", 262);
	ctlposition(ctlCommSep,190,382,320);
	ctlposition(ctlComment,190,392);

    // Make the requester non modal.
	reqopen();
}

// Updating if the option box is active or not
toggleOptions: value
{
    return(value);
}


//
// FUNCTIONS TO HANDLE LIST EVENTS
// ------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------

// UDF To get the count of items in the list (count_idf)
ListSize
{
    return(arrPresetList.count());
}

// UDF to get a listbox item (name_udf)
ListItem: index
{
    return(arrPresetList[index]);
}

// UDF to run when an item is selected
ListEvent: selectedPreset
{
	// Update the previous selected preset's settings in the array
	if (selPreset != nil)
		savePresetToArray(selPreset);

	// Refresh the Panel with the newly selected preset's settings
	val = selectedPreset[1].asInt();
	refreshPDataPanels(val);
	// Update the var with the newly selected preset
	selPreset = arrPresetList[val].asStr();
}


//
// FUNCTIONS TO HANDLE THE MAIN BUTTONS
// ------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------
/*
 * Adds a New Preset
 *
 * @returns     Nothing
 */
onBtn_NewPreset
{
	// Update the previous selected preset's settings in the array
	if (selPreset != nil)
		savePresetToArray(selPreset);
	// Create a unique new name
	counter = 1;
	newName = "Preset " + counter;
	while (arrPresetList.contains(newName) == true) {
		counter++;
		newName = "Preset " + counter;
	}
	// Add it to the Preset List
	arrPresetList += newName;
	// Add it to the PresetID List
	arrPresetLinks += newName;
	// Get the PresetData ID
	pDataID = getPresetDataID(newName);
	
    requpdate();
	
	// Select the new preset
	setvalue(ctlPresetList,arrPresetList.count());
	selPreset = newName;
	// Populate it with default values
	pDataPos = arrPresetOptions.indexOf("GIPanelEnabled");
	arrPresetData[pDataID][pDataPos] = false;
	pDataPos = arrPresetOptions.indexOf("RenderPanelEnabled");
	arrPresetData[pDataID][pDataPos] = false;
	pDataPos = arrPresetOptions.indexOf("BackdropPanelEnabled");
	arrPresetData[pDataID][pDataPos] = false;
	pDataPos = arrPresetOptions.indexOf("ProcessingPanelEnabled");
	arrPresetData[pDataID][pDataPos] = false;
	pDataPos = arrPresetOptions.indexOf("CameraPanelEnabled");
	arrPresetData[pDataID][pDataPos] = false;
	// Update the preset data panels
	refreshPDataPanels(arrPresetList.count());
}

/*
 * Saves the Current Preset
 *
 * @returns     Nothing
 */
onBtn_Save
{
	// Update the selected preset's settings in the array
	if (selPreset != nil)
		savePresetToArray(selPreset);
		// Update the presets to the disk
		savePresets();
		// Notify the user
		infoWindow("Saved", "Presets saved.", 200);
}

/*
 * Renames the Current Preset
 *
 * @returns     Nothing
 */
onBtn_Rename
{
	// Get the array of selections
	selections = getvalue(ctlPresetList);
	// Check that one, and only one preset is selected
	if (selections.count() == 1) {
		selection = selections[1].asInt();
		oldName = arrPresetList[selection];
		reqbegin("Rename Preset");
		reqsize(300,60);
		c0 = ctlstring("Name:", oldName, 254);

		return if !reqpost();
		// Process the rename request
		newName = getvalue(c0);
		
		// If name hasn't changed, dont do anything
		if (newName != oldName) {
			// If the new name is at least one character, do the rename
			if (newName.size() > 0) {
				// Check so name doesn't already exist
				if (arrPresetList.contains(newName) != true) {
					// Set the new name
					arrPresetList[selection] = newName;
					// Update the name in the PresetID links
					pID = getPresetDataID(oldName);
					arrPresetLinks[pID] = newName;
					// Update the currently selected preset
					selPreset = newName;
				} else {
					renError = 1;
				}
			} else {
				renError = 2;
			}
		}
		reqend();
		requpdate();
	
		// If name was empty
		switch (renError) {
			case 1:
				infoWindow("Error", "The name already exists.", 300);
			break;
			case 2:
				infoWindow("Error", "Name must consist of at least on character.", 300);
			break;
		}
	} else {
		// Handle errors
		if (selections.count() < 1)
			infoWindow("Error", "You need to select a preset to rename.", 300);
		else
			infoWindow("Error", "You can only rename one preset at a time.", 300);
	}
}

/*
 * Deletes the Current Preset
 *
 * @returns     Nothing
 */
onBtn_DelPreset
{
	// Get the array of selections
	selections = getvalue(ctlPresetList);
	// Check that one, and only one preset is selected
	if (selections.count() == 1) {
		selection = selections[1].asInt();

		// Confirm that the user is sure
		reqbegin("Confirm Delete");
		reqsize(300,70);
		c0 = ctltext("","Deleting " + arrPresetList[selection] + ". Are you sure?");
		ctlposition(c0,10,12);
		return if !reqpost();

		// Remove the Presets Data from the Array
		pDataID = getPresetDataID(arrPresetList[selection]);
		presetSize = arrPresetData[pDataID].size();
		for (i = 1; i <= presetSize; i++) {
			arrPresetData[pDataID][i] = nil;
		}
		
		// Remove the Preset from the Preset List
		arrPresetList[selection] = nil;
		arrPresetList.pack();
		arrPresetList.trunc();
		
		requpdate();
		if (arrPresetList.count() == 0) {
			// If all presets are deleted
			setvalue(ctlPresetList,nil);
			arrPresetList = nil;
			selPreset = nil;
		} else {
			// Else set the next item in the list to be selected
			if (selection > arrPresetList.count())
				newSel = selection - 1;
			else
				newSel = selection;
			setvalue(ctlPresetList,newSel);
			// Update the preset data panels
			refreshPDataPanels(newSel);
			// Update the currently selected preset
			selPreset = arrPresetList[newSel].asStr();
		}
	} else {
		// Handle errors
		if (selections.count() < 1)
			infoWindow("Error", "You need to select a preset to delete.", 300);
		else
			infoWindow("Error", "You can only delete one preset at a time.", 300);
	}
}

/*
 * The sort buttons
 * @direction	1 = up, 0= down
 *
 * @returns     Nothing
 */
onBtn_Sort: direction {
	// Get the array of selections
	selections = getvalue(ctlPresetList);
	// Check that one, and only one preset is selected
	if (selections.count() == 1) {
		currentSel = selections[1].asInt();
		listLength = arrPresetList.count().asInt();
		// Update preset's settings in the array
		savePresetToArray(selPreset);
		switch(direction) {
			// Move Down
			case 0:
				// Perform the move if it's not already at the bottom of the list
				if (currentSel < listLength) {
					// Build a temp array with the new order
					for (i = 1; i <= listLength; i++) {
						if (i == (currentSel + 1)) {
							tempArr[i] = arrPresetList[i - 1];
						}
						if (i == currentSel) {
							tempArr[i] = arrPresetList[i + 1];
						}
						if (i != currentSel && i != (currentSel + 1)) {
							tempArr[i] = arrPresetList[i];
						}
					}
					// Copy the temp array into the real array
					arrPresetList = tempArr;
					requpdate();
					setvalue(ctlPresetList,(currentSel + 1));
					val = currentSel + 1;
					refreshPDataPanels(val);
				}
			break;
			// Move Up
			case 1:
				// Perform the move if it's not already at the top of the list
				if (currentSel > 1) {
					// Build a temp array with the new order
					for (i = 1; i <= listLength; i++) {
						if (i == (currentSel - 1)) {
							tempArr[i] = arrPresetList[i + 1];
						}
						if (i == currentSel) {
							tempArr[i] = arrPresetList[i - 1];
						}
						if (i != currentSel && i != (currentSel - 1)) {
							tempArr[i] = arrPresetList[i];
						}
					}
					// Copy the temp array into the real array
					arrPresetList = tempArr;
					requpdate();
					setvalue(ctlPresetList,(currentSel - 1));
					val = currentSel - 1 ;
					refreshPDataPanels(val);
				}
			break;
		}
	} else {
		// Handle errors
		if (selections.count() < 1)
			infoWindow("Error", "You need to select a preset to move.", 300);
		else
			infoWindow("Error", "You can only move one preset at a time.", 300);
	}
}

/*
 * The About button
 *
 * @returns     Nothing
 */
onBtn_About {
		reqbegin("About Render Presets");
		reqsize(300,174);

		ctlLogo = ctlimage("E:/Coding/LightWave/Classic/RenderPresets/trunk/AboutLogo.tga");
		ctlposition(ctlLogo, 0,0);
		
		ctlText1 = ctltext("","Render Presets");
		ctlText2 = ctltext("","Version: " + rp_version);
		ctlText3 = ctltext("","Build Date: " + rp_date);
		ctlText4 = ctltext("","Copyright Johan Steen 2010, http://www.artstorm.net/");
		ctlposition(ctlText1, 10, 60);
		ctlposition(ctlText2, 10, 75);
		ctlposition(ctlText3, 10, 90);
		ctlposition(ctlText4, 10, 115);
		
		return if !reqpost();
		reqend();
}

/*
 * The Apply button
 *
 * @returns     Nothing
 */
onBtn_Apply
{
	// Get the array of selections
	selections = getvalue(ctlPresetList);
	// Check that one, and only one preset is selected
	if (selections.count() == 1) {
		selection = selections[1].asInt();
		// Update preset's settings in the array
		savePresetToArray(selPreset);
		// Get the preset name
		presetName = arrPresetList[selection].asStr();
		// Get the presetData ID
		pDataID = getPresetDataID(presetName);

/* SceneInfo.renderOpts */
// Add +1 to the values for the LScript array
// SHADOWTRACE 			(0)
// REFLECTTRACE 		(1)
// REFRACTTRACE 		(2)
// FIELDS 				(3)
// EVENFIELDS 			(4)
// MOTIONBLUR 			(5)
// DEPTHOFFIELD 		(6)
// LIMITEDREGION 		(7)
// PARTICLEBLUR 		(8)
// ENHANCEDAA 			(9)
// SAVEANIM 			(10)
// SAVERGB 				(11)
// SAVEALPHA 			(12)
// ZBUFFERAA 			(13)
// RTTRANSPARENCIES 	(14)
// RADIOSITY 			(15)
// CAUSTICS 			(16)
// OCCLUSION 			(17)
// RENDERLINES 			(18)
// INTERPOLATED 		(19)
// BLURBACKGROUND		(20)
// USETRANSPARENCY		(21)
// VOLUMETRICRADIOSITY  (22)
// USEAMBIENT           (23)
// DIRECTIONALRAYS      (24)
// LIMITDYNAMICRANGE    (25)
// CACHERADIOSITY       (26)
// USEGRADIENTS         (27)
// USEBEHINDTEST        (28)
// CAUSTICSCACHE        (29)
// EYECAMERA            (30)
// UNPREMULTIPLIEDALPHA (31)

		// GLOBAL ILLUM
		if (isPresetEnabled(pDataID, "GIPanelEnabled") == true) {
			ApplyPreset(pDataID, 1, "EnableRadiosity", 16);
			// Apply the rest of the GI Presets only if Radiosity is enabled.
			if (isPresetEnabled(pDataID, "EnableRadiosity") == true) {
				ApplyPreset(pDataID, 2, "RadiosityType",);
				ApplyPreset(pDataID, 1, "RadiosityInterpolation", 20);
				ApplyPreset(pDataID, 1, "BlurBackgroundRadiosity", 21);
				ApplyPreset(pDataID, 1, "RadiosityTransparency", 22);
				ApplyPreset(pDataID, 0, "VolumetricRadiosity",);
				ApplyPreset(pDataID, 0, "RadiosityUseAmbient",);
				ApplyPreset(pDataID, 0, "RadiosityDirectionalRays",);
				// Only apply these if Radiosity is interpolated
				if (isPresetEnabled(pDataID, "RadiosityInterpolation") == true) {
					ApplyPreset(pDataID, 0, "RadiosityUseGradients",);
					ApplyPreset(pDataID, 0, "RadiosityUseBehindTest",);
				}
				ApplyPreset(pDataID, 0, "RadiosityUseBumps",);
				//
				// Apply these if type is Backdrop Only
				if (isPresetEnabled(pDataID, "RadiosityType") == 1) {
					ApplyPreset(pDataID, 0, "RadiosityIntensity",);
					ApplyPreset(pDataID, 0, "RaysPerEvaluation",);
				}
				// Apply these if type is Monte Carlo
				if (isPresetEnabled(pDataID, "RadiosityType") == 2) {
					ApplyPreset(pDataID, 0, "RadiosityIntensity",);
					ApplyPreset(pDataID, 0, "IndirectBounces",);
					ApplyPreset(pDataID, 0, "RaysPerEvaluation",);
					// Secondary bounces if interpolated and more than one bounce
					if (isPresetEnabled(pDataID, "RadiosityInterpolation") == true && isPresetEnabled(pDataID, "IndirectBounces") > 1) {
						ApplyPreset(pDataID, 0, "RaysPerEvaluation2",);
					}
				}
				// Apply these if type is Final Gather
				if (isPresetEnabled(pDataID, "RadiosityType") == 3) {
					ApplyPreset(pDataID, 0, "RadiosityIntensity",);
					ApplyPreset(pDataID, 0, "IndirectBounces",);
					ApplyPreset(pDataID, 0, "RaysPerEvaluation",);
					// Secondary bounces if more than one bounce
					if (isPresetEnabled(pDataID, "IndirectBounces") > 1) {
						ApplyPreset(pDataID, 0, "RaysPerEvaluation2",);
					}
				}
				// Only Apply these if Interpolated is on, or Final Gather is enabled
				if (isPresetEnabled(pDataID, "RadiosityInterpolation") == true || isPresetEnabled(pDataID, "RadiosityType") == 3) {
					ApplyPreset(pDataID, 0, "RadiosityTolerance",);
					ApplyPreset(pDataID, 0, "RadiosityMinPixelSpacing",);
					ApplyPreset(pDataID, 0, "RadiosityMaxPixelSpacing",);
					ApplyPreset(pDataID, 0, "RadiosityMultiplier",);
				}
			}
		}
		
		// RENDER
		if (isPresetEnabled(pDataID, "RenderPanelEnabled") == true) {
			ApplyPreset(pDataID, 1, "RayTraceShadows", 1);
			ApplyPreset(pDataID, 1, "RayTraceReflection", 2);
			ApplyPreset(pDataID, 1, "RayTraceTransparency", 15);
			ApplyPreset(pDataID, 1, "RayTraceRefraction", 3);
			ApplyPreset(pDataID, 1, "RayTraceOcclusion", 18);
			ApplyPreset(pDataID, 0, "DepthBufferAA", 14);
			ApplyPreset(pDataID, 0, "RenderLines", 19);
			ApplyPreset(pDataID, 0, "RayRecursionLimit",);
			ApplyPreset(pDataID, 0, "RayPrecision",);
			ApplyPreset(pDataID, 0, "RayCutoff",);
		}
		
		// BACKDROP
		if (isPresetEnabled(pDataID, "BackdropPanelEnabled") == true) {
			if (isPresetEnabled(pDataID, "GradientBackdrop") == false) {
				// Disable Gradient Backdrop if enabled
				if (Scene().backdroptype == 2)
					GradientBackdrop();
				ApplyPreset(pDataID, 3, "BackdropColor",);
			} else {
				// Enable Gradient Backdrop if disabled
				if (Scene().backdroptype == 1)
					GradientBackdrop();
				ApplyPreset(pDataID, 3, "ZenithColor",);
				ApplyPreset(pDataID, 3, "SkyColor",);
				// These are only supported in 9.6.1 and above (build 1539 = 9.6)
				if (hostBuild() > 1539) {
					ApplyPreset(pDataID, 0, "SkySqueezeColor",);
					ApplyPreset(pDataID, 0, "GroundSqueezeColor",);
				}
				ApplyPreset(pDataID, 3, "GroundColor",);
				ApplyPreset(pDataID, 3, "NadirColor",);

			}
		}
		
		// PROCESSING
		if (isPresetEnabled(pDataID, "ProcessingPanelEnabled") == true) {
			ApplyPreset(pDataID, 1, "LimitDynamicRange", 26);
			ApplyPreset(pDataID, 2, "DitherIntensity",);
		}

		// CAMERA
		// Ask the user which camera to apply the preset to if multiple cameras
		if (isPresetEnabled(pDataID, "CameraPanelEnabled") == true || isPresetEnabled(pDataID, "ResolutionPanelEnabled") == true) {
			// Build an array of available cameras
			camera = Camera();
			while(camera) {
				camName += camera.name;
				camID += camera.id;
				camera = camera.next();
			}
			
			// If more than one camera, popup a selector so the user can select which camera to use
			if (camName.size() > 1) {
				reqbegin("Select Camera");
				reqsize(300,70);
				c0 = ctlpopup("Apply to Camera", 1, camName);
//				c1 = ctlcameraitems("Apply to Camera");				// Optimize using this instead of the array, if time permits

				ctlposition(c0,10,12);
				if (!reqpost()) {
					cancelCam = true;
				} else {
					cID = getvalue(c0);
					SelectItem(camID[cID]);
					reqend();
				}
			}
		}
		
		// Apply the camera Antialiasing Presets
		if (isPresetEnabled(pDataID, "CameraPanelEnabled") == true) {
			if (!cancelCam) {
				ApplyPreset(pDataID, 0, "Antialiasing",);
				ApplyPreset(pDataID, 2, "ReconstructionFilter",);
				ApplyPreset(pDataID, 2, "NoiseSampler",);
				if (isPresetEnabled(pDataID, "AdaptiveSampling") == true) {
					if (Scene().adaptivesampling == 0)
						ApplyPreset(pDataID, 0, "AdaptiveSampling",);
					ApplyPreset(pDataID, 0, "AdaptiveThreshold",);
					ApplyPreset(pDataID, 0, "Oversampling",);
				} else {
					if (Scene().adaptivesampling == 1)
						ApplyPreset(pDataID, 0, "AdaptiveSampling",);
				}
			}
		}

		// Apply the camera Resolution Presets
		if (isPresetEnabled(pDataID, "ResolutionPanelEnabled") == true) {
			if (!cancelCam) {
				ApplyPreset(pDataID, 4, "ResolutionMultiplier",);
			}
		}
		
		
		// Notify the user
		infoWindow("Applied", presetName + " applied.", 200);
	} else {
		// Handle errors
		if (selections.count() < 1)
			infoWindow("Error", "You need to select a preset to apply.", 300);
		else
			infoWindow("Error", "You can only apply one preset at a time.", 300);
	}
}


//
// FUNCTION TO APPLY THE PRESET TO THE SCENE
// ------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------
/*
 * Applies a preset to the scene
 *
 * @pDataID			The current Preset data ID
 * @mode			The mode to apply with, 0 = normal command input, 1 = toggle only checkboxes, 2 = dropdown menues, 3 = colors, 4 = Resolution Converter
 * @presetOption	The preset option to apply
 * @rFlag			The render option flag for mode 1, to determine if the toggle only checkbox needs toggling
 *
 * @returns     Nothing
 */
ApplyPreset: pDataID, mode, presetOption, rFlag
{
	// Get the position of the option in the array
	pDataPos = arrPresetOptions.indexOf(presetOption);
	// Check so the data array contains the option
	if (pDataPos <= arrPresetData[pDataID].size().asInt() ) {
		// Check so the option has a value
		if (arrPresetData[pDataID][pDataPos] != nil) {
			val = arrPresetData[pDataID][pDataPos];
			// Check which mode to apply the preset with
			switch (mode) {
				case 0:
					CommandInput(presetOption + " " + val);
				break;
				// Toggle only checkboxes
				case 1:
					if (val != Scene().renderopts[rFlag])
						CommandInput(presetOption);
				break;
				// Dropdown menus (need to subtract 1 from the value)
				case 2:
					val = val.asInt() - 1;
					CommandInput(presetOption + " " + val.asStr());
				break;
				// Color Values as vector
				case 3:
					val = val.asVec() / 255;
					CommandInput(presetOption + " " + val);
				break;
				// Resolution Converter
				case 4:
					if (val == 1) { val = 0.25; }
					if (val == 2) { val = 0.5; }
					if (val == 3) { val = 1; }
					if (val == 4) { val = 2; }
					if (val == 5) { val = 4; }
					CommandInput(presetOption + " " + val);
				break;
			}
		}
	}
}


//
// FUNCTIONS FOR THE PRESET DATA PANELS
// ------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------
savePresetToArray: presetName
{
	// Get the preset name
//	presetName = arrPresetList[selection].asStr();
	// Get the presetData ID
	pDataID = getPresetDataID(presetName);

	// COMMENT
	saveInPDArray(pDataID, "Comment", ctlComment);
	// GLOBAL ILLUM
	saveInPDArray(pDataID, "GIPanelEnabled", ctlGIEnabled);
	saveInPDArray(pDataID, "EnableRadiosity", ctlGIEnableRadiosity);
	saveInPDArray(pDataID, "RadiosityType", ctlGIType);
	saveInPDArray(pDataID, "RadiosityInterpolation", ctlGIInterpolated);
	saveInPDArray(pDataID, "BlurBackgroundRadiosity", ctlGIBlurBackground);
	saveInPDArray(pDataID, "RadiosityTransparency", ctlGIUseTransparency);
	saveInPDArray(pDataID, "VolumetricRadiosity", ctlGIVolumetricRadiosity);
	saveInPDArray(pDataID, "RadiosityUseAmbient", ctlGIAmbientOcclusion);
	saveInPDArray(pDataID, "RadiosityDirectionalRays", ctlGIDirectionalRays);
	saveInPDArray(pDataID, "RadiosityUseGradients", ctlGIUseGradients);
	saveInPDArray(pDataID, "RadiosityUseBehindTest", ctlGIUseBehindTest);
	saveInPDArray(pDataID, "RadiosityUseBumps", ctlGIUseBumps);
	//
	saveInPDArray(pDataID, "RadiosityIntensity", ctlGIIntensity);
	saveInPDArray(pDataID, "IndirectBounces", ctlGIIndirectBounces);
	saveInPDArray(pDataID, "RaysPerEvaluation", ctlGIRaysPerEvaluation);
	saveInPDArray(pDataID, "RaysPerEvaluation2", ctlGISecondaryBounceRays);
	saveInPDArray(pDataID, "RadiosityTolerance", ctlGIAngularTolerance);
	saveInPDArray(pDataID, "RadiosityMinPixelSpacing", ctlGIMinimumPixelSpacing);
	saveInPDArray(pDataID, "RadiosityMaxPixelSpacing", ctlGIMaximumPixelSpacing);
	saveInPDArray(pDataID, "RadiosityMultiplier", ctlGIMultiplier);
	
	// RENDER
	saveInPDArray(pDataID, "RenderPanelEnabled", ctlRNDEnabled);
	saveInPDArray(pDataID, "RayTraceShadows", ctlRNDRaytraceShadows);
	saveInPDArray(pDataID, "RayTraceReflection", ctlRNDRaytraceReflection);
	saveInPDArray(pDataID, "RayTraceTransparency", ctlRNDRaytraceTransp);
	saveInPDArray(pDataID, "RayTraceRefraction", ctlRNDRaytraceRefraction);
	saveInPDArray(pDataID, "RayTraceOcclusion", ctlRNDRaytraceOcclusion);
	saveInPDArray(pDataID, "DepthBufferAA", ctlRNDDepthBufferAA);
	saveInPDArray(pDataID, "RenderLines", ctlRNDRenderLines);
	saveInPDArray(pDataID, "RayRecursionLimit", ctlRNDRayRecursion);
	saveInPDArray(pDataID, "RayPrecision", ctlRNDRayPrecision);
	saveInPDArray(pDataID, "RayCutoff", ctlRNDRayCutoff);
	
	// BACKDROP
	saveInPDArray(pDataID, "BackdropPanelEnabled", ctlBDEnabled);
	saveInPDArray(pDataID, "BackdropColor", ctlBDBackdropColor);
	saveInPDArray(pDataID, "GradientBackdrop", ctlBDGradientBackdrop);
	saveInPDArray(pDataID, "ZenithColor", ctlBDZenithColor);
	saveInPDArray(pDataID, "SkyColor", ctlBDSkyColor);
	saveInPDArray(pDataID, "SkySqueezeColor", ctlBDSkySqueeze);
	saveInPDArray(pDataID, "GroundSqueezeColor", ctlBDGroundSqueeze);
	saveInPDArray(pDataID, "GroundColor", ctlBDGroundColor);
	saveInPDArray(pDataID, "NadirColor", ctlBDNadirColor);
	
	// PROCESSING
	saveInPDArray(pDataID, "ProcessingPanelEnabled", ctlPROCEnabled);
	saveInPDArray(pDataID, "LimitDynamicRange", ctlPROCLimitDynamicRange);
	saveInPDArray(pDataID, "DitherIntensity", ctlPROCDitherIntensity);

	// CAMERA
	saveInPDArray(pDataID, "CameraPanelEnabled", ctlCAMEnabled);
	saveInPDArray(pDataID, "Antialiasing", ctlCAMAntialiasing);
	saveInPDArray(pDataID, "ReconstructionFilter", ctlCAMReconstruction);
	saveInPDArray(pDataID, "NoiseSampler", ctlCAMSamplingPattern);
	saveInPDArray(pDataID, "AdaptiveSampling", ctlCAMAdaptiveSampling);
	saveInPDArray(pDataID, "AdaptiveThreshold", ctlCAMTreshold);
	saveInPDArray(pDataID, "Oversampling", ctlCAMOversample);

	// RESOLUTION
	saveInPDArray(pDataID, "ResolutionPanelEnabled", ctlRESEnabled);
	saveInPDArray(pDataID, "ResolutionMultiplier", ctlRESMultiplier);
}

/*
 * Refreshes the data in the panel
 *
 * @returns     Nothing
 */
refreshPDataPanels: selectedPreset
{
	// Get the preset name
	presetName = arrPresetList[selectedPreset].asStr();
	// Get the presetData ID
	pDataID = getPresetDataID(presetName);
	
	// COMMENT
	setGUIValue(pDataID, "Comment", ctlComment, "");

	// GLOBAL ILLUM
	setGUIValue(pDataID, "GIPanelEnabled", ctlGIEnabled, false);
	setGUIValue(pDataID, "EnableRadiosity", ctlGIEnableRadiosity, false);
	setGUIValue(pDataID, "RadiosityType", ctlGIType, 3);
	setGUIValue(pDataID, "RadiosityInterpolation", ctlGIInterpolated, true);
	setGUIValue(pDataID, "BlurBackgroundRadiosity", ctlGIBlurBackground, true);
	setGUIValue(pDataID, "RadiosityTransparency", ctlGIUseTransparency, false);
	setGUIValue(pDataID, "VolumetricRadiosity", ctlGIVolumetricRadiosity, false);
	setGUIValue(pDataID, "RadiosityUseAmbient", ctlGIAmbientOcclusion, false);
	setGUIValue(pDataID, "RadiosityDirectionalRays", ctlGIDirectionalRays, false);
	setGUIValue(pDataID, "RadiosityUseGradients", ctlGIUseGradients, false);
	setGUIValue(pDataID, "RadiosityUseBehindTest", ctlGIUseBehindTest, true);
	setGUIValue(pDataID, "RadiosityUseBumps", ctlGIUseBumps, false);
	//
	setGUIValue(pDataID, "RadiosityIntensity", ctlGIIntensity, 1);
	setGUIValue(pDataID, "IndirectBounces", ctlGIIndirectBounces, 1);
	setGUIValue(pDataID, "RaysPerEvaluation", ctlGIRaysPerEvaluation, 64);
	setGUIValue(pDataID, "RaysPerEvaluation2", ctlGISecondaryBounceRays, 16);
	setGUIValue(pDataID, "RadiosityTolerance", ctlGIAngularTolerance, 45);
	setGUIValue(pDataID, "RadiosityMinPixelSpacing", ctlGIMinimumPixelSpacing, 4.0);
	setGUIValue(pDataID, "RadiosityMaxPixelSpacing", ctlGIMaximumPixelSpacing, 100.0);
	setGUIValue(pDataID, "RadiosityMultiplier", ctlGIMultiplier, 1);
	
	// RENDER
	setGUIValue(pDataID, "RenderPanelEnabled", ctlRNDEnabled, false);
	setGUIValue(pDataID, "RayTraceShadows", ctlRNDRaytraceShadows, false);
	setGUIValue(pDataID, "RayTraceReflection", ctlRNDRaytraceReflection, false);
	setGUIValue(pDataID, "RayTraceTransparency", ctlRNDRaytraceTransp, false);
	setGUIValue(pDataID, "RayTraceRefraction", ctlRNDRaytraceRefraction, false);
	setGUIValue(pDataID, "RayTraceOcclusion", ctlRNDRaytraceOcclusion, false);
	setGUIValue(pDataID, "DepthBufferAA", ctlRNDDepthBufferAA, false);
	setGUIValue(pDataID, "RenderLines", ctlRNDRenderLines, true);
	setGUIValue(pDataID, "RayRecursionLimit", ctlRNDRayRecursion, 16);
	setGUIValue(pDataID, "RayPrecision", ctlRNDRayPrecision, 6.0);
	setGUIValue(pDataID, "RayCutoff", ctlRNDRayCutoff, 0.01);
	
	// BACKDROP
	setGUIValue(pDataID, "BackdropPanelEnabled", ctlBDEnabled, false);
	setGUIValue(pDataID, "BackdropColor", ctlBDBackdropColor, <0, 0, 0> / 255);
	setGUIValue(pDataID, "GradientBackdrop", ctlBDGradientBackdrop, false);
	setGUIValue(pDataID, "ZenithColor", ctlBDZenithColor, <255, 255, 255> / 255);
	setGUIValue(pDataID, "SkyColor", ctlBDSkyColor, <120,180,240> / 255);
	setGUIValue(pDataID, "SkySqueezeColor", ctlBDSkySqueeze, 2.0);
	setGUIValue(pDataID, "GroundSqueezeColor", ctlBDGroundSqueeze, 2.0);
	setGUIValue(pDataID, "GroundColor", ctlBDGroundColor, <50,40,30> / 255);
	setGUIValue(pDataID, "NadirColor", ctlBDNadirColor, <100,80,60> / 255);

	// PROCESSING
	setGUIValue(pDataID, "ProcessingPanelEnabled", ctlPROCEnabled, false);
	setGUIValue(pDataID, "LimitDynamicRange", ctlPROCLimitDynamicRange, false);
	setGUIValue(pDataID, "DitherIntensity", ctlPROCDitherIntensity, 2);

	// CAMERA
	setGUIValue(pDataID, "CameraPanelEnabled", ctlCAMEnabled, false);
	setGUIValue(pDataID, "Antialiasing", ctlCAMAntialiasing, 1);
	setGUIValue(pDataID, "ReconstructionFilter", ctlCAMReconstruction, 1);
	setGUIValue(pDataID, "NoiseSampler", ctlCAMSamplingPattern, 2);
	setGUIValue(pDataID, "AdaptiveSampling", ctlCAMAdaptiveSampling, false);
	setGUIValue(pDataID, "AdaptiveThreshold", ctlCAMTreshold, 0.1);
	setGUIValue(pDataID, "Oversampling", ctlCAMOversample, 0.0);

	// RESOLUTION
	setGUIValue(pDataID, "ResolutionPanelEnabled", ctlRESEnabled, false);
	setGUIValue(pDataID, "ResolutionMultiplier", ctlRESMultiplier, 3);
}

/*
 * Sets a new value in the submitted panel controller
 *
 * @pDataID			The current Preset data ID
 * @presetOption	The preset option to get the data from
 * @ctlGUI			The GUI controller to update
 * @defaultValue	Default value for the controller
 *
 * @returns     Nothing
 */

setGUIValue: pDataID, presetOption, ctlGUI, defaultValue
{
	// Get the position of the option in the array
	pDataPos = arrPresetOptions.indexOf(presetOption);
	// Check so the data array contains the option
	if (pDataPos <= arrPresetData[pDataID].size().asInt() ) {
		// Check so the option has a value
		if (arrPresetData[pDataID][pDataPos] != nil)
			if (defaultValue.isVec() == false) {
				val = arrPresetData[pDataID][pDataPos];
			} else {
				val = arrPresetData[pDataID][pDataPos].asVec() / 255;
			}
		else
			val = defaultValue;
	} else {
		val = defaultValue;
	}
	setvalue(ctlGUI,val);	
}

/*
 * Saves a new/updated value in the Preset Data array
 *
 * @pDataID			The current Preset data ID
 * @presetOption	The preset option to save the data to
 * @ctlGUI			The GUI controller to get the data from
 *
 * @returns     Nothing
 */
saveInPDArray: pDataID, presetOption, ctlGUI {
	// Get the position of the option in the array
	pDataPos = arrPresetOptions.indexOf(presetOption);
	arrPresetData[pDataID][pDataPos] = getvalue(ctlGUI);
}

/*
 * Checks if a Preset Panel is enabled
 *
 * @pDataID			The current Preset data ID
 * @presetOption	The preset option to check
 *
 * @returns     	true / false
 */
isPresetEnabled: pDataID, presetOption {
	// Get the position of the option in the array
	pDataPos = arrPresetOptions.indexOf(presetOption);
	// Check so the data array contains the option
	if (pDataPos <= arrPresetData[pDataID].size().asInt() ) {
		// Check so the option has a value
		if (arrPresetData[pDataID][pDataPos] != nil)
			val = arrPresetData[pDataID][pDataPos];
		else
			val = false;
	} else {
		val = false;
	}
	return val;
}


//
// FUNCTIONS TO LOAD/SAVE THE PRESET FILE
// ------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------
/*
** Function to load the presets
**
** @returns     Nothing
*/
loadPresets {
    // Open file
    loadCfg = File(presetsFile,"r");
	presetFound = false;				// Keeps track if a new preset name has been found
	presetLoading = false;				// Keeps track if the { beginning of a preset has been found

    // Check if file was opened
    if(loadCfg)
    {
        // Loop through file until end
        while( !loadCfg.eof() )
        {
			arrParsedLine = loadCfg.parse("\t");
			
			// Found a new preset name
			if (arrParsedLine[1] == "Preset" && presetFound == false && presetLoading == false) {
				arrPresetList += arrParsedLine[2];
				presetFound = true;
				// Create the link to connect the PresetData with the PresetName
				arrPresetLinks[arrPresetList.count()] = arrParsedLine[2];
			}
			
			// Found the beginning of a preset chunk
			else if (arrParsedLine[1] == "{" && presetFound == true && presetLoading == false) {
				presetLoading = true;
			}
			
			// Found the end of a preset chunk
			else if (arrParsedLine[1] == "}" && presetFound == true && presetLoading == true) {
				presetFound = false;
				presetLoading = false;
			}
			
			// Loading preset data
			else if (presetFound == true && presetLoading == true) {
				// Get preset position in the array
				presetPos = arrPresetOptions.indexOf(arrParsedLine[1]);
				if (presetPos != 0) {
					arrPresetData[arrPresetList.count()][presetPos]= arrParsedLine[2];
				}
			}
		}
        // Close file
        loadCfg.close();
    }
}

/*
** Functions to save the presets
**
** @returns     Nothing
*/
savePresets {
    // Open file
    saveCfg = File(presetsFile,"w");

    // Check if the file was opened
    if(saveCfg)
    {
		for (i = 1; i <= arrPresetList.count(); i++) {
			saveCfg.writeln ( "Preset" + "\t" + arrPresetList[i] );
			saveCfg.writeln ( "{" );
			// Get the presetData ID
			pDataID = getPresetDataID(arrPresetList[i]);
			// Write the data for the preset
			if (arrPresetData != nil) {
				presetSize = arrPresetData[pDataID].size();
				for (j = 1; j <= presetSize; j++) {
					if (arrPresetData[pDataID][j] != nil) {
						saveCfg.writeln ( arrPresetOptions[j] + "\t" + arrPresetData[pDataID][j] );
					}
				}
			}
			saveCfg.writeln ( "}" );
		}
    }
    // Close file
    saveCfg.close();
}


//
// COMMON FUNCTIONS
// ------------------------------------------------------------------------------------------
// ------------------------------------------------------------------------------------------
/*
 * Function to get a Preset Data ID
 * @presetName	The Name of the Preset to retrieve the ID for
 * @returns     The ID
 */
getPresetDataID: presetName {
	pDataID = arrPresetLinks.indexOf(presetName);
	return pDataID;
}

/*
 * Function to popup an information window
 * @title		The title of the window
 * @message		The message displayed to the user
 * @winWidth	The width of the window
 * @returns     nothing
 */
infoWindow: title, message, winWidth {
		reqbegin(title);
		reqsize(winWidth,70);
		
		c0 = ctltext("",message);
		ctlposition(c0,10,12);

		return if !reqpost();
		reqend();
}
