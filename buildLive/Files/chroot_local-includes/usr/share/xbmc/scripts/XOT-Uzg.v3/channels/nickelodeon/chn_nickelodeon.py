#===============================================================================
# Import the default modules
#===============================================================================
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

register.channelRegister.append('chn_nickelodeon.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="nickelodeon")')

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
        self.guid = "8D4EBAE8-F3C6-11DD-92EE-F2FE55D89593"
        self.icon = "nickelodeonicon.png"
        self.iconLarge = "nickelodeonlarge.png"
        self.noImage = "nickelodeonimage.png"
        self.channelName = "Nickelodeon TurboNick"
        self.maxXotVersion = "3.2.0"
        self.channelDescription = "TurboNick afleveringen van Nickelodeon"
        self.moduleName = "chn_nickelodeon.py"
        self.mainListUri = "http://www.nickelodeon.nl/turbonick"
        self.baseUrl = "http://www.nickelodeon.nl"
        self.onUpDownUpdateEnabled = True
        self.sortOrder = 11
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<span[^>]+class="list_title"[^>]+>\W+<a[^>]+href="(/turbonick/programma/[^"]+)" title="([^"]+)">' # used for the ParseMainList
        self.videoItemRegex = '<a[^>]+href="(/turbonick/bekijk/[^"]+)"[^>+]title="([^"]+)">\W+<img[^>]+src="([^"]+)"[^>]+/>\W+</a>'   # used for the CreateVideoItem 
#        self.folderItemRegex = '<a href="\.([^"]*/)(cat/)(\d+)"( style="color:\s*white;"\s*)*>([^>]+)</a><br'  # used for the CreateFolderItem
        self.mediaUrlRegex = '<param name="src" value="([^"]+)" />'    # used for the UpdateVideoItem
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
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateEpisodeItem for %s', self.channelName)
        
        item = mediaitem.MediaItem(resultSet[1], "%s%s" % (self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateVideoItem for %s', self.channelName)
        
        item = mediaitem.MediaItem(resultSet[1], "%s%s" % (self.baseUrl, resultSet[0]))
        
        item.thumbUrl = resultSet[2]
        item.icon = self.icon
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
        
        if item.thumbUrl != "":
            item.thumb = self.CacheThumb(item.thumbUrl)
        else:
            item.thumb = self.noImage
        
        data = uriHandler.Open(item.url, pb=False)
        
        info = common.DoRegexFindAll("var voteUrl = '/scripts/global/vote.php\?type=video&id=(\d+)';\W+var voteAvg\W*(\d+)", data)
        if len(info) < 1:
            logFile.error("Cannot find info and ID information")
            return item
        else:
            info = info[0]
                
        # get the rank
        item.rating = int(info[1])
        
        # get the RTMP url 
        rtmpInfoUrl = "%s/feeds/turbonick/mediaGen.php?id=%s" % (self.baseUrl, info[0])
        rtmpData = uriHandler.Open(rtmpInfoUrl, pb=False)
        rtmpUrls = common.DoRegexFindAll("<src>(rtmp[^<]+)</src>" ,rtmpData)
        
        for rtmpUrl in rtmpUrls:
            item.AppendMediaListItem(rtmpUrl)
        
        item.complete = True
        logFile.debug("Media url: %s", item)
        return item    