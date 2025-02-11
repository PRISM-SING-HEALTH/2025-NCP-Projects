from index.HPOLabelCollector import HPOLabelCollector
from index.LabelProcessor import LabelProcessor
from util import ContentUtil, ConfigConstants
from util.CRConstants import VB_BLACKLIST, POS_LIST
from util.OntoReader import OntoReader


class PreprocessHPOTerms:
    processedTerms = {}
    terms = {}
    catDictionary = {}

    def __init__(self, ontologyFile, externalSynonyms={}, indexConfig={}):
        ontoReader = OntoReader(ontologyFile)
        self.processedTerms = {}

        labelProcessor = LabelProcessor(HPOLabelCollector(ontoReader,
                                                          externalSynonyms=externalSynonyms,
                                                          indexConfig=indexConfig).getTerms(),
                                        indexConfig=indexConfig)
        self.terms = labelProcessor.getProcessedTerms()

        self.filterTerms()
        self.buildCategoriesDictionary(indexConfig, ontoReader)

    def filterTerms(self):
        for uri in self.terms:
            label = self.terms[uri]['label']
            syns = self.terms[uri]['syns']
            categories = []
            if 'categories' in self.terms[uri]:
                categories = self.terms[uri]['categories']

            termLst = []

            tokenSet = self.processTerm(self.processLabel(label))
            filteredTokenSet = self.filter(tokenSet)
            termLst.append({
                'originalLabel': label,
                'preferredLabel': True,
                'tokens': filteredTokenSet
            })

            for syn in syns:
                tokenSet = self.processTerm(self.processLabel(syn))
                filteredTokenSet = self.filter(tokenSet)
                termLst.append({
                    'originalLabel': syn,
                    'preferredLabel': False,
                    'tokens': filteredTokenSet
                })
            entry = {
                'terms': termLst
            }
            if categories:
                entry['categories'] = categories
            self.processedTerms[uri] = entry

    def processLabel(self, label) -> str:
        label = label.lower()
        label = ContentUtil.spaceReplace(label)
        label = ContentUtil.cleanToken(label)
        label = label.replace('  ', ' ')
        return label.strip()

    def processTerm(self, label):
        segments = label.split(' ')
        result = []
        for segment in segments:
            result.append({
                'token': segment
            })
        return result

    def filter(self, tokenSet):
        result = []
        for token in tokenSet:
            if token['token'] in VB_BLACKLIST or token['token'] in POS_LIST:
                continue
            result.append(token)
        return result

    def buildCategoriesDictionary(self, indexConfig, ontoReader):
        if not indexConfig:
            return

        if ConfigConstants.VAR_INCLUDE_CATEGORY in indexConfig:
            if indexConfig[ConfigConstants.VAR_INCLUDE_CATEGORY]:
                for uri in ontoReader.abn_classes:
                    self.catDictionary[uri] = ontoReader.terms[uri]

    def getProcessedTerms(self):
        return self.processedTerms

    def getCategoriesDictionary(self):
        return self.catDictionary
