# PTFViewer
PTFViewer is a Bokeh application for visualizing public light curve data from the [Palomar Transient Factory](http://www.ptf.caltech.edu/) written in Python.

It requires [astropy](http://www.astropy.org/), [astroquery](http://astroquery.readthedocs.io), and [Bokeh](http://bokeh.pydata.org/en/latest/).

This software displays interactive plots and linked table views of Palomar Transient Factory (PTF) DR3 public light curve data through a locally served web app.

Search a coordinate or target name for available PTF data. PTFViewer will download the light curve if available and plot it with error bars. The full data table is displayed below the plot.

The toolbar at the top of the plot window allows you to pan, zoom, select points or save a PNG copy of the current view. The plot and full data table below it are linked, so any selection in one is highlighted in the other.

To launch the Bokeh server, run the command:
```
bokeh serve --show path/to/PTFViewer.py
```
Example data is included for the Type 1a supernova PTF10icb that was discovered in PTF data and announced by [Nugent, P., Sullivan, M., \& Howell, D. A. 2010, The Astronomer's Telegram, 2657](http://www.astronomerstelegram.org/?read=2657). These data are also shown in the example figure below.

![Example data on PTF10icb](https://github.com/keatonb/PTFViewer/blob/master/sampleplot.png)

This project is a work in progress. If there are specific improvements you would like to see, indicate them in the "Issues" on GitHub.

If you find this software useful in your research and wish to acknowledge it in a publication, consider including "This work made use of the PTFViewer application written by Keaton J. Bell: https://github.com/keatonb/PTFViewer/."

---
**To inspect many objects**: you may wish to `import PTFViewer.download_ptf` to your own script that runs through your target list coordinates. To use PTFViewer to display the xml data downloaded to a directory other than the app default, use:
```
bokeh serve --show path/to/PTFViewer.py --args /path/to/xml/data/
```
---
Note current issues:
 - Attempts to determine the coordinate of a named target using the CDS name resolver frequently time out. Try again after a couple seconds.
