import os
import tkinter as tk
from PIL import ImageTk, Image

opsys = os.name

class Filelist:
    def __init__(self, path, lenlimit, recursive):
        self.path = path
        self.filelist = []
        self.recursive = recursive
        self.lenlimit = lenlimit
        if self.recursive == True:
            self.rscan(self.lenlimit)
        else:
            self.nonrscan(self.lenlimit)
        self.sortbylen()
        
    def rscan(self, lenlimit):
        for root, subdir, file in os.walk(self.path):
            for i in file:
                try:
                    extind = i.index('.')
                except ValueError:
                    continue
                if self.lenlimit == 0:
                    self.filelist.append([os.path.join(root, i), i])
                elif len(i[:extind]) <= self.lenlimit:
                    self.filelist.append([os.path.join(root, i), i])

    def nonrscan(self, lenlimit):
        for i in os.listdir(self.path):
            try:
                extind = i.index('.')
            except ValueError:
                continue
            if self.lenlimit == 0:
                self.filelist.append([os.path.join(self.path, i), i])
            elif len(i[:extind]) <= self.lenlimit:
                self.filelist.append([os.path.join(self.path, i), i])

    def sortbylen(self):
        self.filelist.sort(key = lambda x: len(x[1]))
            
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

        # file list setup
        self.recursive = True
        self.showfullpath = True
        self.filepath = ''
        if opsys == 'posix':
            self.noimage = './img/noimage.jpg'
        elif opsys == 'nt':
            self.noimage = '.\\img\\noimage.jpg'
        self.lenlimit = 0

        # Top list area stuff
        self.listframe = tk.Frame(self.window)
        self.scrollbar = tk.Scrollbar(self.listframe, orient='vertical')
        self.listbox = tk.Listbox(self.listframe,
                                  yscrollcommand=self.scrollbar.set,
                                  selectmode=tk.SINGLE)
        self.listbox.configure(exportselection=False)
        self.listbox.selection_set(0)
        self.listbox.bind('<<ListboxSelect>>', self.displayimage)
        self.scrollbar.pack(side='right', fill='y')
        self.listbox.pack(side='left', expand=True, fill='both')
        self.listframe.pack(expand=False, fill='x', padx=10, pady=10)

        # Browsing-for-file widgets etc
        self.browseframe = tk.Frame(self.window)
        self.browsebutton = tk.Button(self.browseframe, text='Browse', command=self.browsewin)
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
        self.browsebutton.grid(row=0)
        self.showfullpathcheck.grid(row=1, sticky='w')
        self.recursivecheck.grid(row=2, sticky='w')
        self.browseframe.pack()

        # Separator
        self.separator = tk.Frame(self.window, height=2, bd=1, relief='solid')
        self.separator.pack(fill='x', padx=5, pady=5)

        # Bottom Section
        self.bottomframe = tk.Frame(self.window)

        # Image frame
        self.imageframe = tk.Frame(self.bottomframe)
        self.imgpanel = tk.Label(self.imageframe, bd=0)
        self.imgpanel.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Rename frame
        self.renameframe = tk.Frame(self.bottomframe)
        self.origname = tk.StringVar()
        self.renameentry = tk.Entry(self.renameframe, width=60, text=self.origname)
        self.renamebutton = tk.Button(self.renameframe, text='Rename', command = self.renameselected)
        self.dimensionlabel = tk.Label(self.renameframe, text='', font=(None, 20))
        self.filesizelabel = tk.Label(self.renameframe, text='', font=(None, 20))
        self.renameentry.pack()
        self.renamebutton.pack()
        self.dimensionlabel.pack()
        self.filesizelabel.pack()

        # Final placements
        self.imageframe.pack(fill='both', expand=True, side='left', padx=10, pady=10)
        self.renameframe.pack(fill='both', expand=False, side='right', padx=10, pady=10)
        self.bottomframe.pack(expand=True, fill='both')

        self.loadimage()
        self.window.bind('<Return>', self.returntorename)
        self.window.bind('<Configure>', self.resizeimagetowindow)
        self.window.lift()
        self.window.mainloop()
        
    def changerecursive(self):
        self.recursive = self.currentrecursivestate.get()
        self.scanlist()
        self.listbox.selection_set(self.cur_sel)
        self.listbox.see(self.cur_sel)

    def changeshowfullpath(self):
        self.showfullpath = self.currentshowfullpathstate.get()
        self.scanlist()
        self.listbox.selection_set(self.cur_sel)
        self.listbox.see(self.cur_sel)

    def renameselected(self):
        self.cur_sel = self.listbox.curselection()
        selectedfilename = self.filelist.filelist[self.listbox.curselection()[0]][1]
        fullpath = self.filelist.filelist[self.listbox.curselection()[0]][0]
        pathonly = fullpath[:fullpath.index(selectedfilename)]
        newname = self.renameentry.get()
        newpath = pathonly + newname + selectedfilename[selectedfilename.index('.'):]
        os.rename(fullpath, newpath)
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
        except AttributeError:
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
            self.strimgsize = '%s x %s' % self.imgsize
            self.strfilesize = round(os.stat(newpath).st_size / 1000)
            self.strfilesize = str(format(int(self.strfilesize), ',d')) +' KB'
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
        newphoto = ImageTk.PhotoImage(newphoto)
        self.imgpanel.config(image=newphoto)
        self.imgpanel.image = newphoto
        self.dimensionlabel.config(text=self.strimgsize)
        self.filesizelabel.config(text=self.strfilesize)

        self.fillrenameentry()
        
    def populatelist(self):
        self.listbox.delete(0, tk.END)
        if self.showfullpath == True:
            for i in self.filelist.filelist:
                self.listbox.insert(tk.END, i[0])
        else:
            for i in self.filelist.filelist:
                self.listbox.insert(tk.END, i[1])

    def scanlist(self):
        self.filelist = Filelist(self.filepath, self.lenlimit, self.recursive)
        self.populatelist()

    def browsewin(self):
        import tkinter.filedialog as fdialog
        self.filepath = fdialog.askdirectory()
        self.scanlist()



gui = GUI()
    

        
