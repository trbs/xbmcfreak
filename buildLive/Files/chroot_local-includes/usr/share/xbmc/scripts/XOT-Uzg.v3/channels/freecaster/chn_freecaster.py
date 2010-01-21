#===============================================================================
# Import the default modules
#===============================================================================
from beautifulsoup import ResultSet
from cgi import log
import xbmc, xbmcgui
import re, sys, os
import urlparse
#===============================================================================
# Make global object available
#===============================================================================
import common
import mediaitem
import config
import controls
import contextmenu
import chn_class
import helpers
from helpers import htmlentityhelper

logFile = sys.modules['__main__'].globalLogFile
uriHandler = sys.modules['__main__'].globalUriHandler

#===============================================================================
# register the channels
#===============================================================================
if (sys.modules.has_key('progwindow')):
    register = sys.modules['progwindow']
elif (sys.modules.has_key('plugin')):
    register = sys.modules['plugin']
#register.channelButtonRegister.append(108)

register.channelRegister.append('chn_freecaster.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="freecaster")')

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """
    
    #===============================================================================
    def InitialiseVariables(self):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self)
        self.guid = "52230AF6-FBA9-11DD-87D4-15B656D89593"
        self.icon = "freecastericon.png"
        self.iconLarge = "freecasterlarge.png"
        self.noImage = "freecasterimage.png"
        self.channelName = "Freecaster.tv"
        self.maxXotVersion = "3.2.0"
        self.channelDescription = "Freecaster.tv movies"
        self.moduleName = "chn_freecaster.py"
        self.mainListUri = "http://freecaster.tv/"
        self.baseUrl = "http://www.freecaster.tv"
        self.onUpDownUpdateEnabled = True
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<li>\W+<a href="http://freecaster.tv([^"]+)" title=[^>]+>([^<]+)</a>\W+</li>'
        self.folderItemRegex = ''
        self.videoItemRegex = '<h3>(<span[^/]+</span>)*<a href="http://freecaster.tv([^"]+)" title="([^"]+)">([^<]+)</a></h3>\W*<a[^>]+><img src="([^"]+)"[^>]+></a>(<p[^>]+>([^<]*)</p>){0,1}' 
        self.mediaUrlRegex = '<param\W+name="URL"\W+value="([^"]+)"'
        self.pageNavigationRegex = '<a rel="pagination" href="([^"]+)(\d+)">\d+</a>' 
        self.pageNavigationRegexIndex = 1 
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item,"dvdplayer")    
    
    def CtMnDownloadItem(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.DownloadVideoItem(item)
        
    #http://freecaster.tv/live
    #==============================================================================
    def ParseMainList(self):
        items = []
        items = chn_class.Channel.ParseMainList(self)
        
        #item = mediaitem.MediaItem("Livestreams", "http://freecaster.tv/live?page=1")
        #item.icon = self.icon
        #item.complete = True
        
        #items.append(item)
        return items
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #item = mediaitem.MediaItem(resultSet[0], "http://www.freecaster.com/helpers/videolist_helper.php?apID=%s&i=0&q=&sortby=date&sort=DESC&event_id=" % resultSet[1])
        item = mediaitem.MediaItem(resultSet[1], "%s%s?page=1" % (self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateVideoItem for %s', self.channelName)
        
        #<h3>(<span[^/]+</span>)*<a href="([^"]+)" title="([^"]+)">([^<]+)</a></h3>\W*<a[^>]+><img src="([^"]+)"[^>]+></a>(<p[^>]+>([^<]*)</p>){0,1}
        #                  0                1               2          3                                    4                5        6
        item = mediaitem.MediaItem(resultSet[3],"%s%s" % (self.baseUrl, resultSet[1]))
        if (resultSet[5] == ""):
            item.description = item.name
        else:
            item.description = resultSet[6]
            
        item.thumbUrl = resultSet[4]
        item.icon = self.icon
        #item.date = resultSet[5]
        item.type = 'video'
        item.complete = False
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        logFile.info('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        # get the thumb
        item.thumb = self.CacheThumb(item.thumbUrl)
        
        # get additional info
        data = uriHandler.Open(item.url, pb=False)
        guid = common.DoRegexFindAll('<link rel="video_src" type="" href="http://play.freecaster.com/player/FCPlayer.swf\?id=([^&]+)&autoplay=true" />', data)
        
        url = ''
        if len(guid) > 0:
            url = 'http://gateway.freecaster.com/VP/%s' % (guid[0],) 
        
        if url == '':
            logFile.error("Cannot find GUID in url: %s", item.url)
            return item
        
        data = uriHandler.Open(url, pb=False)
        urls = common.DoRegexFindAll('<stream[^>]+>([^>]+)</stream_[^>]+>', data)
        
        if len(urls) > 0:
            item.AppendMediaListItem(urls[0])
            item.complete = True
        
        logFile.debug("UpdateVideoItem complete: %s", item)
        
        return item    