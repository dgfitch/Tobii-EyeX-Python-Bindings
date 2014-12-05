#!/usr/bin/env python

#############################################################################
##
## Authors: Tom Vanasse, Nate Vack, and Dan Fitch
##
## This file provides the c_type python structures necessary to 
## run simple funtions with the Tobii Eyex Engine, as well as some basic
## functions of its own
##
## TODO:
##   - Async mode is a test and is TOTALLY NOT WORKING!
##
## This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
## WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
##
#############################################################################


from __future__ import print_function
import array 
import os
import sys 
import threading
from struct import *
from ctypes import *

DEBUG = False
    
#callback_generator = CFUNCTYPE
callback_generator = WINFUNCTYPE

# NOTE: First arg is return type, was c_int but the C example returns void
gaze_callback_type = callback_generator(None, POINTER(TobiiGazeData), 
                            POINTER(TobiiGazeDataExtensions),
                            c_void_p)

general_callback_builder = callback_generator(None, c_uint32, c_void_p)


class TobiiPythonAsyncInterface():
    def __init__(self):
        self.error_code = c_uint32()

        WINDOWS_32BIT = sys.maxint == 2147483647
        if WINDOWS_32BIT:
            self.dll = CDLL(os.getcwd() + '\\tobii\\TobiiGazeCore32.dll');
            url_size = 256
        else:
            self.dll = WinDLL(os.getcwd() + '\\tobii\\TobiiGazeCore64.dll');
            url_size = 256

        c_url_size = c_uint32(url_size)

        self.url = create_string_buffer(url_size)
        
        self.dll.tobiigaze_get_connected_eye_tracker(self.url, c_url_size, None)    
        self.eye_tracker = c_void_p(self.dll.tobiigaze_create(self.url, None))

        if DEBUG:
            print("Connecting...")

        def event_thread():
            self.dll.tobiigaze_run_event_loop(self.eye_tracker, byref(self.error_code))
            # TODO: Needs to return whatever type THREADFUNC_RETURN(self.error_code) is
            
        self.event_thread = threading.Thread(target=event_thread)
        self.event_thread.start()


        def gaze(tobiigaze_gaze_data_ref, tobiigaze_gaze_data_extensions_ref, user_data):
            gazedata = tobiigaze_gaze_data_ref.contents
            print("%20.3f " % (gazedata.timestamp / 1e6), end = "") #in seconds


        def start_tracking(error_code, user_data):
            print("start")

        def stop_tracking(error_code, user_data):
            print("stop")


        def connect(error_code, user_data):
            self.dll.tobiigaze_start_tracking_async(self.eye_tracker, byref(self.start_tracking_callback), byref(self.gaze_callback), 0);

        
        self.gaze_callback = general_callback_builder(gaze)
        self.start_tracking_callback = general_callback_builder(start_tracking)
        self.stop_tracking_callback = general_callback_builder(stop_tracking)
        self.connect_callback = general_callback_builder(connect)



        if DEBUG:
            print("Init complete, status: %s" % self.error_code.value)

        self.eye_data_left = []
        self.eye_data_right = []


    def start_tracking(self):
        if DEBUG:
            print("Start tracking, status: %s" % self.error_code.value)

        self.dll.tobiigaze_connect_async(self.eye_tracker, byref(self.connect_callback), 0)  
        self.event_thread.join(10)
        
        if DEBUG:
            print("Start tracking finished, status: %s" % self.error_code.value)
        
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


