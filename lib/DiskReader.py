"""
#############################################################################################
# Name: DiskReader.py
#
# Author: Daniel Lemay
#
# Date: 2004-02-01
#
# Description:
#
#############################################################################################

"""
import os, os.path, re, commands
from MultiKeysStringSorter import MultiKeysStringSorter
import fet

class _DirIterator(object):
    """ Author: Sebastien Keim

        Used to obtain a list of all entries (filename + directories) contained in a
        root directory
    """
    def __init__(self, path, deep=False):
        self._root = path
        self._files = None
        self.deep = deep

    def __iter__(self):
        return self

    def next(self):
        join = os.path.join
        if self._files:
            d = self._files.pop()
            r = join(self._root, d)
            if self.deep and os.path.isdir(r):
                self._files += [join(d,n) for n in os.listdir(r)]
        elif self._files is None:
            self._files = [join(self._root,n) for n in os.listdir(self._root)]
        if self._files:
            return self._files[-1]
        else:
            raise StopIteration

class DiskReader:

    def __init__(self, path, batch=20000, validation=False, logger=None, sorterClass=None):
        """
        Set the root path and the sorter class used for sorting

        The regex will serve (if we use validation) to validate that the filename has the following form:
        SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339"

        FIXME: The regex should be passed otherwise!  config file?

        """
        self.regex = re.compile(r'^.*?:.*?:.*?:.*?:(\d).*?:.*?:(\d{14})$')  # Regex used to validate filenames
        self.path = path                          # Path from where we ingest filenames
        self.clientName = os.path.basename(path)  # Last part of the path correspond to client name 
        self.validation = validation              # Name Validation active (True or False)
        self.logger = logger                      # Use to log information
        self.batch = batch                        # Maximum number of files that we are interested to sort
        self.files = self._getFilesList()         # List of filenames under the path
        self.sortedFiles = []                     # Sorted filenames
        self.data = []                            # Content of x filenames (x is set in getFilesContent())
        self.sorterClass = sorterClass            # Sorting algorithm that will be used by sort()

    def _validateName(self, filename):
        """
        Validate that the filename has the following form:
        "SACN43_CWAO_012000_CYOJ_41613:ncp1:CWAO:SA:3.A.I.E::20050201200339"
        """
        basename = os.path.basename(filename)
        match = self.regex.search(basename)
        if match:
            #print match.group(2), match.group(1)
            return True
        else:
            #print "Don't match: " + basename
            return False

    def _matchPattern(self, filename):
        pattern = fet.clientMatch(self.client, filename)
        if pattern != None:
           return True
        else:
           return False

    def _getFilesList(self):

        priorities = ['1', '2', '3', '4', '5']
        files = []
        start = 0

        for priority in priorities:
            start = len(files)
            if start < self.batch:
               path = self.path + '/' + priority
               if os.path.exists(path):
                  files += self._getFilesListForOneBranch(path, self.batch - start)
        return files

    def _getFilesListForOneBranch(self, path, batch):
        """
        Set and return a list of all the filenames (not directories) contained in root directory (path) and
        all the subdirectories under it. A validation is done (if self.validation is True) on the names.
        If a filename is not valid, the file is unlinked and a log entry is added to the log. Batch is the
        maximum number of files that can be returned.

        FIXME: Add try/except for unlink
        """
        dirIterator = _DirIterator(path, True)
        files = []
        for file in dirIterator:
            if not os.path.isdir(file):
                basename = os.path.basename(file)
                # Files we don't want to touch
                if basename[0] == '.' or basename[-4:] == ".tmp" or not os.access(file, os.R_OK):
                    continue
                # If we use name validation 
                if self.validation:
                    if not self._validateName(file):
                        os.unlink(file)
                        if self.logger is not None:
                            self.logger.writeLog(self.logger.INFO, "Filename incorrect: " + file + " has been unlinked!")
                        continue
                # Does the filename match a pattern
                if not self._matchPattern(file):
                    os.unlink(file)
                    if self.logger is not None:
                        self.logger.writeLog(self.logger.INFO, "No pattern matching: " + file + " has been unlinked!")
                    continue
                # We don't want to 
                if len(files) >= batch:
                        break
                # All "tests" have been passed
                files.append(file)

        return files
    
    def getFilesContent(self, number=1000000):
        """
        Set and return a list having the content (data) of corresponding filenames in the
        SORTED list (imply sort() must be called before this function). The number of elements is
        determined by "number"
        """
        self.data = []
        shortList = self.sortedFiles[0:number]
        for file in shortList:
            try:
                fileDesc = open(file, 'r')
                self.data.append(fileDesc.read())
            except:
                self.logger.writeLog(self.logger.ERROR,"senderWmo.read(..): Erreur lecture:" + file)
                raise
        return self.data

    def sort(self):
        """
        Set and return a sorted list of the files
        """
        if self.sorterClass is not None:
            sorter = self.sorterClass(self.files)
            self.sortedFiles = sorter.sort()
        else:
            self.sortedFiles = self.files

        return self.sortedFiles

if __name__ == "__main__":

    """
    (status, output) = commands.getstatusoutput("date")
    print output
    #reader = DiskReader("/home/ib/dads/dan/progProj/pds-nccs/bulletins", validation=True, sorterClass=MultiKeysStringSorter)
    reader = DiskReader("/apps/px/bulletins", 41, validation=True, sorterClass=MultiKeysStringSorter)
    (status, output) = commands.getstatusoutput("date")
    print output
    for file in  reader.files:
       print file
    reader.sort()
    print "************************************ Sorted files *******************************************"
    for file in  reader.sortedFiles:
       print file

    (status, output) = commands.getstatusoutput("date")
    print output
    """
    iterator = _DirIterator('/apps/px/toto' , True)
    for file in iterator:
       print file
