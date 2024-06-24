'''
Created 21 Jun 2024

@author: Jake Gordon, <jacob.b.gordon@gmail.com>

Script to convert GPS files from the field to a more user-friendly format.
'''
import sys
from datetime import datetime
from os import path

finalColumnHeadings = ['name', 'description', 'position', 'altitude']

def fixMapSourceTimeStamp(timestamp):
    '''
    Changes a timestamp used in MapSource to one with the desired format.
    These files come with timestamps in "M/DD/YYYY H:MM:SS XM" format, and we
    need them to be "YYYY/MM/DD HH:MM" (24-hr time).
    
    Timestamps may also be in "M/DD/YYYY H:MM:SS XM (UTC+3)" format.
    
    Returns a string: the timestamp in the desired format
    '''
    splitTime = timestamp.split()
    if splitTime[-1] == "(UTC+3)":
        splitTime.pop(-1)
        timestamp = " ".join(splitTime)
    
    thisTime = datetime.strptime(timestamp, "%m/%d/%Y %I:%M:%S %p")
    #print ("Fixing timestamp", thisTime)
    return thisTime.strftime('%Y/%m/%d %H:%M')

def fixBaseCampTimeStamp(timestamp):
    '''
    Changes a timestamp used in BaseCamp to one with the desired format.
    These files come with timestamps in "YYYY-MM-DDTHH:MM:SSZ" format in UTC,
    and we need them to be "YYYY/MM/DD HH:MM" (24-hr time) in local (Kenya)
    time.
    
    Returns a string: the timestamp in the desired format
    '''
    timestamp = timestamp.replace("T", " ")
    timestamp = timestamp.replace("Z", "")
    
    thisTime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    # That time is UTC.  Add 3 hours to bring it to Kenya
    from datetime import timedelta
    thisTime = thisTime + timedelta(hours=3)
    #print ("Fixing timestamp", thisTime)
    return thisTime.strftime('%Y/%m/%d %H:%M')

def convertGPSFile(thisFilePath, newFilePath):
    '''
    Opens a GPS file at thisFilePath (a string containing a path to a file),
    judges if the file came from MapSource or BaseCamp, processes out all the
    junk, then writes a new correctly-formatted file at newFilePath (also a
    string).
    
    MapSource files are identified because the first word of the first row is
    "Grid".
    
    BaseCamp files are identified because their first row is empty, and the
    second row is only the word, "metadata".
    
    Returns a string, "DONE!", if everything goes okay.  Otherwise, returns a
    different string that indicates what went wrong.
    '''
    # Open the file
    thisFile = open(thisFilePath, "r")
    
    # Figure out this file's origin by checking the contents of the first line
    thisLine = thisFile.readline()
    thisLine = thisLine.strip().split()
    if len(thisLine) == 0 or thisLine == ['\ufeff']:
        # First line is empty or just has the "BOM", it's probably a BaseCamp
        # file.  Let's make sure.
        nextLine = thisFile.readline().strip()
        if nextLine[:] == "metadata":
            print("File " + path.basename(thisFilePath) + " is from BaseCamp")
            return convertBaseCampFile(thisFile, newFilePath)
    elif thisLine[0] == 'Grid': # It's MapSource
        print("File " + path.basename(thisFilePath) + " is from MapSource")
        fileIdentified = True
        return convertMapSourceFile(thisFile, newFilePath)
    
    # If we get here at all, something is wrong.
    print("Problem with file " + path.basename(thisFilePath) + "!")
    print("It doesn't look like a MapSource nor BaseCamp file. Cannot convert")
    thisFile.close()
    return "Problem with file " + path.basename(thisFilePath) + "!"

