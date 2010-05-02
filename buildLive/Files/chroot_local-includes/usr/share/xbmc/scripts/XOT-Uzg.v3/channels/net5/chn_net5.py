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
register.channelRegister.append('chn_net5.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="net5")')

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
        
        self.guid = "B374230E-42F3-11DD-984E-E2F555D89593"
        self.icon = "net5icon.png"
        self.iconLarge = "net5large.png"
        self.noImage = "net5image.png"
        self.channelName = "Net 5"
        self.maxXotVersion = "3.2.0"
        self.channelDescription = "Online uitzendingen van www.net5.nl."
        self.sortOrder = 6
        self.moduleName = "chn_net5.py"
        self.mainListUri = "http://www.net5.nl/web/show/id=95681/langid=43"
        self.baseUrl = "http://www.net5.nl"
        self.onUpDownUpdateEnabled = True
        
        self.contextMenuItems = []
#        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=None))            
#        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<div class="thumb">\W+<a[^>]+href="(/[^"]+)"[^>]*>\W+<img[^>]+alt="([^"]+)"/>' # used for the ParseMainList
        self.videoItemRegex = '<div class="item[^"]*">(\W+<div class="thumb"><[^<]+<img src="([^"]+)" [^>]+></a></div>)*[\W]+<div class="title"><a +href="([^"]+)" [^>]+><span>([^<]+)</span></a></div>[\W]+<div class="airtime"><[^<]+<span>([^<]+)</span></a></div>\W+()*<div class="text"><[^<]+<span>([^<]*)</span></a></div>'   # used for the CreateVideoItem 
        self.pageNavigationRegex = '<a href="([^"]+)(\d+)"><span>\d+</span></a>' #self.pageNavigationIndicationRegex 
        self.pageNavigationRegexIndex = 1
                
        # decrepated. Using url based on ID now
        #self.mediaUrlRegex = '<param name="src" value="([^"]+)" />'    # used for the UpdateVideoItem
        
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
#    def CtMnUpdateItem(self, selectedIndex):
#        logFile.debug('Updating item (Called from ContextMenu)')
#        self.onUpDown(ignoreDisabled = True)
#    
#    def CtMnDownloadItem(self, selectedIndex):
#        item = self.listItems[selectedIndex]
#        self.listItems[selectedIndex] = self.DownloadEpisode(item)

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
        
        # dummy class
        item = mediaitem.MediaItem(resultSet[1], urlparse.urljoin(self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.complete = True
        return item
    
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        logFile.debug('starting CreateVideoItem for %s', self.channelName)
        #logFile.debug(resultSet)
        
        item = mediaitem.MediaItem(resultSet[3], urlparse.urljoin(self.baseUrl, resultSet[2]))
        
        item.thumb = self.noImage 
        if (resultSet[0] != ""):
            item.thumbUrl = urlparse.urljoin(self.baseUrl, resultSet[1])
        else:
            item.thumbUrl = ""

        item.icon = self.icon
        item.date = resultSet[4]
        item.description = resultSet[6]                                
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
        
        item.thumb = self.CacheThumb(item.thumbUrl)        
        
        # now the mediaurl is derived
        # http://www.garnierstreamingmedia.com/asx/openclip.asp?file=/sbs6/net5/juliastango_S02/juliastango_S02E07.wmv
        #                                             http://asx.sbsnet.nl/net5/juliastango_S02/juliastango_S02E07.wmv
        
        data = uriHandler.Open(item.url, pb=False)
        urls = common.DoRegexFindAll('<a class="wmv-player-holder" href="(http://asx.sbsnet.nl/net5/)([^"]+)"></a>', data)
        for url in urls:
            item.AppendMediaListItem("http://www.garnierstreamingmedia.com/asx/openclip.asp?file=/sbs6/net5/%s" % (url[1]))
        
        if item.HasMediaListItems():
            logFile.debug("Media url was found: %s", item)
            item.complete = True
        else:
            logFile.debug("Media url was not found.")
        return item    