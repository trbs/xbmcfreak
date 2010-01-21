import xbmc, xbmcgui, subprocess, os, time, sys, urllib, urllib2 
  
class BluRayStarter:
  def __init__(self):
    timeSlept = 0
    self.pDialog = xbmcgui.DialogProgress()
    ret = self.pDialog.create('XBMC', 'Waiting for Disc to be prepared', 'killing previous makemkvcon')
    self.pDialog.update(0 )
    try :
      subprocess.call('killall -9 makemkvcon')
    except:
      pass
    self.pDialog.update(2, 'XBMC', 'Waiting for Disc to be prepared', 'killing previous makemkvcon')
    try :
      tst = subprocess.Popen('makemkvcon stream disc:0', shell=True)
      ret = self.pDialog.update(2, 'XBMC', 'Waiting for Disc to be prepared', 'waiting for stream')
      m2tsTried = False
      while True:   
        try:
          urllib.urlretrieve('http://localhost:51000')
          if (m2tsTried) :
            xbmc.Player().play('http://localhost:51000/stream/title0.vob')
          else :
            m2tsTried = True
            opener = urllib.URLopener()
            opener.open('http://localhost:51000/stream/title0.m2ts')
            del opener
            xbmc.Player().play('http://localhost:51000/stream/title0.m2ts')
          break;
        except IOError:
          pass
	if self.pDialog.iscanceled():
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
    dialog.ok("Info", messageText + " Test")
 
mydisplay = BluRayStarter()
del mydisplay

