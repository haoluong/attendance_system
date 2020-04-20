import numpy as np 
THRESHOLD = 20.0

class Tracker():
    def __init__(self):
        self.identities = []
        self.last_seen = []
        self.timestamp = 0

    def add_ids(self, ids):
        self.timestamp += 1
        if len(ids) > 0:
            distance = self.__calculate_distance(ids)
            self.__assign_group(distance, ids)
        outputs = []
        deleted = []
        for (i,last) in enumerate(self.last_seen):
            if self.timestamp - last >= 5:
                if len(self.identities[i]) > 1:
                    outputs.append(self.identities[i])
                deleted.append(i)
        for i in deleted[::-1]:
            del self.identities[i], self.last_seen[i]
        return outputs
            
    def __assign_group(self, distance, ids):
        ## assign group for each new faces
        min_distance = np.amin(distance, axis=1)
        min_idx = np.argmin(distance, axis=1)
        assigned_list = []
        ## assign for matching faces
        for (i,dis) in enumerate(min_distance):
            new_face_idx = min_idx[i]
            if dis < THRESHOLD and not new_face_idx in assigned_list:
                print("matching: ", i)
                self.identities[i].append(ids[new_face_idx].tolist())
                self.last_seen[i] = self.timestamp
                assigned_list.append(new_face_idx)
        
        ## assign for unmatching faces
        for (i, _id) in enumerate(ids):
            if not i in assigned_list:
                print("nomatching: ", i)
                self.identities.append([_id.tolist()])
                self.last_seen.append(self.timestamp)
        
    def __calculate_distance(self, ids):
        anchors = np.array([ident[-1] for ident in self.identities]).reshape(-1,ids.shape[1])
        ## Calculate distance between new faces to tracking faces
        # (a-b)^2 = a^2 + b^2 -2ab
        ids_square = np.sum(np.square(ids), axis=1)
        ids_square = ids_square.reshape(-1,1)@np.ones([1, anchors.shape[0]])
        anchor_square = np.sum(np.square(anchors), axis=1)
        anchor_square = anchor_square.reshape(-1,1)@np.ones([1,ids.shape[0]])

        return np.sqrt(anchor_square + ids_square.T - 2*anchors@ids.T)

    
