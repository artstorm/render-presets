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
import json
import lwsdk

import pprint

# ------------------------------------------------------------------------------
# Constants
# ------------------------------------------------------------------------------
DEFINITIONS_FILE = 'js_render_presets.def'


# ------------------------------------------------------------------------------
# Master Plugin Class
# ------------------------------------------------------------------------------
class render_presets_master(lwsdk.IMaster):

    def __init__(self, context):
        super(render_presets_master, self).__init__()

        # Init Panel variables
        self._ui = lwsdk.LWPanels()
        self._panel = None


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
            self._panel.set_close_callback(self.panel_close_callback)

            self.create_controls()

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


    # --------------------------------------------------------------------------
    # Custom Methods
    # --------------------------------------------------------------------------
    def create_controls(self):
        """ Creates the controls in the panel.

        Loads a file containing all definitions needed to populate the interface
        and associated commands.
        """

        # Get the path to the definitions file
        script_file = os.path.realpath(__file__)
        dir_path = os.path.dirname(script_file)
        def_file = os.path.join(dir_path, DEFINITIONS_FILE)


        # Need error handling here
        json_data=open(def_file)
        data = json.load(json_data)
        json_data.close()

        pprint.pprint(data)

        # Get rid of Unicode character (u')
  #      print data['tabs']
 #       print temp_list
        # tabs = [s.encode('utf-8') for s in data['tabs']]
        tabs = data['tabs']
#        print tabs
        
        tab_names = []
        for key, val in tabs.iteritems():
            tab_names.append(key.encode('utf-8'))

        # TMP GUI Setup

        c1 = self._panel.listbox_ctl('Listbox', 200, 10, self.name_1d, self.count_1d)
        c1.set_select(self.single_select_event_func)

        self._c2 = self._panel.tabchoice_ctl('Tabs', tab_names)
        self._c2.set_event(self.tabs_callback)

        # print tab_names
        # print tab_names[0]
        # print tabs[tab_names[0]]

        # Optimize: Consolidate below into one loop
        tmp = tabs[tab_names[0]]
        for s in tmp:
            # print s['label']
            # s['control'] = self._panel.bool_ctl(s['label'])
            s['control'] = self._panel.bool_ctl(s['label'])
            s['control'].set_w(200)

        tmp = tabs[tab_names[1]]
        for s in tmp:
            s['control'] = self._panel.bool_ctl(s['label'])
            s['control'].erase()

        tmp = tabs[tab_names[2]]
        for s in tmp:
            s['control'] = self._panel.bool_ctl(s['label'])
            s['control'].erase()

        tmp = tabs[tab_names[3]]
        for s in tmp:
            s['control'] = self._panel.bool_ctl(s['label'])
            s['control'].erase()


        self._tmp_tabs = tabs
        self._tmp_tab_names = tab_names

        # multiple line test
#        print('flag: afsasssssssssssssssssssssssssssssfasfafasfasfa' \
#              + str(self.tab1_c1.flags()) )



    def tabs_callback(self, id, user_data):
#        print 'You selected: %s' % temp_list[self._c2.get_int()]
#        print self._c2.get_int()
        tmp = self._c2.get_int()

        tabs = self._tmp_tabs
        tab_names = self._tmp_tab_names

        # Optimize below: erase in one loop. Don't erase the tab that's clicked.
        # Erase controllers on all tabs
        tmp_pan = tabs[tab_names[0]]
        for s in tmp_pan:
            s['control'].erase()
        tmp_pan = tabs[tab_names[1]]
        for s in tmp_pan:
            s['control'].erase()
        tmp_pan = tabs[tab_names[2]]
        for s in tmp_pan:
            s['control'].erase()
        tmp_pan = tabs[tab_names[3]]
        for s in tmp_pan:
            s['control'].erase()

        # Render the controls on the clicked tab
        tmp_pan = tabs[tab_names[tmp]]
        for s in tmp_pan:
            s['control'].render()




    # Callbacks --------------------------------------
    def name_1d(self, control, userdata, row):
        return temp_list[row]

    def count_1d(self, control, userdata):
        return len(temp_list)

    def single_select_event_func(self, control, user_data, row, selecting):
        if row < 0:
            return  # list selections are being cleared

        action = 'deselected'
        if selecting:
            action = action[2:]

        print 'You %s: %s' % (action, temp_list[row])



temp_list = ['hey', 'ho', 'lets', 'go']

# ------------------------------------------------------------------------------
# Register the Plugin
# ------------------------------------------------------------------------------
ServerTagInfo = [
    ('Render Presets', lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH)
]

ServerRecord = { 
    lwsdk.MasterFactory('js_Render_Presets', render_presets_master) 
    : ServerTagInfo
}
