import re
import json
import requests
import os
import os.path
import timeit
import datetime
import urllib
import sys
from pyquery import PyQuery as pq

class WebScraper:
    debug = False
    errors = []
    baseUrl = ''
    outputFile = 'default'

    isFailing = False

    def __init__(self):
        startTime = timeit.default_timer()
        errorFilePath = "../%s.errors%s" % (self.outputFile, '.debug.json' if self.debug else '.json')
        outputFilePath = "../%s%s" % (self.outputFile, '.debug.json' if self.debug else '.json')

        if os.path.isfile(outputFilePath):
            with open(outputFilePath) as dataFile:
                self.printSuccess("Updating the current '%s.json'" % self.outputFile)
                processedData = json.load(dataFile)
        else:
            self.printSuccess('Processing from scratch')
            processedData = {}

        urls = []

        for arg in sys.argv:
            if not re.match(r'.+\.py', arg):
                urls.append(arg)

        if not len(urls):
            if os.path.isfile(errorFilePath):
                self.printSuccess('Recovering from pending errors')
                with open(errorFilePath) as errorFile:
                    pastErrors = json.load(errorFile)
                    urls = [pastError['url'] for pastError in pastErrors]
            else:
                self.printSuccess('Loading URLs...')
                urls = self.getItemUrls()

        self.printSuccess('Initialization : done')

        for url in urls:
            self.printInfo("Loading : %s" % url)
            page = self.loadPageFrom(url)
            if page is not None:
                keyValue = self._parsePage(page, url)
                if keyValue is not None:
                    processedData[keyValue[0]] = keyValue[1]

        self.printSuccess('Items processing : done')

        self.printSuccess('Urls: %s' % str(len(urls)))
        self.printSuccess('Keys: %s' % str(len(processedData.keys())))

        with open(outputFilePath, 'w') as dataOutput:
            json.dump(processedData, dataOutput)
            self.printSuccess('Data writing : done')

        errorCount = len(self.errors)
        if errorCount:
            self.printError("%s errors reported, writing the details..." % errorCount)
            with open(errorFilePath, 'w') as errorOutput:
                json.dump(self.errors, errorOutput)
                self.printSuccess('Error logs writing : done')
        else:
            self.printSuccess('Full success, cleaning error logs...')
            if os.path.isfile(errorFilePath):
                os.remove(errorFilePath)

        endTime = timeit.default_timer()
        runtime = (endTime - startTime) / 60
        self.printSuccess('Finish (' + str(runtime) + ' minutes)')


    def getItemEndpoints(self):
        raise Exception('You must implement "getItemEndpoints()" and return and array of URLs.')


    def _parsePage(self, page, url, attempt=0):
        self.isFailing = False

        if attempt > 0:
            self.printWarning('Parsing attempt - ' + str(attempt) + ' - ' + url)

        keyValue = self.parsePage(page, url)

        if self.isFailing:
            if attempt < 5:
                return self._parsePage(page, url, attempt + 1)
            self.printAndLogError('Failed to parse', url)
            return None

        return keyValue


    def parsePage(self, page, url):
        raise Exception('You must implement "parsePage(page, url)" and return a tuple as (key, value).')


    def extractFrom(self, string, pattern=None):
        if not self.isString(string):
            self.isFailing = True
            return ''

        if pattern is None:
            return string

        matches = re.findall(pattern, string)
        return matches[0] if len(matches) else ''


    def loadPageFrom(self, url, attempt=0):
        if attempt > 0:
            self.printWarning('Loading attempt - ' + str(attempt) + ' - ' + url)

        try:
            response = requests.get(url, verify=True, timeout=5)

            if response.status_code == 404:
                self.printAndLogError('Broken link (404)', url)
                return None

            return pq(response.text)
        except:
            if attempt < 5:
                return self.loadPageFrom(url, attempt + 1)
            self.printAndLogError('Failed to load', url)
            return None


    def isString(self, variable):
        return isinstance(variable, basestring)


    def printSuccess(self, message):
        print '\033[92m' + message + '\033[0m'


    def printWarning(self, message):
        print '\033[93m' + message + '\033[0m'


    def printAndLogError(self, message, url):
        self.errors.append({
            'message': message,
            'url': url
        })
        self.printError(message)


    def printError(self, message):
        print '\033[91m' + message + '\033[0m'


    def printInfo(self, message):
        print message
