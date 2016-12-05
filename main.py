from glob import glob
import sys
from astropy.table import Table

from bokeh.io import curdoc
from bokeh.layouts import row, column
from bokeh.models import ColumnDataSource, DataRange1d, Range1d, Select, Button, CustomJS, DataTable, TableColumn
from bokeh.plotting import figure

def get_dataset(filename):
    df = Table.read(filename)['obsmjd','mag_autocorr','magerr_auto'].to_pandas().copy()
    df['upper'] = df['mag_autocorr']+df['magerr_auto']
    df['lower'] = df['mag_autocorr']-df['magerr_auto']
    return ColumnDataSource(data=df)

def make_plot(source, title):
    plot = figure(plot_width=800, tools="pan,wheel_zoom,lasso_select,tap,save,box_zoom,reset", 
                  toolbar_location="above",active_drag="box_zoom",active_tap="tap",active_scroll="wheel_zoom")
    plot.title.text = title
    
    
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

def update_plot(attrname, old, new):
    target = target_select.value
    plot.title.text = "PTF light curve for " + target
    src = get_dataset(targets[target])
    source.data.update(src.data)

def prev_target():
    targlist = target_select.options
    currentind = targlist.index(target_select.value)
    if currentind > 0:
        target_select.value = targlist[currentind-1]
        
def next_target():
    targlist = target_select.options
    numtargs = len(targlist)
    currentind = targlist.index(target_select.value)
    if currentind < numtargs -1:
        target_select.value = targlist[currentind+1]

#Check that data dirctory was supplied
datadir = './data/'
if len(sys.argv) > 1:
    datadir = sys.argv[1]
if datadir[-1] != '/':
    datadir += '/'

    
#Set up interaction for selecting data source

#Dict mapping target names to filenames
fnames = glob(datadir+'*.xml')
targets = {}
for fname in fnames:
    targets[fname.split('/')[-1][:-4]] = fname
target = targets.keys()[0]

#Dropdown to select target
target_select = Select(value=target, title='Target', options=sorted(targets.keys()))
target_select.on_change('value', update_plot)

#Buttons to change target
prevtarg = Button(label='Previous')
prevtarg.on_click(prev_target)
nexttarg = Button(label='Next')
nexttarg.on_click(next_target)

#Initialize data source and plot
source = get_dataset(targets[target])
plot = make_plot(source, "PTF light curve for " + target)

#Initialize table
datacolumns = []
fields = ['obsmjd','mag_autocorr','magerr_auto']
for field in fields:
    datacolumns.append(TableColumn(field=field,title=field))
data_table = DataTable(source=source, columns=datacolumns, width=800)

#Set up layout
controls = column(target_select,prevtarg,nexttarg)

curdoc().add_root(column(controls, plot, data_table))
curdoc().title = "PTF Viewer"
