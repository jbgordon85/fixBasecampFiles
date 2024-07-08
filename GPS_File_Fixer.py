'''
Created on 21 Jun 2024

A GUI for choosing a txt file from BaseCamp that we want to clarify.

'''

from os import path
from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from fixGPSFiles import *

class GPS_File_Fixer(Frame):
    '''
    Create the GUI used for checking processed Prim8 data for issues
    '''
    
    def __init__(self, root):
        '''
        Build the GUI.
        '''
        Frame.__init__(self, root)
        
        # Define labels
        l1 = Label(root, text="File from BaseCamp:")
        l2 = Label(root, text="New file that will be created:")
        l2a = Label(root, text="(autofilled)")
        l3 = Label(root, text="Current status:")
        
        # Place (grid) labels
        l1.grid(row=0)
        l2.grid(row=1, column = 0)
        l2a.grid(row=1, column = 3)
        l3.grid(row=2, column= 0)
        
        # Define text variables (tv) and their associated entry (e) fields
        tv1 = StringVar()
        tv2 = StringVar()
        tv3 = StringVar()
        
        e1 = Entry(root, textvariable=tv1) 
        e2 = Entry(root, textvariable=tv2)
        e3 = Entry(root, textvariable=tv3)
        
        # Place (grid) entry fields
        e1.grid(row=0, column=1)
        e2.grid(row=1, column=1)
        e3.grid(row=2, column=1)
        
        # Define buttons
        b1 = Button(root, text='Choose', command = lambda: self.getOpenFileAndAutofill(tv1, tv2, tv3))
        b2 = Button(root, text='Choose', command = lambda: self.getOpenFileName(tv2, tv3))
        b3 = Button(root, text='Go!', command = lambda: self.checkAndFixFile(tv1, tv2, tv3))
        b4 = Button(root, text='Quit', command = lambda: self.endProgram(root))
        
        # Place (grid) buttons
        b1.grid(row=0, column=2, sticky='W', pady=4)
        b2.grid(row=1, column=2, sticky='W', pady=4)
        b3.grid(row=3, column=0, sticky='W',pady=4)
        b4.grid(row=3, column=2, sticky='W',pady=4)
        
    
    def getOpenFileName(self, textVariable, statusBar):
        '''
        Opens a dialog to ask for a file name to open.  Sets textVariable to
        hold the file's path (a string).
        
        statusBar is a part of the GUI that this can write to. There's not
        much to actually do with it in this case, but we want to empty it
        after this finishes.
        '''
        filePath = askopenfilename(filetypes=(('Tab-delimited','*.txt'),('All files','*.*')), title='Choose a file:')
        print("Got file path:", filePath)
        textVariable.set(filePath)
        
        statusBar.set("")
    
    def getOpenFileAndAutofill(self, textVariable1, textVariable2, statusBar):
        '''
        Just like "getOpenFileName", but also creates suggested file
        name and inserts it into textVariable2
        '''
        self.getOpenFileName(textVariable1, statusBar)
        
        sourcePath = str(textVariable1.get())
        
        if len(sourcePath) > 0: # Only do the below if a file was selected
            newPath = sourcePath[:-4] + '_NEW.txt' # So "./filename.txt" suggests "./filename_NEW.txt"
            
            print("Suggesting new file path:", path.basename(newPath))
            textVariable2.set(newPath)
            statusBar.set("Autofilled new file name: " + path.basename(newPath))
        
    
    def endProgram(self, root):
        '''
        Ends the program.
        '''
        print("Closing program!")
        root.quit()
    
    def integrityCheck(self, inputFile, newFile, statusBar):
        '''
        The "file" input values are presumed to be the values given by the
        user in the GUI.  They should be actual strings/booleans/whatever,
        not StrVars/BooleanVars/WhateverVars.
        
        statusBar is a part of the GUI that this will write text to.
        
        Makes sure all needed values have been entered and are not
        reused.
        
        Because file paths are chosen from a dialog, we don't do much
        to test their validity.
        
        Returns True if okay, False if not.
        '''
        allParams = [inputFile, newFile]
        
        # Make sure something was entered
        for item in allParams:
            strItem = str(item)
            if len(strItem) == 0:
                print("Missing value(s)!")
                statusBar.set("Missing value(s)!")
                return False
        
        # Make sure inputs are unique
        setParams = set(allParams)
        return len(setParams) == len(allParams)
    
    def checkAndFixFile(self, inputFile, newFile, statusBar):
        '''
        The "file" inputs should be the values added by the user in the GUI.
        The statusBar is a part of the GUI that this will write text to.
        
        Read the data in the input file, take out the parts that we
        care about, convert units as needed, and write it all into a
        new file at newFile.
        '''
        #Convert the StrVars to strings
        inFile = str(inputFile.get())
        outFile = str(newFile.get())
        
        if not self.integrityCheck(inFile, outFile, statusBar):
            print("Problem with data! No work done.")
        else:
            # This is where we start doing real work
            resultText = convertBaseCampFile(inFile, outFile)
            sourceFileName = path.basename(inFile)
            outFileName = path.basename(outFile)
            print("Finished reading", sourceFileName, "and writing to", outFileName)
            statusBar.set(resultText[:])
            
        # Now, clear out the file names from the GUI
        inputFile.set("")
        newFile.set("")
        

if __name__=='__main__':
    myRoot = Tk()
    GPS_File_Fixer(myRoot)
    myRoot.mainloop()
