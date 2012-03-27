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
import lwsdk
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
            t['control'].unghost()



    # --------------------------------------------------------------------------
    # Custom Methods
    # --------------------------------------------------------------------------
    def create_controls(self):
        """ Creates the controls in the panel.

        Loads a file containing all definitions needed to populate the interface
        and associated commands.

        @return boolean False if definitions file failed to load, otherwise True
        """

        # Get the path to the definitions file. The same location as the script.
        script_file = os.path.realpath(__file__)
        dir_path = os.path.dirname(script_file)
        def_file = os.path.join(dir_path, DEFINITIONS_FILE)

        # Load the JSON data into an OrderedDict
        try:
            f = open(def_file, 'r')
            data = json.load(f, object_pairs_hook=collections.OrderedDict)
            f.close()
        except:
            print >>sys.stderr, 'The file %s was not found.' % DEFINITIONS_FILE
            return False

        # Get rid of Unicode character (u')
        tabs = data['tabs']
        # tabs = [s.encode('utf-8') for s in data['tabs']]

        tab_names = []
        for key, val in tabs.iteritems():
            tab_names.append(key.encode('utf-8'))


        # TMP GUI Setup
        self.c1 = self._panel.listbox_ctl('Presets', 150, 18, self.name_1d, self.count_1d)
        self.c1.set_select(self.single_select_event_func)


        self._controls = {
            0: {'ctl': None, 'lbl': 'New',       'x': 4,    'w': None, 'col': 'l', 'fn': self.new},
            1: {'ctl': None, 'lbl': 'Save',      'x': 82,   'w': None, 'col': 'r', 'fn': self.save},
            2: {'ctl': None, 'lbl': 'Rename',    'x': None, 'w': None, 'col': 'l', 'fn': self.rename},
            3: {'ctl': None, 'lbl': 'Delete',    'x': None, 'w': None, 'col': 'r', 'fn': self.delete},
            4: {'ctl': None, 'lbl': 'Up',        'x': None, 'w': None, 'col': 'l', 'fn': self.up},
            5: {'ctl': None, 'lbl': 'Down',      'x': None, 'w': None, 'col': 'r', 'fn': self.down},
            6: {'ctl': None, 'lbl': 'Duplicate', 'x': None, 'w': None, 'col': 'l', 'fn': self.duplicate},
            7: {'ctl': None, 'lbl': 'About',     'x': None, 'w': None, 'col': 'r', 'fn': self.about},
            8: {'ctl': None, 'lbl': 'Apply',     'x': None, 'w': 150,  'col': 'l', 'fn': self.apply}
        }

        left_column = []
        right_column = []

        for key, val in self._controls.iteritems():
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


        # print tab_names
        # print tab_names[0]
        # print tabs[tab_names[0]]

        # Optimize: Consolidate below into one loop
        tmp = tabs[tab_names[0]]
        y = 40
        for s, v in tmp.iteritems():
            # print 'HERE!'
            v['ctl'] = self._panel.bool_ctl('enable')
            v['ctl'].set_w(200)
            v['ctl'].move(200,y)
            v['ctl'].set_event(self.enable_in_preset_callback, 0)
            self.lookup = v['controls']
            y += 40

            # for t in tmp[s]:
            for t in v['controls']:
                t['control'] = self._panel.bool_ctl(t['label'])
                t['control'].set_w(200)
                t['control'].move(200,y)
                t['control'].ghost()
                y += 40

        # for s in tmp:
        #     # print s['label']
        #     # s['control'] = self._panel.bool_ctl(s['label'])
        #     s['control'] = self._panel.bool_ctl(s['label'])
        #     s['control'].set_w(200)
        #     s['control'].move(200,40)

        y = 40
        tmp = tabs[tab_names[1]]
        for s, v in tmp.iteritems():
        #     s['control'] = self._panel.bool_ctl(s['label'])
        #     s['control'].erase()
        #     s['control'].move(200,40)
            v['ctl'] = self._panel.bool_ctl('enable')
            v['ctl'].set_w(200)
            v['ctl'].move(200,y)
            v['ctl'].erase()
            y += 40

            for t in v['controls']:
                t['control'] = self._panel.bool_ctl(t['label'])
                t['control'].set_w(200)
                t['control'].move(200,y)
                y += 40
                t['control'].erase()

        y = 40
        tmp = tabs[tab_names[2]]
        for s, v in tmp.iteritems():
            v['ctl'] = self._panel.bool_ctl('enable')
            v['ctl'].set_w(200)
            v['ctl'].move(200,y)
            v['ctl'].erase()
            y += 40
        #     s['control'] = self._panel.bool_ctl(s['label'])
        #     s['control'].erase()
        #     s['control'].move(200,40)
            for t in v['controls']:
                t['control'] = self._panel.bool_ctl(t['label'])
                t['control'].set_w(200)
                t['control'].move(200,y)
                y += 40
                t['control'].erase()

        y = 40
        tmp = tabs[tab_names[3]]
        for s, v in tmp.iteritems():
            v['ctl'] = self._panel.bool_ctl('enable')
            v['ctl'].set_w(200)
            v['ctl'].move(200,y)
            v['ctl'].erase()
            y += 40
        #     s['control'] = self._panel.bool_ctl(s['label'])
        #     s['control'].erase()
        #     s['control'].move(200,40)
            for t in v['controls']:
                t['control'] = self._panel.bool_ctl(t['label'])
                t['control'].set_w(200)
                t['control'].move(200,y)
                y += 40
                t['control'].erase()



        self._tmp_tabs = tabs
        self._tmp_tab_names = tab_names

        # multiple line test
