import tensorflow as tf
import numpy as np
import time
from modules.utils import preprocess_input, l2_norm
print(tf.__version__)
THRESHOLD = 40
class MobileNetV2():
    def __init__(self, checkpoint_path, storage):
        self.model = self.__load_model(checkpoint_path)
        self.storage = storage
        self.__load_embeds()

    def __load_embeds(self):
        self.embeds = self.storage.get_embeds()
        self.labels = self.storage.get_labels()
        self.storage.update_reload_status(value=False)

    def __load_model(self, checkpoint_path):
        model = tf.keras.models.load_model(checkpoint_path)
        print("MobileNetV2 loaded at {}".format(checkpoint_path))
        return model
    
    def __check_update_embeds(self):
        return self.storage.check_reload_status()

    def predict(self, batch):
        if self.__check_update_embeds():
            self.__load_embeds()
        batch = preprocess_input(batch)
        embeds = self.model(batch)
        res = [self.__classify(e) for e in embeds]#self.__cosine_classify(embeds)
        return res

    def __classify(self, embeds):
        dis_ = np.sqrt(np.sum(np.square(self.embeds - embeds),axis=1))
        min_dis_idx = np.argmin(dis_)
        predict_label = self.labels[min_dis_idx]
        if dis_[min_dis_idx] > THRESHOLD:
            prob = 0.01
        else:
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
        dis_ = embeds@self.embeds.T
        closest_idx = np.argsort(dis_)[:,-1]
        return [(self.labels[idx],0) for idx in closest_idx]

    def inference(self, batch):
        batch = preprocess_input(batch)
        return self.model(batch).numpy()

    def get_sequence_label(self, seq):
        if self.__check_update_embeds():
            self.__load_embeds()
        predicts = [self.__classify(e) for e in seq]#self.__cosine_classify(embeds)
        label_groups = sorted(set(map(lambda x:x[0], predicts)))
        total_probs = [sum([y[1] for y in predicts if y[0]==x]) for x in label_groups]
        max_prob = max(total_probs)
        max_label = label_groups[total_probs.index(max_prob)]
        average_prob = list(filter(lambda x:x[0] == max_label,predicts))
        return max_label, (sum(x[1] for x in average_prob)/len(average_prob)) * (max_prob/sum(total_probs))
        