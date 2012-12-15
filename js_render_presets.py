""" Render Presets

Enables the user to create a library of presets for render settings to apply and
quickly switch between.
"""

__author__     = 'Johan Steen'
__copyright__  = 'Copyright (C) 2010-2012, Johan Steen'
__credits__    = ''
__license__    = 'New BSD License'
__version__    = '2.0'
__maintainer__ = 'Johan Steen'
__email__      = 'http://www.artstorm.net/contact/'
__status__     = 'Development'
__lwver__      = '11'

# ------------------------------------------------------------------------------
# Import Modules
# ------------------------------------------------------------------------------
import os
import sys
import json
import math
import lwsdk
import webbrowser
import collections


# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
DEFINITIONS_FILE = 'js_render_presets.def'
PRESETS_FILE = 'js_render_presets.cfg'


# ------------------------------------------------------------------------------
# Master Plugin Class
# ------------------------------------------------------------------------------
class RenderPresetsMaster(lwsdk.IMaster):

    def __init__(self, context):
        super(RenderPresetsMaster, self).__init__()

        # Init Panel variables
        self._ui = lwsdk.LWPanels()
        self._panel = None
        self._controls = None

        # Track selected preset
        # (as get_int() won't return -1 for deselections, we track it ourselves)
        self._selection = -1

        # Load user defined presets
        Presets.load()

    def __del__(self):
        """ Destructor

        When the plugin is removed from the Master Plugins list I'd would have
        liked to perform some cleaning up here, like closing the window and
        destroying all objects.

        As of LigthWave 3D v11.0 the desctructor is not called if any events
        or callbacks are defined in the class, which makes it not possible to
        know that the plugin has been removed, and do the cleaning up.
        """
        # Here we'd like to call panel.close() if window is opened and then set
        # all objects to None (ui, panel, controllers). As I use events and
        # callbacks in the class and therefore the destructor not being called,
        # we just keep a pass here and hope that this will be fixed in a future
        # LightWave version.
        pass

    def inter_ui(self):
        # Only create the window and controllers if it does not already exist,
        # to prevent the user opening multiple Render Presets window from the
        # same plugin instance.
        if not self._panel:
            if not self._ui:
                self._ui = lwsdk.LWPanels()

            # Define the Panel
            self._panel = self._ui.create('Render Presets v' + __version__)
            self._panel.setw(500)
            self._panel.seth(420)
            self._panel.setmaxh(420)
            self._panel.set_close_callback(self.panel_close_callback)

            if self.create_controls():
                self._panel.open(lwsdk.PANF_NOBUTT)

        return lwsdk.AFUNC_OK

    # --------------------------------------------------------------------------
    # Callbacks
    # --------------------------------------------------------------------------
    def panel_close_callback(self, panel, data):
        """ If the panel is closed by the user, let's destroy all Panel assets
        so we have a clean slate to recreate all assets in the inter_ui() method
        if the user chooses to open this plugin instance again.
        """
        # We better make sure the presets are stored and saved
        self.store_preset()

        # Calling destroy() here, crashes LightWave (v11.0), so I have it
        # commented out, and relies on only setting the variables to None.
        # self._ui.destroy(self._panel)
        self._panel = None
        self._ui = None
        self._controls = None

        # Perhaps it would be better to remove the plugin completely when
        # closing the window? I keep that line here, commented out, during dev
        # until I've decided. If I keep it, I need to add a method to find the
        # actual index in the Master Plugins list.
        lwsdk.command('RemoveServer MasterHandler 1')

    def button_callback(self, id, user_data):
        """ Handle clicks on on main buttons in the Panel. """
        # Before perfoming any action, store and save the current selection.
        self.store_preset()
        # user_data contains the dictionary key of the pressed button.
        self._controls[user_data]['fn']()

    def tabs_callback(self, id, user_data):
        """ Handles tab switching in the preset setup. """
        # Before switching tab, store and save the current tab.
        self.store_preset()

        # Reference part of the definitions dictionary
        tabs = Presets.definitions['tabs']
        sel_tab = Presets.get_tab_name(self._controls[1].get_int())

        # Loop through tabs
        for tab in tabs:
            if sel_tab == tab:
                self.enable_controls(tabs[tab])
            else:
                self.erase_controls(tabs[tab])

        self.refresh_controls()

    def enable_in_preset_callback(self, id, user_data):
        """ Handle GUI updates with the section enabling buttons. """
        tabs = Presets.definitions['tabs']
        sel_tab = Presets.get_tab_name(self._controls[1].get_int())
        self.enable_controls(tabs[sel_tab])

    def about_url_callback(self, id, user_data):
        """ Handles callbacks from the buttons in the about window. """
        webbrowser.open_new_tab(self._urls[user_data])

    # Preset List Callbacks
    def preset_name_callback(self, control, userdata, row):
        return Presets.names[row]

    def preset_count_callback(self, control, userdata):
        return len(Presets.names)

    def preset_select_callback(self, control, user_data, row, selecting):
        # Before switchin preset, store and save the current selection.
        self.store_preset()
        # Globally track the selected row, as get_int() on the control doesn't
        # return a value to determine when nothing is selected in the list
        # row = -1 when noting is selected
        self._selection = row
        self.refresh_controls()

    # --------------------------------------------------------------------------
    # Custom Methods
    # --------------------------------------------------------------------------
    def create_controls(self):
        """ Creates the controls in the panel.

        Loads a file containing all definitions needed to populate the interface
        and associated commands.

        @return  False if definitions file failed to load
        """
        # Get the path to the definitions file. The same location as the script.
        script_file = os.path.realpath(__file__)
        dir_path = os.path.dirname(script_file)
        def_file = os.path.join(dir_path, DEFINITIONS_FILE)

        # Load the JSON data into an OrderedDict
        try:
            f = open(def_file, 'r')
            Presets.definitions = json.load( \
                f, object_pairs_hook=collections.OrderedDict)
            f.close()
        except:
            print >>sys.stderr, 'The file %s was not found.' % DEFINITIONS_FILE
            return False

        # Define Main controls
        self._controls = {
            0: {'ctl': None, 'lbl': 'List'},
            1: {'ctl': None, 'lbl': 'Tabs'},
            2: {'ctl': None, 'lbl': 'New',       'x': 4,    'w': None, 'col': 'l', 'fn': self.new},
            3: {'ctl': None, 'lbl': 'Save',      'x': 82,   'w': None, 'col': 'r', 'fn': self.save},
            4: {'ctl': None, 'lbl': 'Rename',    'x': None, 'w': None, 'col': 'l', 'fn': self.rename},
            5: {'ctl': None, 'lbl': 'Delete',    'x': None, 'w': None, 'col': 'r', 'fn': self.delete},
            6: {'ctl': None, 'lbl': 'Up',        'x': None, 'w': None, 'col': 'l', 'fn': self.up},
            7: {'ctl': None, 'lbl': 'Down',      'x': None, 'w': None, 'col': 'r', 'fn': self.down},
            8: {'ctl': None, 'lbl': 'Duplicate', 'x': None, 'w': None, 'col': 'l', 'fn': self.duplicate},
            9: {'ctl': None, 'lbl': 'About',     'x': None, 'w': None, 'col': 'r', 'fn': self.about},
           10: {'ctl': None, 'lbl': 'Apply',     'x': None, 'w': 150,  'col': 'l', 'fn': self.apply},
           11: {'ctl': None, 'lbl': 'Comment'}
        }

        # Setup the Preset List Controller
        self._controls[0] = self._panel.listbox_ctl('Presets', 150, 18, \
            self.preset_name_callback, self.preset_count_callback)
        self._controls[0].set_select(self.preset_select_callback)

        # Setup the controllers for the main buttons
        left_column = []
        right_column = []
        for key, val in self._controls.iteritems():
            # Skip the first two (list, tabs)
            if key < 2 or key > 10:
                continue

            # Default width
            w = 72 if val['w'] is None else val['w']

            val['ctl'] = self._panel.wbutton_ctl(val['lbl'], w)
            val['ctl'].set_event(self.button_callback, key)

            x = 0 if val['x'] is None else val['x']
            val['ctl'].move(x, 282)

            # Make two lists with the controllers to split in two columns.
            if val['col'] == 'l':
                left_column.append(val['ctl'])
            else:
                right_column.append(val['ctl'])

        # Align the controllers in columns
        self._panel.align_controls_vertical(left_column)
        self._panel.align_controls_vertical(right_column)

        # Create the tab controller
        # Reference part of the definitions dictionary
        tabline_ctl = self._panel.area_ctl('', 310, 0)
        tabline_ctl.move(180, 20)
        tabs = Presets.definitions['tabs']
        tab_names = []
        for key in tabs:
            tab_names.append(key.encode('utf-8'))
        self._controls[1] = self._panel.tabchoice_ctl('', tab_names)
        self._controls[1].set_event(self.tabs_callback)
        self._controls[1].move(180, 0)

        # Create the comments controller
        border_bottom_ctl = self._panel.border_ctl('', 310, 0)
        border_bottom_ctl.move(180, 380)
        self._controls[11]['ctl'] = self._panel.str_ctl('Comment', 50)
        self._controls[11]['ctl'].move(180, 390)

        # Setup the controllers for preset definitions
        enable = 0
        for tab in tabs:
            y = 30
            prev_col = ''
            del left_column[:]
            del right_column[:]

            # loop the sections
            for k, v in tabs[tab].iteritems():
                # Hard code the offsets for the sections. I'll probably remove
                # sections in a future update, so I take the quick way out now
                if tab == "Camera" and y > 30:
                    y = 240
                if tab == "Effects" and y > 30:
                    y = 260

                v['ctl'] = self._panel.bool_ctl('Enable in Preset')
                v['ctl'].set_w(150)
                v['ctl'].move(180, y)
                v['ctl'].set_event(self.enable_in_preset_callback, enable)
                y += 30

                if tab == 'Render':
                    v['ctl'].ghost()
                else:
                    v['ctl'].erase()

                # Loop controls in the sections
                for ctl in v['controls']:

                    ctl['enable'] = enable

                    ctl2 = getattr(self._panel, ctl['type'] + '_ctl')
                    if ctl['type'] in ['bool', 'int', 'float', 'angle', 'percent']:
                        ctl['ctl'] = ctl2(ctl['label'])
                        try:
                            width = ctl['width']
                        except:
                            width = 150
                        ctl['ctl'].set_w(width)

                    if ctl['type'] in ['wpopup']:
                        # Get rid of Unicode character (u')
                        items = [s.encode('utf-8') for s in ctl['items']]
                        ctl['ctl'] = ctl2(ctl['label'], items, 150)

                    if ctl['type'] in ['minirgb']:
                        ctl['ctl'] = ctl2(ctl['label'])
                        ctl['ctl'].set_ivec(200, 200, 200)

                    # Consolidate this with the one in refresh_controls into a function
                    if ctl['type'] in ['bool', 'int', 'wpopup']:
                        ctl['ctl'].set_int(ctl['default'])

                    if ctl['type'] in ['float', 'percent']:
                        ctl['ctl'].set_float(ctl['default'])

                    if ctl['type'] in ['minirgb']:
                        rgb = ctl['default']
                        ctl['ctl'].set_ivec(rgb[0], rgb[1], rgb[2])

                    if ctl['type'] in ['angle']:
                        rad = math.radians(ctl['default'])
                        ctl['ctl'].set_float(rad)

                    if ctl['column'] == 'right':
                        right_column.append(ctl['ctl'])
                        ctl['ctl'].move(360, y)
                        if ctl['type'] == 'minirgb':
                            ctl['ctl'].move(260, y)
                    else:
                        ctl['ctl'].move(180, y)
                        left_column.append(ctl['ctl'])

                    if ctl['column'] == prev_col:
                        y += 10

                    if ctl['column'] == 'right':
                        prev_col = 'right'
                    else:
                        prev_col = 'left'

                    if tab == 'Render':
                        ctl['ctl'].ghost()
                    else:
                        ctl['ctl'].erase()

                enable += 1
            # Align the controllers in columns
            if tab in ['Render', 'Global Illum']:
                self._panel.align_controls_vertical(left_column)
            self._panel.align_controls_vertical(right_column)

            # Move the controls back in X for a tighter layout
            if tab == 'Render':
                offset = 24
            elif tab == 'Global Illum':
                offset = 54
            elif tab == 'Camera':
                offset = 114
            elif tab == 'Effects':
                for k, v in tabs[tab].iteritems():
                    for ctl in v['controls']:
                        if ctl['type'] in ['minirgb']:
                            y = ctl['ctl'].y()
                            x = ctl['ctl'].x()
                            ctl['ctl'].move(x - 80, y)
                offset = 1

            # Tighten up the Y distances
            if tab in ['Render', 'Global Illum']:
                offset_y = 0
                for ctl in left_column:
                    y = ctl.y()
                    x = ctl.x()
                    ctl.move(x, y - offset_y)
                    offset_y += 5
            offset_y = 0
            for ctl in right_column:
                y = ctl.y()
                x = ctl.x()
                ctl.move(x - offset, y - offset_y)
                offset_y += 5
                # Hard code the offsets for the sections. I'll probably remove
                # sections in a future update, so I take the quick way out now
                if tab == 'Render' and offset_y == 15:
                    offset_y -= 25
                if tab == 'Camera' and offset_y == 35:
                    offset_y -= 50
                if tab == 'Effects' and offset_y == 40:
                    offset_y -= 50

        self.refresh_main_buttons()
        return True

    def enable_controls(self, tab):
        """ Enable controls in tab.

        @param  ref  tab  Pointer to the tab in the dict to enable controls in
        """
        # Loop sections
        for k, v in tab.iteritems():
            v['ctl'].render()
            v['ctl'].unghost()
            enable = v['ctl'].get_int()
            # Loop controls in section
            for ctl in v['controls']:
                ctl['ctl'].render()
                if enable:
                    ctl['ctl'].unghost()
                else:
                    ctl['ctl'].ghost()

    def erase_controls(self, tab):
        """ Erase controls in tab.

        @param  ref  tab  Pointer to the tab in the dict to erase controls in
        """
        # Loop sections
        for k, v in tab.iteritems():
            v['ctl'].erase()
            # Loop controls in section
            for ctl in v['controls']:
                ctl['ctl'].erase()

    def ghost_controls(self, tab):
        """ Ghost controls in tab.

        @param  ref  tab  Pointer to the tab in the dict to ghost controls in
        """
        # Loop sections
        for k, v in tab.iteritems():
            v['ctl'].ghost()
            # Loop controls in section
            for ctl in v['controls']:
                ctl['ctl'].ghost()

    def refresh_controls(self):
        """ Refresh GUI controls to reflect the current selected preset. """
        # Get name of selected preset and tab
        row = self._selection
        name = Presets.get_name(row)
        sel_tab = Presets.get_tab_name(self._controls[1].get_int())

        # Reference part of the definitions dictionary
        tabs = Presets.definitions['tabs']

        # If nothing is selected, ghost all controls in tab
        if name == False:
            self.ghost_controls(tabs[sel_tab])
            self.refresh_main_buttons()
            return

        # Get the selected presets dict to read settings from
        settings = Presets.user['presets'][name]

        # Loop tabs
        for tab in tabs:
            # Loop sections in tab
            for k, v in tabs[tab].iteritems():
                # Store setting if the section is enabled
                v['ctl'].set_int(settings[k])

                # Loop controls in section
                for ctl in v['controls']:
                    cmd = ctl['command']

                    # Consolidate this with the one in create_controls into a function

                    # Set settings depending on controller type
                    if ctl['type'] in ['bool', 'int', 'wpopup']:
                        ctl['ctl'].set_int(settings[cmd])
                    if ctl['type'] in ['float', 'percent']:
                        ctl['ctl'].set_float(settings[cmd])
                    if ctl['type'] in ['minirgb']:
                        rgb = settings[cmd]
                        ctl['ctl'].set_ivec(rgb[0], rgb[1], rgb[2])
                    if ctl['type'] in ['angle']:
                        rad = math.radians(settings[cmd])
                        ctl['ctl'].set_float(rad)

                if tab == sel_tab:
                    self.enable_controls(tabs[tab])

        self._controls[11]['ctl'].set_str(settings['comment'])
        self.refresh_main_buttons()

    def refresh_main_buttons(self):
        """ Handle ghost and unghost of main buttons depending on selection. """
        for k, v in self._controls.iteritems():
            # Controllers always unghosted (list, tabs, new, about)
            if k < 3 or k == 9:
                continue

            # When preset is selected, unghost everything (with exceptions)
            if self._selection >= 0:
                v['ctl'].unghost()
                # Ghost up if first preset selected
                if self._selection == 0 and k == 6:
                    v['ctl'].ghost()
                # Ghost down if last preset selected
                if self._selection == len(Presets.names) - 1 and k == 7:
                    v['ctl'].ghost()
                continue
            # Ghost the rest
            v['ctl'].ghost()

    def refresh_list(self, index):
        """ ll """
        self._controls[0].redraw()
        self._controls[0].set_int(index)
        self._selection = index
        self.refresh_controls()

    def store_preset(self):
        """ Copy selected preset settings from GUI to user dict. """
        # Get name of selected preset
        row = self._selection
        name = Presets.get_name(row)

        # Return if nothin selected
        if name == False:
            return

        # Reference part of the definitions dictionary
        tabs = Presets.definitions['tabs']

        # Loop tabs
        for tab in tabs:
            # Loop sections in tab
            for k, v in tabs[tab].iteritems():
                # Store setting if the section is enabled
                cmd = v['id']
                Presets.user['presets'][name][cmd] = v['ctl'].get_int()

                # Loop controls in section
                for ctl in v['controls']:
                    cmd = ctl['command']

                    # Store setting depending on controller type
                    if ctl['type'] in ['bool', 'int', 'wpopup']:
                        Presets.user['presets'][name][cmd] = ctl['ctl'].get_int()
                    if ctl['type'] in ['float', 'percent']:
                        Presets.user['presets'][name][cmd] = ctl['ctl'].get_float()
                    if ctl['type'] in ['minirgb']:
                        Presets.user['presets'][name][cmd] = ctl['ctl'].get_ivec()
                    if ctl['type'] in ['angle']:
                        deg = math.degrees(ctl['ctl'].get_float())
                        Presets.user['presets'][name][cmd] = deg

        Presets.user['presets'][name]['comment'] = self._controls[11]['ctl'].get_str()
        Presets.save()

    # --------------------------------------------------------------------------
    # Button Methods
    # --------------------------------------------------------------------------
    def new(self):
        """ Add new preset. """
        # Create a unique new name
        ctr = 1
        name = 'Preset %s' % ctr
        while name in Presets.names:
            ctr += 1
            name = 'Preset %s' % ctr

        # Add preset and select it
        if Presets.add(name) != False:
            idx = Presets.names.index(name)
            self.refresh_list(idx)

    def save(self):
        """ Force a presets save. """
        self.store_preset()
        Presets.save()

    def rename(self):
        """ Create a rename dialog. """
        row = self._selection
        name = Presets.get_name(row)
        if name == False:
            return

        new_name = lwsdk.LWMessageFuncs().askName('Rename Preset', 'Name', name)

        Presets.rename(row, new_name)
        self.refresh_list(row)

    def delete(self):
        """ Delete selected preset. """
        # Get selected row
        row = self._selection

        # Check so we have a selection, else return
        if row < 0:
            return

        # Confirm that the user is sure
        confirm = lwsdk.LWMessageFuncs().yesNo('Confirm Delete', \
            'Deleting preset "%s".' % Presets.get_name(row), 'Are you sure?')
        if confirm == False:
            return

        Presets.delete(row)

        # Refresh GUI and selection
        self.refresh_list(-1)

    def up(self):
        """ Move selection up the list. """
        # Get selected row
        row = self._selection

        # Check so we can move up, else return
        if row <= 0:
            return

        # move it up
        new_row = row - 1
        # delete old, and insert it on the new index
        Presets.names.insert(new_row, Presets.names.pop(row))

        # Refresh GUI and selection
        self.refresh_list(new_row)

    def down(self):
        """ Move selection down the list. """
        # Get selected row
        row = self._selection

        # Check so we can move down, else return
        if row == -1 or row >= (len(Presets.names) - 1):
            return

        # move it down
        new_row = row + 1
        # delete old, and insert it on the new row
        Presets.names.insert(new_row, Presets.names.pop(row))

        # Refresh GUI and selection
        self.refresh_list(new_row)

    def duplicate(self):
        """ Duplicate selected preset. """
        # Get selected row
        row = self._selection

        # Check so we have a selection, else return
        if row < 0:
            return

        Presets.duplicate(row)

        # Refresh GUI and selection
        self.refresh_list(row)

    def about(self):
        """ Display About window. """
        panel = self._ui.create('About Render Presets')
        panel.setw(200)
        panel.seth(180)

        # Create the controls
        auth_ctl = panel.text_ctl('Author:', [__author__])
        vers_ctl = panel.text_ctl('Version:', [__version__])
        copy_ctl = panel.text_ctl('', [__copyright__])
        info_ctl = panel.wbutton_ctl('Info >>', 80)
        supp_ctl = panel.wbutton_ctl('Support >>', 80)
        cont_ctl = panel.wbutton_ctl('Contact the Author >>', 170)

        # Position them
        auth_ctl.move(10, 0)
        vers_ctl.move(10, 20)
        copy_ctl.move(10, 40)
        info_ctl.move(18, 80)
        supp_ctl.move(108, 80)
        cont_ctl.move(18, 110)

        # Set URLs in a global list
        self._urls = [
        'http://www.artstorm.net/plugins/render-presets/',
        'https://github.com/artstorm/render-presets/issues',
        __email__
        ]

        # Set callbacks for the buttons
        info_ctl.set_event(self.about_url_callback, 0)
        supp_ctl.set_event(self.about_url_callback, 1)
        cont_ctl.set_event(self.about_url_callback, 2)

        if panel.open(lwsdk.PANF_BLOCKING) == 0:
            self._ui.destroy(panel)
            return

        self._ui.destroy(panel)

    def apply(self):
        """ Apply selected preset. """
        row = self._controls[0].get_int()
        name = Presets.get_name(row)

        # Reference part of the definitions dictionary
        tabs = Presets.definitions['tabs']
        # Get the selected presets dict to read settings from
        settings = Presets.user['presets'][name]

        # Loop tabs
        for tab in tabs:
            # Loop sections in tab
            for k, v in tabs[tab].iteritems():
                # If section is enabled, apply the commands in the section
                if settings[k] == True:

                    # Loop commands in section
                    for ctl in v['controls']:
                        # Create and set command line
                        val = settings[ctl['command']]

                        if self.gi_tab_logic(settings, ctl['command']) == False:
                            continue

                        if self.fx_tab_logic(settings, ctl['command'], val) == False:
                            continue

                        if self.cam_tab_logic(settings, ctl['command']) == False:
                            continue

                        try:
                            mode = ctl['mode']
                        except:
                            mode = False

                        if ctl['type'] == 'percent':
                            val = val / 100

                        if ctl['type'] == 'minirgb':
                            val = '%(r)s %(g)s %(b)s' % \
                            {'r': val[0] / 255.0, \
                             'g': val[1] / 255.0, \
                             'b': val[2] / 255.0}

                        if ctl['command'] == 'ResolutionMultiplier':
                            # Resolution Converter
                            res = [0.25, 0.5, 1, 2, 4]
                            val = res[val]

                        # Handle buttons that just toggles their state which can
                        # not by command be set to a specific state.
                        if mode == 'toggle':
                            scene = lwsdk.LWSceneInfo()
                            render_flag = getattr(lwsdk, ctl['flag'])
                            if render_flag & scene.renderOpts > 0:
                                button_state = True
                            else:
                                button_state = False

                            if val != button_state:
                                lwsdk.command(ctl['command'])
                        else:
                            lwsdk.command(ctl['command'] + ' ' + str(val))

                        if ctl['command'] == 'EnableRadiosity' and val == False:
                            break

    # --------------------------------------------------------------------------
    # Apply Helpers
    # --------------------------------------------------------------------------
    def gi_tab_logic(self, settings, cmd):
        """ The controller logic for the Global Illum tab. """

        # If radiosity is not interpolated, don't apply these
        if settings['RadiosityInterpolation'] == False and cmd in \
        ['RadiosityUseGradients', 'RadiosityUseBehindTest']:
            return False

        # Don't apply these on Backdrop Only
        if settings['RadiosityType'] == 0 and cmd in \
        ['IndirectBounces', 'RaysPerEvaluation2']:
            return False

        # Don't apply these on Backdrop Only/Monte Carlo, no interpolation
        if settings['RadiosityInterpolation'] == False and \
        settings['RadiosityType'] in [0, 1] and cmd in \
        ['RaysPerEvaluation2', 'RadiosityTolerance', 'RadiosityMinPixelSpacing', 'RadiosityMaxPixelSpacing', 'RadiosityMultiplier']:
            return False

        return True

    def fx_tab_logic(self, settings, cmd, val):
        """ The controller logic for the Effects tab. """
        bd_info = lwsdk.LWBackdropInfo()

        # The Gradient Backdrop Button
        if cmd == 'GradientBackdrop':
            if bd_info.type == val:
                return False
        # Single color
        if settings['GradientBackdrop'] == 1 and cmd == 'BackdropColor':
            return False

        # Gradient color
        if settings['GradientBackdrop'] == 0 and cmd in \
        ['ZenithColor', 'SkyColor', 'GroundColor', 'NadirColor', 'SkySqueezeColor', 'GroundSqueezeColor']:
            return False

        return True

    def cam_tab_logic(self, settings, cmd):
        """ The controller logic for the Camera tab. """

        # Adaptive Sampling
        scene = lwsdk.LWSceneInfo()
        if cmd == 'AdaptiveSampling':
            if scene.adaptiveSampling == settings[cmd]:
                return False

        # Threshold
        if settings['AdaptiveSampling'] == False and cmd in \
        ['MaxAntialiasing', 'AdaptiveThreshold']:
            return False

        return True


