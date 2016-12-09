from __future__ import absolute_import
from __future__ import print_function
from glob import glob
import numpy as np
import sys
import os
from astroquery.irsa import Irsa
from astropy.coordinates import SkyCoord
from astropy.table import Table
import astropy.units as u

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, DataRange1d, Select, Button, DataTable, TableColumn, TextInput, Div, VBox, RadioButtonGroup
from bokeh.plotting import figure



#Before everything, check if data directory was supplied
#Check that data dirctory was supplied.
#If it doesn't exist, create a data directory.
datadir = os.getcwd()+'/data/'
if len(sys.argv) > 1:
    datadir = sys.argv[1]
if datadir[-1] != '/':
    datadir += '/'
if not os.path.exists(datadir):
    datadir = os.getcwd()+'/data/'
    print(('Created data directory at '+datadir))
    if not os.path.exists(datadir):
        os.makedirs(datadir)


#Define many needed functions

#Read in data from file
def get_dataset(filename):
    df = Table.read(filename).to_pandas().copy()
    cols = df.keys()
    df['upper'] = df['mag_autocorr']+df['magerr_auto']
    df['lower'] = df['mag_autocorr']-df['magerr_auto']
    return ColumnDataSource(data=df),cols

#Make initial plot object
def make_plot(source, title):
    plot = figure(plot_width=800, tools="pan,wheel_zoom,lasso_select,tap,save,box_zoom,reset", 
                  toolbar_location="above",active_drag="box_zoom",active_tap="tap",active_scroll="wheel_zoom",
                  title=title)
    
    
    plot.segment(x0='obsmjd',y0='lower',x1='obsmjd',y1='upper',source=source,color="black")
    plot.circle(x='obsmjd',y='mag_autocorr',source=source,size=10, color="red", alpha=1)  

    # fixed attributes
    plot.xaxis.axis_label = "MJD"
    plot.yaxis.axis_label = "mag"
    plot.axis.axis_label_text_font_style = "bold"
    plot.x_range = DataRange1d(range_padding=0.1)
    plot.y_range = DataRange1d(range_padding=0.1,flipped=True)
    plot.grid.grid_line_alpha = 0.3

    return plot

#Update plot with new data
def update_plot(attrname, old, new):
    target = target_select.value
    plot.title.text = "PTF light curve for " + target
    src,_ = get_dataset(targets[target])
    source.data.update(src.data)
    xstart=min(source.data["obsmjd"])
    xend=max(source.data["obsmjd"])
    xpad = 0.1*(xend-xstart)/2.
    plot.x_range.start=xstart-xpad
    plot.x_range.end=xend+xpad
    ystart=max(source.data["upper"])
    yend=min(source.data["lower"])
    ypad = 0.1*(ystart-yend)/2.
    plot.y_range.start=ystart+ypad
    plot.y_range.end=yend-ypad

#Examine previous target in list
def prev_target():
    targlist = target_select.options
    currentind = targlist.index(target_select.value)
    if currentind > 0:
        target_select.value = targlist[currentind-1]

#Examine next target in list
def next_target():
    targlist = target_select.options
    numtargs = len(targlist)
    currentind = targlist.index(target_select.value)
    if currentind < numtargs -1:
        target_select.value = targlist[currentind+1]

#Clear search fields
def clearfields():
    targ_input.value = ''
    ra_input.value = ''
    dec_input.value = ''

