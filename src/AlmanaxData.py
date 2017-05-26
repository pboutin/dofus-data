# coding=utf-8

from AbstractWebScraper import AbstractWebScraper

import re
from datetime import datetime

class AlmanaxData(AbstractWebScraper):
    outputFile = 'almanax-data'
    baseUrl = 'http://www.krosmoz.com/fr/almanax'


    def getItemUrls(self):
        months = [31,29,31,30,31,30,31,31,30,31,30,31]

        urls = []
        year = datetime.now().year
        for yearOffset in range(2):
            currentMonth = 1
            for daysCount in months:
                month = self.padTwoDigit(str(currentMonth))
                for day in range(daysCount):
                    day = self.padTwoDigit(str(day + 1))
                    urls.append("%s/%s-%s-%s" % (self.baseUrl, year, month, day))
                currentMonth = currentMonth + 1
            year = year + 1

        return urls


    def parsePage(self, itemPage, itemUrl):
        itemId = self.extractFrom(itemUrl, u'\d{4}-\d{2}-\d{2}$')

        rawBonus = itemPage('div.dofus div.more').text()

        rawQuest = itemPage('div.dofus div.more p.fleft').text()
        rawQuest = self.extractFrom(rawQuest, r'\d.+')

        rawItemId = itemPage('div.dofus div.more img').attr('src')
        rawItemId = self.extractFrom(rawItemId, r'\d+\..+\.png')

        item = {
            'bonus': self.extractFrom(rawBonus, r'.+?\.'),
            'quest': re.sub(r' et rapporter.*', '', rawQuest),
            'id': self.extractFrom(rawItemId, r'^\d+')
        }

        return (itemId, item)


    def padTwoDigit(self, input):
        return input if len(input) is 2 else '0' + input


AlmanaxData()
