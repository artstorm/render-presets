"""Render Presets

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
import lwsdk


# ------------------------------------------------------------------------------
# Master Plugin Class
# ------------------------------------------------------------------------------
class render_presets_master(lwsdk.IMaster):

    def __init__(self, context):
        super(render_presets_master, self).__init__()

    def inter_ui(self):


# ------------------------------------------------------------------------------
# Register the Plugin
# ------------------------------------------------------------------------------
ServerTagInfo = [
                    ( "Render Presets", lwsdk.SRVTAG_USERNAME | lwsdk.LANGID_USENGLISH )
                ]

ServerRecord = { lwsdk.MasterFactory("js_Render_Presets", render_presets_master) : ServerTagInfo }
