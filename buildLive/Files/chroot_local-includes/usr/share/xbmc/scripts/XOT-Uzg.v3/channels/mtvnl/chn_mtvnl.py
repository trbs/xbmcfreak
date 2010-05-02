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

register.channelRegister.append('chn_mtvnl.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="mtvnl")')

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
        self.guid = "7C52452A-F2F9-11DD-BE3F-3F7356D89593"
        self.icon = "mtvnlicon.png"
        self.iconLarge = "mtvnllarge.png"
        self.noImage = "mtvnlimage.png"
        self.channelName = "MTV.nl"
        self.maxXotVersion = "3.2.0"
        self.channelDescription = "MTV.nl Episodes"
        self.moduleName = "chn_mtvnl.py"
        self.mainListUri = "http://www.mtv.nl/artikel.php?article=6330"
        self.baseUrl = "http://nl.esperanto.mtvi.com/www/xml"
        self.onUpDownUpdateEnabled = True
        self.sortOrder = 9
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<a href="(http://www.mtv.nl/artikel.php\?article=\d+)"[^<]+><strong>([^<]+)<' # used for the ParseMainList
        self.videoItemRegex = '<td>(\W{0,1}<a href="javascript:launchOverdrive\([^)]+\'(id=\d+)\'\);">([^<]*)</a>)(\W{0,1}<a [^>]+>([^<]*)</a>){0,1}(\W{0,1}<a [^>]+>([^<]*)</a>){0,1}\W{0,1}</td>[\n\r]'   # used for the CreateVideoItem 
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
        
        # <li><a href="(/guide/season/[^"]+)">(\d+)</a></li>
        item = mediaitem.MediaItem(resultSet[1], resultSet[0])
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
        """
        (
        0 '<a href="javascript:launchOverdrive(\'name=ontv\',\'id=106960\');">Fur TV - Episode 101 </a>'
        1 'id=106960'
        2 'Fur TV - Episode 101 '
        3, ''
        4, 'test'
        5, ''
        6, 'test')
        """
        item = mediaitem.MediaItem("%s%s%s" % (resultSet[2], resultSet[4], resultSet[6]), "%s/content.jhtml?%s" % (self.baseUrl, resultSet[1]))
        
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
        
        data = uriHandler.Open(item.url,pb=False)
        info = common.DoRegexFindAll('<image>([^<]*)</image>[\W\w]+<headline><!\[CDATA\[([^<]+)\]\]></headline>[\W\w]*<subhead><!\[CDATA\[([^<]+)\]\]></subhead>', data)
        if len(info)> 0:
            info = info[0]
            
        #logFile.debug(info)
        
        item.description = "%s %s" % (info[1], info[2])
        item.name = info[1]
        item.thumbUrl = info[0]
        
        if item.thumbUrl != "":
            item.thumb = self.CacheThumb(item.thumbUrl)
        else:
            item.thumb = self.noImage
        
        # get the RTMP urls
        #<src>rtmp://cp40493.edgefcs.net/ondemand/comedystor/_!/com/sp/acts/Season01/E_0102/compressed/flv/0102_3_DI_640x480_500kbps.flv</src>
        #rtmp://cp40493.edgefcs.net/ondemand?slist=comedystor/_!/com/sp/acts/Season01/E_0106/compressed/flv/0106_4_DI_640x480_700kbps 
        urlInfo = common.DoRegexFindAll('<videourl>/www/xml([^<]+)</videourl>', data)
        for url in urlInfo:
            rtmpData = uriHandler.Open("%s%s" % (self.baseUrl, url), pb=False)
            rtmpUrl = common.DoRegexFindAll('<src>([^<]+ondemand)/([^<]+).flv</src>', rtmpData)[-1]
            item.AppendMediaListItem("%s?slist=%s" % rtmpUrl)
        
        item.complete = True         
        logFile.debug("Media url of item: %s", item)
        
        return item    