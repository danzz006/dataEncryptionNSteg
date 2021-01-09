from PIL import Image
import imghdr
import binascii
import numpy as np
import random
import cv2
from matplotlib import pyplot as plt
import operator
import json
import os
from Crypto.Cipher import DES3
from Crypto.Random import get_random_bytes
from base64 import b64encode
from base64 import b64decode
from TDES import  encryptTripleDES, decryptTripleDES
import time


class ImageSteg:

    key = {'TDES': 'NONE KEY INITIALIZE'}

    def __init__(self, filename, message_path):
        self.filename = filename
        self.msg_path = message_path

        self.cover_img = Image.open(self.filename)
        self.cover_img_size = self.cover_img.size
        self.cover_img_size = self.cover_img_size[0] * self.cover_img_size[1]


        self.keys = {'R': (), 'G': (), 'B': (), 'TDES': ImageSteg.key['TDES']}
        self.file = open(message_path, 'r')
        self.msg = self.file.read()
        self.binary_msg = ''.join(format(ord(i), '08b') for i in self.msg)

        self.pixels_data = list(self.cover_img.getdata())
        self.red_channel = self.cover_img.getchannel(channel='R')
        self.red_channel_list = list(self.red_channel.getdata())
        self.green_channel = self.cover_img.getchannel(channel='G')
        self.green_channel_list = list(self.green_channel.getdata())
        self.blue_channel = self.cover_img.getchannel(channel='B')
        self.blue_channel_list = list(self.blue_channel.getdata())



    @staticmethod
    def encrypter(cls, msg_file, msg_save_to):
        with open(msg_file, 'r') as txt:
            plain_txt = txt.read()

        
        while True:
            try:
                key = DES3.adjust_key_parity(get_random_bytes(24))
                if len(key) == 24:
                    break
            except ValueError:
                print('TDES KEY SIZE ERROR')
        

        cipher_txt_encoded = encryptTripleDES(plain_txt, key)
        key_encoded = b64encode(key).decode('utf-8')


        with open(msg_save_to, 'w') as enc_msg_file:
            enc_msg_file.write(cipher_txt_encoded)
        
        cls.key['TDES'] = key_encoded

        return msg_save_to


    
    def keys_writer(self, keys, save_to):
        stego_key_name = 'image_keys.json'
        save_to = save_to.split('/')
        save_to.append(stego_key_name)
        save_to = '/'.join(save_to)
        #('KEYS SAVE T0 -> ', save_to)
        with open(save_to, 'w') as keys_file:
            json.dump(keys, keys_file)
            #('keys saved')

    @staticmethod
    def capacityChkLite(img_path, msg_path):

        img = Image.open(img_path)
        img_size = img.size[0] * img.size[1]

        count = 0
        with open(msg_path, 'r') as msg:
            count = len(msg.read()) * 8

        if img_size >= count:
            return True
        else: return False



    def embedding_capacity_chk(self):
        if self.cover_img_size >= len(self.binary_msg):

            
            return True
        else:
            #('capacity check fail')
            return False

    def channel_to_msg_capacity_chk(self, channel, msg):
        if len(channel) > len(msg):
            return True
        else:
            return False


    def channel_binarize(self, channel):
        for val in range(len(channel)):
            channel[val] = format(channel[val], '08b')
        return channel

    def channel_to_int(self, channel):
        for val in range(len(channel)):
            channel[val] = int(channel[val], 2)
        return channel

    def random_pixel_position_selector(self, channel_list):
        random_range = round(len(channel_list)/8)

        random_index = random.randrange(random_range)
        #(f'start = {random_index}')
        return random_index    

    def image_split(self):
        red_channel = self.cover_img.getchannel(channel='R')
        green_channel = self.cover_img.getchannel(channel='G')
        blue_channel = self.cover_img.getchannel(channel='B')

        red_data = red_channel.getdata()
        green_data = green_channel.getdata()
        blue_data = blue_channel.getdata()

        red_list = list()
        green_list = list()
        blue_list = list()

        for pix in red_data:
            red_list.append(pix)

        for pix in green_data:
            green_list.append(pix)

        for pix in blue_data:
            blue_list.append(pix)
        
        return red_list, green_list, blue_list

    def max_channel_identifier(self, red_channel, green_channel, blue_channel):
        red_adder = 0
        green_adder = 0
        blue_adder = 0

        for i in red_channel:
            red_adder += i

        for i in green_channel:
            green_adder += i

        for i in blue_channel:
            blue_adder += i

        vals_dict = {'red': red_adder, 'green': green_adder, 'blue': blue_adder}
        max_val = max(vals_dict.items(), key=operator.itemgetter(1))[0]

        #(f'MAX CHANNEL = {max_val}')

        return max_val

    def second_channel_identifier(self, one_channel, two_channel):
        one_adder = 0
        two_adder = 0

        for i in one_channel:
            one_adder += i

        for i in two_channel:
            two_adder += i

        vals_dict = {'one': one_adder, 'two': two_adder}
        max_val = max(vals_dict.items(), key=operator.itemgetter(1))[0]

        #(f'SECOND MAX = {max_val}')

        return max_val


    def image_channel_merge(self, red_channel, green_channel, blue_channel):
        red = Image.new('L', self.cover_img.size)
        green = Image.new('L', self.cover_img.size)
        blue = Image.new('L', self.cover_img.size)

        red.putdata(red_channel)
        green.putdata(green_channel)
        blue.putdata(blue_channel)

        im1 = Image.merge('RGB', (red, green, blue))

        return im1

    @staticmethod
    def initialSpecCheck(img_path):

        if imghdr.what(img_path) == 'png':
            img = Image.open(img_path)
            if img.mode == 'RGB':
                return True
        return False

            

    def data_division(self, msg):
        p1 = (len(msg) / 100) * 45
        p2 = (len(msg) / 100) * 35
        p3 = (len(msg) / 100) * 20

        p2 = round(p2)
        p3 = round(p3)
        p1 = round(p1)

        msg45 = msg[:p1]
        #(f'\nmsg45 = {msg45}\n')
        #(f'msg45 length = {len(msg45)}')

        msg35 = msg[p1:(p2+p1)]
        #(f'msg35 = {msg35}\n')
        #(f'msg35 length = {len(msg35)}\n')

        msg20 = msg[(p1+p2):]
        #(f'msg20 = {msg20}\n')
        #(f'msg20 length = {len(msg20)}')
        return msg45, msg35, msg20


        
    def stego_img_creator(self, red_channel, green_channel, blue_channel, save_to):
        stego_filename = 'stego_'+self.filename.split('/')[-1]
        save_to = save_to.split('/')
        save_to.append(stego_filename)
        save_to = '/'.join(save_to)
        #('IMG SAVE TO -> ', save_to)

        stego_img_form = self.image_channel_merge(red_channel, green_channel, blue_channel)
        stego_img_form.save(save_to, compress_level=0, optimize=False)
        #('STEGO IMAGE CREATED AND SAVED')



    def embed(self, save_to):
        start_time = time.time()
        if self.embedding_capacity_chk():

            def insert_pixel(binary_msg_bit, pixel):

                pixel = list(pixel)
                try:
                    if ''.join(pixel[:3]) == '111':


                        pixel[5:] = binary_msg_bit[:3]
                        #('done1')
                        return ''.join(pixel)



                    elif ''.join(pixel[:2]) == '11':
                        pixel[6:] = binary_msg_bit[:2]
                        #('done2')
                        return ''.join(pixel)
            
                    else:
                        pixel[-1] = binary_msg_bit[0]
                        return ''.join(pixel)
                except IndexError:
                    pass
                    #('OUT OF INDEX: ORIGIN -> METHOD insert_pixel() CLASS ImageSteg')
            
            def max_embedder(max_channel, sec_max):
                if max_channel == 'red':
                    pix_index = self.random_pixel_position_selector(self.red_channel_list)
                    self.keys['R'] += (pix_index,)
                    if self.channel_to_msg_capacity_chk(self.red_channel_list[pix_index:], msg45):
                        temp_bin_msg_size = 0
                        while temp_bin_msg_size <= len(msg45):

                            if len(msg45[temp_bin_msg_size:]) != 0:
                                red_channel[pix_index]= insert_pixel(msg45[temp_bin_msg_size:], red_channel[pix_index])
                            else:
                                break

                            if red_channel[pix_index][:3] == '111':
                                temp_bin_msg_size += 3
                                #('done1 chk')
                            elif red_channel[pix_index][:2] == '11':
                                temp_bin_msg_size += 2
                                #('done2 chk')
                            else:
                                temp_bin_msg_size += 1

                            pix_index += 1
                        self.keys['R'] += (pix_index,)
                        #(f'last pix_index = {pix_index}')
                    
                    else:
                        pass
                        #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(1)')

                elif max_channel == 'green':
                    pix_index = self.random_pixel_position_selector(self.green_channel_list)
                    self.keys['G'] += (pix_index,)
                    if self.channel_to_msg_capacity_chk(self.green_channel_list[pix_index:], msg45):
                        temp_bin_msg_size = 0
                        while temp_bin_msg_size <= len(msg45):

                            if len(msg45[temp_bin_msg_size:]) != 0:
                                green_channel[pix_index]= insert_pixel(msg45[temp_bin_msg_size:], green_channel[pix_index])
                            else:
                                break

                            if green_channel[pix_index][:3] == '111':
                                temp_bin_msg_size += 3
                            elif green_channel[pix_index][:2] == '11':
                                temp_bin_msg_size += 2
                            else:
                                temp_bin_msg_size += 1
                            

                            pix_index += 1
                        self.keys['G'] += (pix_index,)
                        #(f'last pix_index = {pix_index}')
                    
                    else:
                        pass
                        #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(2)')

                else:
                    pix_index = self.random_pixel_position_selector(self.blue_channel_list)
                    self.keys['B'] += (pix_index,)
                    if self.channel_to_msg_capacity_chk(self.blue_channel_list[pix_index:], msg45):
                        temp_bin_msg_size = 0
                        while temp_bin_msg_size <= len(msg45):

                            if len(msg45[temp_bin_msg_size:]) != 0:
                                blue_channel[pix_index]= insert_pixel(msg45[temp_bin_msg_size:], blue_channel[pix_index])
                            else:
                                break

                            if blue_channel[pix_index][:3] == '111':
                                temp_bin_msg_size += 3
                            elif blue_channel[pix_index][:2] == '11':
                                temp_bin_msg_size += 2
                            else:
                                temp_bin_msg_size += 1

                            pix_index+= 1
                        self.keys['B'] += (pix_index,)
                        #(f'last pix_index = {pix_index}')

                    else:
                        pass
                        #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(3)')

                if sec_max == 'red':
                    pix_index = self.random_pixel_position_selector(self.red_channel_list)
                    self.keys['R'] += (pix_index,)
                    if self.channel_to_msg_capacity_chk(self.red_channel_list[pix_index:], msg35):
                        temp_bin_msg_size = 0
                        while temp_bin_msg_size <= len(msg35):

                            if len(msg35[temp_bin_msg_size:]) != 0:
                                red_channel[pix_index]= insert_pixel(msg35[temp_bin_msg_size:], red_channel[pix_index])
                            else:
                                break

                            if red_channel[pix_index][:3] == '111':
                                temp_bin_msg_size += 3
                            elif red_channel[pix_index][:2] == '11':
                                temp_bin_msg_size += 2
                            else:
                                temp_bin_msg_size += 1



                            pix_index+= 1
                        self.keys['R'] += (pix_index,)
                        #(f'last pix_index = {pix_index}')

                    else:
                        pass
                        #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(4)')
                    
                    if max_channel == 'green':
                        pix_index = self.random_pixel_position_selector(self.blue_channel_list)
                        self.keys['B'] += (pix_index,)
                        if self.channel_to_msg_capacity_chk(self.blue_channel_list[pix_index:], msg20):
                            temp_bin_msg_size = 0
                            while temp_bin_msg_size <= len(msg20):

                                if len(msg20[temp_bin_msg_size:]) != 0:
                                    blue_channel[pix_index] = insert_pixel(msg20[temp_bin_msg_size:], blue_channel[pix_index])
                                else:
                                    break

                                if blue_channel[pix_index][:3] == '111':
                                    temp_bin_msg_size += 3
                                elif blue_channel[pix_index][:2] == '11':
                                    temp_bin_msg_size += 2
                                else:
                                    temp_bin_msg_size += 1



                                pix_index += 1
                            self.keys['B'] += (pix_index,)
                            #(f'last pix_index = {pix_index}')

                        else:
                            pass
                            #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(5)')

                    else:
                        pix_index = self.random_pixel_position_selector(self.green_channel_list)
                        self.keys['G'] += (pix_index,)
                        if self.channel_to_msg_capacity_chk(self.green_channel_list[pix_index:], msg20):
                            temp_bin_msg_size = 0
                            while temp_bin_msg_size <= len(msg20):

                                if len(msg20[temp_bin_msg_size:]) != 0:
                                    green_channel[pix_index] = insert_pixel(msg20[temp_bin_msg_size:], green_channel[pix_index])
                                else:
                                    break

                                if green_channel[pix_index][:3] == '111':
                                    temp_bin_msg_size += 3
                                elif green_channel[pix_index][:2] == '11':
                                    temp_bin_msg_size += 2
                                else:
                                    temp_bin_msg_size += 1


                                pix_index += 1
                            self.keys['G'] += (pix_index,)
                            #(f'last pix_index = {pix_index}')

                        else:
                            pass
                            #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(6)')

                elif sec_max == 'green':
                    pix_index = self.random_pixel_position_selector(self.green_channel_list)
                    self.keys['G'] += (pix_index,)
                    if self.channel_to_msg_capacity_chk(self.green_channel_list[pix_index:], msg35):
                        temp_bin_msg_size = 0
                        while temp_bin_msg_size <= len(msg35):

                            if len(msg35[temp_bin_msg_size:]) != 0:
                                green_channel[pix_index]= insert_pixel(msg35[temp_bin_msg_size:], green_channel[pix_index])
                            else:
                                break

                            if green_channel[pix_index][:3] == '111':
                                temp_bin_msg_size += 3
                            elif green_channel[pix_index][:2] == '11':
                                temp_bin_msg_size += 2
                            else:
                                temp_bin_msg_size += 1


                            pix_index += 1
                        self.keys['G'] += (pix_index,)
                        #(f'last pix_index = {pix_index}')

                    else:
                        pass
                        #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(7)')

                    if max_channel == 'red':
                        pix_index = self.random_pixel_position_selector(self.blue_channel_list)
                        self.keys['B'] += (pix_index,)
                        if self.channel_to_msg_capacity_chk(self.blue_channel_list[pix_index:], msg20):
                            temp_bin_msg_size = 0
                            while temp_bin_msg_size <= len(msg20):

                                if len(msg20[temp_bin_msg_size:]) != 0:
                                    blue_channel[pix_index]= insert_pixel(msg20[temp_bin_msg_size:], blue_channel[pix_index])
                                else:
                                    break

                                if blue_channel[pix_index][:3] == '111':
                                    temp_bin_msg_size += 3
                                elif blue_channel[pix_index][:2] == '11':
                                    temp_bin_msg_size += 2
                                else:
                                    temp_bin_msg_size += 1


                                pix_index += 1
                            self.keys['B'] += (pix_index,)
                            #(f'last pix_index = {pix_index}')

                        else:
                            pass
                            #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(8)')

                    else:
                        pix_index = self.random_pixel_position_selector(self.red_channel_list)
                        self.keys['R'] += (pix_index,)
                        if self.channel_to_msg_capacity_chk(self.red_channel_list[pix_index:], msg20):
                            temp_bin_msg_size = 0
                            while temp_bin_msg_size <= len(msg20):

                                if len(msg20[temp_bin_msg_size:]) != 0:
                                    red_channel[pix_index]= insert_pixel(msg20[temp_bin_msg_size:], red_channel[pix_index])
                                else:
                                    break

                                if red_channel[pix_index][:3] == '111':
                                    temp_bin_msg_size += 3
                                elif red_channel[pix_index][:2] == '11':
                                    temp_bin_msg_size += 2
                                else:
                                    temp_bin_msg_size += 1


                                pix_index+= 1
                            self.keys['R'] += (pix_index,)
                            #(f'last pix_index = {pix_index}')

                        else:
                            pass
                            #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(9)')

                else:
                    pix_index = self.random_pixel_position_selector(self.blue_channel_list)
                    self.keys['B'] += (pix_index,)
                    if self.channel_to_msg_capacity_chk(self.blue_channel_list[pix_index:], msg35):
                        temp_bin_msg_size = 0

                        while temp_bin_msg_size <= len(msg35):

                            if len(msg35[temp_bin_msg_size:]) != 0:
                                blue_channel[pix_index]= insert_pixel(msg35[temp_bin_msg_size:], blue_channel[pix_index])
                            else:
                                break

                            if blue_channel[pix_index][:3] == '111':
                                temp_bin_msg_size += 3
                            elif blue_channel[pix_index][:2] == '11':
                                temp_bin_msg_size += 2
                            else:
                                temp_bin_msg_size += 1

                            pix_index+= 1
                        self.keys['B'] += (pix_index,)
                        #(f'last pix_index = {pix_index}')

                    else:
                        pass
                        #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(10)')

                    if max_channel == 'red':
                        pix_index = self.random_pixel_position_selector(self.green_channel_list)
                        self.keys['G'] += (pix_index,)
                        if self.channel_to_msg_capacity_chk(self.green_channel_list[pix_index:], msg20):

                            temp_bin_msg_size = 0
                            while temp_bin_msg_size <= len(msg20):

                                if len(msg20[temp_bin_msg_size:]) != 0:
                                    green_channel[pix_index]= insert_pixel(msg20[temp_bin_msg_size:], green_channel[pix_index])
                                else:
                                    break

                                if green_channel[pix_index][:3] == '111':
                                    temp_bin_msg_size += 3
                                elif green_channel[pix_index][:2] == '11':
                                    temp_bin_msg_size += 2
                                else:
                                    temp_bin_msg_size += 1



                                pix_index += 1
                            self.keys['G'] += (pix_index,)
                            #(f'last pix_index = {pix_index}')
                        else:
                            pass
                            #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(11)')
                    
                    else:
                        pix_index = self.random_pixel_position_selector(self.red_channel_list)
                        self.keys['R'] += (pix_index,)
                        if self.channel_to_msg_capacity_chk(self.red_channel_list[pix_index:], msg20):
                            temp_bin_msg_size = 0
                            while temp_bin_msg_size <= len(msg20):

                                if len(msg20[temp_bin_msg_size:]) != 0:
                                    red_channel[pix_index]= insert_pixel(msg20[temp_bin_msg_size:], red_channel[pix_index])
                                else:
                                    break

                                if red_channel[pix_index][:3] == '111':
                                    temp_bin_msg_size += 3
                                elif red_channel[pix_index][:2] == '11':
                                    temp_bin_msg_size += 2
                                else:
                                    temp_bin_msg_size += 1


                                pix_index += 1
                            self.keys['R'] += (pix_index,)
                            #(f'last pix_index = {pix_index}')

                        else:
                            pass
                            #('CHANNEL TO MESSAGE CAPACITY FAIL max_embedder(12)')


            msg45, msg35, msg20 = self.data_division(self.binary_msg)

            
            red_channel, green_channel, blue_channel = self.image_split()
            max_channel = self.max_channel_identifier(red_channel, green_channel, blue_channel)
            if max_channel == 'red':
                sec_max = self.second_channel_identifier(green_channel, blue_channel)

                if sec_max == 'one':
                    sec_max_channel = 'green'

                else:
                    sec_max_channel = 'blue'


            elif max_channel == 'green':
                sec_max = self.second_channel_identifier(red_channel, blue_channel)

                if sec_max == 'one':
                    sec_max_channel = 'red'
                else:
                    sec_max_channel = 'blue'
            
            else:
                sec_max = self.second_channel_identifier(red_channel, green_channel)

                if sec_max == 'one':
                    sec_max_channel = 'red'
                else:
                    sec_max_channel = 'green'

            red_channel = self.channel_binarize(red_channel)

            green_channel = self.channel_binarize(green_channel)
            blue_channel = self.channel_binarize(blue_channel)

            max_embedder(max_channel, sec_max_channel)



            red_channel = self.channel_to_int(red_channel)
            green_channel = self.channel_to_int(green_channel)
            blue_channel = self.channel_to_int(blue_channel)
            self.stego_img_creator(red_channel, green_channel, blue_channel, save_to)


            



            #(self.keys)
            self.keys_writer(self.keys, save_to)



            self.file.close()

            #('Time to execute = {} seconds'.format(time.time() - start_time))

            return True
        else:
            return False


    @staticmethod
    def deEmbedNDecrypt(img_path, keys_file, msg_save_path):

        msg_name = 'message_from_image.txt'
        msg_save_path = msg_save_path.split('/')
        msg_save_path.append(msg_name)
        msg_save_path = '/'.join(msg_save_path)

        img = Image.open(img_path)


        with open(keys_file, 'r') as keys_file:
            keys = json.load(keys_file)
        
        red_ch = img.getchannel(channel='R')
        green_ch = img.getchannel(channel='G')
        blue_ch = img.getchannel(channel='B')

        red_ch_list = list(red_ch.getdata())
        red_big_val = 0
        green_big_val = 0
        blue_big_val = 0
        green_ch_list = list(green_ch.getdata())
        blue_ch_list = list(blue_ch.getdata())

        for i in range(len(red_ch_list)):
            red_big_val += red_ch_list[i]

        for i in range(len(green_ch_list)):
            green_big_val += green_ch_list[i]
        
        for i in range(len(blue_ch_list)):
            blue_big_val += blue_ch_list[i]

        channel_to_list_dict = {
            'R': red_ch_list,
            'G': green_ch_list,
            'B': blue_ch_list
        }


        channel_vals_dict = {'R': red_big_val, 'G': green_big_val, 'B': blue_big_val}

        word = ''
        msg_lsb = ''
        bits = ''

        for _ in range(3):
            channel = max(channel_vals_dict.items(), key=operator.itemgetter(1))[0]
            #('max = ',channel)


            st_index, en_index = keys[channel]

            msg_list = channel_to_list_dict[channel][st_index:en_index]

            for item in range(len(msg_list)):
                bits += format(msg_list[item], '08b')
                #("bits = ", bits)

                if bits[:3] == '111':
                    msg_lsb += bits[5:]
                elif bits[:2] == '11':
                    msg_lsb += bits[6:]
                else:
                    msg_lsb += bits[-1]


                if len(msg_lsb) >= 8:
                    #("True")
                    #(msg_lsb[:8])
                    msg_bin_word = int(msg_lsb[:8], 2)
                    word += chr(msg_bin_word)
                    msg_lsb = msg_lsb[8:]

                bits = ''


            del channel_vals_dict[channel]

        #(word)


        tdes_key = keys['TDES']
        tdes_key_decode = b64decode(tdes_key)


        word_plain_str = decryptTripleDES(word, tdes_key_decode)

        with open(msg_save_path, 'w') as dcp_msg:
            dcp_msg.write(word_plain_str)

        #('DECRYPTED MESSAGE SAVED')


    
                
