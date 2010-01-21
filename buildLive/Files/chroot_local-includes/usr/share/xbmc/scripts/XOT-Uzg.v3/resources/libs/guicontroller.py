#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

#===============================================================================
# Import the default modules
#===============================================================================
import xbmc, xbmcgui 
import sys, os
#===============================================================================
# Make global object available
#===============================================================================
import common
import mediaitem
import config
import controls
import helpers
from helpers import encodinghelper
#import contextmenu

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

#===============================================================================
# GuiController class
#===============================================================================
class GuiController:
    """
        Controls all actions towards the GUI
    """
    #============================================================================== 
    def __init__(self, *args, **kwargs):
        """
            Initialises the GUI for a specific window (args[0])
        """
        # logFile.debug("GuiController :: Starting")
        
        if len(args)<1:
            raise ReferenceError 
        
        # set the to be controlled window
        self.window = args[0]
        self.progressBarItemLimit = 50
        self.decoder = encodinghelper.EncodingHelper()   

    #==============================================================================
    def DisplayPageNavigation(self, items):
        """ 
            Displays the pagenavigation using the items
        """
        if self.window.pluginMode:
            return
        
        logFile.debug("DisplayPageNavigation starting")
        
        try:            
            pageControl = self.window.getControl(controls.PG_LIST)
            pageControl.reset()

            for item in items:
                if item.type == "page":
                    tmp = xbmcgui.ListItem(item.name)
                    pageControl.addItem(tmp)
        
        except TypeError:
            logFile.info("DisplayPageNavigation :: Non-Existing Control - controls.PG_LIST")
            pass        
        
        return
    
    #==============================================================================
    def DisplayProgramList(self, items):
        self.window.getControl(controls.PR_LIST).reset()
                    
        if len(items)==0:
            # add dummy item
            tmp = mediaitem.MediaItem("No Files","")
            tmp.complete = True
            items.append(tmp)
        
        for m in items:
            self.window.getControl(controls.PR_LIST).addItem(xbmcgui.ListItem(self.decoder.Decode(m.name),m.date,m.icon, m.icon))

    #==============================================================================
    def DisplayFolderList(self, items, position):
        """ 
        Accepts an list of items and fills the windowlist. Clearing windows,
        Restore previous states and filling.
        """
        logFile.debug("DisplayFolderList needs to display %s items. \nFocussed is on item %s", len(items), position)
        self.window.clearList()
        
        if len(items)==0:
            logFile.debug("Adding Dummy Item")
            tmp = mediaitem.MediaItem("No Files", "")
            tmp.complete = True
            tmp.thumb = self.window.noImage
            tmp.icon = self.window.icon
            items.append(tmp)
        
        # check if a progressbar is needed:
        pbEnabled = len(items) > self.progressBarItemLimit
        
        if pbEnabled:
            logFile.info("Using Progressbar to display %s items", len(items))
            percentagePerItem = 100.0/len(items)
            itemNr = 0
            progDialog = xbmcgui.DialogProgress()
            progDialog.create("Please Wait...", "Adding Items to list")
        for item in items:
            if not item.type == "page":
                tmp = xbmcgui.ListItem(self.decoder.Decode(item.name), item.date, item.icon, item.icon)
                self.window.addItem(tmp)
                if pbEnabled:
                    itemNr = itemNr + 1
                    progDialog.update(int(percentagePerItem * itemNr), "Adding Items to list", "Adding item %s of %s" % (itemNr, len(items)))
                    if progDialog.iscanceled() == True:
                        break
        if pbEnabled:
            progDialog.close()
        
        self.window.setFocus(self.window.getControl(controls.EP_LIST))
        self.window.setCurrentListPosition(position)
        if not self.window.listItems[position].complete:
            item = self.window.UpdateVideoItem(self.window.listItems[position])
            
            # if the mediaUrl is not filled: item is not complete (DOES NOT WORK WELL)
            if not item.HasMediaListItems():
                item.complete = False
                
            # check if the list has not changed during upate:
            if self.window.listItems[position].Equals(item):
                logFile.info("Updating item (GUIDs match)")                
                self.window.listItems[position] = item
            else:
                logFile.error("Aborting Update because of GUID mismatch")
        
        # if somehow the list focus was already changed, don't update 
        if self.window.getCurrentListPosition() == position:
            logFile.info("All items where shown. Now fetching focussed item info for item number %s", position)
            self.ShowData(self.window.listItems[position])
    
    #============================================================================== 
    def ShowData(self, item):
        """ 
        Accepts an item with URL set and get additional details for the folder item 
        """
        logFile.debug("Fetching info for '%s'. Setting:\nDescription: %s\nImage: %s", item.name, item.description.lstrip('\n'), item.thumb)
        text = self.decoder.Decode(item.description.lstrip('\n'))
        self.window.getControl(controls.EP_DESCRIPTION).reset()
        self.window.getControl(controls.EP_DESCRIPTION).setText(text)
        self.window.getControl(controls.EP_THUMB).setImage(item.thumb)
        
        if item.complete and item.type=="video":
            self.window.getControl(controls.EP_COMPLETE).setVisible(True)
        else:
            self.window.getControl(controls.EP_COMPLETE).setVisible(False)
                
        self.ShowRating(item.rating)
    
    #==============================================================================     
    def ShowRating(self, value):
        """ 
            Displays the rating stars
        """
        
        logFile.debug("Showing rating: %s", value)
        try:            
            self.window.getControl(controls.EP_RATING + 1).setVisible(False)
            self.window.getControl(controls.EP_RATING + 2).setVisible(False)
            self.window.getControl(controls.EP_RATING + 3).setVisible(False)
            self.window.getControl(controls.EP_RATING + 4).setVisible(False)
            self.window.getControl(controls.EP_RATING + 5).setVisible(False)
            if not value == None:
                self.window.getControl(controls.EP_RATING + value).setVisible(True)
        except:
            logFile.info("ShowRating :: Non-Existing Control - controls.EP_RATING", exc_info=True)
            pass
    
    #============================================================================== 
    def ShowChannelInfo(self, channel):
        try:                
            imageHolder = self.window.getControl(controls.PL_LARGE_ICON)
            imageHolder.setImage(channel.iconLarge)
            self.window.getControl(controls.PL_CHANNEL_NAME).setLabel(channel.channelName)
            self.window.getControl(controls.PL_CHANNEL_DESCRIPTION).setLabel(channel.channelDescription)
        except:
            logFile.info("ShowChannelInfo :: Non-Existing Channelinformation Control")
            pass

        return
    
    #==============================================================================
    def ClearEpisodeLists(self):
        self.window.clearList()
        
        try:            
            self.window.getControl(controls.PG_LIST).reset()
        except TypeError:
            logFile.info("ClearEpisodeLists :: Non-Existing Control - controls.PG_LIST")
            pass        

        return
     
    #============================================================================== 
    def GetImageLocation(self, image):
        """ NOT USER EDITABLE
            check if image is present in skin-folder. If so, use that one, of not,
            us the local one
        """
        if image == "":
            return ""
        if not os.path.exists(os.path.join(config.rootDir,"resources", "skins", config.skinFolder, "media", image)):
            image = os.path.join(config.rootDir, "channels", self.__module__.replace("chn_", ""), image)
        return image
    