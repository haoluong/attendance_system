import tensorflow as tf
import settings
print(tf.__version__)
def create_mbv2_model(image_shape):
  model = tf.keras.models.load_model(settings.CHECKPOINT_PATH)
  return tf.keras.Sequential(model.layers[:2])