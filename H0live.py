"""
Script for live estimation of combined H0 posterior from  pre-computed likelihood

Tathagata ghosh
"""

import pandas as pd
import numpy as np
from scipy.integrate import simpson, cumtrapz
import matplotlib.pyplot as plt
from scipy.optimize import fmin
from scipy.interpolate import interp1d, UnivariateSpline
import streamlit as st
from matplotlib.backends.backend_agg import RendererAgg
from seaborn import color_palette

_lock = RendererAgg.lock


class H0live :
    def __init__ (self, events, H0prior="uniform", level=0.9, likelihood_fname="test.csv", planck=True) :


        likelihood_allevents = pd.read_csv (likelihood_fname)

        self.H0_array = likelihood_allevents.H0.values

        log_likelihood_combined = 0

        for event in events :
            log_likelihood_combined += np.log (likelihood_allevents[event].values)
    
        self.likelihood_combined = np.exp(log_likelihood_combined)
        self.H0prior = H0prior

        pH0_normalized = self.probability ()
        
        CI = credible_interval (pH0_normalized, self.H0_array, level=level)
        H0low = CI.lower_level
        H0high = CI.upper_level
        H0map = CI.map

        # plot
        ymin = 0
        ymax = 1.1*max(pH0_normalized)
        c = color_palette('colorblind')
	
        with _lock :
            fig = plt.figure()
            plt.plot (self.H0_array, pH0_normalized, lw=2.5, color=c[0], label="Combined Posterior")
            plt.plot (self.H0_array, self.prior(), ls="--", color=c[1], lw=2, alpha=0.8, label="Prior")
            plt.axvline (H0map, color=c[2], lw=2, alpha=0.7)
            plt.axvline (H0low, color=c[2], lw=2, alpha=0.7)
            plt.axvline (H0high, color=c[2], lw=2, alpha=0.7)
            
			# Planck
            if planck is True :
                planck_H0_value = 67.74
                planck_H0_sigma = 0.62
                plt.fill_betweenx([ymin,ymax], planck_H0_value-planck_H0_sigma, planck_H0_value+planck_H0_sigma, color=c[3], alpha=0.3, label="Placnk")
        
            plt.xlim (self.H0_array[0],self.H0_array[-1])
            plt.ylim (ymin, ymax)
            plt.xlabel (r"$H_{0}$", size=15)
            plt.ylabel (r"$p(H_{0})$", size=15)
            plt.title (r"$H_{0}=%.2f^{+%.2f}_{+%.2f}\ {\rm km\ s^{-1}\ Mpc^{-1}} (%d %s {\rm CI})$"
        %(H0map, H0high-H0map, H0map-H0low, level*100, r"$%$"))
            plt.tick_params(labelsize=12, direction='in')
            plt.legend (fontsize=11)
            plt.tight_layout ()

            st.pyplot(fig, clear_figure=True)

    def probability (self) :

        if self.H0prior=="uniform" :
            pH0_normalized = self.likelihood_combined/simpson (self.likelihood_combined,self.H0_array)
        elif self.H0prior=="log" : 
            pH0 = self.likelihood_combined/self.H0_array
            pH0_normalized =  pH0/simpson (pH0,self.H0_array)

        return pH0_normalized

    def prior (self) :
        if self.H0prior=="uniform" :
            H0prior = np.ones (self.H0_array.size)/(self.H0_array[-1]-self.H0_array[0])
        elif self.H0prior=="log" :
            invH0prior = self.H0_array*(np.log(self.H0_array[-1])-np.log(self.H0_array[0]))
            H0prior = 1/invH0prior
        
        return H0prior


class credible_interval:
    def __init__(self, posterior, H0, level, verbose=False):
        self.posterior = posterior
        self.H0 = H0
        self.level = level
        self.verbose = verbose
        self.lower_level, self.upper_level = self.HDI()
        self.interval = self.upper_level - self.lower_level
        self.map = self.MAP()
        
    def HDI(self):
        cdfvals = cumtrapz(self.posterior, self.H0)
        sel = cdfvals > 0.
        x = self.H0[1:][sel]
        cdfvals = cdfvals[sel]
        ppf = interp1d(cdfvals, x, fill_value=0., bounds_error=False)

        def intervalWidth(lowTailPr):
            ret = ppf(self.level + lowTailPr) - ppf(lowTailPr)
            if (ret > 0.):
                return ret
            else:
                return 1e4
        HDI_lowTailPr = fmin(intervalWidth, 1. - self.level, disp=self.verbose)[0]
        return ppf(HDI_lowTailPr), ppf(HDI_lowTailPr + self.level)


    def MAP(self):
        sp = UnivariateSpline(self.H0, self.posterior, s=0.)
        x_highres = np.linspace(self.H0[0], self.H0[-1], 100000)
        y_highres = sp(x_highres)
        return x_highres[np.argmax(y_highres)]


			
