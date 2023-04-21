"""
Script to calculate H0 likelihood for Bright GW event(s)

Tathagata ghosh
"""

import numpy as np
import healpy as hp
from scipy.stats import norm, truncnorm
from scipy.integrate import simpson
from scipy.interpolate import interp1d
from astropy.cosmology import FlatLambdaCDM
from astropy import constants as const, units as u
from ligo.skymap.io.fits import read_sky_map
import pandas as pd
import json



class RedshiftEvolutionModel :
    def __init__ (self, gamma=4.59, k=2.86, zp=2.47) :
        self.gamma = gamma
        self.k = k
        self.zp = zp
        
    def RedshiftEvolutionPowerLaw (self, z) :
        return (1+z)**(self.gamma)

    def RedshiftEvolutionMadau (self, z) :
        C = 1+(1+self.zp)**(-self.gamma-self.k)
        return C*((1+z)**self.gamma)/(1+((1+z)/(1+self.zp))**(self.gamma+self.k))
        
    def RedshiftEvolutionConstant (self, z) :
        return 1
            
            
class H0likelihood :

    def __init__ (self, bright_siren_information, Om0=0.3, H0min=20, H0max=140, H0bins=100, redshift_bins = 10000, filename="test.csv", zcut=None, redshift_evolution= None, gamma=None, k=None, zp=None) :

        # redshift-luminosity distance relation
        cosmoref = FlatLambdaCDM(H0=70, Om0=Om0, Tcmb0=2.725)
        if zcut is None :
            zcut = 10
        zref = np.arange (0,zcut+0.01,0.01)
        dlref = cosmoref.luminosity_distance (zref).value
        self.dlH02z = interp1d (dlref*70, zref)
        diff_comoving_vol = interp1d(zref, cosmoref.differential_comoving_volume(zref).to(u.Gpc**3 / u.sr).value)
        
        cval = const.c.to('km/s').value
        
        # H0 array
        self.H0bins = H0bins
        self.H0_array = np.linspace ( H0min, H0max, self.H0bins)
        self.Om0 = Om0

        if redshift_evolution=='PowerLaw' :
            if gamma is not None:
                self.model = RedshiftEvolutionModel (gamma=gamma).RedshiftEvolutionPowerLaw
            else :
                self.model = RedshiftEvolutionModel().RedshiftEvolutionPowerLaw	
        elif redshift_evolution=='Madau' :
            if gamma is not None and k is not None and zp is not None:
                self.model = RedshiftEvolutionModel (gamma=gamma, k=k, zp=zp).RedshiftEvolutionMadau
            else :
                self.model = RedshiftEvolutionModel().RedshiftEvolutionMadau
        elif redshift_evolution is None:
            self.model = RedshiftEvolutionModel().RedshiftEvolutionConstant
            
        print(f'Assuming a {redshift_evolution} redshift evolution model')
        
        with open(bright_siren_information, "r") as bright_siren_info:
            bright_siren_information_dictionary = json.load(bright_siren_info)
        
        self.bright_siren_dictionary = {}
        self.dl_out={}
        
        for event in bright_siren_information_dictionary.keys () :

            self.bright_siren_dictionary [event] = {}
            self.dl_out[event]={}

            for em_info in bright_siren_information_dictionary [event]['Counterparts'].keys() :

                # em_name = bright_siren_information_dictionary[event]["Counterparts"][em_info]["Name"]
                em_name = em_info
            
                skymap = bright_siren_information_dictionary [event] ["Skymap"]
                counterpart_ra = bright_siren_information_dictionary [event] ['Counterparts'] [em_info] ["Parameters"] ["counterpart_ra"]
                counterpart_dec = bright_siren_information_dictionary [event] ['Counterparts'] [em_info] ["Parameters"] ["counterpart_dec"]
            
                # skymap
                (prob, distmu, distsigma, distnorm), metadata = read_sky_map (skymap, distances=True, moc=False, nest=True)
            
                # pixel corresponding to sky position of identified galaxy	
                npix = len(prob)
                nside = hp.npix2nside (npix)
                counterpart_pix = hp.ang2pix (nside, np.pi/2 - counterpart_dec, counterpart_ra, nest=True)
            
                # counterpart information
                counterpart_muz = bright_siren_information_dictionary [event] ['Counterparts'] [em_info] ["Parameters"] ["counterpart_cz"]/cval
                counterpart_sigmaz =  bright_siren_information_dictionary [event] ['Counterparts'] [em_info] ["Parameters"] ["counterpart_sigma_cz"]/cval
                a = (0.0 - counterpart_muz) / counterpart_sigmaz
                counterpart_z_array = np.linspace (0.5*counterpart_muz, 2*counterpart_muz, redshift_bins)
                counterpart_pdf = truncnorm (a,5, counterpart_muz, counterpart_sigmaz).pdf (counterpart_z_array)
        
                # redshift prior
                dVc_by_dz = diff_comoving_vol (counterpart_z_array)
                pz = self.model (counterpart_z_array)*dVc_by_dz/(1+counterpart_z_array)
        
                # likelihood in luminosity distance from skymap
                distmu_los = distmu [counterpart_pix]
                distsigma_los = distsigma [counterpart_pix]
                likelihood_x_dl_skymap = norm (distmu_los, distsigma_los) 

                # minimum and maximum distance of GW event
                self.dlGWmin = distmu_los - 5*distsigma_los
                self.dlGWmax = distmu_los + 5*distsigma_los
                if self.dlGWmin <=0 :
                    self.dlGWmin = 0
            
            
                self.bright_siren_dictionary [event] [em_name] = {}
                self.bright_siren_dictionary [event] [em_name] ["counterpart_z_array"] = counterpart_z_array
                self.bright_siren_dictionary [event] [em_name] ["counterpart_pdf"] = counterpart_pdf
                self.bright_siren_dictionary [event] [em_name] ["likelihood"] = likelihood_x_dl_skymap
                self.bright_siren_dictionary [event] [em_name] ["z_prior"] = pz

                self.dl_out[event][em_name]={'dist_mean':distmu_los,'dist_sigma':distsigma_los}

        # save likelihood information
        likelihood_df = self.H0likelihood_events ()
        likelihood_df.insert (0, "H0", self.H0_array) 
        likelihood_df.to_csv (filename, index=False)
    
        return
    
    def get_distance(self):
        return self.dl_out
    
    def likelihood_x_z_H0_single_event (self, event, H0, em_name, counterpart_z_array, redshift_bins_temp = 10000) :
    
        cosmo = FlatLambdaCDM(H0=H0, Om0=self.Om0, Tcmb0=2.725)
        zmin = self.dlH02z(self.dlGWmin*H0) *0.5
        zmax = self.dlH02z(self.dlGWmax*H0) *2
            
        zGW_array_temp = np.linspace (zmin,zmax,redshift_bins_temp)
        dl_array_temp = cosmo.luminosity_distance (zGW_array_temp).value
        
        likelihood_x_z_H0= self.bright_siren_dictionary [event] [em_name] ["likelihood"].pdf(dl_array_temp)
        likelihood_x_z_H0 /= simpson (likelihood_x_z_H0, zGW_array_temp)
        
        px_z_H0_interp = interp1d(zGW_array_temp,likelihood_x_z_H0,kind="linear",bounds_error=False,fill_value=0)
        
        return px_z_H0_interp (counterpart_z_array)


    def H0likelihood_events (self) :

        likelihood_dictionary = {}

        for event in self.bright_siren_dictionary.keys () :
            for em_name in self.bright_siren_dictionary[event].keys() :

                counterpart_z_array_event = self.bright_siren_dictionary [event]  [em_name] ["counterpart_z_array"]
                zprior_event = self.bright_siren_dictionary [event]  [em_name] ["z_prior"]
                counterpart_pdf = self.bright_siren_dictionary [event]  [em_name] ["counterpart_pdf"]

                likelihood_array = np.zeros (self.H0bins)

                for hh, H0 in enumerate (self.H0_array) :

                    px_z_H0 = self.likelihood_x_z_H0_single_event (event, H0, em_name, counterpart_z_array_event)
                    likelihood_array [hh] = simpson (px_z_H0*zprior_event*counterpart_pdf, counterpart_z_array_event)/H0**3

                likelihood_array /= simpson (likelihood_array, self.H0_array)

                likelihood_dictionary [f'{event}_{em_name}'] = likelihood_array

                likelihood_df = pd.DataFrame(likelihood_dictionary)

        return likelihood_df
            
