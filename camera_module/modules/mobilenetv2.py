import tensorflow as tf
import numpy as np
import time
print(tf.__version__)
class MobileNetV2():
    def __init__(self, checkpoint_path, anchor_path, label_path):
        self.model = self.__load_model(checkpoint_path)
        self.anchors = np.load(anchor_path)['arr_0']
        # anchors_norm = np.sqrt(np.sum((self.anchors**2),axis=1)).reshape(-1,1)
        # self.anchors /= anchors_norm
        self.labels = np.load(label_path)['arr_0']

    def __load_model(self, checkpoint_path):
        model = tf.keras.models.load_model(checkpoint_path)
        print("MobileNetV2 loaded at {}".format(checkpoint_path))
        return tf.keras.Sequential(model.layers[:2])
    
    def predict(self, batch):
        embeds = self.model(batch)
        res = [self.__classify(e) for e in embeds]#self.__cosine_classify(embeds)
        return res

    def __classify(self, embeds):
        dis_ = np.sqrt(np.sum(np.square(self.anchors - embeds),axis=1))
        min_dis_idx = np.argmin(dis_)
        predict_label = self.labels[min_dis_idx]
        same_label_idx = np.where(self.labels == predict_label)[0]
        same_label_idx = np.delete(same_label_idx, np.where(same_label_idx == min_dis_idx)[0])
        filter_dis = np.delete(dis_,same_label_idx)
        func = np.vectorize(lambda x: np.exp(-x))
        prob = np.exp(-dis_[min_dis_idx])/np.sum(func(filter_dis))
        # return labels[np.argmin(dis_)], np.amin(dis_)
        return predict_label, prob

    def __cosine_classify(self, embeds):
        norms = np.sqrt(np.sum((embeds**2),axis=1)).reshape(-1,1)
        embeds /= norms
        dis_ = embeds@self.anchors.T
        closest_idx = np.argsort(dis_)[:,-1]
        return [(self.labels[idx],0) for idx in closest_idx]

    def inference(self, batch):
        return self.model(batch).numpy()

    def get_sequence_label(self, seq):
        predicts = [self.__classify(e) for e in seq]#self.__cosine_classify(embeds)
        label_groups = sorted(set(map(lambda x:x[0], predicts)))
        total_probs = [sum([y[1] for y in predicts if y[0]==x]) for x in label_groups]
        max_prob = max(total_probs)
        max_label = label_groups[total_probs.index(max_prob)]
        average_prob = list(filter(lambda x:x[0] == max_label,predicts))
        return max_label, (sum(x[1] for x in average_prob)/len(average_prob)) * (max_prob/sum(total_probs))
        