import urllib,urllib2,re,cookielib,string,os
import xbmc, xbmcgui, xbmcaddon, xbmcplugin
from t0mm0.common.net import Net as net

addon_id = 'plugin.video.sportsaccess'
selfAddon = xbmcaddon.Addon(id=addon_id)
prettyName='SportsAccess'
art = xbmc.translatePath(os.path.join('special://home/addons/plugin.video.sportsaccess/resources/art', ''))
datapath = xbmc.translatePath(selfAddon.getAddonInfo('profile'))
UpdatePath=os.path.join(datapath,'Update')
try: os.makedirs(UpdatePath)
except: pass

def OPENURL(url, mobile = False, q = False, verbose = True, timeout = 10, cookie = None, data = None, cookiejar = False, log = True, headers = [], type = '',ua = False,setCookie = []):
    import urllib2 
    UserAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
    if ua: UserAgent = ua
    try:
        if log:
            print "Openurl = " + url
        if cookie and not cookiejar:
            import cookielib
            cookie_file = os.path.join(os.path.join(datapath,'Cookies'), cookie+'.cookies')
            cj = cookielib.LWPCookieJar()
            if os.path.exists(cookie_file):
                try:
                    cj.load(cookie_file,True)
                    for c in setCookie:
                        cj.set_cookie(c)
                except: cj.save(cookie_file,True)
            else: cj.save(cookie_file,True)
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        elif cookiejar:
            import cookielib
            cj = cookielib.LWPCookieJar()
            opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
        else:
            opener = urllib2.build_opener()
        if mobile:
            opener.addheaders = [('User-Agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')]
        else:
            opener.addheaders = [('User-Agent', UserAgent)]
        for header in headers:
            opener.addheaders.append(header)
        if data:
            if type == 'json': 
                import json
                data = json.dumps(data)
                opener.addheaders.append(('Content-Type', 'application/json'))
            else: data = urllib.urlencode(data)
            response = opener.open(url, data, timeout)
        else:
            response = opener.open(url, timeout=timeout)
        if cookie and not cookiejar:
            cj.save(cookie_file,True)
        link=response.read()
        response.close()
        opener.close()
        #link = net(UserAgent).http_GET(url).content
        link=link.replace('&#39;',"'").replace('&quot;','"').replace('&amp;',"&").replace("&#39;","'").replace('&lt;i&gt;','').replace("#8211;","-").replace('&lt;/i&gt;','').replace("&#8217;","'").replace('&amp;quot;','"').replace('&#215;','x').replace('&#038;','&').replace('&#8216;','').replace('&#8211;','').replace('&#8220;','').replace('&#8221;','').replace('&#8212;','')
        link=link.replace('%3A',':').replace('%2F','/')
        if q: q.put(link)
        return link
    except Exception as e:
        if verbose:
            xbmc.executebuiltin("XBMC.Notification(Sorry!,Source Website is Down,3000,"+elogo+")")
        xbmc.log('***********Website Error: '+str(e)+'**************', xbmc.LOGERROR)
        xbmc.log('***********Url: '+url+' **************', xbmc.LOGERROR)
        import traceback
        traceback.print_exc()
        link ='website down'
        if q: q.put(link)
        return link


user = selfAddon.getSetting('skyusername')
passw = selfAddon.getSetting('skypassword')
cookie_file = os.path.join(os.path.join(datapath,''), 'sportsaccess.cookies')
if user == '' or passw == '':
    if os.path.exists(cookie_file):
        try: os.remove(cookie_file)
        except: pass
    dialog = xbmcgui.Dialog()
    ret = dialog.yesno('[COLOR red]SportsAccess[/COLOR]', 'Please set your SportsAccess credentials','or register if you don have an account','at sportsaccess.se','Cancel','Login')
    if ret == 1:
        keyb = xbmc.Keyboard('', 'Enter Username or Email')
        keyb.doModal()
        if (keyb.isConfirmed()):
            search = keyb.getText()
            username=search
            keyb = xbmc.Keyboard('', 'Enter Password:')
            keyb.doModal()
            if (keyb.isConfirmed()):
                search = keyb.getText()
                password=search
                selfAddon.setSetting('skyusername',username)
                selfAddon.setSetting('skypassword',password)
                
user = selfAddon.getSetting('skyusername')
passw = selfAddon.getSetting('skypassword')

