import numpy as np
import cv2

class FaceAligner():
    def __init__(self, desiredFaceSize=160):
        self.desiredFaceSize = desiredFaceSize

    def __get_desiredLeftEye__(self, leftEye, rightEye, b_box):
        self.desiredLeftEye = (
            (leftEye[0] - b_box[0])/(b_box[2]-b_box[0]),
            (leftEye[1] - b_box[1])/(b_box[3]-b_box[1])
        )
        self.desiredRightEye = (
            (rightEye[0] - b_box[0])/(b_box[2]-b_box[0]),
            (rightEye[1] - b_box[1])/(b_box[3]-b_box[1])
        )
        dx = self.desiredRightEye[0]-self.desiredLeftEye[0]
        dy = self.desiredRightEye[1]-self.desiredLeftEye[1]
        self.desiredDist = np.sqrt(dx**2+dy**2)

    def align(self, image, landmarks, b_box):
        left_eye = landmarks["left_eye"]
        right_eye = landmarks["right_eye"]
        nose = landmarks["nose"]
        left_mouth = landmarks["left_mouth"]
        right_mouth = landmarks["right_mouth"]

        eyeCenter = (int((right_eye[0]+left_eye[0])/2), int((right_eye[1]+left_eye[1])/2))
        mouthCenter = (int((right_mouth[0] + left_mouth[0])/2), int((right_mouth[1] + left_mouth[1])/2))

        # compute the angle between the eye centroids
        dY = eyeCenter[1] - mouthCenter[1]
        dX = eyeCenter[0] - mouthCenter[0]
        angle = np.degrees(np.arctan2(dY, dX))+90
        # if abs(angle) > -1:
        #     croped_image = image[b_box[1]:b_box[3],b_box[0]:b_box[2], :]
        #     return cv2.resize(croped_image, (self.desiredFaceSize,self.desiredFaceSize), interpolation=cv2.INTER_CUBIC)
        # compute the desired right eye x-coordinate based on the
        # desired x-coordinate of the left eye
        # desiredRightEyeX = 1.0 - self.desiredLeftEye[0]

        # determine the scale of the new resulting image by taking
        # the ratio of the distance between eyes in the *current*
        # image to the ratio of distance between eyes in the
        # *desired* image
        dist = np.sqrt((dX ** 2) + (dY ** 2))
        eye_dist = np.sqrt((right_eye[0]-left_eye[0])**2+(right_eye[1]-left_eye[1])**2)
        # desiredDist = self.desiredDist #(desiredRightEyeX - self.desiredLeftEye[0])
        # desiredDist *= self.desiredFaceSize
        scale = np.sqrt(0.4*(b_box[3]-b_box[1]) / dist - 1.2*(eye_dist/(b_box[2]-b_box[0])) + 0.5)
        # compute center (x, y)-coordinates (i.e., the median point)
        # between the two eyes in the input image
        # eyesCenter = ((left_eye[0] + right_eye[0]) // 2,
        #     (left_eye[1] + right_eye[1]) // 2)
        center = ((b_box[0]+b_box[2])//2, (b_box[1]+b_box[3])//2)
        # grab the rotation matrix for rotating and scaling the face
        M = cv2.getRotationMatrix2D(center, angle, 1)

        # update the translation component of the matrix
        tX = self.desiredFaceSize * 0.5
        tY = self.desiredFaceSize * 0.5
        M[0, 2] += (tX - center[0])
        M[1, 2] += (tY - center[1])

        # apply the affine transformation
        (w, h) = (self.desiredFaceSize, self.desiredFaceSize)
        output = cv2.warpAffine(image, M, (w, h),
            flags=cv2.INTER_CUBIC)
        cv2.imshow('aligned', output)
        if cv2.waitKey(1) == ord('q'):
            exit()
        return output