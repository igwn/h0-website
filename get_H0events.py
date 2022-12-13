## Import events from GraceDB
import os
from ligo.gracedb.rest import GraceDb
import numpy as np
import json
import requests
from bs4 import BeautifulSoup
from astropy.time import Time

eventsIn=json.load(open("events-list.json"))

#Open GraceDB public connection
service_url = 'https://gracedb.ligo.org/api/'
print('Retrieving GraceDB data from {}'.format(service_url))
client = GraceDb(service_url,force_noauth=True)

for e in eventsIn:
    print(e)
    ev=eventsIn[e]
    if not "data" in ev:
        continue
    if not "src" in ev["data"]:
        continue
    if ev["data"]["src"]=="gracedb":
        sid=ev["data"].get("src-id","")
    voreq=client.voevents(sid)
    voevents=json.loads(voreq.content)
    #ev['data']['event-data']=voevents

    evOut={}
    evOut['meta']={'retrieved':Time.now().isot,'src':service_url}
    evOut['voevents']=voevents
    #filter event list
    volist=voevents['voevents']
    good_voevents = [voe for voe in volist if voe['voevent_type'] != 'RE']
    Ngood=len(good_voevents)
    thisvo=good_voevents[Ngood-1]
    cdate=Time(' '.join(thisvo['created'].split(' ')[0:2]))
    thisvoe_url = thisvo['links']['file']
    vonum=thisvo['N']
    evOut['vonum']=vonum
    evOut['xmlfile']=[os.path.split(thisvoe_url)[-1],thisvoe_url]
    xml={}
    print('  parsing {}'.format(evOut['xmlfile'][0]))
    xmlurl=evOut['xmlfile'][1]
    xmlreq=requests.get(xmlurl)
    soup=BeautifulSoup(xmlreq.text,'lxml')
    validXML=False
    try:
        params=soup.what.find_all('param',recursive=False)
        validXML=True
    except:
        print('problem with {}: {}'.format(sid,evOut['xmlfile'][0]))
    if validXML:
        for p in params:
            xml[p.attrs['name']]=p.attrs['value']
        groups=soup.what.find_all('group',recursive=False)
        for g in groups:
            gt=g.attrs['type']
            xml[gt]={}
            gparams=g.find_all('param',recursice=False)
            for gp in gparams:
                xml[gt][gp.attrs['name']]=gp.attrs['value']
        if 'GW_SKYMAP' in xml:
            if 'skymap_fits' in xml['GW_SKYMAP']:
                mapfile=xml['GW_SKYMAP']['skymap_fits']
                evOut['mapfile']=[os.path.split(mapfile)[-1],mapfile]
        ev['data']['xml']=xml



print(eventsIn)

fOut=open('events-list-out.json','w')
eventsOut=json.dump(eventsIn,fOut,indent=2)
fOut.close()

#Get list of all superevents
#events = client.superevents('far < 1#.0e-4')
