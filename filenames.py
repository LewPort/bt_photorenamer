import os
import tkinter as tk
import tkinter.messagebox
from PIL import ImageTk, Image
import time
from send2trash import send2trash


opsys = os.name

class Filelist:
    def __init__(self, path, lenlimit, recursive, sortby):
        self.path = path
        self.filelist = []
        self.recursive = recursive
        self.lenlimit = lenlimit
        self.sortby = sortby
        if self.recursive == True:
            self.rscan(self.lenlimit)
        else:
            self.nonrscan(self.lenlimit)
        self.sort(self.sortby)

    def appendfilelist(self, root, i):
        self.filelist.append([os.path.join(root, i), i, os.path.getsize(os.path.join(root, i))])
        
        
    def rscan(self, lenlimit):
        for root, subdir, file in os.walk(self.path):
            for i in file:
                try:
                    extind = i.index('.')
                except ValueError:
                    continue
                if self.lenlimit == 0:
                    self.appendfilelist(root, i)
                elif len(i[:extind]) <= self.lenlimit:
                    self.appendfilelist(root, i)

    def nonrscan(self, lenlimit):
        for i in os.listdir(self.path):
            try:
                extind = i.index('.')
            except ValueError:
                continue
            if self.lenlimit == 0:
                self.appendfilelist(self.path, i)
            elif len(i[:extind]) <= self.lenlimit:
                self.appendfilelist(self.path, i)

    def sortbylen(self):
        self.filelist.sort(key = lambda x: len(x[1]))

    def sortbyname(self):
        self.filelist.sort(key=lambda x: str.lower(x[1]))

    def sortbysize(self):
        self.filelist.sort(key= lambda x: int(x[2]))

    def sort(self, sortby):
        print('sorting...')
        if self.sortby == 'Sort By: Name Length':
            self.sortbylen()
        elif self.sortby == 'Sort By: Alphabetical':
            self.sortbyname()
        elif self.sortby == 'Sort By: File Size':
            self.sortbysize()
        
            
