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
    def get_matrix_closet_idx(anchor, source, voter=10):
        dis_ = np.sqrt(np.sum(np.square(source - anchor),axis=1))
        min_dis_idx = dis_.argsort()[:voter] #np.argmin(dis_ + np.eye(1,dis_.shape[0])*10)
        return min_dis_idx

    @staticmethod
    def get_closet(anchor, source, typ='matrix', voter=10):
        if typ == 'matrix':
            closest_idx = [Measure.get_matrix_closet_idx(a, source, voter) for a in anchor]
        elif typ == 'kdtree':
            tree = KDTree(source)
            closest_idx = [tree.query(a[np.newaxis,...], k=voter, return_distance=False)[0] for a in anchor] #shape (anchor.shape[0],2)
        elif typ == 'nn':
            neigh = NearestNeighbors(n_neighbors=voter, radius=0.4, algorithm='ball_tree')
            neigh.fit(source)
            closest_idx = [neigh.kneighbors(a[np.newaxis,...],n_neighbors=voter, return_distance=False)[0] for a in anchor]
        elif typ == 'lsh':
            params = get_default_parameters(source.shape[0], source.shape[1])
            lsh = LSHIndex(params)
            lsh.setup(source)
            query_obj = lsh.construct_query_object(num_probes=1000)
            closest_idx = [query_obj.find_k_nearest_neighbors(an, k=voter) for an in anchor]
        return closest_idx
    
    @staticmethod
    def get_accuracy(predict, truth):
        truth_count, total = 0,0
        for i in range(len(predict)):
            if predict[i] == truth[i]:
                truth_count+=1
            total +=1
        return truth_count, total, truth_count/total

    def get_label(self, votes):
        labels = [self.labels[i] for i in votes]
        # import pdb; pdb.set_trace()
        return max(set(labels), key = labels.count) 

    def eval(self, typ='matrix', voter=10):
        anchor = self.embeds
        anchor_label = self.labels
        start = time.time()
        closest_idx = Measure.get_closet(anchor, self.embeds, typ=typ, voter=voter)
        end = time.time() - start
        print("{} query {} times from {} takes {}s - {}s in average".format(typ, anchor.shape[0], self.embeds.shape[0], end, end/self.embeds.shape[0]))
        predict_labels = [self.get_label(idxes) for idxes in closest_idx]
        print(Measure.get_accuracy(predict_labels, anchor_label))
    
    def evaluate(self, typ='matrix', voter=10):
        if typ != 'all':
            self.eval(typ, voter=voter)
        else:
            for typ in ["matrix","kdtree","lsh","nn"]:
                self.eval(typ, voter=voter)
Measure().evaluate(typ="all", voter=5)
