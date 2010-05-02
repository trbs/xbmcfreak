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
import sys, os, time
import zipfile

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
from helpers import htmlentityhelper
#from enums import *

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler


#===============================================================================
class Updater(xbmcgui.WindowXMLDialog):
    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0):
        logFile.debug("Updater started")
        self.updateItems = []

    #===============================================================================
    def onInit(self):
        try:
            self.LoadChannels()
            if len(self.updateItems) > 0:
                self.DisplayInfo(0)
            else:
                dialog = xbmcgui.Dialog()
                dialog.ok("No updates","There are no updated \nchannels at the moment.")
                self.close()

                
        except:
            logFile.error("Error initializing the Updater GUI", exc_info=True)
                
    #===============================================================================
    def onAction(self, action):
        try:
            logFile.debug("OnAction")
            try:
                #controlID = self.getFocusId()
                if not action.getId() in controls.ACTION_MOUSE_MOVEMENT:
                    # if it was no mousemovement, reset the clicked
                    logFile.debug("Resetting self.click")
                    self.clicked = False
            except:
                logFile.error("updater::onAction exception determining controlID", exc_info=True)
                return
            
            #===============================================================================
            # Handle Back actions
            #===============================================================================
            if action in controls.ACTION_EXIT_CONTROLS:
                logFile.debug("Closing updater")
                self.close()
                pass
            
            elif action in controls.ACTION_UPDOWN:
                self.DisplayInfo(self.getCurrentListPosition())
            
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
    def onClick(self, controlID):
        try:
            logFile.debug("onClick ControlID=%s", controlID)
            if controlID == controls.UD_EXIT:
                time.sleep(0.1)
                self.close()
            
            elif controlID == controls.UD_LIST:
                updateItem = self.updateItems[self.getCurrentListPosition()]
                dialog = xbmcgui.Dialog()
                go = dialog.yesno('Confirm update', 'Are you sure you want to update %s? \nIf the channel already exists it will be deleted!' % (updateItem.name))
                if go:
                    self.UpdateChannel(updateItem)
            pass
        except:
            logFile.critical("Error handling onClick on controlID=%s", controlID, exc_info=True)
            
    #===============================================================================
    def onFocus(self, controlID):
        """"
            onFocus(self, int controlID)
            This function has been implemented and works
        """
        try:
            logFile.debug("onFocus :: Control %s has focus now", controlID)
            pass
        except: 
            logFile.critical("Error handling onFocus on ControlID=%s", controlID, exc_info=True)
    
    #===============================================================================
    #    Custom loading methodes
    #===============================================================================
    def LoadChannels(self):
        data = uriHandler.Open("http://code.google.com/p/xot-uzg/downloads/list?q=label:AutoUpdate", pb=False)
        channels = common.DoRegexFindAll('href="detail\?name=([^&]+)[^"]+">\W*([^<]+)\W*</a>[^!]+[^>]+>[^>]+>\W*([^<]+)\W*</a>', data)
        guiController = guicontroller.GuiController(self)
        
        for channel in channels:
            logFile.debug(channel)
            item = mediaitem.MediaItem(channel[0], "http://xot-uzg.googlecode.com/files/%s" % channel[0])
            item.description = htmlentityhelper.HtmlEntityHelper.ConvertHTMLEntities(channel[1])
            item.icon = guiController.GetImageLocation("xot_updateicon.png")
            item.date = channel[2]
            self.updateItems.append(item)
            item = xbmcgui.ListItem(channel[0], channel[2], item.icon, item.icon) 
            self.addItem(item)

    #============================================================================== 
    def DisplayInfo(self, position):
        item = self.updateItems[position]
        self.getControl(controls.UD_DESCRIPTION).reset()
        self.getControl(controls.UD_DESCRIPTION).setText(item.description)
        pass
    
    #==============================================================================
    def UpdateChannel(self, item):
        logFile.debug("Starting update for %s", item.url)
        file = uriHandler.Download(item.url, item.name, uriHandler.defaultLocation)
        logFile.debug("Download succeeded: %s", file)
        channelDir = os.path.join(config.rootDir, "channels")
        
        zipFile = zipfile.ZipFile(file, 'r')
        try:
            content = ""
            for name in zipFile.namelist():
                if name.endswith("/") or name.endswith("\\"):
                    name = name.rstrip("/")
                    name = name.rstrip("\\")                    
                    channelPath = os.path.join(channelDir, name,"")                 
                    
                    if os.path.exists(channelPath):
                        content = "%s\n%s (Update)" % (content, channelPath)
                        self.CleanupOldChannel(channelPath)                        
                    else:
                        content = "%s\n%s (New)" % (content, channelPath)
                        os.mkdir(channelPath)
            
            #now extract
            for name in zipFile.namelist():
                if not name.endswith("/") and not name.endswith("\\"):
                    fileName = os.path.join(channelDir, name)
                    logFile.debug("Updating %s", fileName)
                    outfile = open(fileName, 'wb')
                    outfile.write(zipFile.read(name))
                    outfile.close()
                    
            zipFile.close()
            
            dialog = xbmcgui.Dialog()
            dialog.ok("Restart XOT","The update of '%s' was complete. \nPlease restart XOT to complete the update." % (item.name))                   
        except:
            zipFile.close()
            logFile.debug("Error handling zipfiles during update", exc_info=True)
            dialog = xbmcgui.Dialog()
            dialog.ok("Update Failed","The update of '%s' failed. Please \nretry or manualy update the channel." % (item.name))
    
    #============================================================================== 
    def CleanupOldChannel(self, channelPath, all=False): 
        # delete the original folder
        for root, dirs, files in os.walk(channelPath, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))                
        if (all):
            os.rmdir(channelPath)
         
    