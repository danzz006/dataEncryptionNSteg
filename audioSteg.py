import wave as wav
import numpy as np
import struct
import sndhdr
import random
import json
import os
import time
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from base64 import b64encode
from base64 import b64decode
from TDES import encryptTripleDES, decryptTripleDES



class AudioSteg:

    TDES_key = 0

    def is_form_correct(self, audio_file_path):

        header = sndhdr.what(audio_file_path)

        if header.filetype == 'wav' and header.nchannels == 2:
            #('FILE SUPPORTED')
            return True
        return False
        

    @staticmethod
    def encryptMsg(cls, msg_file):
        with open(msg_file, 'r') as secret_msg_file:
            secret_msg = secret_msg_file.read()

        while True:
            try:
                key = DES3.adjust_key_parity(get_random_bytes(24))
                break
            except ValueError:
                pass
                #('KEY SIZE ERROR AUDIO STEG')
        
        enc_msg = encryptTripleDES(secret_msg, key)
        cls.TDES_key = b64encode(key).decode('utf-8')

        with open('encrypted_msg_audio.txt', 'w') as enc_file:
            enc_file.write(enc_msg)
            #('ENCRYPTED MESSAGE FILE CREATED AND SAVED')



    def __init__(self, audio_file_path, msg_path):

        try:
            self.audio_file_wave = wav.open(audio_file_path)

            if self.is_form_correct(audio_file_path):
                self.audio_file_path = audio_file_path
                self.channels = self.audio_file_wave.getnchannels()
                self.frame_rate = self.audio_file_wave.getframerate()
                self.sample_width = self.audio_file_wave.getsampwidth()
                self.total_frames = self.audio_file_wave.getnframes()
                self.start_index = 0
                self.end_index = 0
                self.msg_bin_list = list()
                if os.path.isfile(msg_path):
                    if os.stat(msg_path).st_size > 0:
                        with open(msg_path, 'r') as self.msg_file:
                            self.msg = self.msg_file.read()
                            for char in self.msg:
                                temp_bin_word = list(format(ord(char), '08b'))
                                for bit in temp_bin_word:
                                    self.msg_bin_list.append(bit)
                    
                    else:
                        pass
                        #('FILE EMPTY')
                    
                else:
                    pass
                    #('GIVEN PATH DOES NOT LEAD TO TEXT FILE')
            
            else:
                pass
                #('FORMAT OR TYPE OF PROVIDED AUDIO NOT SUPPORTED')

        except FileNotFoundError:
            pass
            #('FILE NOT FOUND')


    def random_loc(self):
        index = random.randrange(round(self.total_frames/8))
        #(index)
        return index



    def to_frames(self):
        frame_data = self.audio_file_wave.readframes(-1)
        frame_data_list = np.frombuffer(frame_data, dtype=np.int16)
        frame_data_list.shape = -1, 2
        frame_data_list = frame_data_list.T
        frame_data_new = np.array(frame_data_list)

        return frame_data_new

    
    def audio_writer(self, frame_data_new, save_to):

        stego_filename = 'stego_'+self.audio_file_path.split('/')[-1]
        save_to = save_to.split('/')
        save_to.append(stego_filename)
        save_to = '/'.join(save_to)

        stego_sound = wav.open(save_to, 'w')

        stego_sound.setnchannels(self.channels)
        stego_sound.setsampwidth(self.sample_width)
        stego_sound.setframerate(self.frame_rate)

        for sample_index in range(len(frame_data_new[0])):
            raw_sample1 = frame_data_new[0][sample_index]
            raw_sample2 = frame_data_new[1][sample_index]
            stego_sound.writeframesraw(struct.pack('<hh', raw_sample1, raw_sample2))
        stego_sound.close() 


    def keys_writer(self, start, end, tdes_key, save_to):
        keys_name = 'audio_keys.json'
        save_to = save_to.split('/')
        save_to.append(keys_name)
        save_to = '/'.join(save_to)
        with open(save_to, 'w') as key_file:
            keys = {'start': start, 'end': end, 'TDES': tdes_key}
            json.dump(keys, key_file)
        #('keys saved')


    def embedder(self,save_to):
        start_time = time.time()
        frame_data_new = self.to_frames()
        msg_bin = self.msg_bin_list
        i = self.random_loc()
        if len(frame_data_new[0][i:]) > len(msg_bin):
            #('capacity check cleared')
            self.start_index = i                        
            word_count = 0
            run = True
            while run:                                        
                for k in range(2):
                    bin_frame = list(format(frame_data_new[k][i], '016b'))

                    if word_count < len(msg_bin):

                        if abs(frame_data_new[k][i]) >= 16384:
                            bin_frame[8:] = msg_bin[word_count:(word_count+8)]
                            word_count += 8
                        elif abs(frame_data_new[k][i]) >= 8192:
                            bin_frame[9:] = msg_bin[word_count:(word_count+7)]
                            word_count += 7
                        elif abs(frame_data_new[k][i]) >= 4096:
                            bin_frame[10:] = msg_bin[word_count:(word_count+6)]
                            word_count += 6
                        elif abs(frame_data_new[k][i]) >= 2048:
                            bin_frame[11:] = msg_bin[word_count:(word_count+5)]
                            word_count += 5
                        elif abs(frame_data_new[k][i]) >= 1024:
                            bin_frame[12:] = msg_bin[word_count:(word_count+4)]
                            word_count += 4
                        elif abs(frame_data_new[k][i]) >= 512:
                            bin_frame[13:] = msg_bin[word_count:(word_count+3)]
                            word_count += 3
                        elif abs(frame_data_new[k][i]) >= 256:
                            bin_frame[14:] = msg_bin[word_count:(word_count+2)]
                            word_count += 2
                        else:
                            bin_frame[-1] = msg_bin[word_count]
                            word_count += 1

                    else:
                        run = False

                    bin_str_frame = ''.join(bin_frame)
                    bin_int = int(bin_str_frame, 2)
                    frame_data_new[k][i] = bin_int

                i += 1
            self.end_index = i-1
            #(i)

            self.audio_writer(frame_data_new, save_to)     
            #('Stego object created') 

            self.keys_writer(self.start_index, self.end_index, self.TDES_key, save_to)
            #('Execution time = {} seconds'.format(time.time() - start_time))
            return True

        else:
            #('capacity check failed')
            return False


    def decrypt(self, message, key, save_to):
        key = b64decode(key)

        dec_msg = decryptTripleDES(message, key)

        with open(save_to, 'w') as file:
            file.write(dec_msg)
            #('DECREYTED MESSAGE FROM AUDIO SAVED')


    @classmethod
    def de_embed(cls, audio_file, key_file, save_to):

        msg_name = 'message_from_audio.txt'
        save_to = save_to.split('/')
        save_to.append(msg_name)
        save_to = '/'.join(save_to)

        if os.path.isfile(key_file):

            if os.stat(key_file).st_size > 0:
                with open(key_file, 'r') as json_key_file:
                    keys = json.load(json_key_file)
            else:
                pass
                #(' KEYS FILE EMPTY')

        else:
            pass
            #('KEYS FILE PATH DOES NOT LEAD TO FILE')
        
        try:
            stego_wave = wav.open(audio_file)
        
            if cls.is_form_correct(cls, audio_file):
                    frames = stego_wave.readframes(-1)
                    frames_list = np.frombuffer(frames, dtype=np.int16)
                    frames_list.shape = -1,2
                    frames_list = frames_list.T
                    frames_array = np.array(frames_list)
                    # #(frames_array)
                    result_list = []

                    for val in range(keys['start'], keys['end']):                               
                        for i in range(2):
                            bin_frame = format(frames_array[i][val], '016b')
             
                            if abs(frames_array[i][val]) >= 16384:
                                for bit in bin_frame[8:]:
                                    result_list.append(bit)

                            elif abs(frames_array[i][val]) >= 8192:
                                for bit in bin_frame[9:]:
                                    result_list.append(bit)
                            elif abs(frames_array[i][val]) >= 4096:
                                for bit in bin_frame[10:]:
                                    result_list.append(bit)
                            elif abs(frames_array[i][val]) >= 2048:
                                for bit in bin_frame[11:]:
                                    result_list.append(bit)
                            elif abs(frames_array[i][val]) >= 1024:
                                for bit in bin_frame[12:]:
                                    result_list.append(bit)
                            elif abs(frames_array[i][val]) >= 512:
                                for bit in bin_frame[13:]:
                                    result_list.append(bit)
                            elif abs(frames_array[i][val]) >= 256:
                                for bit in bin_frame[14:]:
                                    result_list.append(bit)
                            else:
                                result_list.append(bin_frame[-1])

                    result_bits = ''
                    result_formed_list_temp = []
                    result_string = ''

                    while True:
                        if len(result_list) % 8 == 0:
                            break
                        result_list.remove(result_formed_list_temp[-1])

                    for i in result_list:
                        result_bits += i
                        if len(result_bits) == 8:
                            result_formed_list_temp.append(int(result_bits, 2))
                            result_bits = ''

                    for i in result_formed_list_temp:
                        result_string += chr(i)
                    
                    msg_retv = open('messageSoundEncrypted.txt', 'w')
                    msg_retv.write(result_string)
                    msg_retv.close()
                    #('encrypted message file created and saved')


                    with open('messageSoundEncrypted.txt', 'r') as enc_file:
                        enc_msg = enc_file.read()
                    
                    cls.decrypt(cls, enc_msg, keys['TDES'], save_to)

            else:
                pass
                #('TYPE OR FORMAT OF PROVIDED FILE NOT SUPPORTED')
        
        except FileNotFoundError:
            pass
            #('AUDIO FILE NOT FOUND')

        except ValueError:
            print("Value error")







































