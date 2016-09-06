# coding=utf-8

import re
import json
import requests
import os.path
import timeit
import datetime
import urllib
from pyquery import PyQuery as pq

errors = []

baseUrl = 'http://www.dofus.com'
imageBaseUrl = 'http://staticns.ankama.com/dofus/www/game/items/200'

webRessources = {
    '/fr/mmorpg/encyclopedie/armes?size=150': 6,
    '/fr/mmorpg/encyclopedie/equipements?size=150': 17,
    '/fr/mmorpg/encyclopedie/consommables?size=150': 8,
    '/fr/mmorpg/encyclopedie/ressources?size=150': 18
}

result = {}

def main():
    startTime = timeit.default_timer()

    for ressourcesEndpoint, pagesCount in webRessources.items():
        for currentPage in range(1, pagesCount + 1):
            printSuccess('Fetching ' + ressourcesEndpoint + ' page ' + str(currentPage))
            listPage = loadPageFrom(ressourcesEndpoint + '&page=' + str(currentPage))

            itemRows = listPage('table.ak-table tbody tr')

            for itemRow in itemRows:
                itemEndpoint = pq(itemRow).find('td').eq(1).find('a').attr('href')
                process(itemEndpoint)

    printSuccess('Download done')

    if os.path.exists('dofus-data.json'):
        with open('dofus-data.json') as dataInput:
            printInfo('Updating the existing "dofus-data.json"')
            existingData = json.load(dataInput)
            newData = existingData['data']

            for key, value in result.iteritems():
                if (not key in newData) or (not value is None):
                    newData[key] = value
    else:
        newData = result

    with open('dofus-data.json', 'w') as output:
        printInfo('Writing the new "dofus-data.json"')
        json.dump({
            'metadata': {
                'baseUrl': baseUrl
            },
            'data': newData
        }, output)

    with open('errors.log', 'a') as errorOutput:
        printInfo('Writing errors log')
        errorOutput.write('LOGS FOR ' + str(datetime.datetime.now()))
        for error in errors:
            errorOutput.write("%s\n" % error)
            printError(error)

    endTime = timeit.default_timer()
    runtime = (endTime - startTime) / 60
    printSuccess('Done (' + str(runtime) + ' minutes)')


def loadPageFrom(endpoint, attempt=0):
    try:
        completeUrl = baseUrl + endpoint

        if attempt > 0:
            printWarning('Loading attempt - ' + str(attempt) + ' - ' + completeUrl)

        response = requests.get(completeUrl, verify=True, timeout=5)

        if response.status_code == 404:
            errors.append('broken link : ' + completeUrl)
            return None

        return pq(response.text)
    except:
        if attempt < 5:
            return loadPageFrom(endpoint, attempt + 1)
        raise Exception('Too many timeouts')


def extractInfo(type, string, itemEndpoint):
    patterns = {
        'id': u'\/([\w\-ō]+)$',
        'name': None,
        'level': u'\d+',
        'image': u'\/\d+.png$',
        'type': None,
        'quantity': r'\d+'
    }

    correspondingPattern = patterns[type]

    if correspondingPattern is None:
        if string == '':
            return None
        return string

    matches = re.findall(correspondingPattern, string)
    if len(matches) == 1:
        return matches[0]

    return None


def process(itemEndpoint, attempt=0):
    if attempt == 0:
        printInfo(itemEndpoint)
    elif attempt == 5:
        printError('failed to parse - ' + itemEndpoint)
    else:
        printWarning('Processing attempt - ' + str(attempt) + ' - ' + itemEndpoint)

    itemPage = loadPageFrom(itemEndpoint)

    itemId = extractInfo('id', itemEndpoint, itemEndpoint)

    if itemId is None:
        return process(itemEndpoint, attempt + 1)

    # 404 handling
    if itemPage is None:
        result[itemId] = None
        return

    recipeItems = itemPage('div.ak-crafts div.ak-list-element')

    recipe = None
    if recipeItems:
        recipe = {}
        for recipeItem in recipeItems:
            rawRecItemId = pq(recipeItem).find('div.ak-content a').attr('href')
            rawRecItemQuantity = pq(recipeItem).find('div.ak-front').text()

            if not (isString(rawRecItemId) and isString(rawRecItemQuantity)):
                return process(itemEndpoint, attempt + 1)

            recItemId = extractInfo('id', rawRecItemId, itemEndpoint)
            recItemQuantity = extractInfo('quantity', rawRecItemQuantity, itemEndpoint)
            recipe[recItemId] = recItemQuantity

    rawName = itemPage('div.ak-title-container h1').text()
    rawLevel = itemPage('div.ak-encyclo-detail-level').text()
    rawType = itemPage('div.ak-encyclo-detail-type span').text()

    rawImage = itemPage('div.ak-encyclo-detail-illu img').attr('src')
    imageFullUrl = imageBaseUrl + extractInfo('image', rawImage, itemEndpoint)
    urllib.urlretrieve(imageFullUrl, 'images/' + itemId + '.png')

    if not (isString(rawName) and isString(rawLevel) and isString(rawImage) and isString(rawType)):
        return process(itemEndpoint, attempt + 1)

    result[itemId] = {
        'name': extractInfo('name', rawName, itemEndpoint),
        'level': extractInfo('level', rawLevel, itemEndpoint),
        'type': extractInfo('type', rawType, itemEndpoint),
        'link': itemEndpoint,
        'recipe': recipe
    }

def isString(variable):
    return isinstance(variable, basestring)

def printSuccess(message):
    print '\033[92m' + message + '\033[0m'

def printWarning(message):
    print '\033[93m' + message + '\033[0m'

def printError(message):
    print '\033[91m' + message + '\033[0m'

def printInfo(message):
    print message

main()
