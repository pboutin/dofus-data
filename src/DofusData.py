# coding=utf-8

from WebScraper import WebScraper

import re
import json
import requests
import os
import os.path
import timeit
import datetime
import urllib
from pyquery import PyQuery as pq

class DofusData(WebScraper):
    outputFile = 'dofus-data'
    baseUrl = 'http://www.dofus.com'
    imageBaseUrl = 'http://staticns.ankama.com/dofus/www/game/items/200'


    def getItemUrls(self):
        ressourcesIndexes = [
            '/fr/mmorpg/encyclopedie/armes',
            '/fr/mmorpg/encyclopedie/equipements',
            '/fr/mmorpg/encyclopedie/consommables',
            '/fr/mmorpg/encyclopedie/ressources'
        ]

        urls = []

        for ressourcesEndpoint in ressourcesIndexes:
            currentPage = 1

            while True:
                indexUrl = "%s%s?page=%s"  % (self.baseUrl, ressourcesEndpoint, str(currentPage))
                self.printInfo("Fetching : %s" % indexUrl)
                listPage = self.loadPageFrom(indexUrl)

                itemRows = listPage('table.ak-table tbody tr')

                if not itemRows:
                    break

                for itemRow in itemRows:
                    endpoint = pq(itemRow).find('td').eq(1).find('a').attr('href')
                    urls.append(self.baseUrl + endpoint)

                currentPage = currentPage + 1

            self.printSuccess("Url processing for '%s' : done, Urls count : %s" % (ressourcesEndpoint, str(len(urls))))
        return urls


    def parsePage(self, itemPage, itemUrl):
        itemId = self.extractFrom(itemUrl, u'\/([\w\-ō]+)$')

        recipe = self._parseRecipe(itemPage('div.ak-crafts div.ak-list-element'))

        rawImageSrc = itemPage('div.ak-encyclo-detail-illu img').attr('src')
        imageUrl = self.imageBaseUrl + self.extractFrom(rawImageSrc, u'\/\d+.png$')

        try:
            itemIdDigits = self.extractFrom(itemId, r'^\d+')
            urllib.urlretrieve(imageUrl, '../images/' + itemIdDigits + '.png')
        except:
            self.isFailing = True
            self.printWarning("Failed to download image : %s" % imageUrl)

        item = {
            'name': self.extractFrom(itemPage('div.ak-title-container h1').text()),
            'level': self.extractFrom(itemPage('div.ak-encyclo-detail-level').text(), u'\d+'),
            'type': self.extractFrom(itemPage('div.ak-encyclo-detail-type span').text()),
            'link': itemUrl,
            'recipe': recipe
        }

        return (itemId, item)


    def _parseRecipe(self, rawRecipeElements):
        recipe = None
        if rawRecipeElements:
            recipe = {}
            for recipeElement in rawRecipeElements:
                rawRecItemId = pq(recipeElement).find('div.ak-content a').attr('href')
                rawRecItemQuantity = pq(recipeElement).find('div.ak-front').text()

                recItemId = self.extractFrom(rawRecItemId, u'\/([\w\-ō]+)$')
                recItemQuantity = self.extractFrom(rawRecItemQuantity, r'\d+')
                recipe[recItemId] = recItemQuantity

        return recipe

DofusData()
