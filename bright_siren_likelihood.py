"""
Script to calculate H0 likelihood for Bright GW event(s)

Tathagata ghosh
"""

import numpy as np
import healpy as hp
from scipy.stats import norm, truncnorm
from scipy.integrate import simpson
from scipy.interpolate import interp1d
from astropy import constants as const, units as u
from ligo.skymap.io.fits import read_sky_map
import pandas as pd
import json
import bilby
            
class H0likelihood :

    def __init__ (self, bright_siren_information, H0min=20, H0max=140, H0bins=100, redshift_bins = 10000, filename="test.csv") :

        """
        Class to calculate likelihood on the Hubble constant
        Parameters
        ----------

        bright_siren_information : dictionary (Json file )
            Contain bright sirens data (electromagnetic counterpart (rac, dec, redshift ), GW data (skymap)) from GraceDB
        H0min : Float (Default is 20)
            Minimum value of H0 for which likelihood is computed
        H0min : Float (Default is 140)
            Maximum value of H0 for which likelihood is computed
        H0bins : Integer (Default is 100)
            Number of points to construct H0 array over which H0 likelihood would be computed
        redshift_bins : Integer (Default is 1000)
            Number of redshift bins to construct redshift array over which redshift posterior(?) is constructed using the elctromagnetic counterpart data stored in bright_siren_information(dictionary)
        filename : Str (CSV File)
            File to array of H0 and corresponding ;ikelihood for the givent events mentioned in bright_siren_information(dictionary)
        """

        # Speed of light in km.s-1
        self.cval = const.c.to('km/s').value
        
        # H0 array between H0min and H0max with H0bins
        self.H0bins = H0bins
        self.H0_array = np.linspace ( H0min, H0max, self.H0bins)

         # Load the bright siren informations into a python dict{}
        with open(bright_siren_information, "r") as bright_siren_info:
            bright_siren_information_dictionary = json.load(bright_siren_info)
        
        self.bright_siren_dictionary = {}

        # Store mean and standard deviation of dl posterior obtained for a particular (line of sight) pixel from the skymap of each of the venet
        self.dl_out={}

        # Loop over each event in the Json file with the bright siren information 
        for event in bright_siren_information_dictionary.keys () :

            # Creates a sub dict for each event
            self.bright_siren_dictionary [event] = {}
            self.dl_out[event]={}

            # Loop over all potential electromagnetic counterpart info for a specific event
            for em_info in bright_siren_information_dictionary [event]['Counterparts'].keys() :

                # Store the key of the electromagnetic counterpart info
                em_name = em_info

                # Load the skymap (.gz file) from the Json file for the events
                skymap = bright_siren_information_dictionary [event] ["Skymap"]
                # Extract the right acencion and declination for this event and for this e.m.c info
                counterpart_ra = bright_siren_information_dictionary [event] ['Counterparts'] [em_info] ["Parameters"] ["counterpart_ra"]
                counterpart_dec = bright_siren_information_dictionary [event] ['Counterparts'] [em_info] ["Parameters"] ["counterpart_dec"]
            
                # Skymap
                # read_sky_map : https://lscsoft.docs.ligo.org/ligo.skymap/io/fits.html#ligo.skymap.io.fits.read_sky_map
                # Read a LIGO/Virgo/KAGRA-type sky map and return a tuple of the HEALPix array and a dictionary of metadata from the header.
                (prob, distmu, distsigma, distnorm), metadata = read_sky_map (skymap, distances=True, moc=False, nest=True)

                # Check the source of the sky map in the metadata to define the dl prior later
                if metadata['creator']=='ligo-skymap-from-samples':
                    dl_prior = bilby.gw.prior.UniformSourceFrame(minimum=0.0, maximum=5000.0, name='luminosity_distance', unit='Mpc')
                elif metadata['creator']=='BAYESTAR':
                    dl_prior = bilby.gw.prior.PowerLaw(alpha=2, minimum=0.0, maximum=5000.0, name='luminosity_distance', unit='Mpc')
            
                # Pixel corresponding to sky position of identified galaxy
                # Total number of pixels over the entire sky 
                npix = len(prob)
                # nside : read https://healpy.readthedocs.io/en/latest/generated/healpy.pixelfunc.npix2nside.html#healpy.pixelfunc.npix2nside
                nside = hp.npix2nside (npix)
                # Identify particualar pixel in the skymap from the electromagnetic counterpart information
                counterpart_pix = hp.ang2pix (nside, np.pi/2 - counterpart_dec, counterpart_ra, nest=True)
            
                # counterpart information
                counterpart_muz = bright_siren_information_dictionary [event] ['Counterparts'] [em_info] ["Parameters"] ["counterpart_cz"]/self.cval
                counterpart_sigmaz =  bright_siren_information_dictionary [event] ['Counterparts'] [em_info] ["Parameters"] ["counterpart_sigma_cz"]/self.cval
                a = (0.0 - counterpart_muz) / counterpart_sigmaz
                counterpart_z_array = np.linspace (0.5*counterpart_muz, 2*counterpart_muz, redshift_bins)
                # Constructiong pdf of the redshift using the electromagnetic counterpart information
                counterpart_pdf = truncnorm (a,5, counterpart_muz, counterpart_sigmaz).pdf (counterpart_z_array)
        
                # redshift prior
                pz = np.power(counterpart_z_array, 2)
        
                # Posterior of luminosity distance from skymap
                # mean of the Gaussian distribution, which is estimated distance posterior
                distmu_los = distmu [counterpart_pix]
                # standard deviation of the Gaussian distribution, which is estimated distance posterior
                distsigma_los = distsigma [counterpart_pix]
                # Posterior of luminosity distance for counterpart_pix (described above) from skymap
                posterior_x_dl_skymap = norm (distmu_los, distsigma_los) 

                # minimum and maximum distance of GW event at 5 sigma error
                self.dlGWmin = distmu_los - 5*distsigma_los
                self.dlGWmax = distmu_los + 5*distsigma_los
                # Minimum distance (in Mpc) cannot be negative
                if self.dlGWmin <0 :
                    self.dlGWmin = 1e-3
            
            
                self.bright_siren_dictionary [event] [em_name] = {}
                self.bright_siren_dictionary [event] [em_name] ["counterpart_z_array"] = counterpart_z_array
                self.bright_siren_dictionary [event] [em_name] ["counterpart_pdf"] = counterpart_pdf
                self.bright_siren_dictionary [event] [em_name] ["posterior"] = posterior_x_dl_skymap
                self.bright_siren_dictionary [event] [em_name] ["z_prior"] = pz
                self.bright_siren_dictionary [event] [em_name] ["dl_prior"] = dl_prior

                self.dl_out[event][em_name]={'dist_mean':distmu_los,'dist_sigma':distsigma_los}

        # save H0 likelihood as a function of H0 (array)
        likelihood_df = self.H0likelihood_events ()
        # H0 array and the corresponding likelihood
        likelihood_df.insert (0, "H0", self.H0_array) 
        # Save into a csv file
        likelihood_df.to_csv (filename, index=False)
    
        return
    
    def get_distance(self):
        return self.dl_out
    
    def likelihood_x_z_H0_single_event (self, event, H0, em_name, counterpart_z_array, redshift_bins_temp = 10000) :

        # minimum and maximum distance of GW event at 5 sigma error for a given H0
        zmin = self.dlGWmin*H0/self.cval 
        zmax = self.dlGWmax*H0/self.cval 

        # redshift array of the GW
        zGW_array_temp = np.linspace (zmin,zmax,redshift_bins_temp)
        # convert the above redshift array into luminosity distance array
        dl_array_temp = self.cval*zGW_array_temp/H0 
        
        likelihood_x_z_H0= self.bright_siren_dictionary [event] [em_name] ["posterior"].pdf(dl_array_temp)/self.bright_siren_dictionary [event] [em_name] ["dl_prior"].prob(dl_array_temp)
        likelihood_x_z_H0 /= simpson (likelihood_x_z_H0, zGW_array_temp)
        
        px_z_H0_interp = interp1d(zGW_array_temp,likelihood_x_z_H0,kind="linear",bounds_error=False,fill_value=0)
        
        return px_z_H0_interp (counterpart_z_array)


    def H0likelihood_events (self) :

        likelihood_dictionary = {}

        # Loop over the events in the dict built in the init function
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
            
