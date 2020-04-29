from absl import app, flags, logging
from absl.flags import FLAGS
import cv2
import os
import numpy as np
import tensorflow as tf

from utils.evaluation import get_val_data, perform_val
from modules.utils import set_memory_growth, load_yaml, l2_norm


flags.DEFINE_string('cfg_path', './configs/arc_mbv2.yaml', 'config file path')
flags.DEFINE_string('gpu', '0', 'which gpu to use')

def main(_argv):
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
    os.environ['CUDA_VISIBLE_DEVICES'] = FLAGS.gpu

    logger = tf.get_logger()
    logger.disabled = True
    logger.setLevel(logging.FATAL)
    set_memory_growth()

    cfg = load_yaml(FLAGS.cfg_path)

    model = tf.keras.models.load_model(cfg['model_path'])

    
    print("[*] Loading LFW, AgeDB30 and CFP-FP...")
    lfw, agedb_30, cfp_fp, lfw_issame, agedb_30_issame, cfp_fp_issame = \
        get_val_data(cfg['test_dataset'])

    print("[*] Perform Evaluation on LFW...")
    acc_lfw, best_th = perform_val(
        cfg['embd_shape'], cfg['batch_size'], model, lfw, lfw_issame,
        is_ccrop=cfg['is_ccrop'])
    print("    acc {:.4f}, th: {:.2f}".format(acc_lfw, best_th))

    print("[*] Perform Evaluation on AgeDB30...")
    acc_agedb30, best_th = perform_val(
        cfg['embd_shape'], cfg['batch_size'], model, agedb_30,
        agedb_30_issame, is_ccrop=cfg['is_ccrop'])
    print("    acc {:.4f}, th: {:.2f}".format(acc_agedb30, best_th))

    print("[*] Perform Evaluation on CFP-FP...")
    acc_cfp_fp, best_th = perform_val(
        cfg['embd_shape'], cfg['batch_size'], model, cfp_fp, cfp_fp_issame,
        is_ccrop=cfg['is_ccrop'])
    print("    acc {:.4f}, th: {:.2f}".format(acc_cfp_fp, best_th))


if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass