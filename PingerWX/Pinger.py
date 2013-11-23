"""
PingerWX -- a WX-based http graphical ping tool

Will Groves 2013
"""
import os
import pprint
import random
import sys
import wx
import datetime
import time 
import threading
import urllib2


class PingerFrame(wx.Frame):
    """ The main frame of the application
    """
    title = 'PingerWX'
    
    def __init__(self,httphosts, timerms, checkfrequency, greensecs, redsecs):
        self.checkfrequency = checkfrequency
        self.greensecs = greensecs
        self.redsecs = redsecs
        self.timerms = timerms
        self.thischeck = 0
        self.pause = False

        self.datal = [('192.168.1.1',-1.0),
                      ('www.yahoo.com',-1.0),
                      ]
        if httphosts != []:
            ##then override the default
            tmpdata = []
            for ipport in httphosts:
                tmpdata.append((ipport,-1.0))
            self.datal = tmpdata
    
        wx.Frame.__init__(self, None, -1, self.title)
        self.create_menu()
        self.create_main_panel()
        self.redraw_timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_redraw_timer, self.redraw_timer)
        self.redraw_timer.Start(self.timerms)

    def create_menu(self):
        self.menubar = wx.MenuBar()
        menu_file = wx.Menu()
        m_about = menu_file.Append(-1, "&About\tF1", "About the demo")
        self.Bind(wx.EVT_MENU, self.on_about, m_about)
        
        menu_file.AppendSeparator()
        m_exit = menu_file.Append(-1, "E&xit\tCtrl-Q", "Exit")
        self.Bind(wx.EVT_MENU, self.on_exit, m_exit)
        self.Bind(wx.EVT_CLOSE, self.on_exit, m_exit)##window close event
        
        self.menubar.Append(menu_file, "&File")
        self.SetMenuBar(self.menubar)

    def create_main_panel(self):
        """ 

        """
        self.panel = wx.Panel(self)
        self.vbox = wx.GridSizer(0,2,5,5)
        self.textl = []
        self.vall = []
        self.buttonl = []
        self.tmptext = wx.StaticText(self, -1, '      Hostname', style=wx.TE_CENTER)
        self.vbox.Add(self.tmptext, 0,  wx.ALIGN_CENTER_VERTICAL )
        self.tmptext = wx.StaticText(self, -1, 'Last Response (sec)', style=wx.TE_CENTER)
        self.vbox.Add(self.tmptext, 0,  wx.ALIGN_CENTER_VERTICAL )
        for datatup in self.datal:            
            self.tmptext = wx.StaticText(self, -1, "      "+datatup[0], style=wx.TE_RIGHT)
            self.vbox.Add(self.tmptext, 0,  wx.ALIGN_CENTER_VERTICAL )
            self.tmp = wx.TextCtrl(self, -1, "Never Seen", style=wx.TE_LEFT
                                   )
            self.tmp.SetBackgroundColour(self.getColorFromWait(datatup[1]))
            self.vbox.Add(self.tmp , 0,wx.ALIGN_CENTER_VERTICAL | wx.EXPAND )
            self.textl.append(self.tmptext)
            self.vall.append(self.tmp)

        self.panel.SetSizer(self.vbox)
        self.vbox.Fit(self)
        self.SetSizer(self.vbox)
        self.Centre()
    
    def on_exit(self, event):
        print "Exiting... waiting for timers to clean up..."
        self.pause = True##stops emission of new requests
        time.sleep(3)
        print "Quitting!"
        sys.exit(0)

    def on_about(self, event):
        dlg = wx.MessageDialog(self, "A simple graphical python "
                "application for\n"
                "watching connectivity via HTTP in real time.\n\n"
                "Will Groves 2010",
                "About PingerWX", wx.OK|wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def on_redraw_timer(self,event):    
        self.thischeck += 1
        if self.thischeck % self.checkfrequency == 0 and self.pause == False:
            ##start new queries
            for idx in range(len(self.datal)):
                def callback(self, idx, rttime):
                    if rttime != None:
                        timerval = 0.0
                        self.datal[idx] = self.datal[idx][0:1] + (0,rttime,)
                    
                asyncopen(self.datal, self.vall, idx, callback)
        
        for idx in range(len(self.datal)):
            timerval = self.datal[idx][1]
            if timerval > -1.0:
                timerval+=self.timerms/1000.0
            
            self.datal[idx] = self.datal[idx][0:1] + (timerval,) +self.datal[idx][2:]
            textstr  = "Never Seen"
            if timerval != -1.0:
                textstr = "%3.1f"%timerval
            self.vall[idx].SetValue(textstr)
            self.vall[idx].SetBackgroundColour(self.getColorFromWait(timerval))
    
    def getColorFromWait(self,waittime):
        '''
        given a wait time (in secs), compute the 
        color (from green to white to red)
        '''
        if type(waittime) == type("hi") or waittime < 0:
            return (255,0,0)
        if waittime <= self.greensecs:
            return (255-int(min(255,1.0*(self.greensecs-waittime)/self.greensecs*255)),
                    255,
                    255-int(min(255,1.0*(self.greensecs-waittime)/self.greensecs*255)),)
        else:
            return (255,
                    255-int(min(255,(waittime-self.greensecs)*255.0/self.redsecs)),
                    255-int(min(255,(waittime-self.greensecs)*255.0/self.redsecs)),)



class AsyncOpen(threading.Thread):
    """
    Asyncronous thread dispatch for http based query 
    """
    def __init__(self, datal, vall, idx,  callback):
        super(AsyncOpen, self).__init__()
        self.datal = datal
        self.vall = vall
        self.idx = idx
        self.callback = callback
    def run(self):
        
        self.url = "http://"+self.datal[self.idx][0]+"/"
        #print "request started"
        try:
            nowb = datetime.datetime.now()
            request = urllib2.urlopen(self.url,None,2)
            #print "request succeeded", self.url
            outputstr = request.read()
            nowe = datetime.datetime.now()
            rt = (nowe-nowb).seconds + (nowe-nowb).microseconds/1000000.0
            #print "response time:", rt
            self.callback(self, self.idx, rt)
        except Exception as e:
            ##some kind of failure occurred
            print str(datetime.datetime.now()),"request not succeed", self.url, str(e)
            #self.callback(None)
        #print "request over"

def asyncopen(datal, vall, idx, callback):
    AsyncOpen(datal,vall,idx, callback).start()

def cb(content):
    """
    generic callback with write to console
    """
    print content

if __name__ == '__main__':
    app = wx.PySimpleApp()
    
    ##parse input arguments here
    import optparse
    usage = "usage: %prog [options] "
    parser = optparse.OptionParser(usage)
    parser.add_option("--update-ms", dest="timerms",default=450,type=int,
                      help="display update interval in ms (default 450)")
    parser.add_option("--check-freq", dest="checkfrequency",default=7,type=int,
                      help="frequency that hosts are queried in terms of number of display updates (default 7)")
    parser.add_option("--max-green", dest="greensecs",default=4,type=int,
                      help="number of seconds until green color dissipates (default 4)")
    parser.add_option("--max-red", dest="redsecs",default=20,type=int,
                      help="number of seconds until red color reaches full strength (default 20)")
    parser.add_option("--hq","--httpquery", dest="httphosts",action='append',
                      help="specify host and port to query via http (ip:port)", default=[])
    (options, args) = parser.parse_args()
    
    
    app.frame = PingerFrame(options.httphosts,
                            options.timerms,
                            options.checkfrequency,
                            options.greensecs,
                            options.redsecs)
    app.frame.Show()
    app.MainLoop()