def setCookie(srDomain):
    cookieExpired = False
    if os.path.exists(cookie_file):
        try:
            cookie = open(cookie_file).read()
            expire = re.search('expires="(.*?)"',cookie, re.I)
            if expire:
                expire = str(expire.group(1))
                import time
                if time.time() > time.mktime(time.strptime(expire, '%Y-%m-%d %H:%M:%SZ')):
                   cookieExpired = True
        except: cookieExpired = True 
    if not os.path.exists(cookie_file) or cookieExpired:
        html = net().http_GET(srDomain).content
        r = re.findall(r'<input type="hidden" name="(.+?)" value="(.+?)" />', html, re.I)
        post_data = {}
        post_data['amember_login'] = user
        post_data['amember_pass'] = passw
        for name, value in r:
            post_data[name] = value
        net().http_GET('https://hostaccess.org/amember/protect/new-rewrite?f=2&url=/member1/&host=hostaccess.org&ssl=off')
        net().http_POST('https://hostaccess.org/amember/protect/new-rewrite?f=2&url=/member1/&host=hostaccess.org&ssl=off',post_data)
        net().save_cookies(cookie_file)
    else:
        net().set_cookies(cookie_file)

           
def cleanHex(text):
    def fixup(m):
        text = m.group(0)
        if text[:3] == "&#x": return unichr(int(text[3:-1], 16)).encode('utf-8')
        else: return unichr(int(text[2:-1])).encode('utf-8')
    return re.sub("(?i)&#\w+;", fixup, text.decode('ISO-8859-1').encode('utf-8'))

def MAINSA():
    setCookie('http://hostaccess.org/7-SFE-SZE-HOSTACCESS/')
    response = net().http_GET('http://hostaccess.org/7-SFE-SZE-HOSTACCESS/')
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    if '<title>Axxess Streams </title>' in link:
        addLink('[COLOR red]Elite Member[/COLOR]','','')
    else:
        addLink('[COLOR red]Free Member[/COLOR]','','')
    addDir('[COLOR blue]Schedule[/COLOR]','http://www.sportsaccess.se/forum/calendar.php?action=weekview&calendar=1',476,art+'/skyaccess.png')
    #addDir('Free Streams','http://sportsaccess.se/forum/misc.php?page=livestreams',412,art+'/skyaccess.png')
    if '<title>Axxess Streams </title>' in link:
        #addDir('Elite Streams',link,410,art+'/skyaccess.png')
        i=0
        match=re.compile('<li><a href="([^"]+)"><center>(.+?)</a>').findall(link)                 
        for url,name in match:
                thumb=['http://i.imgur.com/zo1FeZA.png','http://i.imgur.com/R7xiSJg.png','http://i.imgur.com/KF3PQAV.png','http://i.imgur.com/uQunKHh.png','http://i.imgur.com/OOaeIzT.png']
                name = re.sub('(?sim)<[^>]*?>','',name)
                if 'http' not in url: url = 'http://hostaccess.org'+url
                addDir(name,url,411,thumb[i])
                i=i+1
    #addPlay('[COLOR blue]Click here for Subscription Info[/COLOR]','https://dl.dropboxusercontent.com/u/35068738/picture%20for%20post/sky.png',244,art+'/skyaccess.png')


        
def Calendar(murl):
    setCookie(murl)
    response = net().http_GET(murl)
    link = response.content
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    print link
    month=re.findall('(?sim)<td class="tcat smalltext" colspan="2">([^<]+?)</td>',link)
    match=re.findall('(?sim)<td class="trow_sep.+?>([^<]+?)</td></tr><tr><td class=".+?<span class="largetext">(\d+)</span></td><td class="trow1.+?>(.+?)</td>',link)
    for day,num,data in match:
       addLink('[COLOR blue]'+day+' '+num+' '+month[0]+'[/COLOR]','','')
       match2=re.findall('(?sim)<a href=".+?" class=" public_event" title="(.+?)">.+?</a>',data)
       for title in match2:
           addLink(title,'','')

def LISTMENU(murl):
    i=0
    match=re.compile('<li><a href="([^"]+)"><center>(.+?)</a>').findall(murl)                 
    for url,name in match:
        thumb=['http://i.imgur.com/zo1FeZA.png','http://i.imgur.com/R7xiSJg.png','http://i.imgur.com/KF3PQAV.png','http://i.imgur.com/uQunKHh.png','http://i.imgur.com/OOaeIzT.png']
        name = re.sub('(?sim)<[^>]*?>','',name)
        if 'http' not in url: url = 'http://hostaccess.org'+url
        addDir(name,url,411,thumb[i])
        i=i+1

