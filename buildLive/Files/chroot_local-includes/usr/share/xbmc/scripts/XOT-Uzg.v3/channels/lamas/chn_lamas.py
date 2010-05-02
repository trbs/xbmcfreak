#===============================================================================
# Import the default modules
#===============================================================================
import xbmc, xbmcgui
import re, sys, os

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
register.channelRegister.append('chn_lamas.Channel("uzg-channelwindow.xml", config.rootDir, config.skinFolder, channelCode="delamas")')

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
        
        self.guid = "9B43CA5A-42F3-11DD-9D91-B6F355D89593"
        self.icon = "lamasicon.png"
        self.iconLarge = "lamasiconlarge.png"
        self.noImage = "lamasimage.png"
        self.channelName = "De Lama's"
        self.channelDescription = "Al de clips en bonus materiaal van De Lama's site"
        self.moduleName = "chn_lamas.py"
        self.maxXotVersion = "3.2.0"
        self.sortOrder = 255
        
        self.mainListUri = "http://www.delamas.nl"
        self.baseUrl = "http://www.bnn.nl/players/MDPlayerCore/public/xml/"
        self.onUpDownUpdateEnabled = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=False))            
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        self.requiresLogon = False
        
        self.episodeItemRegex = '' # used for the ParseMainList
        self.videoItemRegex = '<item>\W+<id>([^<]+)</id>\W+<title>([^<]+)</title>\W+<de[^>]+n>(&lt;(p|font face=&quot;Arial&quot;)&gt;)*([^</]+)(&lt;[^<]+)*</description>\W+<play_count>[^<]+</play_count>\W+<rate_avg>[^<]+</rate_avg>\W+<rate_count>[^<]+</rate_count>\W+<thumbnail>([^<]+)</thumbnail>'   # used for the CreateVideoItem 
        self.folderItemRegex = ''  # used for the CreateFolderItem
        self.mediaUrlRegex = '<source>([^<]+)</source>'    # used for the UpdateVideoItem
        
        #========================================================================== 
        # non standard items
        self.topDescription = ""
        
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnDownloadItem(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.listItems[selectedIndex] = self.DownloadVideoItem(item)

    def CtMnPlayMplayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item, "mplayer")
    
    def CtMnPlayDVDPlayer(self, selectedIndex):
        item = self.listItems[selectedIndex]
        self.PlayVideoItem(item,"dvdplayer")    
          
    #==============================================================================
    def ParseMainList(self):
        """ 
        accepts an url and returns an list with items of type CListItem
        Items have a name and url. This is used for the filling of the progwindow
        """
        items = []
        
        itemBonusNew = mediaitem.MediaItem("Bonus Materiaal (Op datum)", "http://www.bnn.nl/players/MDPlayerCore/public/xml/md_lister.xml.php?cat=bonus&sort=creationDate&show_start=0&show_count=500&instance=lamas/", "folder")
        itemBonusNew.icon = self.folderIcon
        itemBonusRanked = mediaitem.MediaItem("Bonus Materiaal (Op ranking)", "http://www.bnn.nl/players/MDPlayerCore/public/xml/md_lister.xml.php?cat=bonus&sort=rateAverage&show_start=0&show_count=500&instance=lamas/", "folder")
        itemBonusRanked.icon = self.folderIcon
        itemBonusView = mediaitem.MediaItem("Bonus Materiaal (Op views)", "http://www.bnn.nl/players/MDPlayerCore/public/xml/md_lister.xml.php?cat=bonus&sort=playCount&show_start=0&show_count=500&instance=lamas/", "folder")
        itemBonusView.icon = self.folderIcon
        
        itemClipsNew = mediaitem.MediaItem("Clips (Op datum)", "http://www.bnn.nl/players/MDPlayerCore/public/xml/md_lister.xml.php?cat=clips&sort=creationDate&show_start=0&show_count=500&instance=lamas/", "folder")
        itemClipsNew.icon = self.folderIcon
        itemClipsRanked = mediaitem.MediaItem("Clips (Op ranking)", "http://www.bnn.nl/players/MDPlayerCore/public/xml/md_lister.xml.php?cat=clips&sort=rateAverage&show_start=0&show_count=500&instance=lamas/", "folder")
        itemClipsRanked.icon = self.folderIcon 
        itemClipsView = mediaitem.MediaItem("Clips (Op views)", "http://www.bnn.nl/players/MDPlayerCore/public/xml/md_lister.xml.php?cat=clips&sort=playCount&show_start=0&show_count=500&instance=lamas/", "folder")
        itemClipsView.icon = self.folderIcon
            
        items.append(itemBonusNew)
        items.append(itemBonusRanked)
        items.append(itemBonusView)
        
        items.append(itemClipsNew)
        items.append(itemClipsRanked) 
        items.append(itemClipsView)
            
        return items
       
    #============================================================================= 
    def CreateVideoItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #logFile.debug('starting CreateVideoItem for %s', self.channelName)
        #http://www.bnn.nl/players/MDPlayerCore/public/xml/md_player.xml.php?id=057ecea4859307cc0f583bc503fdecd7&instance=lamas/
        #logFile.debug(len(resultSet))
        #logFile.debug(resultSet)
        """
        0 '82a5b0b32929776fca27f1a8fce532af', 
        1 "Backstage bij de laatste Lama's", 
        2 '&lt;p&gt;', 
        3 'p', 
        4 "De Lama's nemen afscheid in stijl!", 
        5 '&lt;/p&gt;', 
        6 'http://download.bnn.nl/bnn/mediadepot/media_thumbnails/14/8440.jpg'        
        """
        item = mediaitem.MediaItem(resultSet[1], "http://www.bnn.nl/players/MDPlayerCore/public/xml/md_player.xml.php?id=%s&instance=lamas/" % (resultSet[0]))
        
        item.description = "%s\n\n%s" % (resultSet[1], resultSet[4])
        item.icon = self.icon
        
        # temp store the thumb for use in UpdateVideoItem
        item.thumbUrl = resultSet[6]
        item.thumb = self.noImage
        item.type = 'video'
        item.downloadable = True
        
        # getting the URL is part of the PlayVideo
        item.complete = False
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb!
        """
        logFile.info('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        _data = uriHandler.Open(item.url, pb=False)

        item.AppendMediaListItem(common.DoRegexFindAll(self.mediaUrlRegex, _data)[-1])
        item.thumb = self.CacheThumb(item.thumbUrl)

        logFile.info('finishing UpdateVideoItem: %s', item)
        
        item.complete = True
        return item
        