# ------------------------------------------------------------------------------
# Presets Class
# ------------------------------------------------------------------------------
class Presets:
    """ Handles storage, loading and saving of user defined presets. """
    # --------------------------------------------------------------------------
    # Static variables
    # --------------------------------------------------------------------------
    # Predefined definitions, and control references
    definitions = None
    # User defined Presets
    user = None
    # User defined Preset Names
    names = None

    # --------------------------------------------------------------------------
    # Methods
    # --------------------------------------------------------------------------
    @staticmethod
    def load():
        """ Loads the user presets into the class static variable """
        # Load the JSON data into an OrderedDict
        try:
            # f = open(Presets.file_path()+'ad', 'r')
            f = open(Presets.file_path(), 'r')
            Presets.user = json.load( \
                f, object_pairs_hook=collections.OrderedDict)
            f.close()
        except:
            Presets.user = {
            'version': __version__,
            'presets': {}
            }
            Presets.names = []

        Presets.names = []

        for s, v in Presets.user['presets'].iteritems():
            Presets.names.append(s.encode('utf-8'))

    @staticmethod
    def save():
        """ Saves the user presets to a json formatted file """
        # Recreate the presets dictionary, in the current order found in the
        # names list, to save user sorting.
        presets = {
            'version': __version__,
            'presets': collections.OrderedDict({})
        }
        for name in Presets.names:
            presets['presets'][name] = Presets.user['presets'][name]

        # Save the dict as json
        f = open(Presets.file_path(), 'w')
        json.dump(presets, f, indent=4)
        f.close()

    @staticmethod
    def file_path():
        """ @return Absolute path to the presets file """
        # Get path to LightWave's config folder, and join with the filename
        folder = lwsdk.LWDirInfoFunc(lwsdk.LWFTYPE_SETTING)
        file_path = os.path.join(folder, PRESETS_FILE)
        return file_path

    @staticmethod
    def add(name):
        """ Adds a new preset.

        @param   string  name  The name of the preset to add.
        @return  False if failed to add
        """
        # Check so we got a unique name
        if name in Presets.names:
            return False

        # Add the new preset to list of names and to definitions
        Presets.names.append(name)
        Presets.user['presets'][name] = {}

        # reference part of the definitions dictionary
        defaults = Presets.definitions['tabs']

        # Set the default values for the new preset
        for tab in defaults:
            for section in defaults[tab]:
                # Set default value for section bool ctl to false
                section_id = defaults[tab][section]['id']
                Presets.user['presets'][name][section_id] = 0

                for control in defaults[tab][section]['controls']:
                    # Set the default values from definitions for the controls.
                    # We treat the command as an ID for the controls.
                    cmd = control['command']
                    Presets.user['presets'][name][cmd] = control['default']

        Presets.user['presets'][name]['comment'] = ''
        Presets.save()

    @staticmethod
    def delete(row):
        """ Delete a preset.

        @param   int    row       The row in the list to rename

        @return  False if failed to delete
        """
        # Get name of preset to delete
        name = Presets.get_name(row)

        if name == False:
            return False

        # Remove from ordereddict and list of names
        del Presets.user['presets'][name]
        Presets.names.remove(name)

    @staticmethod
    def rename(row, new_name):
        """ Rename a preset.

        @param   int    row       The row in the list to rename
        @param   string new_name  The new name of the preset

        @return  False if failed to rename
        """
        # Get the old name
        old_name = Presets.get_name(row)

        # If the new name is the same as the old, silently return
        if old_name == new_name:
            return False

        # Check so we got a unique name, else return with an error message.
        if new_name in Presets.names:
            lwsdk.LWMessageFuncs().error('Name "%s" already exists.' % new_name, \
                'rename error')
            return False

        # Make a copy with the new name, and then delete the old name
        Presets.user['presets'][new_name] = Presets.user['presets'][old_name]
        del Presets.user['presets'][old_name]

        # Also update the list of names
        Presets.names.insert(row, new_name)
        Presets.names.remove(old_name)

    @staticmethod
    def duplicate(row):
        """ Duplicate a preset.

        @param   int    row       The row in the list to rename

        @return  False if failed to duplicate
        """
        if row < 0 or row >= len(Presets.names):
            return False

        # Get the old name
        src_name = Presets.get_name(row)

        # Generate the destination name
        dest_name = src_name + ' - Copy'
        ctr = 1
        while dest_name in Presets.names:
            ctr += 1
            dest_name = src_name + ' - Copy %s' % ctr

        # Copy the preset, and add the new name to the list of names
        Presets.user['presets'][dest_name] = Presets.user['presets'][src_name].copy()
        Presets.names.append(dest_name)

    # --------------------------------------------------------------------------
    # Helpers
    # --------------------------------------------------------------------------
    @staticmethod
    def get_name(row):
        """ Return the name, or False if the row doesn't exist.

        @param   int  row  The row in the list to retrieve

        @return  False if no name was found.
        """
        if row < 0 or row >= len(Presets.names):
            return False

        return Presets.names[row]

    @staticmethod
    def get_tab_name(index):
        """ Return the tab name, or False if the tab doesn't exist.

        @param   int  index  The index of the tab to retrieve

        @return  False if no name was found, else the name as string.
        """
        # Reference part of the definitions dictionary
        tabs = Presets.definitions['tabs']

        # Make a list of tab names
        names = []
        for tab in tabs:
            names.append(tab.encode('utf-8'))

        # Return False if index out of list scope
        if index < 0 or index >= len(names):
            return False

        return names[index]


# ------------------------------------------------------------------------------
# Register the Plugin
# ------------------------------------------------------------------------------
ServerTagInfo = [
    ('Render Presets', lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH)
]

ServerRecord = {
    lwsdk.MasterFactory('js_Render_Presets', RenderPresetsMaster): ServerTagInfo
}
