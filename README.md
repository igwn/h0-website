# Hubble constant viewer

This app takes distance measurements from LIGO-Virgo-KAGRA measurements of gravitational wave events, combined with electromagnetic counterpart data, and calculates an estimate of the Hubble constant. The distance likelihood measurements from one or more events is used along with the redshift measurement (and uncertainty) of potential counterparts to calculate the posterior probability of the Hubble constant.

This is not intended for scientific purposes, but to get a "quick look" at the estimated 

## Web-interface
Prototype at https://h0-constant-ligo.streamlit.app/

## Data Processing
* process_events.py
    1. Import events from `events-list.json`
    1. Download skymap from external sources (e.g. GraceDB) if required
    1. Collate EM counterparts and produce column names
    1. Export column names to `column-names.py`
    1. Export GW/EM data to `bright-sirens.json`
    1. Run `bright_siren_likelihood.py` (see below)
    1. Add distance mean and uncertainty to `bright-sirens.json`


* bright_siren_likelihood.py
    1. load skymap for GW event
    1. Use RA/DEC of EM counterpart to extract distance likelihood data
    1. Use distance likelihood and EM counterpart redshift to calculate H0 likelihood
    1. Export H0 likelihoods to `bright_sirens.csv`

The `bright-sirens.json` file is used by the web interface, along with the data in `bright_sirens.csv`.

## Data structure (events-list.json)

The three sections of the `events-list.json` are:
* `H0events` :the pairings of the GW and EM counterparts
    * This can include one or more EM counterparts for each GW event
* `GW_data`: GW events
* `EM_data`: EM events

##### JSON file structure:

```
{
    "H0events":{
        <GW event name>:{
            "GW": GW event code (in GW_data)
            "EM": [list of one or more EM counterpart codes (in EM_data)]
        }    
    },
    "GW_data":{
        <GW event code 1>:{
            "src": "local" for local skymap or "gracedb" for gracedb event
            "id": ID of event in gracedb
            "display_name": Name to display on website
            "Skymap": file containing skymap (for local events)
            "reference": Citation for data/publication
        },
        <GW event code 2>:{
            ...
        }
    },
    "EM_data":{
        <EM event code 1>:{
            "src": "local" (no other options at present),
            "id": ID of event (not used for local events),
            "display_name": Name to display on website,
            "cz_mean": Mean velocity (km/s),
            "cz_sigma": Velocity uncertainty (km/s),
            "ra_deg": Right ascension of source (decimal degrees),
            "dec_deg": Declination of source (decimal degrees),
            "reference": Citation for data/publication
        },
        <EM event code 2>:{
            ...
        } 
    }
}
```
