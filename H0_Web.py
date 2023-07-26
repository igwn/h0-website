"""
Script for website 

Luis Miguel Galvis E
"""

#Libraries
import streamlit as st
from PIL import Image
from H0live import *
from numpy import where,array
import json

###########################################
#Session status
if 'object' not in st.session_state:
    st.session_state.object = None


sb = st.sidebar

st.title('$H_0$ estimator')

#add columns for subtitle and LOGO.
col1, col2 = st.columns([7, 2])

with col1:
    st.subheader('An estimator for the Hubble Constant based on gravitational wave multi-messenger observations')

with col2:
    image = Image.open('LVK_rainbow_dark.png')
    st.image(image)

sb.header("Adjust the assumptions that are used when estimating the Hubble constant")

csvfile='bright_sirens.csv'
jsonfile='bright-sirens.json'

#Function to read the csv file and get the events
def list_events_old(csv_file):
    ev1=pd.read_csv(csv_file,sep=",",engine='python')
    return ev1.columns[1:].values.tolist()

class list_events:
    def __init__(self,jsonfile):
        jsonin=json.load(open(jsonfile))
        self.evlist={}
        for gwev in jsonin:
            gwname=jsonin[gwev]['display_name']
            self.evlist[gwname]={}
            self.evlist[gwname]['counterpart']=[]
            self.evlist[gwname]['column']=[]
            for emev in jsonin[gwev]['Counterparts']:
                emname=jsonin[gwev]['Counterparts'][emev]['display_name']
                self.evlist[gwname]['counterpart'].append(emname)
                self.evlist[gwname]['column'].append(jsonin[gwev]['Counterparts'][emev]['column_name'])
        return
    
    def list(self):
        return self.evlist
    def getcolumn(self,gwev,emev):
        print(gwev,emev,self.evlist[gwev]['counterpart'])
        print(np.argwhere(self.evlist[gwev]['counterpart']==emev))
        return self.evlist[gwev]['column'][np.where(np.array(self.evlist[gwev]['counterpart'])==emev)[0][0]]

ev_list = list_events(jsonfile)
dictionary=ev_list.list()
print(dictionary)

#To create the lists to be used
Events=[]
Events_in_checbox=[]
Counterpart_in_selectbox=[]

#To create the sidebar form
with sb.form("My form"):
#To select the events and their counterparts
    st.subheader("Events and counterparts")
    st.markdown("""Select the GW events you want to include, and its EM counterpart:""")
    for key in dictionary:
        if Events_in_checbox==[] and Counterpart_in_selectbox==[]:
            Events_in_checbox.append(st.checkbox(key,True))
            Events.append(key)
            Counterpart_in_selectbox.append(st.selectbox("Counterpart ",dictionary[key]['counterpart'],key=key,label_visibility="collapsed"))
        else:
            Events_in_checbox.append(st.checkbox(key))
            Events.append(key)
            Counterpart_in_selectbox.append(st.selectbox("Counterpart ",dictionary[key]['counterpart'],key=key,label_visibility="collapsed"))
    
 
#To select the desired prior
    #st.markdown("""Select the prior you want to use for the $H_0$ estimation:""")
    prior_list=['uniform', 'log']
    choice = st.selectbox("**Prior**",prior_list) 

#To select additional H0 estimates and the plot of Individual event likelihoods 
    st.subheader("Additional options")
    planck_checkbox = st.checkbox('Planck H0 estimate',help='Planck Collaboration. *Planck 2018 results VI. Cosmological parameters*. **A&A** 641, A6 (2020). [https://doi.org/10.1051/0004-6361/201833910](https://doi.org/10.1051/0004-6361/201833910)')
    sh0es_checkbox = st.checkbox('SH0ES H0 estimate',help='Riess, A. G., Casertano, S., Yuan, W., Macri, L. M., and Scolnic, D. *Large Magellanic Cloud Cepheid Standards Provide a 1% Foundation for the Determination of the Hubble Constant and Stronger Evidence for Physics beyond ΛCDM*. **The Astrophysical Journal** 876, no. 1 (2019). [https://doi.org/10.3847/1538-4357/ab1422](https://doi.org/10.3847/1538-4357/ab1422)')
    indivual_likelihoods_checkbox = st.checkbox('Individual event likelihoods')
    add_options_choice=[planck_checkbox,sh0es_checkbox,indivual_likelihoods_checkbox]
    


