#!/usr/bin/env python3

from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer

class NLTK_CountVectorizer(CountVectorizer):
    def __init__(self, lang, **kwargs):
        CountVectorizer.__init__(self, kwargs)

        try:
            self.stemmer = SnowballStemmer(lang.lower()).stem
            self.vect = CountVectorizer()
            self.analyzer = self.analyzer_nltk
        except ValueError:
            pass

    def analyzer_nltk(self, x):
        return [self.stemmer(e) for e in self.vect.build_analyzer()(x)]

    def fit_transform(self, x, y):
        res = super().fit_transform(x, y)

        try:
            self.vect.fit(x, y)

            vocabs = dict()
            for v_it in self.vect.vocabulary_:
                expr = self.stemmer(v_it)
                if expr in vocabs:
                    vocabs[expr].append(v_it)
                else:
                    vocabs[expr] = [v_it]

            self.vocabulary_nltk = [min(words) for words in vocabs.values()]
        except AttributeError:
            self.vocabulary_nltk = self.vocabulary_.copy()

        return res

class LDA_CountVectorizer(NLTK_CountVectorizer):
    def __init__(self, lang, vocabs, **kwargs):
        NLTK_CountVectorizer.__init__(self, lang, **kwargs)

        try:
            self.vocabulary_lda = [self.stemmer(e) for e in vocabs]
        except AttributeError:
            self.vocabulary_lda = vocabs
        self.analyzer = self.analyzer_lda

    def analyzer_lda(self, x):
        return [e for e in self.analyzer_nltk(x) if e in self.vocabulary_lda]
