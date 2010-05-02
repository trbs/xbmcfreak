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
import urlparse, re, sys, os
from urlparse import urlparse

#===============================================================================
# Make global object available
#===============================================================================
import config
import controls
import contextmenu
import common
import mediaitem
import settings
import guicontroller
import update
import updater
import helpers
from helpers.stopwatch import StopWatch
#from enums import *

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

try:
    channelRegister = []
    
    # load all channels in channel folder
    channelImport = os.listdir(os.path.join(config.rootDir,"channels"))
    channelImport.sort()
    
    # first import base class
    import chn_class
    
    importTimer = StopWatch("Progwindow :: importing channels", logFile)
    for channel in channelImport:
        channelDir = os.path.join(config.rootDir, "channels", channel)
        if os.path.isdir(channelDir) and not channel.startswith("."):
            sys.path.append(channelDir)
            logFile.info("Importing chn_%s", channel)
            exec("import chn_%s" % channel) 
    importTimer.Lap()
    #channels imported, but not initialised, that happens in the __init__!
            
except:
    logFile.critical("Error loading channel modules", exc_info=True)
    
#===============================================================================
class GUI(xbmcgui.WindowXML):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0):
        try:
            self.mainlistItems = []
            self.initialised = False
            self.contextMenu = True
            self.channelGUIs = []
            self.channelButtonRegister = []
            self.activeChannelGUI = None
            self.selectedChannelIndex = 0
            self.listMode = ProgListModes.Normal#1 # 1=normal, 2=favorites 
            
            # create channel GUIs (channel classes are initiated)
            guidList = []
            for channel in channelRegister:
                self.channelGUIs.append(eval(channel))   
                
                # if out of date, remove again!
                if self.channelGUIs[-1].OutOfDate:
                    self.channelGUIs.pop()
                
                # chech for duplicate guids
                if self.channelGUIs.count(self.channelGUIs[-1]) > 1:
                    duplicateChannel = self.channelGUIs.pop()
                    presentChannel = self.channelGUIs[self.channelGUIs.index(duplicateChannel)]
                    logFile.error("Removing channel %s\nbecause a channel with the same guid already exist:\n%s.", duplicateChannel, presentChannel)
            importTimer.Stop()
            
            # order them by channelName MUST Also sort the buttons
            #self.channelGUIs.sort(lambda x,y: cmp(x.channelName.lower(), y.channelName.lower))
            self.channelGUIs.sort(self.sortChannel)
            
            # now that they are ordered: get the buttoncodes. So the order in the buttoncode 
            # list is the same!
            for channel in self.channelGUIs:
                if channel.buttonID >0:
                    self.channelButtonRegister.append(channel.buttonID)
            self.panelViewEnabled = self.channelButtonRegister == []
            
            logFile.info("Starting %s ProgWindow with Fallback=%s and DefaultName=%s",config.appName, strFallbackPath,strDefaultName)
        except:
            logFile.debug("Error in __init__ of ProgWindow", exc_info=True)
    #===============================================================================
    def onInit(self):
        try:
            # check, if there are buttons registerd, and if there are, if
            # the buttoncount is the same as the channelcount
            if self.channelButtonRegister != []:
                if len(self.channelButtonRegister) != len(channelRegister):
                    logFile.critical("The number of buttons that were registered is not the same as the number of channels")
                    self.close()
                    
            if not self.initialised:
                logFile.debug("Doing first initialisation of ProgWindow")
                # hide programlist 
                self.getControl(controls.PR_LIST_WRAPPER).setVisible(False)
                
                # if buttons are present, hide the panelView
                if not self.panelViewEnabled:
                    self.getControl(controls.CH_LIST_WRAPPER).setVisible(False)
                    
                # set initialvalues
                self.DisplayGUIs()
                
                # Set icon
                self.selectedChannelIndex = self.getCurrentListPosition()
                self.activeChannelGUI = self.channelGUIs[self.selectedChannelIndex]
                
                self.ShowChannelInfo()
                
                self.initialised = True
            
            self.setCurrentListPosition(self.selectedChannelIndex)
        except:
            logFile.error("Error Initializing Progwindow", exc_info = True)      

    #===============================================================================
    def onAction(self, action):
        try:
            # get the FocusID
            try:
                controlID = self.getFocusId()
            except:
                logFile.debug("Unknown focusID for action ID: %s and ButtonCode: %s", action.getId(), action.getButtonCode())
                return
            
            #===============================================================================
            # Handle Back actions
            #===============================================================================
            if action == controls.ACTION_PARENT_DIR or action == controls.ACTION_PREVIOUS_MENU:
                logFile.debug("Going back a level")
                if self.mainlistItems == [] or not self.panelViewEnabled:
                    logFile.debug("Closing ProgWindow")
                    self.close()
                else:
                    # hide programlist and show channelpannel
                    logFile.debug("Switching ProgWindow Mode")
                    self.activeChannelGUI = None
                    self.mainlistItems = []
                    self.ChannelListVisible(True)
                    self.listMode = ProgListModes.Normal
            
            elif action in controls.ACTION_CONTEXT_MENU_CONTROLS:
                logFile.debug("Showing contextmenu")
                self.onActionFromContextMenu(controlID)
                        
            #===============================================================================
            # Handle UP/Down on mainlist
            #===============================================================================
            elif (action in controls.ACTION_UPDOWN or action in controls.ACTION_LEFTRIGHT or action in controls.ACTION_MOUSE_MOVEMENT) and self.mainlistItems == [] and controlID == controls.CH_LIST:
                # Determine the active channel only when EP_LIST is in focus
                self.selectedChannelIndex = self.getCurrentListPosition()
                self.activeChannelGUI = self.channelGUIs[self.selectedChannelIndex]
                
                self.ShowChannelInfo()
            
            #===============================================================================
            # Handle onClicks
            #===============================================================================
            #elif action == controls.ACTION_SELECT_ITEM:
            #    logFile.debug("Progwindow :: Performing a SelectItem")
            #    # handle the onClicks. Because we use a WrapList the onClick also triggers
            #    # an onAction, causing some problems. That is why we handle onclicks here now.
            #    # normally the onClick occurs and then the onAction
            #    #self.onSelect(controlID)
            
            else:
                if not action.getId() in controls.ACTION_MOUSE_MOVEMENT:
                    logFile.critical("OnAction::unknow action (id=%s). Do not know what to do", action.getId())            
        except:
            logFile.critical("OnAction Error", exc_info=True)
            self.close()
            
    #===============================================================================
    def onSelect(self, controlID):
        """
            Handles the onSelect from the GUI
        """
        logFile.debug("onSelect on ControlID=%s", controlID)
        
        #===============================================================================
        # Handle main lists
        #===============================================================================
        if controls.EP_LIST <= controlID <= controls.EP_LIST + 9 and self.mainlistItems==[]:
            # set the active channel in case no up/down was done!
            self.selectedChannelIndex = self.getCurrentListPosition()
            self.activeChannelGUI = self.channelGUIs[self.selectedChannelIndex]
        
            # Get MainlistItems
            self.mainlistItems = self.activeChannelGUI.ParseMainList()
            self.ShowListItems(self.mainlistItems)
            
            # hide Main ChannelList and show ProgramList
            self.ChannelListVisible(False)
                                
        # if mainlist is not empty, then the episodewindow should be dispalyed
        elif controlID == controls.PR_LIST and self.mainlistItems != []:
            selectedPosition = self.getControl(controls.PR_LIST).getSelectedPosition()
            if self.listMode == ProgListModes.Favorites:
                if selectedPosition > len(self.favoriteItems):
                    logFile.error("Favorites list does not have %s items, so item %s cannot be selected",selectedPosition,selectedPosition)
                    return
                selectedUrl = self.favoriteItems[selectedPosition].url
            else: 
                selectedUrl = self.mainlistItems[selectedPosition].url
            logFile.info('opening episode list GUI with uri=%s',selectedUrl)
            self.activeChannelGUI.ShowEpisodeWindow(selectedUrl)
        
        
        #===============================================================================
        # check if a button that was registered was pressed!
        #===============================================================================
        elif controlID in self.channelButtonRegister:
            # set the active channel in case no up/down was done!
            self.selectedChannelIndex = self.channelButtonRegister.index(controlID)
            self.activeChannelGUI = self.channelGUIs[self.selectedChannelIndex]
        
            self.getControl(controls.PR_LIST).reset()
            self.ChannelListVisible(False)
            
            # Get MainlistItems
            self.mainlistItems = self.activeChannelGUI.ParseMainList()
            
            for m in self.mainlistItems:
                self.getControl(controls.PR_LIST).addItem(xbmcgui.ListItem(m.name,"",m.icon, m.icon))
       
    #===============================================================================
    def onClick(self, controlID):
        try:
            logFile.debug("Progwindow :: onClick ControlID=%s", controlID)
            self.onSelect(controlID)
        except:
            logFile.critical("Error handling onClick on controlID=%s", controlID, exc_info=True)
            
    #===============================================================================
    def onFocus(self, controlID):
        """"
            onFocus(self, int controlID)
            This function has been implemented and works
        """
        try:
            #logFile.debug("onFocus :: Control %s has focus now", controlID)
            pass
        except: 
            logFile.critical("Error handling onFocus on ControlID=%s", controlID, exc_info=True)
    
    #===============================================================================
    #    Contextmenu stuff
    #===============================================================================
    def onActionFromContextMenu(self, controlID):        
        if self.contextMenu is False:
            return None
         
        contextMenuItems = []
         
        # determine who called the menu
        if controlID <> controls.CH_LIST:
            selectedIndex = self.getControl(controls.PR_LIST).getSelectedPosition()
            parentControl = self.getFocus()
            # determine if favorites are enabled 
            if (self.listMode == ProgListModes.Normal):
                contextMenuItems.append(contextmenu.ContextMenuItem("Show Favorites", "CtMnShowFavorites"))
                contextMenuItems.append(contextmenu.ContextMenuItem("Add to Favorites", "CtMnAddToFavorites"))                        
            else:
                contextMenuItems.append(contextmenu.ContextMenuItem("Hide Favorites", "CtMnHideFavorites"))
                contextMenuItems.append(contextmenu.ContextMenuItem("Remove from Favorites", "CtMnRemoveFromFavorites"))                        
            # or not
        
        elif controlID == controls.CH_LIST:
            selectedIndex = self.getCurrentListPosition()#getControl(controls.CH_LIST).getSelectedPosition()
            parentControl = self.getControl(controls.CH_LIST_WRAPPER)
            contextMenuItems.append(contextmenu.ContextMenuItem("Update channels","CtMnUpdateChannels"))
            contextMenuItems.append(contextmenu.ContextMenuItem("Check for XOT updates","CtMnUpdateXOT"))
            
        # build menuitems
        selectedItem = None
        contextMenu = contextmenu.GUI(config.contextMenuSkin, config.rootDir, config.skinFolder, parent=parentControl, menuItems = contextMenuItems)
        selectedItem = contextMenu.selectedItem
        del contextMenu
                
        # handle function from items
        if (selectedItem is not None):    
            selectedMenuItem = contextMenuItems[selectedItem]
            functionString = "self.%s(%s)" % (selectedMenuItem.functionName, selectedIndex)
            logFile.debug("Calling %s", functionString)
            try:
                exec(functionString)
            except:
                logFile.error("onActionFromContextMenu :: Cannot execute '%s'.", functionString, exc_info = True)

        return None
    
    #============================================================================== 
    def CtMnShowFavorites(self, selectedIndex):
        self.listMode = ProgListModes.Favorites
        # Get Favorites
        self.favoriteItems = settings.LoadFavorites(self.activeChannelGUI)
        self.ShowListItems(self.favoriteItems)  
    
    def CtMnHideFavorites(self, selectedIndex):
        self.listMode = ProgListModes.Normal
        self.ShowListItems(self.mainlistItems)  
                
    def CtMnAddToFavorites(self, selectedIndex):
        settings.AddToFavorites(self.mainlistItems[selectedIndex], self.activeChannelGUI)

    def CtMnRemoveFromFavorites(self, selectedIndex):
        settings.RemoveFromFavorites(self.favoriteItems[selectedIndex], self.activeChannelGUI)
        #reload the items
        self.favoriteItems = settings.LoadFavorites(self.activeChannelGUI)
        self.ShowListItems(self.favoriteItems)

    def CtMnUpdateXOT(self, selectedIndex):
        update.CheckVersion(config.version, config.updateUrl, verbose=True)

    def CtMnUpdateChannels(self, selectedIndex):
        updaterWindow = updater.Updater(config.updaterSkin ,config.rootDir, config.skinFolder)
        updaterWindow .doModal()
        del updaterWindow 

    #===============================================================================
    # Fill the channels
    #===============================================================================
    def DisplayGUIs(self):
        timer = StopWatch("Progwindow :: showing channels", logFile)
        self.clearList()
        xbmcgui.lock()
        try:
            for channelGUI in self.channelGUIs:
                tmp = xbmcgui.ListItem(channelGUI.channelName,"" , channelGUI.icon , channelGUI.iconLarge)
                #logFile.debug("Adding %s", channelGUI.channelName)
                self.addItem(tmp)
        finally:
            xbmcgui.unlock()
        timer.Stop()
    
    #==============================================================================
    def ShowListItems(self, items):
        guiController = guicontroller.GuiController(self)
        guiController.DisplayProgramList(items)

    #===============================================================================
    def ChannelListVisible(self, visibility):
        if visibility:
            logFile.debug("Showing Channels")
            self.getControl(controls.CH_LIST_WRAPPER).setVisible(True)
            self.getControl(controls.PR_LIST_WRAPPER).setVisible(False)
            self.setFocusId(controls.CH_LIST_WRAPPER)
            self.setFocusId(controls.CH_LIST)
            
            # this is a work around for a recent bug that was introduced
            if self.getControl(controls.CH_LIST).size() < 1:
                logFile.info("Somehow the list was cleared...filling it again")
                self.DisplayGUIs()
        else:
            logFile.debug("Hiding Channels")
            self.getControl(controls.CH_LIST_WRAPPER).setVisible(False)
            self.getControl(controls.PR_LIST_WRAPPER).setVisible(True)
            self.setFocusId(controls.PR_LIST)
        return
    
    #============================================================================== 
    def ShowChannelInfo(self):
        guiControler = guicontroller.GuiController(self)
        guiControler.ShowChannelInfo(self.activeChannelGUI)
        return
    
    #==============================================================================
    def sortChannel(self, channel1, channel2):
        try:
            compVal = cmp(channel1.sortOrder, channel2.sortOrder)
            if compVal == 0:
                compVal = cmp(channel1.channelName, channel2.channelName)
            #logFile.debug("Ordering %s (%s) and %s (%s): %s", channel1.channelName, channel1.sortOrder, channel2.channelName, channel2.sortOrder, compVal)
        except:
            logFile.debug("Error Comparing", exc_info=True)
            compVal = 0
        return compVal

#===============================================================================
# Progwindow Enumeration
#===============================================================================
class ProgListModesEnum:
    def __init__(self):
        self.Normal = 1
        self.Favorites = 2
ProgListModes = ProgListModesEnum()
