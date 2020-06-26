from modules.db_redis import Rediser
import settings
import numpy as np
import time
from sklearn.neighbors import KDTree
from falconn import LSHIndex, get_default_parameters
class Measure():
    def __init__(self):
        db = Rediser(settings)
        self.embeds = db.get_embeds()
        self.labels = db.get_labels()

    @staticmethod
    def cal_dis(anchor, source):
        source_square = np.sum(np.square(source), axis=1, keepdims=True)
        anchor_square = np.sum(np.square(anchor), axis=1, keepdims=True)
        dis = anchor_square + source_square.T - 2*anchor@source.T
        return dis
        
    @staticmethod
    def get_closet(anchor, source, typ='matrix'):
        if typ == 'matrix':
            dis = Measure.cal_dis(anchor, source)
            dis += np.eye(dis.shape[0])*10
            closest_idx = np.argmin(dis, axis=1)
        elif typ == 'kdtree':
            tree = KDTree(source)
            res = tree.query(anchor, k=2, return_distance=False) #shape (anchor.shape[0],2)
            closest_idx = res[:,1]
        elif typ == 'lsh':
            params = get_default_parameters(source.shape[0], source.shape[1])
            lsh = LSHIndex(params)
            lsh.setup(source)
            query_obj = lsh.construct_query_object(num_probes=1000)
            closest_idx = [query_obj.find_k_nearest_neighbors(an, k=2)[1] for an in anchor]
        return closest_idx
    
    @staticmethod
    def get_accuracy(predict, truth):
        truth_count, total = 0,0
        for i in range(len(predict)):
            if predict[i] == truth[i]:
                truth_count+=1
            total +=1
        return truth_count, total, truth_count/total

    def eval(self, typ='matrix'):
        start = time.time()
        closest_idx = Measure.get_closet(self.embeds, self.embeds, typ=typ)
        print("{} query {} times from {} takes {}s".format(typ, self.embeds.shape[0], self.embeds.shape[0], time.time() - start))
        predict_labels = [self.labels[i] for i in closest_idx]
        print(Measure.get_accuracy(predict_labels, self.labels))
    
    def evaluate(self, typ='matrix'):
        if typ != 'all':
            self.eval(typ)
        else:
            for typ in ["matrix","kdtree","lsh"]:
                self.eval(typ)
Measure().evaluate(typ="all")
