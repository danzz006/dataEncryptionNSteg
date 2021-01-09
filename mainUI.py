# import pkg_resources.py2_warn

from imageSteg import ImageSteg
from audioSteg import AudioSteg
from videoSteg import VideoSteg
import json
import os

from PIL import Image, ImageTk

import tkinter as tk
from tkinter import font as tkfont
from tkinter import filedialog
from tkinter import ttk
from ttkthemes import themed_tk as thk
from tkinter import PhotoImage
from time import sleep


class StegoApp(thk.ThemedTk):

    def __init__(self, *args, **kwargs):
        thk.ThemedTk.__init__(self, *args, **kwargs)
        self.get_themes()
        self.set_theme('breeze')
        self.geometry('700x500')
        self.title('Stegonic  v1.0')
        self.resizable(0,0)

        self.title_font = tkfont.Font(family='futura', size=25)

        container = tk.Frame(self)
        container.pack(side='top', fill='both', expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (StartPage, EncryptionPage, DecryptionPage):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            frame.grid(row=0, column=0, sticky='nsew')

        self.show_frame('StartPage')

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()


class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        label = tk.Label(self, background='black', fg='white', text = 'Welcome To Stegonic, a Privacy Solution', font=('futura', 25))
        label.pack(side='top', fill='x', pady=10)

        img1 = Image.open('icons/enc.png')
        img2 = Image.open('icons/dec.png')

        self.icon1 = ImageTk.PhotoImage(img1)
        self.icon2 = ImageTk.PhotoImage(img2)
        btn_enc_frame = tk.Button(self, text='Encrypt & Embed', font=('helvetica', 25, 'italic'), image=self.icon1, compound='left', bg='#24258E', fg='white', relief='raised', padx=119, command=lambda: controller.show_frame('EncryptionPage'))

        btn_enc_frame.place(x=0, y=145) #150 145
        btn_dec_frame = tk.Button(self, text='Deembed & Decrypt', font=('helvetica', 25, 'italic'), image=self.icon2, compound='left', bg='#24258E', fg='white', relief='raised', padx=119, command=lambda: controller.show_frame('DecryptionPage'))
        btn_dec_frame.place(x=0, y=300) #150 300


class EncryptionPage(tk.Frame):

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.medium_path = ''
        self.msg_path = ''
        self.medium_type = ''
        self.save_to_path = ''

        img1 = Image.open('icons/folder.png')
        img2 = Image.open('icons/back.png')
        img3 = Image.open('icons/process.png')
        img4 = Image.open('icons/directory.png')

        self.icon1 = ImageTk.PhotoImage(img1)
        self.icon2 = ImageTk.PhotoImage(img2)
        self.icon3 = ImageTk.PhotoImage(img3)
        self.icon4 = ImageTk.PhotoImage(img4)



        label = tk.Label(self, bg='black', fg='white', text = 'Encryption & Embedding', font = controller.title_font)
        label.pack(side='top', fill='x', pady=10)

        label_med_msg = tk.Label(self, text='Enter path to medium')
        label_med_msg.place(x=29, y=80)
        

        self.input_medium_field = ttk.Entry(self, width=90)
        self.input_medium_field.place(x=30, y=100)


        btn_med = ttk.Button(self, text='Browse', image=self.icon1, compound='left', command=lambda: self.fileDialogue(self.input_medium_field))
        btn_med.place(x=552, y=135)

        label_msg_path = tk.Label(self, text='Enter path to message')
        label_msg_path.place(x=29, y=180)

        self.input_msg_field = ttk.Entry(self, width=90)
        self.input_msg_field.place(x=30, y=200)


        btn_msg = ttk.Button(self, text='Browse', image=self.icon1, compound='left', command=lambda: self.fileDialogue(self.input_msg_field))
        btn_msg.place(x=552, y=235)

        label_save_path = tk.Label(self, text='Enter path to save results')
        label_save_path.place(x=29,y=280)

        self.input_save_to_field = ttk.Entry(self, width=90)
        self.input_save_to_field.place(x=30, y=300)


        btn_save = ttk.Button(self, text='Browse', image=self.icon4, compound='left', command=lambda: self.dirDialogue(self.input_save_to_field))
        btn_save.place(x=552, y=335)

        btn_embed = ttk.Button(self, text='Launch', image=self.icon3, compound='left', command=self.stegoInitiator)
        btn_embed.place(x=290, y=385)


        btn = ttk.Button(self, text='Back', image=self.icon2, compound='left', command=lambda: controller.show_frame('StartPage'))
        btn.place(x=570, y=450)



    def dirDialogue(self, obj):
        self.dir_name = filedialog.askdirectory()
        obj.delete(0,"end")
        obj.insert(0,self.dir_name)


    def fileDialogue(self, obj):
        self.file_name = filedialog.askopenfilename(initialdir='/', title='Select File', filetype=(("AVI", ".avi"), ("MP4", ".mp4"), ("JSON", ".json"), ("WAV", ".wav"), ("PNG", ".png"),("TEXT",".txt"),('All Files', "*.*")))
        obj.delete(0,"end")
        obj.insert(0, self.file_name)

    def msgCheckTrigger(self, msg_path):
        if self.medium_path != '':
            if msg_path != '':
                if msg_path[-3:] == 'txt':
                    self.msg_path = msg_path

                    try:
                        with open(msg_path, 'r') as msg_file:
                            if len(msg_file.read()) < 1:
                                #('FILE EMPTY -> ui.py -> EncryptionPage -> msgCheckTrigger()')
                                label_msg_fail = tk.Label(self, fg='red', text='Message file empty                        ')
                                label_msg_fail.place(x=30, y=233)
                                return False
                            else:
                                # self.stegoInitiator()
                                label_msg_pass = tk.Label(self, fg='green', text='Message file status ok ✓                           ')
                                label_msg_pass.place(x=30, y=233)
                                # self.msg_path = r'{}'.format(msg_path)
                                return True

                    except FileNotFoundError:
                        #('MESSAGE FILE NOT FOUND -> ui.py -> EncryptionPage -> msgCheckTrigger()')
                        label_msg_pass = tk.Label(self, fg='red', text='Message file not found         ')
                        label_msg_pass.place(x=30, y=233)
                        return False

                else:
                    #('MESSAGE FILE FORMAT ERROR -> ui.py -> EncryptionPage -> msgCheckTrigger()')
                    label_msg_pass = tk.Label(self, fg='red', text='Message file invalid format              ')
                    label_msg_pass.place(x=30, y=233)
                    return False
                
            else:
                #('MESSAGE PATH NOT PROVIDED -> ui.py -> EncryptionPage -> msgCheckTrigger()')
                label_msg_pass = tk.Label(self, fg='red', text='Message file not provided                                ')
                label_msg_pass.place(x=30, y=233)
                return False

        else:
            #('MEDIUM PATH NOT PROVIDED -> ui.py -> EncryptionPage -> msgCheckTrigger()')
            label_msg_pass = tk.Label(self, fg='red', text='Medium path not provided          ')
            label_msg_pass.place(x=30, y=233)
            return False



    def stegoInitiator(self):

        med_path = self.input_medium_field.get()
        msg_path = self.input_msg_field.get()

        self.save_to_path = self.input_save_to_field.get()

        if med_path == '' and msg_path == '' and self.save_to_path == '':
            self.label_msg_no_item = tk.Label(self, fg='red', text='Please provide required items                                  ')
            self.label_msg_no_item.place(x=29, y=333)
            label_cleaner = tk.Label(self, text='                                                                        ')
            label_cleaner.place(x=29,y=355)
            return 

        if self.save_to_path == '':
            self.label_msg_no_item = tk.Label(self, fg='red', text='Please provide path to destination directory                    ')
            self.label_msg_no_item.place(x=29, y=333)
            label_cleaner = tk.Label(self, text='                                                                        ')
            label_cleaner.place(x=29,y=355)
            return


        if self.mediumCheckTrigger(med_path):
            if self.msgCheckTrigger(msg_path):

                if not os.path.isdir(self.save_to_path):
                    #('DIRECTORY PATH DOES NOT LEAD TO DIRECTORY -> ui.py -> EncryptionPage -> stegoInitiator')
                    self.label_msg_no_item = tk.Label(self, fg='red', text='Path does not lead to existing directory                    ')
                    self.label_msg_no_item.place(x=29, y=333)
                    label_cleaner = tk.Label(self, text='                                                                        ')
                    label_cleaner.place(x=29,y=355)
                    return
                else:
                    pass

                if self.medium_type == 'img':
                    if not ImageSteg.capacityChkLite(self.medium_path, self.msg_path):
                        label_cap_exceeded = tk.Label(self, fg='red', text='Provided medium does not have enough embedding capacity                          ')
                        label_cap_exceeded.place(x=29,y=133)
                        #('CAPACITY CHECK LITE FAILED -> stegInitiator() -> mainUI')
                        return

                    enc_msg_file_path = ImageSteg.encrypter(ImageSteg, self.msg_path, 'messageImageEncrypted.txt')
                    #('ENCRYPTED MESSAGE FILE CREATED')

                    steg_img_obj = ImageSteg(self.medium_path, enc_msg_file_path)
                    #('STEGO CLASS INITIALIZED')


                    if steg_img_obj.embed(self.save_to_path):
                        pass
                        #('STEGO OBJECT CREATED SUCCESSFULLY')
                    else:
                        label_cap_exceeded = tk.Label(self, fg='red', text='Provided medium does not have enough embedding capacity                          ')
                        label_cap_exceeded.place(x=29,y=133)
                        return 
                    try:
                        self.label_msg_no_item.destroy()
                    except AttributeError:
                        pass
                    finally:
                        label_cleaner = tk.Label(self, text='                                                                                            ')
                        label_cleaner.place(x=29,y=333)

                    label_msg_pass = tk.Label(self, fg='green', text='Stego medium and keys file created and saved ✓                          ')
                    label_msg_pass.place(x=29, y=355)

                elif self.medium_type == 'aud':
                    AudioSteg.encryptMsg(AudioSteg, self.msg_path)
                    #('ENCRYPTED MESSAGE SAVED AUDIO')
                    steg_aud_obj = AudioSteg(self.medium_path, 'encrypted_msg_audio.txt')

                    if not steg_aud_obj.embedder(self.save_to_path):
                        label_cap_exceeded = tk.Label(self, fg='red', text='Provided medium does not have enough embedding capacity                          ')
                        label_cap_exceeded.place(x=29,y=133)
                        return 

                    #('STEGO AUDIO CREATED SUCCESSFULLY')
                    try:
                        self.label_msg_no_item.destroy()
                    except AttributeError:
                        pass
                    finally:
                        label_cleaner = tk.Label(self, text='                                                                                            ')
                        label_cleaner.place(x=29,y=333)

                    label_msg_pass = tk.Label(self, fg='green', text='Stego medium and keys file created and saved ✓                              ')
                    label_msg_pass.place(x=29, y=355)

                elif self.medium_type == 'vid':
                    vid_obj = VideoSteg(self.medium_path, self.msg_path)
                    vid_obj.embed(self.save_to_path)
                    #('VIDEO INDEXED SUCCESSFULLY')
                    try:
                        self.label_msg_no_item.destroy()
                    except AttributeError:
                        pass
                    finally:
                        label_cleaner = tk.Label(self, text='                                                                                            ')
                        label_cleaner.place(x=29,y=333)

                    label_msg_pass = tk.Label(self, fg='green', text='Keys file created and saved ✓                                   ')
                    label_msg_pass.place(x=29, y=355)


                else:
                    #('NON SUPPORTED FORMATE PROVIDED -> ui.py -> EncryptionPage -> stegoInitiator')
                    try:
                        self.label_msg_no_item.destroy()
                    except AttributeError:
                        pass
                    finally:
                        label_cleaner = tk.Label(self, text='                                                                                            ')
                        label_cleaner.place(x=29,y=333)

                    label_msg_pass = tk.Label(self, fg='red', text='Please provide a supported format                          ')
                    label_msg_pass.place(x=29, y=355)



    
    def imageTrigger(self, med_path):
        self.medium_path = r'{}'.format(med_path) 
        
        try:
            if ImageSteg.initialSpecCheck(self.medium_path):
                #('SPECS PASSED')
                label_spec_pass = tk.Label(self, fg='green', text="Format met specifications ✓                                              ")
                label_spec_pass.place(x=29, y=133)
                return True
            else:
                self.medium_type = ''
                #('SPECS FAILED ui.py -> EncryptionPage -> imageCheckTrigger()')
                label_spec_pass = tk.Label(self, fg='red', text="Format specifications not supported                                        ")
                label_spec_pass.place(x=29, y=133)
                return False
    
        except FileNotFoundError:
            #('File not found')  
            label_spec_fail = tk.Label(self, fg='red', text="File not found                                                                ")
            label_spec_fail.place(x=29, y=133)
            return False


    def audioTrigger(self, med_path):
        self.medium_path = r'{}'.format(med_path)
        try:
            if AudioSteg.is_form_correct(AudioSteg, self.medium_path):
                #('SPECS PASSED')
                label_spec_pass = tk.Label(self, fg='green', text="Format met specifications ✓                                              ")
                label_spec_pass.place(x=29, y=133)
                return True
            else:
                self.medium_type = ''
                #('SPECS FAILED ui.py -> EncryptionPage -> audioTrigger()')
                label_spec_pass = tk.Label(self,fg='red', text="Format specifications not supported                                              ")
                label_spec_pass.place(x=29, y=133)
                return False
        
        except FileNotFoundError:
            #('File not found')  
            label_spec_fail = tk.Label(self, fg='red', text="File not found                                              ")
            label_spec_fail.place(x=29, y=133)
            return False
        except AttributeError:
            tk.messagebox.showerror("Error", "Audio specification attribute error refer documentation for more detail")


    def videoTrigger(self, med_path):
        self.medium_path = r'{}'.format(med_path)

        try:
            vid_obj = VideoSteg(med_path)
            if VideoSteg.initialSpecCheck(vid_obj, med_path):
                #('SPECS PASSED')
                label_spec_pass = tk.Label(self, text="Format met specifications ✓                                              ")
                label_spec_pass.place(x=29, y=133)
                return True
            else:
                self.medium_type = ''
                #('SPECS FAILED ui.py -> EncryptionPage -> videoTrigger()')
                label_spec_pass = tk.Label(self, text="Format specifications not supported                                              ")
                label_spec_pass.place(x=29, y=133)
                return False

        except FileNotFoundError:
            self.medium_path = ''
            #('File not found')  
            label_spec_fail = tk.Label(self, text="File not found                                              ")
            label_spec_fail.place(x=29, y=133)
            return False


    
    def mediumCheckTrigger(self, med_path):
        if med_path != '':
            if med_path[-3:] == 'png':
                self.medium_type = 'img'
                return self.imageTrigger(med_path)

            elif med_path[-3:] == 'wav':
                self.medium_type = 'aud'
                return self.audioTrigger(med_path)

            elif med_path[-3:] == 'avi' or med_path[-3:] == 'mp4':
                self.medium_type = 'vid'
                return self.videoTrigger(med_path)

            
            else:
                self.medium_path = r'{}'.format(med_path)
                #('INVALID FORMAT')
                label_spec_fail = tk.Label(self, fg='red', text="Format specifications not supported                           ")
                label_spec_fail.place(x=29, y=133)
                return False

        else:
            #('NO PATH PROVIDED')
            label_spec_fail = tk.Label(self, fg='red', text="No path provided                               ")
            label_spec_fail.place(x=29, y=133)
            return False




class DecryptionPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.medium_path = ''
        self.medium_type = ''
        self.key_file_path = ''
        self.save_to_path = ''
        label = tk.Label(self, fg='white', bg='black', text='De-embedding & Decryption', font=controller.title_font)
        label.pack(side='top', fill='x', pady=10)

        img1 = Image.open('icons/folder.png')
        img2 = Image.open('icons/back.png')
        img3 = Image.open('icons/land.png')
        img4 = Image.open('icons/directory.png')

        self.icon1 = ImageTk.PhotoImage(img1)
        self.icon2 = ImageTk.PhotoImage(img2)
        self.icon3 = ImageTk.PhotoImage(img3)
        self.icon4 = ImageTk.PhotoImage(img4)




        label_steg_msg = tk.Label(self, text='Enter path to stego medium')
        label_steg_msg.place(x=29, y=80)

        input_steg_path = ttk.Entry(self, width=90)
        input_steg_path.place(x=30, y=100)

        btn_steg = ttk.Button(self, text='Browse', image=self.icon1, compound='left', command=lambda: self.fileDialogue(input_steg_path))
        btn_steg.place(x=552, y=135)


        label_steg_key = tk.Label(self, text='Enter path to key file')
        label_steg_key.place(x=29, y=180)

        self.input_steg_key = ttk.Entry(self, width=90)
        self.input_steg_key.place(x=30, y=200)

        btn_key = ttk.Button(self, text='Browse',image=self.icon1, compound='left', command=lambda: self.fileDialogue(self.input_steg_key))
        btn_key.place(x=552, y=235)

        label_save_path = tk.Label(self, text='Enter path to save extracted message')
        label_save_path.place(x=29,y=280)

        self.input_save_to_field = ttk.Entry(self, width=90)
        self.input_save_to_field.place(x=30, y=300)


        btn_save = ttk.Button(self, text='Browse', image=self.icon4, compound='left', command=lambda: self.dirDialogue(self.input_save_to_field))
        btn_save.place(x=552, y=335)


        btn = ttk.Button(self, text='Back', image=self.icon2, compound='left', command=lambda: controller.show_frame('StartPage'))
        btn.place(x=570, y=450)

        btn_embed = ttk.Button(self, text='Receive', image=self.icon3, compound='left', command=lambda: self.destegInitiator(input_steg_path.get()))
        btn_embed.place(x=290, y=385)

    
    def dirDialogue(self, obj):
        self.dir_name = filedialog.askdirectory()
        obj.delete(0,"end")
        obj.insert(0,self.dir_name)


    def fileDialogue(self, obj):
        self.file_name = filedialog.askopenfilename(initialdir='/', title='Select File', filetype=(("AVI", ".avi"), ("MP4", ".mp4"), ("JSON", ".json"), ("WAV", ".wav"), ("PNG", ".png"),("TEXT",".txt"),('All Files', "*.*")))
        obj.delete(0,"end")
        obj.insert(0, self.file_name)

    def imageTrigger(self, med_path):
        self.medium_path = '{}'.format(med_path) 
        
        try:
            if ImageSteg.initialSpecCheck(self.medium_path):
                #('SPECS PASSED')
                label_spec_pass = tk.Label(self, fg='green', text="Format met specifications ✓                                                 ")
                label_spec_pass.place(x=29, y=133)
                return True
            else:
                self.medium_type = ''
                #('SPECS FAILED ui.py -> EncryptionPage -> imageCheckTrigger()')
                label_spec_pass = tk.Label(self, fg='red', text="Format specifications not supported                       ")
                label_spec_pass.place(x=29, y=133)
                return False
    
        except FileNotFoundError:
            #('File not found')  
            label_spec_fail = tk.Label(self, fg='red', text="File not found                                                                                    ")
            label_spec_fail.place(x=29, y=133)
            return False

        except Exception as e:
            label_spec_pass = tk.Label(self, fg='red', text="Format specifications not supported                                                                               ")
            label_spec_pass.place(x=29, y=133)
            return False


    def audioTrigger(self, med_path):
        self.medium_path = '{}'.format(med_path)
        try:
            if AudioSteg.is_form_correct(AudioSteg, self.medium_path):
                #('SPECS PASSED')
                label_spec_pass = tk.Label(self, fg='green', text="Format met specifications ✓                                              ")
                label_spec_pass.place(x=29, y=133)
                return True
            else:
                self.medium_type = ''
                #('SPECS FAILED ui.py -> EncryptionPage -> audioTrigger()')
                label_spec_pass = tk.Label(self, fg='red', text="Format specifications not supported                       ")
                label_spec_pass.place(x=29, y=133)
                return False
        
        except FileNotFoundError:
            #('File not found')  
            label_spec_fail = tk.Label(self, fg='red', text="File not found                                      ")
            label_spec_fail.place(x=29, y=133)
            return False

        except Exception as e:
            label_spec_pass = tk.Label(self, fg='red', text="Format specifications not supported                       ")
            label_spec_pass.place(x=29, y=133)
            return False


    def videoTrigger(self, med_path):
        self.medium_path = '{}'.format(med_path)
        try:
            vid_obj = VideoSteg(med_path)
            if VideoSteg.initialSpecCheck(vid_obj, med_path):
                #('SPECS PASSED')
                label_spec_pass = tk.Label(self, fg='green', text="Format met specifications ✓                                               ")
                label_spec_pass.place(x=29, y=133)
                return True
            else:
                self.medium_type = ''
                #('SPECS FAILED ui.py -> EncryptionPage -> videoTrigger()')
                label_spec_pass = tk.Label(self, fg='red', text="Format specifications not supported                             ")
                label_spec_pass.place(x=29, y=133)
                return False

        except FileNotFoundError:
            #('File not found')  
            label_spec_fail = tk.Label(self, fg='red', text="File not found                                             ")
            label_spec_fail.place(x=29, y=133)
            return False

        except Exception as e:
            label_spec_pass = tk.Label(self, fg='red', text="Format specifications not supported                             ")
            label_spec_pass.place(x=29, y=133)
            return False


    def destegInitiator(self, med_path):

        self.save_to_path = self.input_save_to_field.get()
        key_file_path = self.input_steg_key.get()

        if med_path == '' and key_file_path == '' and self.save_to_path == '':
            self.label_msg_no_item = tk.Label(self, fg='red', text='Please provide required items                                  ')
            self.label_msg_no_item.place(x=29, y=333)
            label_cleaner = tk.Label(self, text='                                                                        ')
            label_cleaner.place(x=29,y=355)
            return        


        if self.save_to_path == '':
            self.label_msg_no_dir = tk.Label(self, fg='red', text='Please provide path to destination directory                             ')
            self.label_msg_no_dir.place(x=29, y=333)
            label_cleaner = tk.Label(self, text='                                                          ')
            label_cleaner.place(x=29,y=355)
            return




        if self.mediumCheckTrigger(med_path):
            if self.keyFileCheck(key_file_path):

                if not os.path.isdir(self.save_to_path):
                    self.label_msg_no_dir = tk.Label(self, fg='red', text='Path does not lead to existing directory                             ')
                    self.label_msg_no_dir.place(x=29, y=333)
                    label_cleaner = tk.Label(self, text='                                                          ')
                    label_cleaner.place(x=29,y=355)
                    return
                else:
                    pass
            
                if self.medium_type == 'aud':
                    try:
                        AudioSteg.de_embed(self.medium_path, self.key_file_path, self.save_to_path)
                    #('AUDIO CLASS METHOD CALLED')
                        label_msg_pass = tk.Label(self, fg='green', text='Secret message retriveved and saved                             ')
                        label_msg_pass.place(x=29, y=355)
                    except Exception as e:
                        label_msg_pass = tk.Label(self, fg='red', text='Error with content encoding                                                            ')
                        label_msg_pass.place(x=30, y=232)
                    try:
                        self.label_msg_no_dir.destroy()
                    except AttributeError:
                        pass
                    finally:
                        label_cleaner = tk.Label(self, text='                                                                                            ')
                        label_cleaner.place(x=29,y=333)
                    #('RETRIVAL PROCESS SUCCESSFUL')

                elif self.medium_type == 'img':
                    try:
                        ImageSteg.deEmbedNDecrypt(self.medium_path, self.key_file_path, self.save_to_path)
                    #('IMAGE CLASS METHOD CALLED')
                        label_msg_pass = tk.Label(self, fg='green', text='Secret message retriveved and saved                             ')
                        label_msg_pass.place(x=29, y=355)
                    except Exception as e:
                        label_msg_pass = tk.Label(self, fg='red', text='Error with content encoding                                               ')
                        label_msg_pass.place(x=30, y=232)
                    try:
                        self.label_msg_no_dir.destroy()
                    except AttributeError:
                        pass
                    finally:
                        label_cleaner = tk.Label(self, text='                                                                                            ')
                        label_cleaner.place(x=29,y=333)
                    #('RETRIVAL PROCESS SUCCESSFUL')

                elif self.medium_type == 'vid':
                    try:
                        VideoSteg.alternateDeEmbedding(self.key_file_path, self.medium_path, save_to_file_path=self.save_to_path)
                    #('VIDEO STATIC DEEMBED CALLED')
                        label_msg_pass = tk.Label(self, fg='green', text='Secret message retriveved and saved                             ')
                        label_msg_pass.place(x=29, y=355)
                    except:
                        label_msg_pass = tk.Label(self, fg='red', text='Error with content encoding                                                        ')
                        label_msg_pass.place(x=30, y=232)
                    try:
                        self.label_msg_no_dir.destroy()
                    except AttributeError:
                        pass
                    finally:
                        label_cleaner = tk.Label(self, text='                                                                                            ')
                        label_cleaner.place(x=29,y=333)
                    #('RETRIVAL PROCESS SUCCESSFUL')


                else:
                    #('INVALID MEDIUM TYPE -> deStegInitiator() -> Decryption page mainUI.py')
                    label_msg_pass = tk.Label(self, fg='red', text='Invalid format provided                               ')
                    label_msg_pass.place(x=29, y=355)
                    try:
                        self.label_msg_no_dir.destroy()
                    except AttributeError:
                        pass
                    finally:
                        label_cleaner = tk.Label(self, text='                                                                                            ')
                        label_cleaner.place(x=29,y=333)

            else:
                pass
                #('KEY FILE CHECK FAILED -> deStegInitiator() -> mainUI.py')


    
    def mediumCheckTrigger(self, med_path):
        if med_path != '':
            if med_path[-3:] == 'png':
                self.medium_type = 'img'
                return self.imageTrigger(med_path)

            elif med_path[-3:] == 'wav':
                self.medium_type = 'aud'
                return self.audioTrigger(med_path)
            
            elif med_path[-3:] in ['avi', 'mp4']:
                self.medium_type = 'vid'
                return self.videoTrigger(med_path)

            
            else:
                #('INVALID FORMAT')
                label_spec_fail = tk.Label(self, fg='red', text="Format specifications not supported              ")
                label_spec_fail.place(x=29, y=133)
                return False

        else:
            #('NO PATH PROVIDED')
            label_spec_fail = tk.Label(self, fg='red', text="No path to stego object provided                           ")
            label_spec_fail.place(x=29, y=133)
            return False



    def keyFileCheck(self, key_file_path):
        if self.medium_path != '':
            if key_file_path != '':
                if key_file_path[-4:] == 'json':
                    if self.medium_type == 'img':
                        try:
                            with open(key_file_path, 'r') as key_file:
                                if len(key_file.read()) > 0:
                                    key_file.seek(0)
                                    key_data = json.load(key_file)
                                    if 'R' and 'G' and 'B' in key_data:
                                        for key in ('R', 'G', 'B'):
                                            accurate_key_data = False
                                            if key in key_data:
                                                if len(key_data[key]) == 2:
                                                    accurate_key_data = True
                                        if accurate_key_data:            
                                            if key_data['TDES'] != '':
                                                #('KEY FILE STATUS OK')
                                                label_msg_pass = tk.Label(self, fg='green', text='key file status ok ✓                                                                     ')
                                                label_msg_pass.place(x=30, y=232)
                                        
                                                self.key_file_path = key_file_path
                                             
                                                return True

                                            else:
                                                #('ERROR WITH KEY FILE -> ui.py -> DecryptionPage -> keyFileCheck()')
                                                label_msg_pass = tk.Label(self, fg='red', text='Error with key file contents                               ')
                                                label_msg_pass.place(x=30, y=232)
                                                return False
                                        elif not accurate_key_data:
                                            #('ERROR WITH KEY FILE -> ui.py -> DecryptionPage -> keyFileCheck()')
                                            label_msg_pass = tk.Label(self, fg='red', text='Error with key file contents                               ')
                                            label_msg_pass.place(x=30, y=232)
                                            return False
                                    else:
                                        #('KEY NOT COMPATIBLE WITH THIS STEGO OBJECT')
                                        label_msg_pass = tk.Label(self, fg='red', text='Provided key file not compatible with this stego medium                                 ')
                                        label_msg_pass.place(x=30, y=232)
                                        return False

                                else:
                                    #('key FILE EMPTY -> ui.py -> DecryptionPage -> keyFileCheck()')
                                    label_msg_pass = tk.Label(self, fg='red', text='Empty key file provided                                  ')
                                    label_msg_pass.place(x=30, y=232)
                                    return False

                        except FileNotFoundError:
                            #('FILE NOT FOUND -> ui.py -> DecryptionPage -> keyFileCheck()')
                            label_msg_pass = tk.Label(self, fg='red', text='Provided file does not exist                                  ')
                            label_msg_pass.place(x=30, y=232)
                            return False
                    elif self.medium_type == 'aud':
                        try:
                            with open(key_file_path, 'r') as key_file:
                                    if len(key_file.read()) > 0:
                                        key_file.seek(0)
                                        key_data = json.load(key_file)
                                        if 'start' in key_data:
                                            if 'end' in key_data:
                                                if 'TDES' in key_data:
                                                    if key_data['start'] != None:
                                                        if key_data['end'] != None:
                                                            if key_data['TDES'] != None:
                                                                self.key_file_path = key_file_path
                                                                #('KEY FILE CHECK PASSED')
                                                                label_msg_pass = tk.Label(self, fg='green', text='key file status ok ✓                                                                     ')
                                                                label_msg_pass.place(x=30, y=232)
                                                                return True
                                        else:
                                            #('KEY NOT COMPATIBLE WITH THIS STEGO OBJECT')
                                            label_msg_pass = tk.Label(self, fg='red', text='Provided key file not compatible with this stego medium                                 ')
                                            label_msg_pass.place(x=30, y=232)
                                            return False
                                    else:
                                        #('ERROR WITH KEY FILE -> ui.py -> DecryptionPage -> keyFileCheck()')
                                        label_msg_pass = tk.Label(self, fg='red', text='Error with key file contents                               ')
                                        label_msg_pass.place(x=30, y=232)
                                        return False

                        except FileNotFoundError:
                            #('ERROR WITH KEY FILE -> ui.py -> DecryptionPage -> keyFileCheck()')
                            label_msg_pass = tk.Label(self, fg='red', text='Provided file does not exist                                     ')
                            label_msg_pass.place(x=30, y=232)
                            return False

                        
                    elif self.medium_type == 'vid':
                        try:
                            with open(key_file_path, 'r') as key_file:
                                if len(key_file.read()) > 0:
                                    key_file.seek(0)
                                    key_data = json.load(key_file)
                                    if 'TDES' in key_data:
                                        if key_data['TDES'] != None:
                                            if list(key_data.keys())[1].isnumeric():
                                                one = list(key_data.keys())[1]
                                                if len(key_data[one]) > 0:
                                                    if len(key_data[one][0]) == 3:
                                                        self.key_file_path = key_file_path
                                                        #('KEY FILE CHECK PASSED')
                                                        label_msg_pass = tk.Label(self, fg='green', text='key file status ok ✓                                                                     ')
                                                        label_msg_pass.place(x=30, y=232)
                                        
                                                        return True
                                                    
                                                    else:
                                                        #('KEY NOT COMPATIBLE WITH THIS STEGO OBJECT')
                                                        label_msg_pass = tk.Label(self, fg='red', text='Provided key file not compatible with this stego medium                                 ')
                                                        label_msg_pass.place(x=30, y=232)
                                                        return False

                                                else:
                                                    #('KEY NOT COMPATIBLE WITH THIS STEGO OBJECT')
                                                    label_msg_pass = tk.Label(self, fg='red', text='Provided key file not compatible with this stego medium                                 ')
                                                    label_msg_pass.place(x=30, y=232)
                                                    return False

                                            else:
                                                #('KEY NOT COMPATIBLE WITH THIS STEGO OBJECT')
                                                label_msg_pass = tk.Label(self, fg='red', text='Provided key file not compatible with this stego medium                                 ')
                                                label_msg_pass.place(x=30, y=232)
                                                return False

                                        else:
                                            #('KEY NOT COMPATIBLE WITH THIS STEGO OBJECT')
                                            label_msg_pass = tk.Label(self, fg='red', text='Provided key file not compatible with this stego medium                                 ')
                                            label_msg_pass.place(x=30, y=232)
                                            return False

                                    else:
                                        #('KEY NOT COMPATIBLE WITH THIS STEGO OBJECT')
                                        label_msg_pass = tk.Label(self, fg='red', text='Provided key file not compatible with this stego medium                                 ')
                                        label_msg_pass.place(x=30, y=232)
                                        return False

                                else:
                                    #('ERROR WITH KEY FILE -> ui.py -> DecryptionPage -> keyFileCheck()')
                                    label_msg_pass = tk.Label(self, fg='red', text='Error with key file contents                               ')
                                    label_msg_pass.place(x=30, y=232)
                                    return False

                        except FileNotFoundError:
                            #('ERROR WITH KEY FILE -> ui.py -> DecryptionPage -> keyFileCheck()')
                            label_msg_pass = tk.Label(self, fg='red', text='Provided file does not exist                                       ')
                            label_msg_pass.place(x=30, y=232)
                            return False

                        except Exception as e:
                            pass


                else:
                    #('INVALID KEY FILE FORMAT -> ui.py -> DecryptionPage -> keyFileCheck()')
                    label_msg_pass = tk.Label(self, fg='red', text='File of unsupported format provided                   ')
                    label_msg_pass.place(x=30, y=232)
                    return False
            else:
                #('NO KEY FILE PROVIDED -> ui.py -> DecryptionPage -> keyFileCheck()')
                label_msg_pass = tk.Label(self, fg='red', text='Provide path to key file                                                    ')
                label_msg_pass.place(x=30, y=232)
                return False

        else:
            #('NO PATH TO MEDIUM PROVIDED -> ui.py -> DecryptionPage -> keyFileCheck()')
            label_msg_pass = tk.Label(self, fg='red', text='Provide path and varify stego medium first                                                       ')
            label_msg_pass.place(x=30, y=232)
            return False



def main():
    try:
        app = StegoApp()
        app.mainloop()
    except Exception as e:
        tk.messagebox.showinfo("Error", "Unknown exception refer to documentation for details")


if __name__ == '__main__':
    main()