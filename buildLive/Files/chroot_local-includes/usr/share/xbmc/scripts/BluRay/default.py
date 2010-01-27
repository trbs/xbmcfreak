import xbmc, xbmcgui, subprocess, os, time, sys, urllib, urllib2, re, xml.parsers.expat
  
__scriptname__ = "MakeMKV BluRay Watch Script"
__author__ = "Magnetism"
__url__ = "http://bultsblog.com/arne"
__credits__ = ""
__version__ = "0.2"


__language__ = xbmc.Language( os.getcwd() ).getLocalizedString
_ = sys.modules[ "__main__" ].__language__
__settings__ = xbmc.Settings( path=os.getcwd() )

class BluRaySettings:
  def __init__(self):
    self.local = __settings__.getSetting('local_remote') == "0"
    self.mkvLocation = __settings__.getSetting('mkvlocation')
    self.ipAddress = __settings__.getSetting('ip_address')
    self.portNumber =__settings__.getSetting('port_number')
    self.rootURL = 'http://%s:%s/' %(self.ipAddress, self.portNumber)
    self.autoPlay = __settings__.getSetting('auto_start') == "true"
    #Make sure local means 127.0.0.1 ...
    if (self.local):
      self.ipAddress = '127.0.0.1'


class BluRayStarter:
  def __init__(self):
    self.settings = BluRaySettings()
    self.pDialog = xbmcgui.DialogProgress()
    self.pDialog.create('XBMC', 'Starting BluRay', 'Intializing')

  def killAndStart(self):
    if self.settings.local:
      self.killMkv()
      # Determine if we're doing the disc or if we're browsing..
      choiceDialog = xbmcgui.Dialog()
      selection = choiceDialog.select(_(50003), [_(100), _(101)])
      mkvStart = "jjrkr3i3oqwjelrkjewlwrj"
      if selection == 0:
        self.pDialog.update(1,'XBMC', 'Waiting for Disc to be prepared', 'killing previous makemkvcon')
        mkvStart = '"%s" stream disc:0' %(self.settings.mkvLocation)
      elif selection == 1:
        choice = choiceDialog.browse(1, _(50004), 'video', 'index.bdmv|.iso|.MDS|.CUE|.CDI|.CCD', False, False, '') 
        if re.search("BDMV.index.bdmv", choice) :
          # Treat as file
          mkvStart = '"%s" stream file:%s' %(self.settings.mkvLocation, choice[:-15])
        else:
          # Treat as iso
          mkvStart = '"%s" stream iso:%s' %(self.settings.mkvLocation, choice)
      print mkvStart
      return subprocess.Popen(mkvStart, shell=True)
    else:
      return FakeFileClass()

  def killMkv(self):
    # Linux
    try :
      subprocess.call('killall -9 makemkvcon', shell=True)
    except:
      pass

    #Windows.
    try :
      subprocess.call('taskkill /F /IM makemkvcon.exe', shell=True)
    except:
      pass

  def browse(self, url) :
    self.pDialog.close()
    h = BrowseHandler()
    h.start(url)
    choiceDialog = xbmcgui.Dialog()
    selections = []
    paths = []
    for k,v in h.titleMap.iteritems() :
      #selections.append(xbmcgui.ListItem(k, 'duration %s, chapters: %s' %(v['duration'], v['chaptercount']), path = v['file']))
      selections.append("duration " + v['duration'] + ", chapters: 20" )
      paths.append(v['file'])
          #k + " d: " + v['duration'] + " c:" + v['chaptercount'])
    selection = choiceDialog.select('Test', selections)
    print selection
    print(paths[selection])
    xbmc.Player().play(paths[selection])


    #selection = SelDialog()
    #selection.setTitleItems(selections)
    #selection.doModal();
    #print selection.selection
    


  def process(self):
    timeSlept = 0
    try :
      tst = self.killAndStart()
      self.pDialog.update(2, 'XBMC', 'Waiting for Disc to be prepared', 'waiting for stream')
      m2tsTried = False      
      while True:   
        try:
          urllib.urlretrieve(self.settings.rootURL)
          # the Stream has started, start auto playback?
          if self.settings.autoPlay:
            if (m2tsTried) :
              xbmc.Player().play(self.settings.rootURL + 'stream/title0.vob')
            else :
              m2tsTried = True
              opener = urllib.URLopener()
              opener.open(self.settings.rootURL + 'stream/title0.m2ts')
              del opener
              xbmc.Player().play(self.settings.rootURL + 'stream/title0.m2ts')
          else:
            self.browse(self.settings.rootURL)
          break;
        except IOError:
          pass
        if self.pDialog.iscanceled():
          break
        if tst.poll() :
          if tst.returncode != 0 :
            self.message('Running MakeMKV endend abnormally. Is it installed?')
            break
        time.sleep(1)
        timeSlept = timeSlept + 1
        self.pDialog.update(timeSlept)
        if timeSlept > 120 :
          break
    except :
        self.message('Error trying to open makemkv stream ')
        self.pDialog.close()
        raise
    else :
        self.pDialog.close()

  def message(self, messageText):
    dialog = xbmcgui.Dialog()
    dialog.ok("Info", messageText)