def LISTMENU2(murl):
    response = net().http_GET(murl)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    match=re.compile('<li><a href="(.+?)"><center>(.+?)<img src="(.+?)".+?>').findall(link)
    for url,name,thumb in match:
        thumb=thumb.replace('http://i.imgur.com/D2gzK0U.png','http://i.imgur.com/zo1FeZA.png').replace('http://cdn0.agoda.net/images/default/icon_questionmark.png','http://i.imgur.com/R7xiSJg.png').replace('http://i.imgur.com/8h0WVhG.png','http://i.imgur.com/KF3PQAV.png').replace('http://i.imgur.com/my0hcfg.png','http://i.imgur.com/uQunKHh.png').replace('http://i.imgur.com/ufhNZ8q.png','http://i.imgur.com/OOaeIzT.png')
        name = re.sub('(?sim)<[^>]*?>','',name)
        addDir(name,'http://sportsaccess.se'+url,411,thumb)

def LISTCONTENT(murl,thumb):
    setCookie(murl)
    response = net().http_GET(murl)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    if 'http://hostaccess.org/7-SFE-SZE-HOSTACCESS/media/vod.php' == murl:
        response = net().http_GET('http://sportsaccess.se/forum/misc.php?page=Replays')
        link = response.content
        link = cleanHex(link)
        link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
        
        match=re.compile('<a href="([^"]+)"><img src="([^"]+)" width=".+?alt="([^"]+)"></a>').findall(link)
        for url,thumb,name in match:
            if 'http' not in thumb:
                    thumb='http://sportsaccess.se/forum/'+thumb
            addDir(name,url,411,thumb)
    else:
        match=re.compile('<a href="(.+?)">(.+?)</a>').findall(link)
        for url,name in match:
            if 'GO BACK' not in name and '1 Year Subscriptions' not in name and 'Live Broadcasts' not in name and '<--- Return To On Demand Guide' not in name:
                name = re.sub('(?sim)<[^>]*?>','',name)
                if 'http' not in url:
                    url='http://sportsaccess.se'+url
                addPlay(name,url,413,thumb)


def get_link(murl):
    setCookie(murl)
    response = net().http_GET(murl)
    link = response.content
    link = cleanHex(link)
    link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
    m3u8=re.findall('<a href="([^"]+?.m3u8)">',link)
    iframe=re.findall('<iframe src="(http://admin.livestreamingcdn.com[^"]+?)"',link)
    if m3u8:
        return m3u8[0]
    elif iframe:
        response = net().http_GET(iframe[0])
        link = response.content
        link = cleanHex(link)
        link=link.replace('\r','').replace('\n','').replace('\t','').replace('&nbsp;','').replace('  ','')
        vlink=re.findall('file: "([^"]+?.m3u8)"',link)
        return vlink[0]
    else:
        swf=re.findall("src='([^<]+).swf'",link)[0]
        file=re.findall("file=(.+?)&",link)[0] 
        file=file.replace('.flv','')
        streamer=re.findall("streamer=(.+?)&",link)[0]
        if '.mp4' in file and 'vod' in streamer:
            file='mp4:'+file
            return streamer+' playpath='+file+' swfUrl='+swf+'.swf pageUrl='+murl
        else:
            return streamer+' playpath='+file+' swfUrl='+swf+'.swf pageUrl='+murl+' live=true timeout=20'
    
def PLAYLINK(mname,murl,thumb):
        ok=True
        stream_url = get_link(murl)     
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        listitem = xbmcgui.ListItem(thumbnailImage=thumb)
        liz=xbmcgui.ListItem(mname, iconImage=thumb, thumbnailImage=thumb)
        playlist.add(stream_url,listitem)
        xbmcPlayer = xbmc.Player()
        xbmcPlayer.play(playlist)
        return ok
                                             