def convertMapSourceFile(openedFile, outFilePath):
    '''
    Take the data in openedFile--a file object that has already been opened to
    read and has had its first line read and was determined to be a txt file
    exported by Garmin MapSource-- then write a new correctly-formatted file
    at outFilePath (a string).
    
    Returns the string, "DONE!". (Used in the GUI)
    '''
    # Read (omit) the next two lines
    thisLine = openedFile.readline()
    #print ("Skip this line:", thisLine)
    thisLine = openedFile.readline()
    #print ("Skip this line:", thisLine)
    
    # Next line is the column headers, tab delimited.  Keep and split the line.
    columnHeaders = openedFile.readline().strip().split("\t")
    #print ("Column Headers are:")
    #print (columnHeaders)
    # Convert all column headers to lowercase
    columnHeaders = [column.lower() for column in columnHeaders]
    #print ("and after lowercasing...")
    #print (columnHeaders)
    
    # Now (finally) we're to the data. Read the remaining lines into a
    # new list, then strip and split them
    theData = openedFile.readlines()
    #print ("The actual data:")
    #print (theData)
    theData = [line.strip().split("\t") for line in theData]
    
    # Done with openedFile, so close it
    openedFile.close()
    print ("Closed source file")
    
    # Make list as holding place for processed data rows
    newData = []
    
    # Iterate through the remaining lines. Read each into a dictionary,
    # using the columnHeaders as keys. Then write a new line to newData 
    # using only finalColumnHeadings. Don't write directly to newFile
    # because we need to sort the data by date/time first.
    for line in theData:
        if len(line) <= 1:
            # Then this is an empty line that we don't want
            print ("Skipping empty line", line)
            continue
        #print ("Starting line:")
        #print (line)
        thisDict = {}
        for (column, data) in zip(columnHeaders, line):
            thisDict[column] = data
        #print ("This line as a dict:")(
        #print (thisDict)
        
        # Set the "description" column to equal the "date modified"
        # column after reformatting the timestamp
        #print ("Frob description column")
        thisDict["description"] = fixMapSourceTimeStamp(thisDict["date modified"])
        
        # Temporary list to hold output values
        thisNewRow = []
        
        # Add the desired columns to thisNewRow
        for column in finalColumnHeadings:
            thisNewRow.append(thisDict[column])
        #print ("All the desired data:")
        #print (thisNewRow)
                
        # Add thisNewRow to newData
        newData.append(thisNewRow)
        
        #print ("Done with", line)
    
    # Sort the rows in newData, by date/time (index 1)
    #print ("Sorting newData. First row is:")
    #print (newData[0])
    #print ("...and last row is:")
    #print (newData[-1])
    newData = sorted(newData, key = lambda this_row: this_row[1])
    #print ("Done sorting newData. First row NOW is:")
    #print (newData[0])
    #print ("...and last row NOW is:")
    #print (newData[-1])
    
    # Turn all these newData rows into joined strings
    #print ("Begin tab-joining items in each line of newData")
    newData = [("\t".join(line) + "\n") for line in newData]
    #print ("Done. Sample newData row:")
    #print (newData[0])
    
    # Open the new file and get ready to start writing
    print ("Open the new file at", path.basename(outFilePath))
    newFile = open(outFilePath, "w")
    
    # Write the column heading
    newLine = "\t".join(finalColumnHeadings) + "\n"
    #print ("Column names are", newLine)
    newFile.write(newLine)
    
    # Write newData
    newFile.writelines(newData)
    
    # Close the new file
    #print ("Closing output file")
    newFile.close()
    
    print ("Done writing to", path.basename(outFilePath), "!")
    return "DONE!"
    