#        print('flag: afsasssssssssssssssssssssssssssssfasfafasfasfa' \
#              + str(self.tab1_c1.flags()) )
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
                t['control'].erase()

        tmp_pan = tabs[tab_names[1]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].erase()
            for t in v['controls']:
                t['control'].erase()

        tmp_pan = tabs[tab_names[2]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].erase()
            for t in v['controls']:
                t['control'].erase()

        tmp_pan = tabs[tab_names[3]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].erase()
            for t in v['controls']:
                t['control'].erase()

        # Render the controls on the clicked tab
        tmp_pan = tabs[tab_names[tmp]]
        for s, v in tmp_pan.iteritems():
            v['ctl'].render()
            for t in v['controls']:
                t['control'].render()


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


        self.c1.redraw()

        # Presets.save()

    def save(self):
        print 'save'
        Presets.save()

    def rename(self):
        print 'rename'

    def delete(self):
        print 'delete'
        Presets.names.remove('new preset')
        self.c1.redraw()

    def up(self):
        print 'up'
        # get the current index
        old_index = Presets.names.index('new preset')
        # move it up
        new_index = old_index - 1

        # delete old, and insert it on the new index
        Presets.names.insert(new_index, Presets.names.pop(old_index))

        self.c1.redraw()

    def down(self):
        print 'down'
        # get the current index
        old_index = Presets.names.index('new preset')
        # move it down
        new_index = old_index + 1

        # delete old, and insert it on the new index
        Presets.names.insert(new_index, Presets.names.pop(old_index))

        self.c1.redraw()

    def duplicate(self):
        print 'duplicate'

    def about(self):
        print 'about'

    def apply(self):
        print 'apply'


    # Callbacks --------------------------------------
    def name_1d(self, control, userdata, row):
        return Presets.names[row]

    def count_1d(self, control, userdata):
        return len(Presets.names)

    def single_select_event_func(self, control, user_data, row, selecting):
        if row < 0:
            return  # list selections are being cleared

        action = 'deselected'
        if selecting:
            action = action[2:]

        print 'You %s: %s' % (action, Presets.names[row])


# ------------------------------------------------------------------------------
# Presets Class
# ------------------------------------------------------------------------------
class Presets:
    """ Handles storage, loading and saving of user defined presets. """
    # Static variables
    defs = None
    names = None

    @staticmethod
    def load():
        """ Loads the presets into the class static variable """
        # Load the JSON data into an OrderedDict
        try:
            # f = open(Presets.file_path()+'ad', 'r')
            f = open(Presets.file_path(), 'r')
            Presets.defs = json.load( \
                f, object_pairs_hook = collections.OrderedDict)
            f.close()
        except:
            Presets.defs = {
            'version': __version__,
            'presets': {}
            }
            Presets.names = []

        Presets.names = []

        for s, v in Presets.defs['presets'].iteritems():
            print s
            Presets.names.append(s.encode('utf-8'))

        print Presets.defs
        print Presets.names


    @staticmethod
    def save():
        """ Saves the presets to a json formatted file """
        f = open(Presets.file_path(), 'w')
        json.dump(Presets.defs, f, indent=4)
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
        @return  True on success, else False
        """
        # Check so we got a unique name
        if name in Presets.names:
            return False

        # Add the new preset to list of names and to definitions
        Presets.names.append(name)
        Presets.defs['presets'][name] = {}

        # TODO:
        # Set default values

        # Presets.defs['presets']['New Preset '+str(Presets.ctr)]['GIPanelEnabled'] = 1
        # Presets.defs['presets']['New Preset '+str(Presets.ctr)]['RenderPanel'] = 1

        # // Populate it with default values
        # pDataPos = arrPresetOptions.indexOf("GIPanelEnabled");
        # arrPresetData[pDataID][pDataPos] = false;
        # pDataPos = arrPresetOptions.indexOf("RenderPanelEnabled");
        # arrPresetData[pDataID][pDataPos] = false;
        # pDataPos = arrPresetOptions.indexOf("BackdropPanelEnabled");
        # arrPresetData[pDataID][pDataPos] = false;
        # pDataPos = arrPresetOptions.indexOf("ProcessingPanelEnabled");
        # arrPresetData[pDataID][pDataPos] = false;
        # pDataPos = arrPresetOptions.indexOf("CameraPanelEnabled");
        # arrPresetData[pDataID][pDataPos] = false;
        # // Update the preset data panels
        # refreshPDataPanels(arrPresetList.count());

        Presets.save()



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