#To create the list of events and their counterparts chosen
    choice_list1=[]
    for i in range(len(Events_in_checbox)):
        if Events_in_checbox[i]==True:
            choice_list1.append(ev_list.getcolumn(Events[i],str(Counterpart_in_selectbox[i])))
            # choice_list1.append(str(Events[i])+"_"+str(Counterpart_in_selectbox[i]))


     
    #To calculate the H0    
    Calculated = st.form_submit_button("Calculate")   

#When no event is selected
if choice_list1==[]:
    if  Calculated or not Calculated:
        st.header(":red[Please select an event and its counterpart!]")

    

#Default values starting the program
else:
    choice_list2=[]

    if not Calculated and st.session_state.object is None:
        # choice_list2.append(str(Events[0])+"_"+str(dictionary[Events[0]][0]))
        choice_list2.append(ev_list.getcolumn(Events[0],str(Counterpart_in_selectbox[0])))
        h0live_output=H0live(choice_list2, choice,planck=add_options_choice[0],riess=add_options_choice[1],likelihood_plot=add_options_choice[2],data_download=True,likelihood_fname=csvfile)
        csv = h0live_output.H0data_download.to_csv(index=False)
                
        sb.download_button(
        "Download data",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv')  
#If events are selected
    if Calculated:
        st.session_state.object=H0live(choice_list1, choice,planck=add_options_choice[0],riess=add_options_choice[1],likelihood_plot=add_options_choice[2],data_download=True,likelihood_fname=csvfile)
        csv = st.session_state.object.H0data_download.to_csv(index=False)
        a=sb.download_button(
        "Download data",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv')     
        
#To work outside of form without disappearing the image
    if not Calculated and st.session_state.object is not None:
        h0live_output=H0live(choice_list1, choice,planck=add_options_choice[0],riess=add_options_choice[1],likelihood_plot=add_options_choice[2],data_download=True,likelihood_fname=csvfile)
        csv = h0live_output.H0data_download.to_csv(index=False)
        b=sb.download_button(
        "Download data",
        csv,
        "file.csv",
        "text/csv",
        key='download-csv')  

st.markdown("""
            **Did you know that gravitational waves can be used to measure the expansion of the Universe? 
            This plot shows one estimate - change the assumptions and events included to update the estimate.**
            """)


st.divider()
st.header('What is the Hubble constant?')
st.markdown("""
            The Hubble constant, $H_0$, is a measure of how fast our universe is expanding. As the universe expands, objects such as galaxies get further apart. From Earth, the galaxies appear to be moving away from us. The speed at which they do so is known as their "recession velocity" ($v$), and it is directly proportional to their distance ($D$) from us: $v = H_0 D$.
            
            This is known as the Hubble–Lemaître law, and the constant of proportionality is the Hubble constant. It is usually measured in km/s/Mpc (kilometers per second per megaparsec, where a megaparsec is just over 3 million light years), and today we know that it has a value of about 70 km/s/Mpc. This means that for every Mpc of distance from us, a galaxy’s recession velocity increases by around 70 km/s.
            """)
            

st.subheader('Why use gravitational waves to measure $H_0$?')
st.markdown("""
            Other techniques for measuring the Hubble constant, such as using Type IA supernovae (by e.g. the SH0ES Collaboration) and measurements of the very early Universe (by e.g. the [Planck Collaboration](https://www.cosmos.esa.int/web/planck/planck-collaboration)), currently disagree with each other, with values of around 73 km/s/Mpc and 67 km/s/Mpc respectively (which you can add to the plot if you like). 
            Gravitational waves, by making an independent measurement of the Hubble constant, might be able to 
            shed light on this apparent discrepancy.
            """)
            
st.divider()
st.header('How do you measure the Hubble constant using gravitational waves?')
st.markdown("""
            Gravitational wave observations of merging black holes and neutron stars by [Advanced LIGO](https://www.ligo.org/about.php), [Virgo](https://www.virgo-gw.eu/) and [KAGRA](https://gwcenter.icrr.u-tokyo.ac.jp/en/) provide us with a direct measurement of their luminosity distance ($D_L$).
            
            In the nearby universe, the Hubble–Lemaître law can be expressed in terms of luminosity distance and redshift ($z$) as $c z ≈ H_0 D_L$, where $c$ is the speed of light. 
            
            If the gravitational wave is well localised on the sky astronomers can use their telescopes to search this area for any electromagnectic (EM) signals produced by the merging objects, covering wavelengths from radio to gamma rays. If an EM counterpart is detected, it can be used to identify the host galaxy of the gravitational wave, and then the redshift of that galaxy can be used in combination with the GW distance to measure $H_0$!
            
            There are large uncertainties on the distance measured by today's GW detectors -- usually around 30%. This means that the measurement of $H_0$ from a single GW event will have a large uncertainty associated with it. However, by combining the results from multiple GW-EM observations, these uncertainties will decrease, leading to a more informative measurement. The plot above shows a quick estimate of the Hubble constant based on the selected GW and EM events. Try changing the GW events and EM counterparts which are selected to see how the estimate changes.
            """)

st.subheader('The assumptions used in this website')
st.markdown("""
            This website only uses publicly available GW and EM data. The GW data comes in the form of skymaps from [GraceDB](https://gracedb.ligo.org/). These provide an estimate of the 3D localisation of the GW event, in the form of a sky probability and Gaussian distance estimate for every line-of-sight. This information is produced from a preliminary, "quick" analysis of the GW event, and will differ from the final volume localisation produced by the LVK for this event, for which a more rigorous analysis is applied. This means that, while the distance estimate will be in the right ballpark, the shape of the distance distribution, including its peak and width, is likely to change with later analyses.
            
            A number of other simplifying assumptions are made to produce the estimate above. The linear Hubble relation written above is only valid in the local universe, but is used throughout this analysis, meaning that for higher distance events the result will be less reliable. This allows us to approximate GW selection effects as $∝ H_0^3$, which means we can ignore the impact of detector sensitivity and the GW mass distribution (among other things), which are required to accurately estimate this.
            
            This website neglects the impact of galaxy peculiar velocity can have on the result. Galaxy motion not due to the expansion of the universe is known as its peculiar velocity, and can have a large impact on the galaxy's measured redshift, especially for galaxies which are relatively nearby to us. The result above also treats the selected EM counterparts as if they are confidently associated with the GW event, and does not take into account any uncertainty in the association.
            """)


st.divider()
st.header('Additional information')
st.markdown("""
            The values of the Hubble constant provided here are not intended to be scientifically accurate estimates. This website is intended to be an educational resource. For the latest official measurement of the Hubble constant from the LVK collaboration, look out for the [latest LVK publications](https://pnp.ligo.org/ppcomm/Papers.html).
            
            If you have questions about gravitational wave science, please visit [https://ask.igwn.org](https://ask.igwn.org).
            """)


st.subheader('How to cite this website?')
st.markdown("""
            If you would like to use the plot on this website, then please do so. Please quote the URL, 
            with credit to the LIGO-Virgo-KAGRA Collaboration. Please note that users will not necessarily 
            use the same events that you have selected, and that the options may change over time.
            """)



st.subheader('Credits and contacts')
st.markdown("""
            The website is provided on behalf of the LIGO-Virgo-KAGRA collaboration. It was developed by <>. 
            
            If you find an issue with the website, please report it on the Github repository 
            [H0WEBSITE](https://github.com/SergioVallejoP/H0WEBSITE).
            """)