#search for and download new PTF data
def search():
    #See if target name was supplied
    hasName = False
    if (targ_input.value.replace(" ","") != ""):
        hasName = True
    
    #See if coordinates were supplied
    hasCoords = False
    if ((ra_input.value.replace(" ","") != "") & (dec_input.value.replace(" ","") != "")):
        hasCoords = True
    
    raunits = [u.hourangle,u.deg][ra_format.active]
    
    coords = None
    if hasCoords:
        coords = SkyCoord(ra=ra_input.value.strip(),dec=dec_input.value.strip(),
                          unit=(raunits,u.deg),frame='icrs')
    elif hasName:
        coords = SkyCoord.from_name(targ_input.value.strip())
        ra = ''
        dec = ''
        if ra_format.active == 0:
            ra,dec = coords.to_string('hmsdms').split()
        elif ra_format.active == 1:
            ra,dec = coords.to_string('dms').split()
        
        ra_input.value = ra
        dec_input.value = dec
    if coords is not None:
        if hasName:
            download_ptf(coords,targ_input.value.strip(),directory=datadir)
        else:
            download_ptf(coords,directory=datadir)

#Download PTF data and add to list
def download_ptf(coords,name=None,directory='./'):
    """Download PTF light curve data.

    Keyword arguments:
    coords -- astropy.coordinates.SkyCoord object
    name -- string for filename (default None, i.e. PTF oid)
    directory -- location to save data (default './')
    """
    #Download the PTF data
    table = Irsa.query_region(coordinates=coords,catalog='ptf_lightcurves',radius=5*u.arcsec)
    table = table.filled(-99)
    nearest = np.where(table['dist'] == np.min(table['dist']))
    if name is None:
        name = str(table["oid"][0])
    fname = datadir+name+'.xml'
    table[nearest].write(fname, format='votable', overwrite=True)
    #add to target menu and display
    targets[name] = fname
    target_select.options.append(name)
    target_select.value = target_select.options[-1]
    
    

    
#Set up interaction for selecting data source

#Dict mapping target names to filenames
fnames = glob(datadir+'*.xml')
targets = {}
if len(fnames) == 0:
    targets["SAMPLE DATA. Search for your target above."] = './sampledata.xml'
for fname in fnames:
    targets[fname.split('/')[-1][:-4]] = fname
target = list(targets.keys())[0]

#Dropdown to select target
target_select = Select(value=target, title='Target to display:', options=sorted(targets.keys()),width=220)
target_select.on_change('value', update_plot)

#Buttons to change target
prevtarg = Button(label='Previous',width=100)
prevtarg.on_click(prev_target)
nexttarg = Button(label='Next',width=100)
nexttarg.on_click(next_target)

#Paragraph at top
div = Div(text="""Select a new target from the left to
              display data or use the form to the right to
              download new data. <p />More information about
              this tool can be found at 
              <a href="https://github.com/keatonb/PTFViewer">
              https://github.com/keatonb/PTFViewer</a>""",
              width=400, height=100)

#Set up area to download data:
targ_input = TextInput(value="", title="Search Target:",width=300)
ra_input = TextInput(value="", title="Right Ascension:",width=120)
ra_box = VBox(ra_input,width=150,height=50)
dec_input = TextInput(value="", title="Declination:",width=120)
dec_box = VBox(dec_input,width=150,height=50)
ra_format = RadioButtonGroup(labels=["hours","degrees"],active=0,width=220)
clearbtn = Button(label='clear',width=80)
clearbtn.on_click(clearfields)
search_button = Button(label='Search and Download Nearest Object',width=300)
search_button.on_click(search)

#Initialize data source and plot
source,cols = get_dataset(targets[target])
plot = make_plot(source, title="PTF light curve for " + target)

#Initialize table
datacolumns = []
for field in cols:
    datacolumns.append(TableColumn(field=field,title=field,width=150))
data_table = DataTable(source=source, columns=datacolumns, width=800, height=300, 
                       fit_columns=False, selectable=True)

#Set up layout
datacontrols = column(target_select,row(prevtarg,nexttarg))
coords_in = row(ra_box,dec_box,width=300)
search_in = column(targ_input,coords_in,row(ra_format,clearbtn),search_button)

sep = Div(text="",width=100)
header = row(div,sep,search_in)

curdoc().add_root(column(header,datacontrols, plot, data_table))
curdoc().title = "PTF Viewer"
