import cv2
import numpy as np
from random import randint
import os
import time
from json import load, dump, dumps, loads
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from base64 import b64encode
from base64 import b64decode
from TDES import encryptTripleDES, decryptTripleDES


class VideoSteg:

    def __init__(self, path_to_vid_file, path_to_msg_file=0):
        self.cap = cv2.VideoCapture(path_to_vid_file)

        self.VID_FILE_PATH = path_to_vid_file
        self.MSG_FILE_PATH = path_to_msg_file
        self.KEYS = dict()

        self.FRAME_WIDTH = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.FRAME_HEIGHT = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.FRAME_SIZE = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) * int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) * 3
        self.TOTAL_FRAMES = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.FRAMES_PER_SECOND = int(self.cap.get(cv2.CAP_PROP_FPS))
        self.TOTAL_EMBEDDING_CAPACITY = self.FRAME_SIZE * self.TOTAL_FRAMES
        self.TOTAL_DURATION = int(self.TOTAL_FRAMES/self.FRAMES_PER_SECOND)

    def retrieveDesiredFrame(self, cap, frame_list):

        for x in range(len(frame_list)):
            for _ in range(frame_list[x]):
                _, frame = cap.read()

            cap.set(1, 0.0)
            yield frame



    def openNBinarizeMsg(self, msg_file_path):
        if os.path.isfile(msg_file_path):
                    if os.stat(msg_file_path).st_size > 0:
                        with open(msg_file_path, 'r') as msg_file:
                            msg = msg_file.read()
                            msg_bin_list = list()
                            for char in msg:
                                temp_bin_word = list(format(ord(char), '08b'))
                                for bit in temp_bin_word:
                                    msg_bin_list.append(bit)
                        return msg_bin_list
                    
                    else:
                        #('FILE EMPTY')
                        return -1
                    
        else:
            #('GIVEN PATH DOES NOT LEAD TO TEXT FILE')
            return -1



    def randomFrameSelection(self, total_payload_size=0, custom=0):
        if total_payload_size == 0 and custom == 1:
            rand_frame = randint(1, self.TOTAL_FRAMES)
            return rand_frame
        else:
            frame_list = list()
            num_of_frames_req = self.numberOfFramesReq(total_payload_size)
            frame_range = round((num_of_frames_req/100)*self.TOTAL_FRAMES)
            #('frame_range = ', frame_range)
            while True:
                for _ in range(num_of_frames_req):
                    rand_frame = randint(1, frame_range)
                    if rand_frame not in frame_list:
                        frame_list.append(rand_frame)

                if len(frame_list) == num_of_frames_req:
                    return sorted(frame_list)
                frame_list = []


    def numberOfFramesReq(self, total_payload_size):
        
        for x in range(1, self.TOTAL_FRAMES+1):
            if x*self.FRAME_SIZE > total_payload_size:
                return x
        return -1


    def initialCapacityCheck(self, payload_data):

        if self.TOTAL_EMBEDDING_CAPACITY > payload_data:
            return True
        else:
            return False

    def frameStartIndex(self, frame, payload_size):

        while True:
            frame_index = randint(0, frame.shape[0]/4)
            remaining_rows = frame.shape[0] - frame_index

            if remaining_rows*frame.shape[1]*frame.shape[2] > payload_size:
                return frame_index

    ''' Legacy method '''
    def frameWriter(self, cap, substitute_frames_loc, substitute_frames):
        out = cv2.VideoWriter('outVideo.avi', cv2.VideoWriter_fourcc(*'HFYU'), self.FRAMES_PER_SECOND, (self.FRAME_WIDTH, self.FRAME_HEIGHT))

        cap.set(1, 0.0)
        x = 0
        y = 0 
        while True:
            ret, frame = cap.read()
            if ret:
                if x+1 in substitute_frames_loc:
                    try:
                        out.write(substitute_frames[y])
                        #('frame inserted')
                    except IndexError:
                        #('error_index = ',y)
                        exit()
                    y += 1
                    x += 1
                else:
                    out.write(frame)
                    x += 1
            else:
                out.release()
                break
            



    def embeddingPerFrame(self, frame, start_index, payload_data, frame_key=0):

        row = start_index
        col = 0
        x = 0
        while x < len(payload_data):

            for val in range(3):
                #('old_val = ', frame[row][col][val])
                bin_form = list(format(frame[row][col][val], '08b'))
                #('old bin_form = ', bin_form)
                bin_form[-1] = payload_data[x]
                #('payload_data = ', payload_data[x])
                #('new bin_form = ', bin_form)
                new_val = ''.join(bin_form)
                frame[row][col][val] = int(new_val, 2)
                #('new_val = ', frame[row][col][val])
                x += 1
                if x >= len(payload_data):
                    break

            col += 1
            if col == frame.shape[1]:
                row  += 1
                col = 0
        
        #('end_index = ', (row, col))
        self.KEYS[frame_key].append((row, col))
        
        return frame


    def embeddingCapacityPerFrame(self, payload_size):
        if self.FRAME_SIZE > payload_size:
            return True
        else:
            return False


    def payloadBinarySizeCalc(self, path_to_msg_file):
        a = 0
        with open(path_to_msg_file, 'r') as f:
            for line in f:
                for _ in line:
                    a += 8

        return a


    def payloadCharSizeCalc(self, path_to_msg_file):
        a = 0
        with open(path_to_msg_file, 'r') as f:
            for line in f:
                for _ in line:
                    a += 1

        return a

    def binarizePayload(self, msg):
        msg_bin_list = list()
        for char in msg:
            temp_bin_word = list(format(ord(char), '08b'))
            for bit in temp_bin_word:
                msg_bin_list.append(bit)
        return msg_bin_list

    def payloadDivision(self, parts):

        payload_size = self.payloadCharSizeCalc(self.MSG_FILE_PATH)
        x = 0
        with open(self.MSG_FILE_PATH, 'r') as payload_file:
            for _ in range(parts):
                part = payload_file.read()[x:x+int(payload_size/parts)]
                x += int(payload_size/parts)
                
                payload_file.seek(0, 0)

                part = self.binarizePayload(part) 

                yield part




    @staticmethod
    def initialSpecCheck(obj, path_to_file):

        allowed_formats = ['mp4', 'avi']
        if path_to_file[-3:] not in allowed_formats:
            return False
        try:
            cap = cv2.VideoCapture(path_to_file)
        except:
            return False

        _, frame = cap.read()

        fps = [x for x in range(1, 31)]
        try:
            if frame.ndim == 3:
                if frame.dtype == 'uint8':
                    if obj.FRAMES_PER_SECOND in fps:
                        if obj.TOTAL_DURATION > 0 and obj.TOTAL_DURATION <= 60:
                            return True
            
            return False

        except Exception as e:
            #(e)
            return False

    def mainProcess(self):
        msg_bin_size = self.payloadBinarySizeCalc(self.MSG_FILE_PATH)

        #('len of msg = ', msg_bin_size)
        if self.initialCapacityCheck(msg_bin_size):
            modified_frames_list = list()
            random_frames = self.randomFrameSelection(msg_bin_size)
            #('frames required = ', len(random_frames))
            #('indexes of random frame = ', random_frames)

            frame_retrieve_gen_func = self.retrieveDesiredFrame(self.cap, random_frames)
            payload_part_gen_func = self.payloadDivision(len(random_frames))


            
            for x in random_frames:
                frame = next(frame_retrieve_gen_func)
                payload = next(payload_part_gen_func)
                #('size of payload part = ', len(payload))
                start_index = self.frameStartIndex(frame, len(payload))
                #('start_index = ', (start_index, 0))
                self.KEYS[f'{str(x)}'] = [(start_index, 0)]



                modified_frame = self.embeddingPerFrame(frame, start_index, payload, f'{str(x)}')
                modified_frames_list.append(modified_frame)


            self.frameWriter(self.cap, random_frames, modified_frames_list)

            #('len(modified_frames_list) = ', len(modified_frames_list))
            self.cap.release()

            return 1


    def encryptMsg(self, msg_file):
        with open(msg_file, 'r') as secret_msg_file:
            secret_msg = secret_msg_file.read()

        while True:
            try:
                key = DES3.adjust_key_parity(get_random_bytes(24))
                break
            except ValueError:
                pass
                #('KEY SIZE ERROR VIDEO STEG')
        
        enc_msg = encryptTripleDES(secret_msg, key)
        self.KEYS['TDES'] = b64encode(key).decode('utf-8')

        with open('encrypted_msg_video.txt', 'w') as enc_file:
            enc_file.write(enc_msg)

        return 'encrypted_msg_video.txt'


    def embed(self, save_to):
        enc_msg_file_path = self.encryptMsg(self.MSG_FILE_PATH)
        self.MSG_FILE_PATH = enc_msg_file_path
        self.alternateEmbedding(save_to)



    def alternateEmbedding(self, save_to):
        key_name = 'video_keys.json'
        save_to = save_to.split('/')
        save_to.append(key_name)
        save_to = '/'.join(save_to)


        frame_index = self.randomFrameSelection(custom=1)
        key = self.KEYS

        key[str(frame_index)] = []
        frame = self.retrieveDesiredFrame(self.cap, [frame_index])

        p = self.payloadDivision(1)

        payload = next(p)
        f = next(frame)

        row = 0
        col = 0
        x = 0

        while x < len(payload):
            for val in range(3):
                if format(f[row][col][val], '08b')[-1] == payload[x]:
                    key[str(frame_index)].append([row, col, val])
                    x += 1 
                    if x == len(payload):
                        break
            col += 1
            if col == self.FRAME_WIDTH:
                row += 1
                col = 0
            if row == self.FRAME_HEIGHT:
                if len(list(key.keys())) < self.TOTAL_FRAMES:
                    while True:
                        frame_index = self.randomFrameSelection(custom=1)
                        if frame_index not in key.keys():
                            break
                    frame = self.retrieveDesiredFrame(self.cap, [frame_index])
                    f = next(frame)
                    key[str(frame_index)] = []
                    row = 0
                    col = 0
                else:
                    #('data capacity exceeded, ending, process unsuccessful...')
                    return -1

        with open(save_to, 'w') as file:
            dump(key, file)

        self.cap.release()

        return 1


    def decrypt(self, message, key):
        key = b64decode(key)

        dec_msg = decryptTripleDES(message, key)

        return dec_msg
        


    @classmethod
    def alternateDeEmbedding(cls, key_file_path, vid_path, save_to_file_path=0):
        msg_filename = 'message_from_video.txt'
        save_to_file_path = save_to_file_path.split('/')
        save_to_file_path.append(msg_filename)
        save_to_file_path = '/'.join(save_to_file_path)

        cap = cv2.VideoCapture(vid_path)

        with open(key_file_path, 'r') as file:
            key = load(file)
        
        msg = ''
        binary = ''
        for x in key:
            if x.isnumeric():
                frame = cls.retrieveDesiredFrame(cls, cap, [int(x)])
                f = next(frame)

                for y in key[x]:

                    binary += format(f[y[0], y[1], y[2]], '08b')[-1]
                    if len(binary) == 8:
                        msg += chr(int(binary, 2))
                        binary = ''

        msg = cls.decrypt(cls, msg, key['TDES'])
        #(msg)

        if save_to_file_path != 0:
            with open(save_to_file_path, 'w') as save_to_file:
                save_to_file.write(msg)
                #('message saved to ', save_to_file_path)


        cap.release()

            
    ''' Legacy method testing phase '''
    @classmethod
    def deEmbedNDecrypt(cls, key_file_path, steg_vid_path):
        cap = cv2.VideoCapture(steg_vid_path)
        key_obj = {'1': [(146,0), (146, 30)]}
        frame_indexes = list(key_obj.keys())
        frame_indexes = [int(x) for x in frame_indexes]
        frame = cls.retrieveDesiredFrame(cls, cap, frame_indexes)

        for x in key_obj:
            row = key_obj[x][0][0]
            col = key_obj[x][0][1]

            end_row = key_obj[x][1][0]
            end_col = key_obj[x][1][1]

            binary = ''
            str_msg = ''

            frm = next(frame)

            while end_row >= row:
                if row != end_row:
                    for y in range(frm.shape[1]):
                        f = frm[row][y]
                        for pix in range(3):
                            val = f[pix]
                            binary += format(val, '08b')[-1]
                            if len(binary) == 8:

                                str_msg += chr(int(binary, 2))
                                binary = ''

                
                    row += 1

                else:
                    for y in range(end_col):
                        f = frm[row][y]
                        for pix in range(3):
                            val = f[pix]
                            #(val)
                            binary += format(val, '08b')[-1]
                            if len(binary) == 8:
                                #(binary)
                                str_msg += chr(int(binary, 2))
                                binary = ''

                    break


                if row == end_row - 1:
                    for y in range(end_col):
                        f = frm[row][y]
                        for pix in range(3):
                            val = f[pix]
                            binary += format(val, '08b')[-1]
                            if len(binary) == 8:
                                str_msg += chr(int(binary, 2))
                                binary = ''

        #(str_msg)






