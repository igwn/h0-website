# process H0 events

import json
import os
from ligo.gracedb.rest import GraceDb
import numpy as np
import json
import requests
from bs4 import BeautifulSoup
from astropy.time import Time
import bright_siren_likelihood as bsl

def readGraceDB(sid,full=False,verbose=True):
    service_url = 'https://gracedb.ligo.org/api/'
    print('Retrieving GraceDB data from {}'.format(service_url))
    client = GraceDb(service_url,force_noauth=True)

    voreq=client.voevents(sid)
    voevents=json.loads(voreq.content)
    
    evOut={}
    evOut['gracedb_meta']={'retrieved':Time.now().isot,'src':service_url}
    # evOut['voevents']=voevents
    #filter event list
    volist=voevents['voevents']
    
    # get the last VO event which wasn't a retraction
    good_voevents = [voe for voe in volist if voe['voevent_type'] != 'RE']
    Ngood=len(good_voevents)
    thisvo=good_voevents[Ngood-1]
    cdate=Time(' '.join(thisvo['created'].split(' ')[0:2]))
    thisvoe_url = thisvo['links']['file']
    vonum=thisvo['N']
    evOut["gracedb_meta"]['vonum']=vonum
    
    xml={}
    xmlurl=thisvoe_url
    print('  parsing {}'.format(xmlurl))
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
                mapurl=xml['GW_SKYMAP']['skymap_fits']
                mapFile="{}_{}".format(sid,os.path.split(mapurl)[-1])

                #download skymap
                try:
                    if verbose:print('Downloading map from {}'.format(mapurl))
                    fOut=open(mapFile,'wb')
                    mapreq=requests.get(mapurl)
                    fOut.write(mapreq.content)
                    fOut.close()
                    if verbose:print('Map saved to {}'.format(mapFile))
                    evOut['Skymap']=mapFile
                except:
                    print('Problem downloading map from {} to {}'.format(mapurl,mapFile))
    if full:
        evOut["xml"]=xml
    return(evOut)

def colname(gwid,emid):
    return f'{gwid}_{emid}'

class EventsList:
    def __init__(self,filein="events-list.json",fileout="bright-sirens.json",colfile="column-names.json"):
        try:
            eventDataIn=json.load(open(filein))
        except:
            print("Error reading input file:",filein)
        self.eventDataIn=eventDataIn
        self.process_events()
        if colfile:
            self.make_colnames(colfile)
        
        json.dump(self.bright_sirens,open(fileout,'w'),indent=2)
        bslH0=bsl.H0likelihood(fileout,filename="bright_sirens.csv")
        self.import_distance(bslH0.get_distance())
        json.dump(self.bright_sirens,open(fileout,'w'),indent=2)
    
    def process_events(self):
        self.bright_sirens={}
        try:
            events_list=self.eventDataIn["H0events"]
            gwdata=self.eventDataIn["GW_data"]
            emdata=self.eventDataIn["EM_data"]
        except:
            print('ERROR: Badly formated file')
        for ev in events_list:
            gwid=events_list[ev]["GW"]
            assert gwid in gwdata,"No event {} in GW_data structure".format(gwid)
            event=gwdata[gwid]
            if gwdata[gwid]["src"].lower()=="gracedb":
                # retrieve data from GraceDB
                gracedb_data=readGraceDB(gwdata[gwid]["id"])
                for x in gracedb_data:
                    print(x,gracedb_data[x])
                    event[x]=gracedb_data[x]

            # get EM counterpart data
            event["Counterparts"]={}
            N_em=0
            for emid in events_list[ev]["EM"]:
                if not emid in emdata:
                    pass
                else:
                    event["Counterparts"][emid]=emdata[emid]
                    # convert parameters
                    try:
                        paramsOut={}
                        paramsOut["counterpart_cz"]=emdata[emid]["cz_mean"]
                        paramsOut["counterpart_sigma_cz"]=emdata[emid]["cz_sigma"]
                        paramsOut["counterpart_ra"]=emdata[emid]["ra_deg"]*np.pi/180
                        paramsOut["counterpart_dec"]=emdata[emid]["dec_deg"]*np.pi/180
                        event["Counterparts"][emid]["Parameters"]=paramsOut
                    except:
                        print(f'Error converting parameters for {emid}')
                    event["Counterparts"][emid]["column_name"]=colname(gwid,emid)
                    N_em=N_em+1
            
            self.bright_sirens[ev]=event

    def make_colnames(self,filename):
        colnames={}
        for gwev in self.bright_sirens:
            colnames[gwev]={}
            for emev in self.bright_sirens[gwev]["Counterparts"]:
                colnames[gwev][emev]=self.bright_sirens[gwev]["Counterparts"][emev]["column_name"]
        json.dump(colnames,open(filename,'w'),indent=2)
        return
    
    def import_distance(self,dist):
        for gwev in dist:
            for emev in dist[gwev]:
                self.bright_sirens[gwev]["Counterparts"][emev]["gw_distance_mean"]=dist[gwev][emev]["dist_mean"]
                self.bright_sirens[gwev]["Counterparts"][emev]["gw_distance_sigma"]=dist[gwev][emev]["dist_sigma"]
        return