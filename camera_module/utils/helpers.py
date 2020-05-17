# import the necessary packages
import numpy as np
import base64
import sys
def base64_encode_image(a):
	# base64 encode the input NumPy array
	return base64.b64encode(a).decode("utf-8")

def base64_decode_image(a, dtype="uint8", shape=None, byte_convert=True):
	# if this is Python 3, we need the extra step of encoding the
	# serialized NumPy string as a byte object
	if sys.version_info.major == 3 and byte_convert:
		a = bytes(a, encoding="utf-8")

	# convert the string to a NumPy array using the supplied data
	# type and target shape
	a = np.frombuffer(base64.decodestring(a), dtype=dtype)
	a = np.resize(a,shape)
	# return the decoded image
	return a

# def decode_image(img, dtype, shape):
# 	# convert the compressed string to a 3D uint8 tensor
# 	img = tf.image.decode_jpeg(img, channels=3)
# 	# Use `convert_image_dtype` to convert to floats in the [0,1] range.
# 	img = tf.image.convert_image_dtype(img, tf.float32)
# 	# resize the image to the desired size.
# 	return tf.image.resize(img, shape)

# def decode_predictions(preds):
# 	with open('id_list.txt', 'r') as f:
# 		id_line = f.read()
# 		id_list = id_line.split(',')[:-1]
# 		id_list.sort()
# 		index_max_prob = np.argmax(preds, axis=1)
# 		return [(id_list[idx], preds[i, idx]) for (i, idx) in enumerate(index_max_prob)]
