#!/usr/bin/env python

#############################################################################
##
## Authors: Tom Vanasse, Nate Vack, and Dan Fitch
##
## This file provides the c_type python structures necessary to 
## run simple funtions with the Tobii Eyex Engine, as well as some basic
## functions of its own  This file works with the 'TobiiGazeCore64.dll' found 
## here: http://developer.tobii.com/eyex-sdk/.
##
## TODO:
##   - Hide more of the innards
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
#############################################################################


from __future__ import print_function
import array 
import os
import sys 
from struct import *
from ctypes import *

DEBUG = False

class TobiiPythonInterface():
    def __init__(self):
        self.error_code = c_uint32()

        WINDOWS_32BIT = sys.maxint == 2147483647
        if WINDOWS_32BIT:
            self.dll = CDLL(os.getcwd() + '\\tobii\\TobiiGazeCore32.dll');
        else:
            self.dll = WinDLL(os.getcwd() + '\\tobii\\TobiiGazeCore64.dll');

        url_size = c_uint32(256)
        self.url = create_string_buffer(256)
        
        self.dll.tobiigaze_get_connected_eye_tracker(self.url, url_size, None)    
        self.eye_tracker = c_void_p(self.dll.tobiigaze_create(self.url, None))
        self.info = TobiiDeviceInfo()
        self.dll.tobiigaze_run_event_loop_on_internal_thread(self.eye_tracker, None, None)
        self.dll.tobiigaze_connect(self.eye_tracker, byref(self.error_code))  
        if DEBUG: print("Init complete, status: %s" % self.error_code.value)
        self.dll.tobiigaze_get_device_info(self.eye_tracker, byref(self.info), byref(self.error_code));

        self.eye_data_left = []
        self.eye_data_right = []


    def get_gaze_callback(self):
        #left = self.eye_data_left
        #right = self.eye_data_right
        def func(tobiigaze_gaze_data_ref, tobiigaze_gaze_data_extensions_ref, user_data):
            gazedata = tobiigaze_gaze_data_ref.contents
            print("%20.3f " % (gazedata.timestamp / 1e6), end = "") #in seconds
            print("%d " % gazedata.tracking_status, end = "")
            
            if (gazedata.tracking_status == TOBIIGAZE_TRACKING_STATUS_BOTH_EYES_TRACKED or
                gazedata.tracking_status == TOBIIGAZE_TRACKING_STATUS_ONLY_LEFT_EYE_TRACKED or
                gazedata.tracking_status == TOBIIGAZE_TRACKING_STATUS_ONE_EYE_TRACKED_PROBABLY_LEFT):
                print("[ %7.4f , %7.4f ] " % (gazedata.left.gaze_point_on_display_normalized.x, 
                    gazedata.left.gaze_point_on_display_normalized.y), end="")
                lefteye = "[ %7.4f , %7.4f ] " % (gazedata.left.gaze_point_on_display_normalized.x, 
                    gazedata.left.gaze_point_on_display_normalized.y) 
                #left.append(lefteye)
            
            else:
                print("[ %7s , %7s ] " % ("-", "-"), end="")
                lefteye = "[ %7s , %7s ] " % ("-", "-")
                #left.append(lefteye)
                
            if (gazedata.tracking_status == TOBIIGAZE_TRACKING_STATUS_BOTH_EYES_TRACKED or
                gazedata.tracking_status == TOBIIGAZE_TRACKING_STATUS_ONLY_RIGHT_EYE_TRACKED or
                gazedata.tracking_status == TOBIIGAZE_TRACKING_STATUS_ONE_EYE_TRACKED_PROBABLY_RIGHT):
                print("[ %7.4f , %7.4f ] " % (gazedata.right.gaze_point_on_display_normalized.x, 
                    gazedata.right.gaze_point_on_display_normalized.y), end="")
                righteye = "[ %7.4f , %7.4f ] " % (gazedata.right.gaze_point_on_display_normalized.x, 
                    gazedata.right.gaze_point_on_display_normalized.y)
                #right.append(righteye)
            
            else:
                print("[ %7s , %7s ] " % ("-", "-"), end="")
                righteye = "[ %7s , %7s ] " % ("-", "-")
                #right.append(righteye)
            
            print("")
            if DEBUG: print("Gaze complete, status: %s" % self.error_code.value)

        return func
    

    def start_tracking(self):
        #callback_generator = CFUNCTYPE
        callback_generator = WINFUNCTYPE

        # NOTE: First arg is return type, was c_int but the C example returns void
        callback_type = callback_generator(None, POINTER(TobiiGazeData), 
                                    POINTER(TobiiGazeDataExtensions),
                                    c_void_p)

        start = self.dll.tobiigaze_start_tracking
        #start.restype = None
        #start.argtypes = (c_void_p, callback_type, c_int_p, c_void_p) 

        start(self.eye_tracker, callback_type(self.get_gaze_callback()), byref(self.error_code), None)                                                        
        
    def stop_tracking(self):
        self.dll.tobiigaze_stop_tracking(self.eye_tracker, byref(self.error_code))
        self.dll.tobiigaze_disconnect(self.eye_tracker)
        self.dll.tobiigaze_break_event_loop(self.eye_tracker)
        self.dll.tobiigaze_destroy(self.eye_tracker)
        
    def isfloat(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False
        
    def clearData(self):
        del self.eye_data_left[:]
        del self.eye_data_right[:]

        
    def grab_x(self):
        string = ((self.eye_data_left.pop().split(" ")[2]))
        if isfloat(string):
            return float(string) 
        else:
            return 0
                
    def grab_y(self):
        string = ((self.eye_data_left.pop().split(" ")[5]))
        if isfloat(string):
            return  float(string) 
        else:
            return 0

