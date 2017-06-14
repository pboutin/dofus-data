#!/usr/bin/env python2
# coding=utf-8

from AbstractWebScraper import AbstractWebScraper

import re
from datetime import datetime

LANGS = {'en', 'fr'}
ET_RAPPORTER = {
    'fr': r' et rapporter l\'offrande.*',
    'en': r' and take the offering.*',
}

class AlmanaxData(AbstractWebScraper):
    def __init__(self, lang):
        if lang not in LANGS:
            raise KeyError('invalid language: ' + lang)
        self.outputFile = 'almanax-data-%s' % (lang,)
        self.baseUrl = 'http://www.krosmoz.com/%s/almanax' % (lang,)
        self.lang = lang
        super(AlmanaxData, self).__init__()

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
            'quest': re.sub(ET_RAPPORTER[self.lang], '', rawQuest),
            'id': self.extractFrom(rawItemId, r'^\d+')
        }

        return (itemId, item)


    def padTwoDigit(self, input):
        return input if len(input) is 2 else '0' + input


for lang in LANGS:
    AlmanaxData(lang)
