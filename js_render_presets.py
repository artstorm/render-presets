""" Render Presets

Enables the user to create a library of presets for render settings to apply and
quickly switch between.
"""

__author__      = 'Johan Steen'
__copyright__   = 'Copyright (C) 2010-2012, Johan Steen'
__credits__     = ''
__license__     = 'New BSD License'
__version__     = '2.0'
__maintainer__  = 'Johan Steen'
__email__       = 'http://www.artstorm.net/contact/'
__status__      = 'Development'
__lwver__       = '11'

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
PRESETS_FILE     = 'js_render_presets.cfg'


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
            self._panel = self._ui.create('Render Presets v'+__version__)
            self._panel.setw(510)
            self._panel.seth(420)
            self._panel.setmaxh(420)
            # TMP height override, until control positions are in place
            self._panel.seth(520)
            self._panel.setmaxh(520)
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
        # We better make sure the presets are saved
        Presets.save()

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
        # user_data contains the dictionary key of the pressed button.
        self._controls[user_data]['fn']()


    def enable_in_preset_callback(self, id, user_data):
        # print 'enable'
        # print id.get_int()
        for t in self.lookup:
            t['ctl'].unghost()

    def about_url_callback(self, id, user_data):
        """ Handles callbacks from the buttons in the about window. """
        webbrowser.open_new_tab(self._urls[user_data])

    # Preset List Callbacks
    def preset_name_callback(self, control, userdata, row):
        return Presets.names[row]
    def preset_count_callback(self, control, userdata):
        return len(Presets.names)
    def preset_select_callback(self, control, user_data, row, selecting):
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
                f, object_pairs_hook = collections.OrderedDict)
            f.close()
        except:
            print >>sys.stderr, 'The file %s was not found.' % DEFINITIONS_FILE
            return False

        # Reference part of the definitions dictionary
        tabs = Presets.definitions['tabs']





        # Get rid of Unicode character (u')
        # tabs = [s.encode('utf-8') for s in data['tabs']]

        tab_names = []
        # for key, val in tabs.iteritems():
        for key in tabs:
            tab_names.append(key.encode('utf-8'))



        self._controls = {
            0: {'ctl': None},
            1: {'ctl': None},
            2: {'ctl': None, 'lbl': 'New',       'x': 4,    'w': None, 'col': 'l', 'fn': self.new},
            3: {'ctl': None, 'lbl': 'Save',      'x': 82,   'w': None, 'col': 'r', 'fn': self.save},
            4: {'ctl': None, 'lbl': 'Rename',    'x': None, 'w': None, 'col': 'l', 'fn': self.rename},
            5: {'ctl': None, 'lbl': 'Delete',    'x': None, 'w': None, 'col': 'r', 'fn': self.delete},
            6: {'ctl': None, 'lbl': 'Up',        'x': None, 'w': None, 'col': 'l', 'fn': self.up},
            7: {'ctl': None, 'lbl': 'Down',      'x': None, 'w': None, 'col': 'r', 'fn': self.down},
            8: {'ctl': None, 'lbl': 'Duplicate', 'x': None, 'w': None, 'col': 'l', 'fn': self.duplicate},
            9: {'ctl': None, 'lbl': 'About',     'x': None, 'w': None, 'col': 'r', 'fn': self.about},
           10: {'ctl': None, 'lbl': 'Apply',     'x': None, 'w': 150,  'col': 'l', 'fn': self.apply}
        }


        # TMP GUI Setup
        self._controls[0] = self._panel.listbox_ctl('Presets', 150, 18, \
            self.preset_name_callback, self.preset_count_callback)
        self._controls[0].set_select(self.preset_select_callback)



        left_column = []
        right_column = []

        for key, val in self._controls.iteritems():
            if key < 2:
                continue

            print key
            w = 72 if val['w'] is None else val['w']

            val['ctl'] = self._panel.wbutton_ctl(val['lbl'], w)
            val['ctl'].set_event(self.button_callback, key)


            x = 0 if val['x'] is None else val['x']
            val['ctl'].move(x, 282)

            if val['col'] == 'l':
                left_column.append(val['ctl'])
            else:
                right_column.append(val['ctl'])

        self._panel.align_controls_vertical(left_column)
        self._panel.align_controls_vertical(right_column)


        self._c2 = self._panel.tabchoice_ctl('Tabs', tab_names)
        self._c2.set_event(self.tabs_callback)
        self._c2.move(200,0)



        for tab in tabs:
            y = 40

            for k, v in tabs[tab].iteritems():
                v['ctl'] = self._panel.bool_ctl('enable')
                v['ctl'].set_w(200)
                v['ctl'].move(200,y)
                v['ctl'].set_event(self.enable_in_preset_callback, 0)
                self.lookup = v['ctl']
                y += 40

                if tab != 'Render':
                    v['ctl'].erase()

                for ctl in v['controls']:

                    ctl2 = getattr(self._panel, ctl['type']+'_ctl')
                    if ctl['type'] in ['bool', 'int', 'intro', 'float', 'angle', 'percent']:
                        ctl['ctl'] = ctl2(ctl['label'])
                        ctl['ctl'].set_w(200)

                    if ctl['type'] in ['wpopup']:
                        # Get rid of Unicode character (u')
                        items = [s.encode('utf-8') for s in ctl['items']]
                        ctl['ctl'] = ctl2(ctl['label'], items, 200)


                    # Consolidate this with the one in refresh_controls into a function
                    if ctl['type'] in ['bool', 'int', 'wpopup']:
                        ctl['ctl'].set_int(ctl['default'])

                    if ctl['type'] in ['float', 'percent']:
                        ctl['ctl'].set_float(ctl['default'])

                    if ctl['type'] in ['angle']:
                        rad = math.radians(ctl['default'])
                        # math.degrees(x)
                        ctl['ctl'].set_float(rad)

                    ctl['ctl'].move(200,y)
                    ctl['ctl'].ghost()
                    y += 20

                    if tab != 'Render':
                        ctl['ctl'].erase()


        self._tmp_tabs = tabs
        self._tmp_tab_names = tab_names

        return True





    def tabs_callback(self, id, user_data):
