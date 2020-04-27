import numpy as np 
THRESHOLD = 30

class Tracker():
    def __init__(self):
        self.tracker_faces = []
        self.locations = []
        self.identities = []
        self.last_seen = []
        self.timestamp = 0

    def add_ids(self, face_boxes, b_boxes, ids):
        self.timestamp += 1
        if len(ids) > 0:
            distance = self.__calculate_distance(b_boxes, ids)
            self.__assign_group(distance, face_boxes, b_boxes, ids)
        outputs = []
        deleted = []
        for (i,last) in enumerate(self.last_seen):
            if self.timestamp - last >= 5:
                if len(self.identities[i]) > 1:
                    direction = self.__detect_direction(self.locations[i][-1])
                    outputs.append({
                        'tracker_images': self.tracker_faces[i],
                        'seq': self.identities[i], 
                        'inKTX': direction
                        })
                deleted.append(i)
        for i in deleted[::-1]:
            del self.identities[i], self.tracker_faces[i], self.locations[i], self.last_seen[i]
        return outputs
            
    def __detect_direction(self, location):
        return True if (location[0] + location[2])/2 <= 0.5 else False

    def __assign_group(self, distance, face_boxes, b_boxes, ids):
        ## assign group for each new faces
        min_distance = np.amin(distance, axis=1)
        min_idx = np.argmin(distance, axis=1)
        assigned_list = []
        ## assign for matching faces
        for (i,dis) in enumerate(min_distance):
            new_face_idx = min_idx[i]
            if dis < THRESHOLD and not new_face_idx in assigned_list:
                print("matching: ", i)
                if len(self.locations[i]) == 32:
                    del self.identities[i][0], self.locations[i][0], self.tracker_faces[i][0]
                self.identities[i].append(ids[new_face_idx].tolist())
                self.locations[i].append(b_boxes[new_face_idx])
                self.tracker_faces[i].append(face_boxes[new_face_idx])
                self.last_seen[i] = self.timestamp
                assigned_list.append(new_face_idx)
        
        ## assign for unmatching faces
        for (i, _id) in enumerate(ids):
            if not i in assigned_list:
                print("nomatching: ", i)
                self.identities.append([_id.tolist()])
                self.locations.append([b_boxes[i]])
                self.last_seen.append(self.timestamp)
                self.tracker_faces.append([face_boxes[i]])
    
    def __calculate_distance(self, b_boxes, ids):
        embeds_distance = self.__calculate_embeds_distance(ids)
        location_distance = self.__calculate_location_distance(b_boxes)
        return location_distance + embeds_distance

    def __calculate_location_distance(self, b_boxes):
        anchors = np.array([loc[-1] for loc in self.locations]).reshape(-1, 4)
        ## Calculate distance between new faces to tracking faces
        # (a-b)^2 = a^2 + b^2 -2ab
        bbox_square = np.sum(np.square(b_boxes), axis=1)
        bbox_square = bbox_square.reshape(-1,1)@np.ones([1, anchors.shape[0]])
        anchor_square = np.sum(np.square(anchors), axis=1)
        anchor_square = anchor_square.reshape(-1,1)@np.ones([1,bbox_square.shape[0]])
        return np.sqrt(anchor_square + bbox_square.T - 2*anchors@np.array(b_boxes).T)

    def __calculate_embeds_distance(self, ids):
        anchors = np.array([ident[-1] for ident in self.identities]).reshape(-1,ids.shape[1])
        ## Calculate distance between new faces to tracking faces
        # (a-b)^2 = a^2 + b^2 -2ab
        ids_square = np.sum(np.square(ids), axis=1)
        ids_square = ids_square.reshape(-1,1)@np.ones([1, anchors.shape[0]])
        anchor_square = np.sum(np.square(anchors), axis=1)
        anchor_square = anchor_square.reshape(-1,1)@np.ones([1,ids.shape[0]])

        return np.sqrt(anchor_square + ids_square.T - 2*anchors@ids.T)

    
