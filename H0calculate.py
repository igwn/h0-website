"""
Script for fast calculation of H0 posterior for Bright GW event 

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
import matplotlib.pyplot as plt



def RedshiftEvolutionPowerLaw (z, power) :
	return (1+z)**(power-1)
			
			
class H0calculate :

	def __init__ (self, bright_siren_information, Om0=0.3, H0min=20, H0max=140, H0bins=100, redshift_bins = 10000, zcut=None) :

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
		
		with open(bright_siren_information, "r") as bright_siren_info:
			bright_siren_information_dictionary = json.load(bright_siren_info)
		
		self.bright_siren_dictionary = {}
		
		for event in bright_siren_information_dictionary.keys () :
			
			skymap = bright_siren_information_dictionary [event] ["skymap"]
			counterpart_ra = bright_siren_information_dictionary [event] ["counterpart_ra"]
			counterpart_dec = bright_siren_information_dictionary [event] ["counterpart_dec"]
			
			# skymap
			(prob, distmu, distsigma, distnorm), metadata = read_sky_map (skymap, distances=True, moc=False, nest=True)
			
			# pixel corresponding to sky position of identified galaxy	
			npix = len(prob)
			nside = hp.npix2nside (npix)
			counterpart_pix = hp.ang2pix (nside, np.pi/2 - counterpart_dec, counterpart_ra, nest=True)
			
			# minimum and maximum distance of GW event
			mu = distmu[(distmu < np.inf) & (distmu > 0)]
			self.dlGWmin = 0.5*min(mu)
			self.dlGWmax = 2*max(mu)
			
			# counterpart information
			counterpart_muz = bright_siren_information_dictionary [event] ["counterpart_cz"]/cval
			counterpart_sigmaz =  bright_siren_information_dictionary [event] ["counterpart_sigma_cz"]/cval
			a = (0.0 - counterpart_muz) / counterpart_sigmaz
			counterpart_z_array = np.linspace (0.5*counterpart_muz, 2*counterpart_muz, redshift_bins)
			counterpart_pdf = truncnorm (a,5, counterpart_muz, counterpart_sigmaz).pdf (counterpart_z_array)
		
			# redshift prior
			dVc_by_dz = diff_comoving_vol (counterpart_z_array)
			pz = RedshiftEvolutionPowerLaw (counterpart_z_array, 0)*dVc_by_dz
		
			# likelihood in luminosity distance from skymap
			distmu_los = distmu [counterpart_pix]
			distsigma_los = distsigma [counterpart_pix]
			likelihood_x_dl_skymap = norm (distmu_los, distsigma_los) 
			
			
			self.bright_siren_dictionary [event] = {}
			self.bright_siren_dictionary [event] ["counterpart_z_array"] = counterpart_z_array
			self.bright_siren_dictionary [event] ["counterpart_pdf"] = counterpart_pdf
			self.bright_siren_dictionary [event] ["likelihood"] = likelihood_x_dl_skymap
			self.bright_siren_dictionary [event] ["z_prior"] = pz
			
			
	
	def likelihood_x_z_H0_single_event (self, event, H0, counterpart_z_array, redshift_bins_temp = 10000) :
	
		cosmo = FlatLambdaCDM(H0=H0, Om0=self.Om0, Tcmb0=2.725)
		zmin = self.dlH02z(self.dlGWmin*H0) *0.5
		zmax = self.dlH02z(self.dlGWmax*H0) *2
			
		zGW_array_temp = np.linspace (zmin,zmax,redshift_bins_temp)
		dl_array_temp = cosmo.luminosity_distance (zGW_array_temp).value
		
		likelihood_x_z_H0= self.bright_siren_dictionary [event] ["likelihood"].pdf(dl_array_temp)
		likelihood_x_z_H0 /= simpson (likelihood_x_z_H0, zGW_array_temp)
		
		px_z_H0_interp = interp1d(zGW_array_temp,likelihood_x_z_H0,kind="linear",bounds_error=False,fill_value=0)
		
		return px_z_H0_interp (counterpart_z_array)


	def probH0 (self) :
		
		log_pH0_comb = 0

		probH0_dictionary = {}
		
		probH0_dictionary ["H0_array"] = self.H0_array
		
		for event in self.bright_siren_dictionary.keys () :
		
			counterpart_z_array_event = self.bright_siren_dictionary [event] ["counterpart_z_array"]
			zprior_event = self.bright_siren_dictionary [event] ["z_prior"]
			counterpart_pdf = self.bright_siren_dictionary [event] ["counterpart_pdf"]
			
			pH0 = np.zeros (self.H0bins)
			
			for hh, H0 in enumerate (self.H0_array) :

				px_z_H0 = self.likelihood_x_z_H0_single_event (event, H0, counterpart_z_array_event)
				
				pH0 [hh] = simpson (px_z_H0*zprior_event*counterpart_pdf, counterpart_z_array_event)/H0**3
		
			pH0 /= simpson (pH0, self.H0_array)
			log_pH0_comb += np.log (pH0)
			
			probH0_dictionary [event] = pH0
		
		pH0_comb = np.exp (log_pH0_comb+np.median(log_pH0_comb)) 
		
		probH0_dictionary ["combined"] = pH0_comb /simpson (pH0_comb, self.H0_array)
		
		probH0_df = pd.DataFrame(probH0_dictionary)
		
		return probH0_df	
		
		
	def result (self, filename="H0_probH0.csv", figname="probability_H0_plot") :
		
		probH0_df = self.probH0 ()
		probH0_df.to_csv(filename)
		
		#plot
		plt.plot (self.H0_array, probH0_df.combined.values, lw=2, color='darkred')	
		plt.xlabel (r"$H_{0}$", size=15)
		plt.ylabel (r"$p(H_{0})$", size=15)
			
		plt.tight_layout ()
		plt.savefig (figname)
		plt.close ()
			