class FakeFileClass:
  def poll(self):
    return False
 
class BrowseHandler:
  def __init__(self) :
    self.catchCharData = False
    self.keyColumn = False
    self.map = {}
    self.lastKey = ''
    self.lastVal = ''
    self.titleMap = {}
  
  def start(self, url, title = 'none'):
    # Initialize all locals
    p = xml.parsers.expat.ParserCreate()
    p.StartElementHandler = self.start_element
    p.CharacterDataHandler = self.char_data
    self.catchCharData = False
    self.keyColumn = False
    self.map[url] = {}
    self.currMap = self.map[url]
    self.lastKey = ''
    self.lastVal = ''
    filename, headers = urllib.urlretrieve(url)
    del headers
    file = open(filename, 'r')

    p.ParseFile(file)
    del file
    del p

    # Now do some processing:
    for k, v in self.map[url].iteritems() :
      if k == 'titles':
        # go straight ahead and parse some more:
        self.start(v)
      if re.search('title\d+', k) :
        self.titleMap[k] = {}
        self.start(v, k)
      if title != 'none':
        if k == 'duration':
          self.titleMap[title]['duration'] = v
        elif k == 'file0':
          self.titleMap[title]['file'] = v
        elif k == 'chaptercount':
          self.titleMap[title]['chaptercount'] = v




  def start_element(self, name, attrs):
    if name == 'td' :
      self.catchCharData = True
      self.keyColumn = not self.keyColumn
    elif name == 'a' and self.catchCharData :
      #We're in a href, the char data doesn't matter, but the href does
      self.currMap[self.lastKey] = attrs['href']
      self.catchCharData = False
    else :
      self.catchCharData = False

    if self.keyColumn :
      self.lastKey = ''
    else :
      self.lastVal = ''

  def char_data(self, data):
      if self.catchCharData:
        if self.keyColumn:
          self.lastKey = self.lastKey + data
        else:
          self.lastVal = self.lastVal + data
          self.currMap[self.lastKey] = self.lastVal

#get actioncodes from keymap.xml
ACTION_PREVIOUS_MENU = 10
ACTION_SELECT_ITEM = 7

class SelDialog(xbmcgui.WindowDialog):
  def __init__(self):
    #self.setCoordinateResolution(0)
    self.addControl( xbmcgui.ControlLabel(100,100,600,400, ''))
    self.selectionList = xbmcgui.ControlList(100,100,600,400, space=5)
    self.addControl(self.selectionList)
    self.setFocus(self.selectionList)
    self.selection = ''

  def setTitleItems(self, items):
    self.selectionList.addItems(items)
  
  def onAction(self, action) :
    if action == ACTION_PREVIOUS_MENU:
      self.close()
    if action == ACTION_SELECT_ITEM:
      self.selection = self.selectionList.getSelectedItem()
      self.close()

mydisplay = BluRayStarter()
mydisplay.process()
del mydisplay

