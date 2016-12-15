# coding=utf-8

from WebScraper import WebScraper

import re
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

                    if self.debug and len(urls) == 10:
                        self.printSuccess("Url processing for '%s' : done, Urls count : %s (debug mode)" % (ressourcesEndpoint, str(len(urls))))
                        return urls

                currentPage = currentPage + 1
        self.printSuccess("Url processing for '%s' : done, Urls count : %s" % (ressourcesEndpoint, str(len(urls))))
        return urls


    def parsePage(self, itemPage, itemUrl):
        itemId = self.extractFrom(itemUrl, u'\/([\w\-ō]+)$')

        rawImageSrc = itemPage('div.ak-encyclo-detail-illu img').attr('src')
        imageUrl = self.imageBaseUrl + self.extractFrom(rawImageSrc, u'\/\d+.png$')

        try:
            itemIdDigits = self.extractFrom(itemId, u'^\d+')
            urllib.urlretrieve(imageUrl, '../images/' + itemIdDigits + '.png')
        except:
            self.isFailing = True
            self.printWarning("Failed to download image : %s" % imageUrl)

        item = {
            'name': self.extractFrom(itemPage('div.ak-title-container h1').text()),
            'level': self.extractFrom(itemPage('div.ak-encyclo-detail-level').text(), u'\d+'),
            'type': self.extractFrom(itemPage('div.ak-encyclo-detail-type span').text()),
            'link': itemUrl,
            'recipe': self._parseRecipe(itemPage('div.ak-crafts div.ak-list-element')),
            'effects': self._parseEffects(itemPage('div.ak-encyclo-detail-right div:last-child div.col-sm-6:first-child div.ak-list-element'))
        }
        return (itemId, item)

    def _parseRecipe(self, recipeElements):
        if recipeElements:
            recipe = {}
            for recipeElement in recipeElements:
                rawRecItemId = pq(recipeElement).find('div.ak-content a').attr('href')
                rawRecItemQuantity = pq(recipeElement).find('div.ak-front').text()

                recItemId = self.extractFrom(rawRecItemId, u'\/([\w\-ō]+)$')
                recItemQuantity = self.extractFrom(rawRecItemQuantity, u'\d+')
                recipe[recItemId] = recItemQuantity
            return recipe
        return None

    def _parseEffects(self, effectElements):
        def _getEffectFor(effectLine):
            matcher = {
                'fo': u'\d Force',                              'ine': u'\d Intelligence',
                'agi': u'\d Agilité',                           'cha': u'\d Chance',
                'sa': u'\d Sagesse',                            'vi': u'\d Vitalité',
                'ini': u'\d Initiative',                        'pod': u'\d Pods',
                'pi_per': u'\d Puissance \(pièges\)',           'prospe': u'\d Prospection',
                'pui': u'\d Puissance',                         're_cri': u'\d Résistance Critiques',
                're_eau': u'\d Résistance Eau',                 're_feu': u'\d Résistance Feu',
                're_neutre': u'\d Résistance Neutre',           're_air': u'\d Résistance Air',
                're_terre': u'\d Résistance Terre',             're_pou': u'\d Résistance Poussée',
                'do_air': u'\d Dommages Air',                   'do_cri': u'\d Dommages Critiques',
                'do_eau': u'\d Dommages Eau',                   'do_feu': u'\d Dommages Feu',
                'do_terre': u'\d Dommages Terre',               'do_neutre': u'\d Dommages Neutre',
                'pi': u'\d Dommages Pièges',                    'do_pou': u'\d Dommages Poussée',
                'do_ren': u'Renvoie \d+ dommages',              'do': u'\d Dommages$',
                'fui': u'\d Fuite',                             'tac': u'\d Tacle',
                'ret_pa': u'\d Retrait PA',                     'ret_pme': u'\d Retrait PM',
                're_pa': u'\d Esquive PA',                      're_pme': u'\d Esquive PM',
                're_per_air': u'\d\% Résistance Air',           're_per_eau': u'\d\% Résistance Eau',
                're_per_feu': u'\d\% Résistance Feu',           're_per_neutre': u'\d\% Résistance Neutre',
                're_per_terre': u'\d\% Résistance Terre',       'cri': u'\d\% Critique',
                'so': u'\d Soins',                              'invo': u'\d Invocations',
                'po': u'\d Portée',                             'ga_pa': u'\d PA',
                'ga_pme': u'\d PM'
            }
            for effect in matcher:
                if re.findall(matcher[effect], effectLine):
                    bonus = max([int(rawBonus) for rawBonus in re.findall(r'-?\d+', effectLine)])
                    return (effect, bonus)
            return (effectLine, None)

        isWeapon = False
        if effectElements:
            effects = []
            for effectElement in effectElements:
                effectText = pq(effectElement).find('div.ak-title').text()
                if not re.findall(r'(\((dommages|vol|PV))', effectText):
                    effect, bonus = _getEffectFor(effectText)
                    # Weapons that removes PA to target
                    if not (effect == 'ga_pa' and bonus == -1 and isWeapon):
                        effects.append(effect)
                        if bonus:
                            effects.append(bonus)
                else:
                    isWeapon = True
            return effects
        return None


DofusData()
