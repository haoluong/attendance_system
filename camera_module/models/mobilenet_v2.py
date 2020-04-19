import tensorflow as tf
print(tf.__version__)
def create_mbv2_model(checkpoint_path):
  model = tf.keras.models.load_model(checkpoint_path)
  return tf.keras.Sequential(model.layers[:2])