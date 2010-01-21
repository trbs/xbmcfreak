#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

from atexit import register
import uriopener
import xbmcplugin, xbmc, xbmcgui
import sys, os, traceback, types
import string
from string import*
import urllib
import pickle

#sys.path.append(os.path.join(os.getcwd().replace(";",""),'libs'))
#===============================================================================
# Import XOT stuff
#===============================================================================
try:
    import config
    import common
    import mediaitem
    logFile = sys.modules['__main__'].globalLogFile
    uriHandler = sys.modules['__main__'].globalUriHandler
    
    #register for channels
    channelRegister = []    
except:
    globalLogFile.critical("Error initializing %s", config.appName, exc_info=True)

#===============================================================================
# Main Plugin Class
#===============================================================================
class XotPlugin:
    """
    Main Plugin Class
    """
    
    def __init__(self, *args, **kwargs):
        logFile.info("*********** Starting %s plugin version v%s ***********", config.appName, config.version)
        logFile.debug(sys.argv)
        self.pluginName = sys.argv[0]
        self.handle = int(sys.argv[1])
        self.params = sys.argv[2].strip('?')
        
        # channel objects
        self.channelObject = ""
        self.channelFile = ""
        self.channelCode = ""   
        self.channelObject = ""     
        self.splitChar = "[[#]]"
        
        logFile.debug("Plugin Params: %s", self.params)   
        #===============================================================================
        #        Start the plugin version of progwindow
        #===============================================================================
        if self.params=='':
            # check for updates
            import update
            try:
                logFile.CleanUpLog()
                common.DirectoryPrinter(config.rootDir)
                update.CheckVersion(config.version, config.updateUrl)
            except:
                logFile.critical("Error checking for updates", exc_info=True)
        
            # now show the list
            self.ShowProgramList()
        #===============================================================================
        #        Start the plugin verion of the episode window
        #===============================================================================
        else:
            try:
                # determine what stage we are in. Therefore we split the
                # params and check the number of different ones.
                self.params = self.params.split(self.splitChar)
                logFile.debug(self.params)
                
                # Check that there are more than 2 Parameters
                if len(self.params)>1:
                    # retrieve channel characteristics
                    self.channelFile = os.path.splitext(self.params[0])[0]
                    self.channelCode = self.params[1]
                    #logFile.debug(self.channelCode)
                    
                    # import the channel
                    self.channelDir = os.path.join(config.rootDir, "channels", self.channelFile.replace('chn_', ''))
                    sys.path.append(self.channelDir)
                    logFile.info("Importing %s from %s", self.channelFile, self.channelDir)
                    exec("import %s" % self.channelFile)
                    logFile.debug(channelRegister)
                    if len(channelRegister)==1:
                        logFile.info("Only one channel present. Intialising it.")
                        self.channelObject = eval(channelRegister[0])
                    else:
                        #determine from channelCode
                        for channel in channelRegister:
                            #logFile.debug("%s (%s)", channel,string.count(channel, 'channelCode="%s"' % (self.channelCode))>0)
                            if string.count(channel, "channelCode=\"%s" % self.channelCode)>0:
                                logFile.debug("caught: %s", channel)
                                self.channelObject = eval(channel)
                                break
                    if self.channelObject == None:
                        logFile.critical("No channel found to be loaded!")
                        return
                    
                    # init the channel as plugin
                    self.channelObject.initPlugin()
                    logFile.info("Loaded: %s", self.channelObject.channelName)
                else:
                    logFile.critical("Error determining Plugin action")
                    return
                
                #===============================================================================
                # See what needs to be done.    
                #===============================================================================
                if len(self.params)==2:
                    # only the channelName and code is present, so ParseMainList is needed
                    self.ParseMainList()

                elif len(self.params)==3:
                    # channelName and URL is present, Parse the folder
                    self.ProcessFolderList()

                elif len(self.params)>3 and self.params[2]=='processVideo':
                    # a videoitem was given with an additional paramters
                    self.ProcessVideoItem()
                
                elif len(self.params)>3 and self.params[2]=='downloadVideo':
                    # download the item
                    self.DownloadVideoItem()                
                
                #if self.handle > -1:
                #    xbmcplugin.endOfDirectory(self.handle)
            except:
                logFile.critical("Error parsing for plugin", exc_info=True)
                #xbmcplugin.endOfDirectory(self.handle)

    #============================================================================== 
    def ShowProgramList(self):
        logFile.info("Plugin::ShowProgramList")
        try:
            # import ProgWindow
            import progwindow
            ok = False
            
            # first start of plugin! Show channels only!
            if len(self.params)<=2:
                #only display channels
                progWindowLib = progwindow.GUI(config.appSkin ,config.rootDir, config.skinFolder)
                for channelGUI in progWindowLib.channelGUIs:
                    item = xbmcgui.ListItem(channelGUI.channelName,channelGUI.channelDescription, channelGUI.icon , channelGUI.iconLarge)
                    item.setInfo("video", {"tracknumber": channelGUI.sortOrder, "Tagline":channelGUI.channelDescription})
                    logFile.debug(channelGUI.sortOrder)
                    url = "%s?%s%s%s" % (self.pluginName, channelGUI.moduleName, self.splitChar, channelGUI.channelCode)
                    #logFile.debug(url)
                    ok = xbmcplugin.addDirectoryItem(self.handle, url, item, isFolder=True)
                    if (not ok): break
            
            xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_TRACKNUM)
            #xbmcplugin.setContent(handle=self.handle, content="video")
            #xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_FILE)
            
            xbmcplugin.endOfDirectory(self.handle, ok)
        except:
            xbmcplugin.endOfDirectory(self.handle, False)
            logFile.critical("Error fetching channels for plugin", exc_info=True)
    
    #============================================================================== 
    def ParseMainList(self):
        """
            Wraps the channel.ParseMainList
        """
        logFile.info("Plugin::ParseMainList")
        try:
            # only the channelName and code is present, so ParseMainList is needed
            logFile.debug("Doing ParseMainlist")
            episodeItems = self.channelObject.ParseMainList()
            icon = self.channelObject.icon
            thumb = self.channelObject.iconLarge
            ok = False
            
            for episodeItem in episodeItems:
                logFile.debug(episodeItem.url)
                if episodeItem.date == '':
                    item = xbmcgui.ListItem(episodeItem.name, iconImage=icon, thumbnailImage=thumb)                    
                else:
                    item = xbmcgui.ListItem("%s (%s)" %(episodeItem.name, episodeItem.date), iconImage=icon, thumbnailImage=thumb)
                item.setInfo("video", {"date": episodeItem.date, "title": episodeItem.name, "PlotOutline": episodeItem.description})                
                
                # create item and add an extra space at the end to prevent removal of last /
                ok = xbmcplugin.addDirectoryItem(self.handle, "%s?%s%s%s%s%s " % (self.pluginName, self.channelObject.moduleName, self.splitChar, self.channelObject.channelCode, self.splitChar, episodeItem.url), item, isFolder=True)
                if (not ok): break

            
            #xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE)
            xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_DATE) 
            xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL) 
            
            # close the directory                
            xbmcplugin.endOfDirectory(self.handle, ok)
        except:
            xbmcplugin.endOfDirectory(self.handle, False)
            logFile.debug("Plugin::Error parsing mainlist", exc_info=True)
                
    #============================================================================== 
    def ProcessFolderList(self):
        """
            Wraps the channel.ProcessFolderList
        """
        logFile.info("Plugin::ProcessFolderList Doing ProcessFolderList")
        try:    
            # strip the extra space from the url
            self.params[2] = string.strip(self.params[2])
            ok = False
            
            episodeItems = self.channelObject.ProcessFolderList(self.params[2])
            logFile.debug("ProcessFolderList returned %s items", len(episodeItems))
            for episodeItem in episodeItems:
                logFile.debug("Adding: %s which complete=%s", episodeItem, episodeItem.complete)
                
                if episodeItem.type == 'folder' or episodeItem.type == 'append' or episodeItem.type == "page":
                    # it's a folder page or append style. Append as an XBMC folder
                    item = xbmcgui.ListItem(episodeItem.name)#, self.channelObject.folderIcon, self.channelObject.folderIcon)
                    item.setInfo("video", {"date": episodeItem.date, "title": episodeItem.name, "PlotOutline": episodeItem.description})                
                    ok = xbmcplugin.addDirectoryItem(self.handle, "%s?%s%s%s%s%s " % (self.pluginName, self.channelObject.moduleName, self.splitChar, self.channelObject.channelCode, self.splitChar, episodeItem.url), item, isFolder=True)
                
                elif episodeItem.type=="video":
                    if len(episodeItem.MediaListItems) == 1 and episodeItem.complete == True and episodeItem.downloadable == False:
                         # it's a complete item with only 1 url
                        item = xbmcgui.ListItem(episodeItem.name, iconImage=self.channelObject.icon, thumbnailImage=self.channelObject.iconLarge)
                        item.setInfo("video", {"date": episodeItem.date, "title": episodeItem.name, "PlotOutline": episodeItem.description})                
                        ok = xbmcplugin.addDirectoryItem(int(self.handle), "%s " % (episodeItem.MediaListItems[0].Url), item)
                    else:   
                        # all other options
                        item = xbmcgui.ListItem(episodeItem.name, iconImage=self.channelObject.icon, thumbnailImage=self.channelObject.iconLarge)
                        item.setInfo("video", {"date": episodeItem.date, "title": episodeItem.name, "PlotOutline": episodeItem.description})                
                        # create serialized cListItem 
                        pickleString = pickle.dumps(episodeItem,0)
                        ok = xbmcplugin.addDirectoryItem(self.handle, "%s?%s%s%s%sprocessVideo%s%s " % (self.pluginName, self.channelObject.moduleName, self.splitChar, self.channelObject.channelCode, self.splitChar, self.splitChar, pickleString), item, isFolder=True)                    
                else:
                    logFile.critical("Plugin::ProcessFolderList: Cannot determine what to add")
                    
                if (not ok): break
            
            xbmcplugin.addSortMethod(handle=int(self.handle), sortMethod=xbmcplugin.SORT_METHOD_DATE) 
            xbmcplugin.addSortMethod(handle=int(self.handle), sortMethod=xbmcplugin.SORT_METHOD_LABEL) 
            
            xbmcplugin.endOfDirectory(self.handle, ok)
        except:
            xbmcplugin.endOfDirectory(self.handle, False)
            logFile.debug("Plugin::Error Processing FolderList", exc_info=True)
                

    #==============================================================================
    def ProcessVideoItem(self):
        """
            Wraps the channel.UpdateVideoItem and adds an folder with videofile options like
            download and play videoitem
        """
        logFile.info("Plugin::ProcessVideoItem starting")
            
        try:
            
            # de-serialize
            pickleString = self.params[3];
            pickleItem = pickle.loads(pickleString)
            ok = False
            
            episodeItem = pickleItem
            logFile.debug("De-Pickled: %s", episodeItem)
            if episodeItem.date != '':
                episodeItem.name = "%s (%s)" % (episodeItem.name, episodeItem.date)
            
            #update the item is not up to date
            if episodeItem.complete==False:
                logFile.debug("Trying to update a videoItem")
                episodeItem =self.channelObject.UpdateVideoItem(episodeItem)
                if len(episodeItem.MediaListItems) == 0:
                    episodeItem.complete = False;
                    
                logFile.debug("Updated MediaItem: %s", episodeItem)
            
            if episodeItem.complete==True and len(episodeItem.MediaListItems) > 0:
                title = "Play Item: %s " % episodeItem.name
                count = 1
                for mediaListItem in episodeItem.MediaListItems:
                    name = "%s(%s)" % (title, count)
                    xbmcListItem = mediaListItem.GetXBMCListItem(name)
                    xbmcListItem.setIconImage(self.channelObject.icon)
                    xbmcListItem.setThumbnailImage(self.channelObject.iconLarge)
                    logFile.debug("Adding item #%s (%s) with url %s", count, name, mediaListItem)
                    logFile.debug(xbmcListItem.getProperty("SWFPlayer"))
                    logFile.debug(xbmcListItem.getProperty("PlayPath"))
                    logFile.debug(xbmcListItem.getProperty("PageURL"))
                    #item = xbmcgui.ListItem(name, episodeItem.name, self.channelObject.icon, self.channelObject.iconLarge)
                    #item.setInfo("video", {"date": episodeItem.date, "title": name, "PlotOutline": episodeItem.description})                
                    ok = xbmcplugin.addDirectoryItem(int(self.handle), url="%s" % mediaListItem.Url, listitem=xbmcListItem)                    
                    count = count + 1
                    if not ok:
                        break
                    
            else:
                logFile.error("could not update videoItem")
            
            if episodeItem.downloadable == True:
                title = "Download Item: %s" % episodeItem.name
                item = xbmcgui.ListItem(title, episodeItem.name, self.channelObject.icon, self.channelObject.iconLarge)                
                item.setInfo("video", {"date": episodeItem.date, "title": title, "PlotOutline": episodeItem.description})
                pickleString = pickle.dumps(episodeItem)                
                ok = xbmcplugin.addDirectoryItem(int(self.handle), "%s?%s%s%s%sdownloadVideo%s%s " % (self.pluginName, self.channelObject.moduleName, self.splitChar, self.channelObject.channelCode, self.splitChar, self.splitChar, pickleString), item)                
            
            #xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_TITLE)
            xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)            
            xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL) 
            
            xbmcplugin.endOfDirectory(self.handle, ok)        
        except:
            xbmcplugin.endOfDirectory(self.handle, False)   
            logFile.critical("Error Updating VideoItem", exc_info=True)
            pass
        
    #==============================================================================
    def DownloadVideoItem(self):
        """
        Warps the DownloadVideoItem method. Downloads the item, show the diffent dialogs.
        """
        logFile.info("Plugin::DownloadVideoItem starting")
            
        try:
            logFile.debug("Trying to update a videoItem")
            
            # de-serialize
            pickleString = self.params[3];
            pickleItem = pickle.loads(pickleString)
            self.channelObject.DownloadVideoItem(pickleItem)            
            xbmcplugin.endOfDirectory(self.handle, True)
        except:
            logFile.critical("Error Downloading VideoItem", exc_info=True)
            xbmcplugin.endOfDirectory(self.handle)   
