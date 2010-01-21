import xbmc, xbmcgui
import sys, re, urllib, math
#===============================================================================
# Make global object available
#===============================================================================
import common
import mediaitem
import config
import controls
import contextmenu
import chn_class
import algorithms

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler
#===============================================================================
# register the channels
#===============================================================================
if (sys.modules.has_key('progwindow')):
    register = sys.modules['progwindow']
elif (sys.modules.has_key('plugin')):
    register = sys.modules['plugin']
#register.channelButtonRegister.append(105)
register.channelRegister.append('chn_quicksilver.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder)')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self)
        
        self.guid = "1ABEDEDC-42F4-11DD-86A5-EAFF55D89593"
        self.mainListUri = "http://quicksilverscreen.com/"
        self.baseUrl = "http://quicksilverscreen.com/"
        self.icon = "quicksilverthumb.png"
        self.iconLarge = "quicksilverlarge.png"
        self.noImage = "quicksilverimage.png"
        self.channelName = "Quicksilver Screen"
        self.channelDescription = "Watch TV shows online free"
        self.moduleName = "chn_quicksilver.py"
        self.maxXotVersion = "3.2.0"
        self.onUpDownUpdateEnabled = False
        
        self.requiresLogon = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=False))            
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        self.episodeItemRegex = '<li><a href="(videos\?c=\d+)">([^<]+)</a></li>'
        #self.videoItemRegex = '<a href="(watch\?video=\d+)"><img src="([^"]+)[^;]+[^<]+<a href="(watch\?video=\d+)">([^<]+)</a>' 
        self.videoItemRegex = '<a href="(watch\?video=\d+)"><img src="([^"]+)[^;]+[^<]+<a href=["\'](watch\?video=\d+)["\']>(<small>\[[^]]+\]</small> )*([^<]+)</a>'
        self.folderItemRegex = '<a href="(videos\?c=\d+)">([^<]+)</a><br/>[\r\n]'
        self.mediaUrlRegex = '<embed type="video/divx" src="([^"]+)" pluginspage'
        
        """ 
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the 
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added. 
        """
        self.pageNavigationRegex = '<li><a rel="nofollow" href="(videos\?[^"]+page=)(\d+)">\d+</a></li>'  
        self.pageNavigationRegexIndex = 1 

        #============================================================================== 
        # non standard items
        self.PreProcessRegex = '<ul title="([^"]*)" rel="([^"]*)videomenu.xml"'
        self.progTitle = ""
        self.videoMenu = ""

        return True
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.info('starting CreateEpisodeItem for %s', self.channelName)
        #<li><a href="(videos\?c=\d+)">([^<]+)</a></li>
        item = mediaitem.MediaItem(resultSet[1], "http://quicksilverscreen.com/%s" % (resultSet[0]))
        item.icon = self.folderIcon
        return item
    
    #==============================================================================
    def PreProcessFolderList(self, data):
        """
        Accepts an data from the ProcessFolderList Methode, BEFORE the items are
        processed. Allows setting of parameters (like title etc). No return value!
        """
        _items = []
        
        # strip the last part of the HTML to prevent the channels to appear as folders
        newdata = common.DoRegexFindAll("([\w\W]+)<h3>Channels:</h3>", data)
        if len(newdata)>0:
            data = newdata[0]
            
        return (data, _items)        
    
    #==============================================================================
    def CreateFolderItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.debug('starting CreateFolderItem for %s', self.channelName)
        #<a href="(videos\?c=\d+)">([^<]+)</a><br/>
        item = mediaitem.MediaItem(resultSet[1], "http://quicksilverscreen.com/%s" % (resultSet[0]))
        item.icon = self.folderIcon
        item.type = 'folder'
        item.thumb = self.noImage
        item.complete = True
        
        item.description = resultSet[1]
        if not self.pluginMode:
            # and only if we have at least 2 history items (first one is always: "Loading data")
            if len(self.folderHistory) > 1:
                if not self.folderHistory[-1].description == "":
                    item.description = "%s\n%s" % (self.folderHistory[-1].description, resultSet[1])
        
        return item
    
    #==============================================================================
    def CreateAppendItem(self, resultSet, pageNr):
        """
        Accepts an resultset
        """
        item = mediaitem.MediaItem("Page %s" % pageNr, "%s%s%s" % (self.mainListUri, resultSet[0], pageNr), type="append")
        item.icon = self.appendIcon  
        item.thumb = self.noImage      
        return item 
        
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.debug('starting FormatVideoItem for %s', self.channelName)
        #'<a href="(watch\?video=\d+)"><img src="([^"]+)[^;]+[^<]+<a href=["\'](watch\?video=\d+)["\']>(<small>\[[^]]+\]</small> )*([^<]+)</a>'
        #                 0                            1                               2                       3                      4
        item = mediaitem.MediaItem(resultSet[4], "http://quicksilverscreen.com/%s" % (resultSet[2]))
        
        item.description = resultSet[4]
        if not self.pluginMode:
            # and only if we have at least 2 history items (first one is always: "Loading data")
            if len(self.folderHistory) > 1:
                if not self.folderHistory[-1].description == "":
                    item.description = "%s\n%s" % (self.folderHistory[-1].description, resultSet[4])
        
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = resultSet[1]
        item.type = 'video'
        item.complete = False        
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        #logFile.debug('starting UpdateVideoItem for %s (%s)',item.name, self.channelName)
        item.thumb = self.CacheThumb(item.thumbUrl)
        # open the url to read the media url
        data = uriHandler.Open(item.url, pb=False)
        
        # create the algorithm helper
        algHelper = algorithms.Algorithms()

        results = common.DoRegexFindAll(self.mediaUrlRegex, data)
        megavideoResults = common.DoRegexFindAll('<param name="movie" value="([^"]+)"></param>', data)
        veohResults = common.DoRegexFindAll('src="http://www.veoh.com/[^?]+\?permalinkId=([^&]+)', data)
        googleResults = common.DoRegexFindAll('(http://video.google.com/googleplayer.swf\?docId=[^"]+)"', data)
        
        # First give it a try using the default regex
        item.complete = True
        if len(results)>0:
            item.AppendMediaListItem(results[-1])
            logFile.debug("MediaUrl found: %s", results[-1])
        
        # If there were no results, try megavideo.com 
        elif len(megavideoResults) > 0:
            url = megavideoResults[-1]
            url = algHelper.DecodeItemUrl(url)
            data = uriHandler.Open(url, pb=True) 
            item.AppendMediaListItem(algHelper.ExtractMediaUrl(url, data))
        
        # then try veoh
        elif len(veohResults) > 0:
            url = "http://www.veoh.com/videos/%s?cmpTag" % veohResults[-1]
            url = algHelper.DecodeItemUrl(url)
            data = uriHandler.Open(url, pb=True)
            item.AppendMediaListItem(algHelper.ExtractMediaUrl(url, data))
        
        # then google
        elif len(googleResults) > 0:
            url = googleResults[-1]
            url = algHelper.DecodeItemUrl(url)
            data = uriHandler.Open(url, pb=True)
            item.AppendMediaListItem(algHelper.ExtractMediaUrl(url, data))
            
        # If all else fails, return an error
        else:
            item.MediaListItems = []
            logFile.error("MediaUrl not found in url: %s", item.url)
            item.complete = False
        
        logFile.debug("Item was updated with mediaUrl: %s", item)
        return item
    
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnUpdateItem(self, selectedIndex):
        logFile.debug('Updating item (Called from ContextMenu)')
        #tempPB = uriPB = xbmcgui.DialogProgress()
        #tempPB.create("Updating item", "Please Wait")
        xbmcgui.lock()
        self.onUpDown(ignoreDisabled = True)
        xbmcgui.unlock()
        #tempPB.close()
    
    def CtMnDownloadItem(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.listItems[selectedIndex] = self.DownloadEpisode(item)

    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item,"dvdplayer")    
    
    