def convertBaseCampFile(openedFile, outFilePath):
    '''
    Take the data in openedFile--a file object that has already been opened to
    read and has had its first line(s) read and was determined to be a txt file
    exported by Garmin BaseCamp-- then write a new correctly-formatted file at
    outFilePath (a string).
    
    Returns the string, "DONE!" (Used in the GUI) when everything is okay.
    ...unless no data can be found, in which case the string "Can't find data"
    is returned.
    '''
    # Skip the rows we don't care about until we find the "table" of waypoints
    lineFound = False
    thisLine = openedFile.readline()
    while not lineFound and thisLine:
        #print("Checking line:" + thisLine)
        splitLine = thisLine.strip().split("\t")
        if splitLine[0] == 'wpt': # We're about to see the waypoints
            #print("Found it:", "\t".join(splitLine))
            lineFound = True
        thisLine = openedFile.readline()
    
    if not lineFound: # We couldn't find what we were looking for
        openedFile.close()
        print("Cannot find a waypoints ('wpt') table, file not converted")
        return "Can't find data in this file"
    
    # Or, we did find it
    # thisLine is column headers, tab delimited. Keep and split the line.
    columnHeaders = thisLine.strip().split("\t")
    #print ("Column Headers are:")
    #print (columnHeaders)
    # Convert all column headers to lowercase
    columnHeaders = [column.lower() for column in columnHeaders]
    #print ("and after lowercasing...")
    #print (columnHeaders)
    
    # Now (finally) we're to the data. Make a new list for the remaining
    # lines, and read lines into it until we find an empty row again
    theData = []
    lineFound = False
    thisLine = openedFile.readline()
    while not lineFound and thisLine:
        #print("Checking line:" + thisLine)
        splitLine = thisLine.strip().split("\t")
        if len(splitLine) == 1: # then we're done
            lineFound = True
        else:
            theData.append(splitLine)
        thisLine = openedFile.readline()
    # We're done getting data from the file, so let's close it
    openedFile.close()
    print ("Closed source file")
    
    #print("theData are:")
    #print(theData)
    # Make list as holding place for processed data rows
    newData = []
    
    # Iterate through theData. Read each line into a dictionary, using
    # the columnHeaders as keys. Using the info in that dictionary,
    # add values for "description", "position", and "altitude".  Then
    # write a new line to newData using only
    # finalColumnHeadings. Don't write directly to a new file because
    # we need to sort the data by date/time first.
    for line in theData:
        #print ("Starting line:")
        #print (line)
        thisDict = {}
        for (column, data) in zip(columnHeaders, line):
            thisDict[column] = data
        #print ("This line as a dict:")
        #print (thisDict)
        
        # The "name" column tends to have superfluous quotation marks. So
        # let's remove them.
        thisDict["name"] = thisDict["name"][:].replace('"', '')
        # Set the "description" column to equal the "time" column, plus 3
        # hours.  Also change the format of the timestamp
        #print ("Frob description column")
        thisDict["description"] = fixBaseCampTimeStamp(thisDict["time"])
        
        # Set the "position" column to be the longitude, then the latitude
        thisDict["position"] = (thisDict["lon"] + " " + thisDict["lat"])
        
        # Set the "altitude" column to be the "ele" (elevation)
        thisDict["altitude"] = thisDict["ele"][:]
        
        # Temporary list to hold output values
        thisNewRow = []
        
        # Add the desired columns to thisNewRow
        for column in finalColumnHeadings:
            thisNewRow.append(thisDict[column])
        #print ("All the desired data:")
        #print (thisNewRow)
            
        # Add thisNewRow to newData
        newData.append(thisNewRow)
        
        #print ("Done with", line)
    
    # Sort the rows in newData, by date/time (index 1)
    #print ("Sorting newData. First row is:")
    #print (newData[0])
    #print ("...and last row is:")
    #print (newData[-1])
    newData = sorted(newData, key = lambda this_row: this_row[1])
    #print ("Done sorting newData. First row NOW is:")
    #print (newData[0])
    #print ("...and last row NOW is:")
    #print (newData[-1])
    
    # Turn all these newData rows into joined strings
    #print ("Begin tab-joining items in each line of newData")
    newData = [("\t".join(line) + "\n") for line in newData]
    #print ("Done. Sample newData row:")
    #print (newData[0])
    
    # Open the new file and get ready to start writing
    print ("Open the new file at", path.basename(outFilePath))
    newFile = open(outFilePath, "w")
    
    # Write the column heading
    newLine = "\t".join(finalColumnHeadings) + "\n"
    #print ("Column names are", newLine)
    newFile.write(newLine)
    
    # Write newData
    newFile.writelines(newData)
    
    # Close the new file
    #print ("Closing output file")
    newFile.close()
    
    print ("Done writing to", path.basename(outFilePath), "!")
    return "DONE!"
    

