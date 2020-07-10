import pickle
from sklearn.linear_model import LogisticRegression
from gensim.utils import simple_preprocess 
from gensim.models.doc2vec import Doc2Vec, TaggedDocument


_fp1 = open("leader_model.pkl", "rb")
logreg_model = pickle.load(_fp1)
_fp1.close()

_fp2 = open("doc2vec_model.pkl", "rb")
doc2vec_model = pickle.load(_fp2)
_fp2.close()

def vec_for_predicting(doc2vec_model, sents):
    tagged_sents = [TaggedDocument(simple_preprocess(sent), tags = 'unknown') for sent in sents]
    return tagged_sents

def classify_leader(sents):
	X = vec_for_predicting(doc2vec_model, sents)
	y_pred = logreg_model.predict(X)
	return y_pred

	