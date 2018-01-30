# -*- coding:utf-8 -*-
__author__ = 'Brick'
import sys
import multiprocessing as pro
from support.proc_tk_gui import gui_mainloop
from support.proc_capturer import BrickCV
import brickCV_package


global p_cap
if __name__ == '__main__':
    pro.freeze_support()

    logger = pro.log_to_stderr()
    logger.setLevel(pro.SUBDEBUG)
    brick=BrickCV()
    q_frames_captured = pro.Queue(1)
    q_massage = pro.Queue(1)
    q_object = pro.Queue(1)
    e_frame_captured = pro.Event()

    p_cap = pro.Process(target=brick.cam_loop, args=(q_frames_captured, q_massage, q_object, e_frame_captured))
    p_gui = pro.Process(target=gui_mainloop, args=(q_frames_captured, q_massage, q_object, e_frame_captured))

    try:

        p_gui.start()
        p_cap.start()


        p_gui.join()
        #p_cap.join()


    except KeyboardInterrupt:
        p_cap.terminate()
        p_gui.terminate()

    p_cap.terminate()
    p_gui.terminate()