#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import os, re, string, sys, time, types
import xbmc, xbmcgui

#===============================================================================
# Make global object available
#===============================================================================
from helpers import htmlentityhelper

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler
#===============================================================================
class MediaItem:
    def __init__(self, title, url, type="folder", parent=None):
        self.name =  htmlentityhelper.HtmlEntityHelper.ConvertHTMLEntities(title).rstrip()
        self.url = url
        self.MediaListItems = []
        self.description = ""
        self.thumb = ""        # image of episode
        self.thumbUrl = ""
        self.icon = ""        # icon for list
        self.date = ""
        self.type = type     # video, folder, append, page
        self.parent = parent
        self.complete = False
        self.downloaded = False
        self.downloadable = False
        self.items = []
        self.rating = None
        # GUID used for identifcation of the object. Do not set from script
        self.guid = ("%s-%s" % (title,url)).replace(" ","") 
    
        self.channels = []    # only needed for Kanalenkiezer 
    
    #================================================================================
    """
        Returns a XBMC Playlist for this item
    """
    def GetXBMCPlayList(self):
        playList = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playList.clear()
        
        for mediaItem in self.MediaListItems:
            logFile.debug("Using new MediaItem object for url %s", mediaItem.Url)
            playList.add(mediaItem.Url, mediaItem.GetXBMCListItem())

        return playList
    
    #============================================================================== 
    def __str__(self):
        value = self.name
        
        if self.type == "video":
            if len(self.MediaListItems) > 0:
                value = "%s [video (complete = %s): " % (value, self.complete)
                for mListItem in self.MediaListItems:
                    value = "%s%s," % (value,mListItem.Url,)
                value = "%s]" % (value,)
            else:
                value = "%s [unknown urls]" % (value, )
        else:
            value = "%s [folder: %s]" % (value, self.url)
        
        return value
    
    def __eq__(self, item):
        return self.Equals(item)
    
    def __ne__(self, item):
        return not self.Equals(item)
    
    def __cmp__(self, other):
        logFile.debug("Comparing")
        if self.type == "video" and other.type == "video":
            if self.date == "" and other.date == "":
                # no date, so us the name
                return cmp(self.name, other.name)
            
            elif self.date == "" and not other.date =="":
                # the other one has a date
                return 1
            elif other.date == "" and not self.date == "":
                return -1                 
            else:
                if self.date == other.date:
                    # check for date and then name
                    return cmp(self.name, other.name)
                else:
                    return 0
                    
        elif self.type == "folder" and other.type == "folder":
            # folders only: just use the name
            return cmp(self.name, other.name)
        else:
            return 0
        
    def AppendMediaListItem(self, url):
        self.MediaListItems.append(MediaListItem(self.name, url))
    
    def HasMediaListItems(self):
        return len(self.MediaListItems) > 0
    
    def Equals(self, item):
        if item == None:
            return False
        
        if self.name == item.name and self.guid != item.guid:
            logFile.debug("Duplicate names, but different guid: %s (%s), %s (%s)", self.name, self.url, item.name, item.url)
        return self.guid == item.guid
    
class MediaListItem:
    def __init__(self, name, url, *args):
        logFile.debug("Creating MediaListItem '%s' for '%s'", name, url)
        self.Name = name
        self.Url = url
        
        self.Properties = []
        for prop in args:
            self.Properties.append(prop)
        
        return
     
    def AddProperty(self, name, value):
        logFile.debug("Adding property: %s = %s", name, value)
        self.Properties.append((name,value))
    
     
    def GetXBMCListItem(self, name=None):
        logFile.debug("Creating XBMC ListItem '%s'", self.Name)
        if name != None:
            item = xbmcgui.ListItem(name)
        else:
            item = xbmcgui.ListItem(self.Name)
        for prop in self.Properties:
            logFile.debug("Adding property: %s", prop)
            item.setProperty(prop[0], prop[1])            
        return item 

    def __str__(self):
        text = "%s (%s)" % (self.Name, self.Url)
        
        for prop in self.Properties:
            text = "%s\nProperty: %s=%s" % (text, prop[0], prop[1]) 
        return text