#        print 'You selected: %s' % temp_list[self._c2.get_int()]
#        print self._c2.get_int()
        tmp = self._c2.get_int()

        tabs = self._tmp_tabs
        tab_names = self._tmp_tab_names

        # Optimize below: erase in one loop. Don't erase the tab that's clicked.
        # Erase controllers on all tabs
        tmp_pan = tabs[tab_names[0]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].erase()
            for t in v['controls']:
                t['ctl'].erase()

        tmp_pan = tabs[tab_names[1]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].erase()
            for t in v['controls']:
                t['ctl'].erase()

        tmp_pan = tabs[tab_names[2]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].erase()
            for t in v['controls']:
                t['ctl'].erase()

        tmp_pan = tabs[tab_names[3]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].erase()
            for t in v['controls']:
                t['ctl'].erase()

        # Render the controls on the clicked tab
        tmp_pan = tabs[tab_names[tmp]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].render()
            for t in v['controls']:
                t['ctl'].render()


    def refresh_controls(self):

        # Reference part of the definitions dictionary
        tabs = Presets.definitions['tabs']

        # TODO: no preset selected and this is called?

        # Get selected preset index
        index = self._controls[0].get_int()

        #Tmp
        tab_names = self._tmp_tab_names

        # Get the selected presets settings
        settings = Presets.user['presets'][Presets.names[index]]


        tmp = tabs[tab_names[0]]
        for k, v in tmp.iteritems():
            # v['ctl'] = self._panel.bool_ctl('enable')
            # v['ctl'].set_w(200)
            # v['ctl'].move(200,y)
            # v['ctl'].set_event(self.enable_in_preset_callback, 0)
            # self.lookup = v['controls']
            # y += 40
            v['ctl'].set_int(settings[k])

            # for t in tmp[s]:
            for t in v['controls']:
                # t['control'] = self._panel.bool_ctl(t['label'])
                # if t['type'] == 'button':
                #     t['control'].set_int(t['default'])
                # t['control'].set_w(200)
                # t['control'].move(200,y)
                # t['control'].ghost()
                # y += 20
                # t['control'].set_int(1)

                # Consolidate this with the one in create_controls into a function
                if t['type'] == 'button':
                    t['ctl'].set_int(settings[t['command']])

                if t['type'] in ['bool', 'int']:
                    t['ctl'].set_int(settings[t['command']])

                if t['type'] in ['float']:
                    t['ctl'].set_float(settings[t['command']])



    # --------------------------------------------------------------------------
    # Button Methods
    # --------------------------------------------------------------------------
    def new(self):

        # TODO:
        # // Update the previous selected preset's settings in the array
        # if (selPreset != nil)
        #     savePresetToArray(selPreset);        
        # temp_list.append('new preset')
        # Presets.presets["presets"].append('new preset')

        # Create a unique new name
        ctr = 1
        name = 'Preset %s' % ctr
        while name in Presets.names:
            ctr += 1
            name = 'Preset %s' % ctr

        Presets.add(name)

        # TODO:
        # // Select the new preset
        # setvalue(ctlPresetList,arrPresetList.count());
        # selPreset = newName;



        # self.c1.redraw()
        self._controls[0].redraw()

        # Presets.save()

    def save(self):
        print self._controls[0].get_int()
        print self._controls[0].get_userdata()
        print 'save'
        Presets.save()

    def rename(self):
        """ Create a rename dialog. """
        # Get the name of the selected preset, or return if nothing selected
        row = self._selection
        name = Presets.get_name(row)
        if name == False:
            return

        panel = self._ui.create('Rename Preset')
        panel.setw(300)
        panel.seth(60)

        # Create the string field, and populate it with the current name.
        name_ctl = panel.str_ctl('Name', 50)
        name_ctl.set_str(name)

        if panel.open(lwsdk.PANF_BLOCKING | lwsdk.PANF_CANCEL) == 0:
            self._ui.destroy(panel)
            return

        Presets.rename(self._selection, name_ctl.get_str())
        self._controls[0].redraw()

        self._ui.destroy(panel)

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
        self._controls[0].set_int(-1)
        self._selection = -1
        self._controls[0].redraw()

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
        self._controls[0].set_int(new_row)
        self._selection = new_row
        self._controls[0].redraw()

    def down(self):
        """ Move selection down the list. """
        # Get selected row
        row = self._selection

        # Check so we can move down, else return
        if row == -1 or row >= (len(Presets.names)-1):
            return

        # move it down
        new_row = row + 1
        # delete old, and insert it on the new row
        Presets.names.insert(new_row, Presets.names.pop(row))

        # Refresh GUI and selection
        self._controls[0].set_int(new_row)
        self._selection = new_row
        self._controls[0].redraw()

    def duplicate(self):
        print 'duplicate'

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
        info_ctl.move(20, 80)
        supp_ctl.move(110, 80)
        cont_ctl.move(20, 110)

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
        print 'Apply selected: ' + str(self._controls[0].get_int())


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
    # TODO: Presets.name ska kanske vara en return funktion istallet? Sa jag ev kan anvanda dict:en (defs) for allt.
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
                f, object_pairs_hook = collections.OrderedDict)
            f.close()
        except:
            Presets.user = {
            'version': __version__,
            'presets': {}
            }
            Presets.names = []

        Presets.names = []

        for s, v in Presets.user['presets'].iteritems():
            print s
            Presets.names.append(s.encode('utf-8'))

        print Presets.user
        print Presets.names


    @staticmethod
    def save():
        """ Saves the user presets to a json formatted file """
        f = open(Presets.file_path(), 'w')
        json.dump(Presets.user, f, indent=4)
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




# ------------------------------------------------------------------------------
# Register the Plugin
# ------------------------------------------------------------------------------
ServerTagInfo = [
    ('Render Presets', lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH)
]

ServerRecord = { 
    lwsdk.MasterFactory('js_Render_Presets', RenderPresetsMaster) 
    : ServerTagInfo
}