''''''''''''''''''''''''''''''''''''
'''tkinter starts hur'''
''''''''''''''''''''''''''''''''''''
class GUI:
    def __init__(self):

        # main window setup
        self.window = tk.Tk()
        self.winW = 1000
        self.winH = 500
        self.window.geometry('%dx%d' % (self.winW, self.winH))
        self.window.title('File Renamer')
        self.filelist = []
        self.filecount = 0

        # file list setup
        self.recursive = True
        self.showfullpath = True
        if opsys == 'posix':
            self.noimage = './img/noimage.jpg'
        elif opsys == 'nt':
            self.noimage = '.\\img\\noimage.jpg'
        self.filepath = None
        self.lenlimit = 0

        # Top list area stuff
        self.listframe = tk.Frame(self.window)
        self.scrollbar = tk.Scrollbar(self.listframe, orient='vertical')
        self.listbox = tk.Listbox(self.listframe,
                                  yscrollcommand=self.scrollbar.set,
                                  selectmode=tk.SINGLE)
        self.scrollbar.config(command=self.listbox.yview)
        self.listbox.configure(exportselection=False)
        self.listbox.selection_set(0)
        self.listbox.bind('<<ListboxSelect>>', self.displayimage)
        self.scrollbar.pack(side='right', fill='y')
        self.listbox.pack(side='left', expand=True, fill='both')
        self.listframe.pack(expand=False, fill='x', padx=10, pady=10)

        # Browsing-for-file widgets etc
        self.browseframe = tk.Frame(self.window)
        self.browsebutton = tk.Button(self.browseframe, text='Browse', width=20, command=self.browsewin)
        
        self.var_sortby = tk.StringVar(self.window)
        self.var_sortby.set('Sort By: Alphabetical')
        self.sortby = tk.OptionMenu(self.browseframe, self.var_sortby,
                                     'Sort By: Alphabetical', 'Sort By: Name Length', 'Sort By: File Size',
                                    command = self.refresh_list)
        self.sortby.config(width=22)
        
        self.filecountlabel = tk.Label(self.browseframe, text=str(self.filecount)+' files found.')
        self.currentrecursivestate=tk.BooleanVar()
        self.currentshowfullpathstate=tk.BooleanVar()
        self.recursivecheck = tk.Checkbutton(self.browseframe,
                                             text='Scan Subfolders',
                                             variable = self.currentrecursivestate,
                                             onvalue=True,
                                             offvalue=False,
                                             command = self.changerecursive)
        self.recursivecheck.select()
        
        self.showfullpathcheck = tk.Checkbutton(self.browseframe,
                                     text='Show Full Path',
                                     variable = self.currentshowfullpathstate,
                                     onvalue=True,
                                     offvalue=False,
                                     command = self.changeshowfullpath)
        self.showfullpathcheck.select()
        self.browsebutton.grid(column=0, row=0)
        self.sortby.grid(column=0, row=1)
        self.filecountlabel.grid(column=1, row=0, sticky='w')
        self.showfullpathcheck.grid(column=1, row=1, sticky='w')
        self.recursivecheck.grid(column=1, row=2, sticky='w')
        self.browseframe.pack()

        # Separators
        self.separatorH = tk.Frame(self.window, height=2, bd=1, relief='sunken')
        self.separatorH.pack(fill='x', padx=5, pady=5)

        # Bottom Section
        self.bottomframe = tk.Frame(self.window)
        self.separatorV = tk.Frame(self.bottomframe, width=2, bd=1, relief='sunken')

        # Image frame
        self.imageframe = tk.Frame(self.bottomframe, bg='black', bd=1, relief='sunken',
                                   padx=5, pady=5)
        self.imgpanel = tk.Label(self.imageframe, bg='black', anchor='center', justify='center')
        self.imgpanel.place(relx=0.5, rely=0.5,
                            relwidth=1, relheight=1, anchor='center')

        # Rename frame
        self.renameframe = tk.Frame(self.bottomframe)
        self.origname = tk.StringVar()
        self.renameentry = tk.Entry(self.renameframe, width=40, text=self.origname)
        self.renamebutton = tk.Button(self.renameframe, text='Rename',
                                      width=20, command = self.renameselected)
        self.deletebutton = tk.Button(self.renameframe, text='Delete',
                                      width=20, command=self.deleteimage)
        self.sizelabel = tk.Label(self.renameframe, text='', justify='center')

        self.renameentry.grid(row=0, column=0, columnspan=2, sticky='nesw')
        self.renamebutton.grid(column=0, row=1, padx=5, pady=5, sticky='nesw')
        self.deletebutton.grid(column=1, row=1, sticky='nesw')
        self.sizelabel.grid(column=0, row=2, columnspan=2, sticky='nesw')

        self.logframe = tk.Frame(self.renameframe)
        self.log = tk.Text(self.logframe, state='normal', width=40, height=7,
                           bd=1, relief='sunken')
        self.logscrollbar = tk.Scrollbar(self.logframe, orient='vertical')
        self.logscrollbar.config(command=self.log.yview)
        self.log.config(yscrollcommand=self.logscrollbar.set)
        self.log.grid(column=0, row=0, sticky='nesw')
        self.logscrollbar.grid(column=1, row=0,sticky='nesw')
        self.logframe.grid(column=0, row=3, columnspan=2, sticky='nesw')
        self.renameframe.columnconfigure(0, weight=1)
        self.renameframe.rowconfigure(3, weight=1)
        self.logframe.rowconfigure(0, weight=1)
        self.logframe.columnconfigure(0, weight=1)

        # Final placements
        self.imageframe.pack(fill='both', expand=True, side='left', padx=5, pady=5)
        self.separatorV.pack(fill='y', side='left', padx=5, pady=5)
        self.renameframe.pack(fill='both', expand=False, side='right', padx=5, pady=5)
        self.bottomframe.pack(expand=True, fill='both')

        self.loadimage()
        self.window.bind('<Return>', self.returntorename)
        self.window.bind('<Configure>', self.resizeimagetowindow)
        self.window.lift()
        self.window.mainloop()

    def deleteimage(self):
        self.cur_sel = self.listbox.curselection()
        selectedfilename = self.filelist.filelist[self.cur_sel[0]][1]
        fullpath = self.filelist.filelist[self.cur_sel[0]][0]
        pathonly = fullpath[:fullpath.index(selectedfilename)]
        ask = tkinter.messagebox.askquestion("Delete %s?" % selectedfilename,
                                          "Are you sure you want to delete %s?" % selectedfilename,
                                          icon='warning', default='no')
        if ask == 'yes':
            send2trash(fullpath)
            timestamp = time.ctime(time.time())
            self.log.config(state='normal')
            self.log.insert(1.0, '%s:\n%s deleted!\n\n' % (timestamp, selectedfilename))
            self.log.config(state='normal')
            self.filelist = Filelist(self.filepath, self.lenlimit, self.recursive)
            self.populatelist()
            self.listbox.selection_set(self.cur_sel)
            self.listbox.see(self.cur_sel)
            self.loadimage()
        else:
            pass


        
        
    def changerecursive(self):
        self.recursive = self.currentrecursivestate.get()
        self.refresh_list()

    def changeshowfullpath(self):
        self.showfullpath = self.currentshowfullpathstate.get()
        self.refresh_list()

    def refresh_list(self, *args):
        if self.filelist:
            self.scanlist()
            self.listbox.selection_set(self.cur_sel)
            self.listbox.see(self.cur_sel)

    def renameselected(self):
        try:
            self.cur_sel = self.listbox.curselection()
            selectedfilename = self.filelist.filelist[self.cur_sel[0]][1]
        except AttributeError:
            return
        fullpath = self.filelist.filelist[self.cur_sel[0]][0]
        pathonly = fullpath[:fullpath.index(selectedfilename)]
        newname = self.renameentry.get()
        illegalchars = ('.', '/', '\\', ':', '|')
        for c in newname:
            if c in illegalchars:
                timestamp = time.ctime(time.time())
                illegalcharstring = '%s:\nERROR: \'%s\' is an illegal character.\n\n' % (timestamp, c)
                self.log.insert(1.0, illegalcharstring)
                return
            else:
                continue
        extension = selectedfilename[selectedfilename.index('.'):]
        newpath = pathonly + newname + extension
        timestamp = time.ctime(time.time())
        try:
            os.rename(fullpath, newpath)
            self.log.insert(1.0, '%s:\n%s -> %s\n\n' % (timestamp, selectedfilename, newname + extension))
        except:
            self.log.insert(1.0, '%s:\nERROR: Could not rename %s.\n\n' % (timestamp, selectedfilename))
            
        self.filelist = Filelist(self.filepath, self.lenlimit, self.recursive)
        self.populatelist()
        self.listbox.selection_set(self.cur_sel)
        self.listbox.see(self.cur_sel)
        self.loadimage()
                         
    def returntorename(self, event):
        self.renameselected()
        
    def fillrenameentry(self):
        try:
            filename = self.filelist.filelist[self.listbox.curselection()[0]][1]
            extind = filename.index('.')
            filename = filename[:extind]
            self.origname.set(filename)
        except (AttributeError, IndexError):
            pass

    def displayimage(self, event):
        self.loadimage()

    def resizeimagetowindow(self, event):
        self.refreshimage()

    def loadimage(self):
        self.imgpanel.image = None
        self.cur_sel = self.listbox.curselection()
        try:
            newpath = self.filelist.filelist[self.cur_sel[0]][0]
            self.newphoto = Image.open(newpath).convert('RGB')
            self.imgsize = self.newphoto.size
            self.strimgsize = '%s x %s | ' % self.imgsize
            self.strfilesize = round(os.stat(newpath).st_size / 1000)
            self.strfilesize = format(int(self.strfilesize), ',d') +' KB'
        except (OSError, AttributeError):
            self.newphoto = Image.open(self.noimage)
            self.strimgsize = ('No Image Recognised')
            self.strfilesize = ''
        self.imginfo = self.newphoto.info
        self.refreshimage()
        

    def refreshimage(self):
        framewidth = self.imageframe.winfo_width()
        frameheight = self.imageframe.winfo_height()
        oldwidth = ImageTk.PhotoImage(self.newphoto).width()
        oldheight = ImageTk.PhotoImage(self.newphoto).height()
        newwidth = oldwidth
        newheight = oldheight
        
        if oldwidth > framewidth:
            newwidth = framewidth
            rfactor = newwidth/oldwidth
            newheight = int(oldheight * rfactor)              

        if newheight > frameheight:
            even_newer_height = frameheight
            rfactor = even_newer_height/newheight
            newwidth = int(newwidth * rfactor)
            newheight = even_newer_height
            
        newphoto = self.newphoto.resize((newwidth, newheight), Image.ANTIALIAS)
        
        loadedphoto = ImageTk.PhotoImage(newphoto)
        self.imgpanel.config(image=loadedphoto)
        self.imgpanel.image = loadedphoto
        self.sizelabel.config(text=self.strimgsize + self.strfilesize)

        self.fillrenameentry()
        
    def populatelist(self):
        self.listbox.delete(0, tk.END)
        self.filecount = len(self.filelist.filelist)
        self.filecount = format(self.filecount, ',d')
        self.filecountlabel.config(text=self.filecount + ' files found.')
        if self.showfullpath == True:
            for i in self.filelist.filelist:
                self.listbox.insert(tk.END, i[0])
        else:
            for i in self.filelist.filelist:
                self.listbox.insert(tk.END, i[1])

    def scanlist(self):
        self.filelist = Filelist(self.filepath, self.lenlimit, self.recursive, self.var_sortby.get())
        self.populatelist()

    def browsewin(self):
        import tkinter.filedialog as fdialog
        self.filepath = fdialog.askdirectory()
        if self.filepath:
            self.scanlist()
        else:
            pass

gui = GUI()
    

        
