import numpy as np
import cv2 as cv
import os


def colorize(path, img_name, folder_name):
    frame = cv.imread(path)

    proto_file = "./models/colorization_deploy_v2.prototxt"
    weights_file = "./models/colorization_release_v2.caffemodel"

    pts_in_hull = np.load('./pts_in_hull.npy')

    net = cv.dnn.readNetFromCaffe(proto_file, weights_file)

    pts_in_hull = pts_in_hull.transpose().reshape(2, 313, 1, 1)
    net.getLayer(net.getLayerId('class8_ab')).blobs = [pts_in_hull.astype(np.float32)]
    net.getLayer(net.getLayerId('conv8_313_rh')).blobs = [np.full([1, 313], 2.606, np.float32)]

    w_in = 224
    h_in = 224

    img_rgb = (frame[:, :, [2, 1, 0]] * 1.0 / 255).astype(np.float32)
    img_lab = cv.cvtColor(img_rgb, cv.COLOR_RGB2Lab)
    img_l = img_lab[:, :, 0]

    img_l_rs = cv.resize(img_l, (w_in, h_in))
    img_l_rs -= 50

    net.setInput(cv.dnn.blobFromImage(img_l_rs))
    ab_dec = net.forward()[0, :, :, :].transpose((1, 2, 0))

    (h_orig, w_orig) = img_rgb.shape[:2]
    ab_dec_us = cv.resize(ab_dec, (w_orig, h_orig))
    img_lab_out = np.concatenate((img_l[:, :, np.newaxis], ab_dec_us), axis=2)
    img_bgr_out = np.clip(cv.cvtColor(img_lab_out, cv.COLOR_Lab2BGR), 0, 1)

    img_name, _, extension = img_name.partition('.')
    output_file = img_name + "_colorized." + extension
    output_file = os.path.join(folder_name, output_file)
    cv.imwrite(output_file, (img_bgr_out*255).astype(np.uint8))
    return output_file
