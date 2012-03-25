""" Render Presets Button

A generic class that can be added as a button to LightWave's GUI that simply
starts Render Presets master class.
LightWave 3D (as of v11) seems to crash when combining plugin classes in the
same file. So I keep the button class separate.
"""

__author__      = 'Johan Steen'
__copyright__   = 'Copyright (C) 2010-2012, Johan Steen'
__credits__     = ''
__license__     = 'New BSD License'
__version__     = '2.0'
__maintainer__  = 'Johan Steen'
__email__       = 'http://www.artstorm.net/contact/'
__status__      = 'Production'
__lwver__       = '11'

# ------------------------------------------------------------------------------
# Import Modules
# ------------------------------------------------------------------------------
import lwsdk


# ------------------------------------------------------------------------------
# Generic Plugin Class
# ------------------------------------------------------------------------------
class render_presets_button(lwsdk.IGeneric):
    # Constants
    SSERVER = 'js_Render_Presets'

    def __init__(self, context):
        super(render_presets_button, self).__init__()

    def process(self, ga):
        item_info = lwsdk.LWItemInfo()

        # Check if Render Presets Master is already added
        index = 1
        server_added = False
        while True:
            server_name = item_info.server(None, 'MasterHandler', index);

            # Reached end of list, break loop
            if server_name == None:
                break

            # Render Presets Master added, break loop
            if server_name == self.SSERVER:
                server_added = True
                break

            index += 1

        # Do the appropriate action on the MasterHandler Render Presets Server
        if server_added:
            # In production Render Presets is always started from the button
            # In development I prefer to toggle it with a remove, for testing
            if __status__ == 'Production':
                lwsdk.command('EditServer MasterHandler ' + str(index))
            else:
                lwsdk.command('RemoveServer MasterHandler ' + str(index))
        else:
            # Not added, so let's add it.
            lwsdk.command('ApplyServer MasterHandler ' + self.SSERVER)
            lwsdk.command('EditServer MasterHandler ' + str(index))

        return lwsdk.AFUNC_OK


# ------------------------------------------------------------------------------
# Register the Plugin
# ------------------------------------------------------------------------------
ServerTagInfo = [
    ('js Render Presets', lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH),
    ('Render Presets', lwsdk.SRVTAG_BUTTONNAME | lwsdk.LANGID_USENGLISH),
    ('Utilities/Python', lwsdk.SRVTAG_MENU | lwsdk.LANGID_USENGLISH)
]

ServerRecord = {
    lwsdk.GenericFactory('js_Render_Presets_Btn', render_presets_button)
    : ServerTagInfo
}
