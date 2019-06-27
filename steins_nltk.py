#!/usr/bin/env python3

from nltk.stem.snowball import SnowballStemmer
#from scipy.sparse import csr_matrix, lil_matrix
from sklearn.feature_extraction.text import CountVectorizer

#class NLTK_CountVectorizer(CountVectorizer):
#    def __init__(self, lang):
#        CountVectorizer.__init__(self)
#        try:
#            self.stemmer = SnowballStemmer(lang.lower())
#        except ValueError:
#            self.stemmer = lambda x: x
#
#    def nltk_transform(self, X):
#        vocabs = set(range(len(self.vocabulary_)))
#        for v_it in self.vocabulary_.items():
#            if not v_it[1] in vocabs:
#                continue
#
#            words = [w_it for w_it in self.vocabulary_.items() if self.stemmer.stem(w_it[0]) == self.stemmer.stem(v_it[0])]
#            words.sort(key=lambda x: x[1])
#            vocabs.remove(words[0][1])
#            for w_it in words[1:]:
#                X[:, words[0][1]] += X[:, w_it[1]]
#                X[:, w_it[1]] = 0.
#                vocabs.remove(w_it[1])
#
#        return X
#
#    def fit_transform(self, X, Y=None):
#        return self.nltk_transform(super().fit_transform(X, Y))
#
#    def transform(self, X):
#        return self.nltk_transform(super().transform(X))

class NLTK_CountVectorizer(CountVectorizer):
    def __init__(self, lang):
        CountVectorizer.__init__(self)

        try:
            self.stemmer = SnowballStemmer(lang.lower()).stem
            self.vect = CountVectorizer()
            self.analyzer = self.analyzer_nltk
        except ValueError:
            pass

    def analyzer_nltk(self, x):
        return [self.stemmer(e) for e in self.vect.build_analyzer()(x)]

    def fit_transform(self, x, y):
        try:
            self.vect.fit(x, y)
            res = super().fit_transform(x, y)

            vocabs = dict()
            for v_it in self.vect.vocabulary_:
                expr = self.stemmer(v_it)
                if expr in vocabs:
                    vocabs[expr].append(v_it)
                else:
                    vocabs[expr] = [v_it]

            self.vocabulary_nltk = [min(words) for words in vocabs.values()]
        except AttributeError:
            res = super().fit_transform(x, y)
            self.vocabulary_nltk = self.vocabulary_.copy()

        return res
