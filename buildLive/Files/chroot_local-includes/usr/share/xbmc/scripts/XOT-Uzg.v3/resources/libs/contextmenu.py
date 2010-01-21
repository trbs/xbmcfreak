#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import xbmc, xbmcgui
import re, sys, time

#===============================================================================
# Make global object available
#===============================================================================
import config
import controls
logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

#------------------------------------------------------------------------------ 
NUM_BUTTONS = 9 #from skin file
#------------------------------------------------------------------------------ 

class ContextMenuItem:
    def __init__(self, label, functionName, itemTypes = None, completeStatus = None):
        self.label = label
        self.functionName = functionName
        self.itemTypes = itemTypes
        self.completeStatus = completeStatus

class GUI(xbmcgui.WindowXMLDialog):
    
    def __init__( self, *args, **kwargs ):
        logFile.info("contextmenu opening")
        xbmcgui.lock()
        self.parent = kwargs["parent"]
        self.menuItems = kwargs["menuItems"]
        self.selectedItem = None
        self.doModal()

    #------------------------------------------------------------------------------ 
    def onInit(self):
        try:
            logFile.info("Initialising ContextMenu")
            self.SetupContextMenu()
            xbmcgui.unlock()
        except:
            logFile.critical("Error aligning the contexmenu", exc_info=True)
        
    #------------------------------------------------------------------------------ 
    def onAction(self, action):
        try:
            if action == controls.ACTION_PARENT_DIR or action == controls.ACTION_PREVIOUS_MENU:
                self.close()
            elif action ==  controls.ACTION_SELECT_ITEM:
                #self.selectedItem = self.getFocusId()-1100 - 1 # -1 for correcting for array items
                #logFile.info("Returning selected value '%s'", self.selectedItem)
                #self.close()
                pass
        except:
            logFile.critical("Could not return selection value from onActions")
                          
    #------------------------------------------------------------------------------ 
    def onClick(self, controlId):
        try:
            logFile.debug("onClick from controlid=%s", controlId)
            self.selectedItem = controlId-1100 - 1 # -1 for correcting for array items
            logFile.info("Returning selected value '%s'", self.selectedItem)
            
            # sleep needed to prevent crash?
            time.sleep(0.1)
            self.close()
            pass
        except:
            logFile.critical("Could not return selection value from onClick", exc_info=True)
        
    #------------------------------------------------------------------------------ 
    def onFocus(self, controlID):
        pass
    
    #------------------------------------------------------------------------------ 
    def SetupContextMenu(self):
        logFile.info("Aligning the contextmenu")
        # get positions and dimensions
        _dialogTopHeight = self.getControl(1001).getHeight()
        _dialogWidth = self.getControl(1002).getWidth()
        _dialogBottomHeight = self.getControl(1003).getHeight()
        _dialogLeft = self.getControl(1001).getPosition()[0]
        _dialogTop = self.getControl(1001).getPosition()[1]
        
        _buttonHeight = self.getControl(1101).getHeight()
        _buttonWidth = self.getControl(1101).getWidth()
        _buttonLeft = self.getControl(1101).getPosition()[0]
        _buttonTop = self.getControl(1101).getPosition()[1]
        _buttonVerticalSpacing = 3
        #_buttonHorizontalSpacing = _buttonLeft + (_dialogWidth-_buttonWidth)/2
        
        _parentHeight = self.parent.getHeight()
        _parentWidth = self.parent.getWidth()
        _parentTop= self.parent.getPosition()[1]
        _parentLeft= self.parent.getPosition()[0]
        
        logFile.debug("Window dim: %s, %s at pos %s, %s", _parentWidth, _parentHeight, _parentLeft, _parentTop)
                
        # now calculate other things
        _numberOfButtons = len(self.menuItems)
        
        _dialogMiddleHeight = (_buttonHeight+_buttonVerticalSpacing)*_numberOfButtons
        self.getControl(1003).setPosition(_dialogLeft, _dialogTop + _dialogTopHeight + _dialogMiddleHeight)
        self.getControl(1002).setHeight(_dialogMiddleHeight)
        
        # want to set it here, but that is not possible at the moment due to exception
        _dialogGroupTop = _parentTop + int((_parentHeight-_dialogMiddleHeight)/2)
        _dialogGroupLeft = _parentLeft + int((_parentWidth - _dialogWidth)/2)
        logFile.debug("%s, %s",_dialogGroupLeft, _dialogGroupTop)
        #self.getControl(1000).setPosition(_dialogGroupLeft, _dialogGroupTop)
        
        # and setup the buttons
        for buttonNr in range(_numberOfButtons):
            logFile.debug("Buttonnr: %s with label %s", 1101+buttonNr, self.menuItems[buttonNr].label)
            buttonControl = self.getControl(1101+buttonNr)
            buttonControl.setPosition(_buttonLeft, _buttonTop + (_buttonVerticalSpacing + _buttonHeight)*buttonNr)
            buttonControl.setLabel(self.menuItems[buttonNr].label)
            buttonControl.setVisible(True)
            buttonControl.setEnabled(True) 
        
        # now arrange the controlnavigation and remove redundant buttons
        self.getControl(1101).controlUp(self.getControl(1100+_numberOfButtons))
        self.getControl(1100+_numberOfButtons).controlDown(self.getControl(1101))
        
        for buttonNr in range(_numberOfButtons, NUM_BUTTONS):
            logFile.debug("Removing button: %s", buttonNr+1101)
            self.removeControl(self.getControl(1101+buttonNr))
        self.setFocusId(1101)
