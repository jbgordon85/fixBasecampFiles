# fixBasecampFiles
For fixing BaseCamp text files so that humans can read them

A simple GUI.  You choose a txt file, which should be a txt file
exported by Garmin's BaseCamp.  You then choose the name of a new
file, or let this GUI make a name for the new file.  Hit "Go", and the
first file is opened/parsed, and the new file is written (or
overwritten, if it already existed).  In the new file, the waypoints
are the only thing retained.  They are sorted chronologically, the
timestamps are all converted to Kenya time (3 hrs ahead of UTC), and
only the columns that are of interest to me remain.

Despite the name "fixBasecampFiles", this package knows how to read
files exported from Garmin's Mapsource, too.
