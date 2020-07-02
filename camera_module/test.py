from modules.db_redis import Rediser
import settings
import numpy as np
import time
from sklearn.neighbors import KDTree, NearestNeighbors
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
    def get_matrix_closet_idx(anchor, source):
        dis_ = np.sqrt(np.sum(np.square(source - anchor),axis=1))
        min_dis_idx = np.argmin(dis_ + np.eye(1,dis_.shape[0])*10)
        return min_dis_idx

    @staticmethod
    def get_closet(anchor, source, typ='matrix'):
        if typ == 'matrix':
            closest_idx = [Measure.get_matrix_closet_idx(a, source) for a in anchor]
        elif typ == 'kdtree':
            tree = KDTree(source)
            closest_idx = [tree.query(a[np.newaxis,...], k=2, return_distance=False)[:,1] for a in anchor] #shape (anchor.shape[0],2)
            # closest_idx = res[:,1]
        elif typ == 'nn':
            neigh = NearestNeighbors(n_neighbors=2, radius=0.4, algorithm='ball_tree')
            neigh.fit(source)
            closest_idx = [neigh.kneighbors(a[np.newaxis,...],n_neighbors=2, return_distance=False)[:,1] for a in anchor]
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
        end = time.time() - start
        print("{} query {} times from {} takes {}s - {}s in average".format(typ, self.embeds.shape[0], self.embeds.shape[0], end, end/self.embeds.shape[0]))
        predict_labels = [self.labels[i] for i in closest_idx]
        print(Measure.get_accuracy(predict_labels, self.labels))
    
    def evaluate(self, typ='matrix'):
        if typ != 'all':
            self.eval(typ)
        else:
            for typ in ["matrix","kdtree","lsh","nn"]:
                self.eval(typ)
Measure().evaluate(typ="all")
