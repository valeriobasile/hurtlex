from corpy.udpipe import Model
import os
from models import udpipe_models, UD_VERSION
import sys
import wget
import csv

HL_VERSION = "1.2"

class HurtLexFeaturizer:
    def __init__(self, language, level="conservative"):
        self.language = language
        self.model = self.load_model()
        self.lexicon = self.read_lexicon(level)

    def load_model(self):
        extension = "-ud-{0}.udpipe".format(UD_VERSION)
        udpipe_model = udpipe_models[self.language]+extension
        model_file = os.path.join("models", udpipe_model)
        if not os.path.exists(model_file):
            url = "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3131/{0}".format(udpipe_model)
            print (url)
            wget.download(url, out="models")
        return Model(model_file)

    def lemmatize(self, text):
        sentences = list(self.model.process(text))
        lemmas = [t.lemma for t in sentences[0].words[1:]]
        return lemmas

    def pos(self, text):
        sentences = list(self.model.process(text))
        pos = [t.upostag for t in sentences[0].words[1:]]
        return pos

    def read_lexicon(self, level):
        lexicon = dict()
        lexicon_filename = "hurtlex_{0}.tsv".format(self.language)
        lexicon_path = os.path.join("../lexica", language, HL_VERSION, lexicon_filename)
        with open(lexicon_path) as f:
            # read categories
            reader = csv.DictReader(f, delimiter="\t")
            self.categories = []
            for row in reader:
                self.categories.append(row["category"])
            self.categories = sorted(list(set(self.categories)))

            f.seek(0)
            reader = csv.DictReader(f, delimiter="\t")
            for row in reader:
                if row["level"]!="conservative" and row["level"]!=level:
                    continue
                if not row["lemma"] in lexicon:
                    lexicon[row["lemma"]] = [0 for category in self.categories]
                lexicon[row["lemma"]][self.categories.index(row["category"])] += 1

        return lexicon

    def process(self, text):
        feature_vector = [0 for category in self.categories]
        for lemma in self.lemmatize(text):
            lemma_vector = self.lexicon.get(lemma, [0 for category in self.categories])
            feature_vector = [i+j for i, j in zip(lemma_vector, feature_vector)]
        return feature_vector