def CheckForAutoUpdate(force = False):
    GitHubRepo    = 'SportsAccess'
    GitHubUser    = 'haze108'
    GitHubBranch  = 'master'
    UpdateVerFile = 'update'
    RunningFile   = 'running'
    verCheck=True 
    if verCheck == True:
        import autoupdate
        import time
        try:
            print "SportsAccess auto update - started"
            html=OPENURL('https://github.com/'+GitHubUser+'/'+GitHubRepo+'?files=1', mobile=True, verbose=False)
        except:
            html=''
        m = re.search("View (\d+) commit",html,re.I)
        if m: gitver = int(m.group(1))
        else: gitver = 0
        UpdateVerPath = os.path.join(UpdatePath,UpdateVerFile)
        try: locver = int(autoupdate.getUpdateFile(UpdateVerPath))
        except: locver = 0
        RunningFilePath = os.path.join(UpdatePath, RunningFile)
        if locver < gitver and (not os.path.exists(RunningFilePath) or os.stat(RunningFilePath).st_mtime + 120 < time.time()) or force:
            UpdateUrl = 'https://github.com/'+GitHubUser+'/'+GitHubRepo+'/archive/'+GitHubBranch+'.zip'
            UpdateLocalName = GitHubRepo+'.zip'
            UpdateDirName   = GitHubRepo+'-'+GitHubBranch
            UpdateLocalFile = xbmc.translatePath(os.path.join(UpdatePath, UpdateLocalName))
            setFile(RunningFilePath,'')
            print "auto update - new update available ("+str(gitver)+")"
            xbmc.executebuiltin("XBMC.Notification(SportsAccess Update,New Update detected,3000,"")")
            xbmc.executebuiltin("XBMC.Notification(SportsAccess Update,Updating...,3000,"")")
            try:os.remove(UpdateLocalFile)
            except:pass
            try: urllib.urlretrieve(UpdateUrl,UpdateLocalFile)
            except:pass
            if os.path.isfile(UpdateLocalFile):
                extractFolder = xbmc.translatePath('special://home/addons')
                pluginsrc =  xbmc.translatePath(os.path.join(extractFolder,UpdateDirName))
                if autoupdate.unzipAndMove(UpdateLocalFile,extractFolder,pluginsrc):
                    autoupdate.saveUpdateFile(UpdateVerPath,str(gitver))
                    print "SportsAccess auto update - update install successful ("+str(gitver)+")"
                    xbmc.executebuiltin("XBMC.Notification(SportsAccess Update,Successful,5000,"")")
                    xbmc.executebuiltin("XBMC.Container.Refresh")

                else:
                    print "SportsAccess auto update - update install failed ("+str(gitver)+")"
                    xbmc.executebuiltin("XBMC.Notification(SportsAccess Update,Failed,3000,"")")

            else:
                print "SportsAccess auto update - cannot find downloaded update ("+str(gitver)+")"
                xbmc.executebuiltin("XBMC.Notification(SportsAccess Update,Failed,3000,"")")
            try:os.remove(RunningFilePath)
            except:pass
        else:
            if force: xbmc.executebuiltin("XBMC.Notification(SportsAccess Update,SportsAccess is up-to-date,3000,"")")
            print "SportsAccess auto update - SportsAccess is up-to-date ("+str(locver)+")"
        return        
                
        

def addPlay(name,url,mode,iconimage):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage='', thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image',art+"fanart.jpg")
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz, isFolder = False)
        return ok


def addLink(name,url,iconimage):
    liz=xbmcgui.ListItem(name, iconImage=art+'/link.png', thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name } )
    liz.setProperty('fanart_image',art+"fanart.jpg")
    return xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=url,listitem=liz)

def addDir(name, url, mode, thumbImage):

        u  = sys.argv[0]

        u += "?url="  + urllib.quote_plus(url)
        u += "&mode=" + str(mode)
        u += "&name=" + urllib.quote_plus(name)

        liz = xbmcgui.ListItem(name, iconImage='', thumbnailImage=thumbImage)
        liz.setInfo( type="Video", infoLabels={ "Title": name } )
        liz.setProperty('fanart_image',art+"fanart.jpg")

        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz,isFolder=True)



def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param
              
params=get_params()
url=None
name=None
mode=None
iconimage=None

try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        mode=int(params["mode"])
except:
        pass
try:
    iconimage=urllib.unquote_plus(params["iconimage"])
    iconimage = iconimage.replace(' ','%20')
except:
        pass

print "Mode: "+str(mode)
print "Name: "+str(name)


if mode==None or url==None or len(url)<1:
        import threading
        threading.Thread(target=CheckForAutoUpdate).start()
        MAINSA()
    
elif mode==410:
        LISTMENU(url)
        
elif mode==411:
        LISTCONTENT(url,iconimage)
        
elif mode==412:
        LISTMENU2(url)
            
elif mode==413:
        PLAYLINK(name,url,iconimage)

elif mode==476:
        Calendar(url)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))

