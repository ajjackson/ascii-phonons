#! /usr/bin/env python

from __future__ import print_function
import ascii_phonons
from os.path import isdir, join
import tempfile

from sys import version_info
if version_info.major > 2:
    import tkinter as tk
    import tkinter.filedialog as filedialog
else:
    import Tkinter as tk
    import tkFileDialog as filedialog

from PIL import ImageTk

preview_placeholder = join(ascii_phonons.ascii_phonons_path, 'images', 'preview.png')

class Application(tk.Frame):
    
    def __init__(self, master):
        self.button_defaults={'fill': "x", 'padx': 10, 'pady': 10}

        # Setup files and paths
        self.input_file = ''
        self.output_file = tk.StringVar(value='phonon')
        _, self.preview_file = tempfile.mkstemp(dir=tempfile.gettempdir())

        self.call_blender_args = {}
        
        tk.Frame.__init__(self, master)


        self.message = tk.StringVar(value='Messages')
        MessageRow = tk.Frame(self).pack(side="bottom")
        tk.Label(MessageRow, textvariable=self.message, height=1).pack(side="bottom", expand="yes", fill=tk.X)


        self.LeftRightFrames = tk.Frame(self)
        self.LeftFrame = tk.Frame(self.LeftRightFrames)
        self.RightFrame = tk.Frame(self.LeftRightFrames)

        self.add_fileopen_row()

        self.add_cell_row()

        self.add_appearance_row()

        self.add_frame_row()

        self.add_render_row()
        
        self.add_preview_panel()

        self.LeftRightFrames.pack(side="top", expand="yes", fill="x")
        self.LeftFrame.pack(side="left", expand="yes", fill="x")
        self.RightFrame.pack(side="right")

        self.pack(side=tk.TOP, expand="yes", fill="both")

    def add_fileopen_row(self):
        self.mode = tk.IntVar(value=0)
        FileopenRow = tk.Frame(self.LeftFrame)
        tk.Button(FileopenRow, text='Open ASCII file',
                  command=self.askinputfilename).pack(side="left", **self.button_defaults)
        tk.Entry(FileopenRow, textvariable=self.mode, width=2).pack(side="right")
        tk.Label(FileopenRow, text='Phonon mode index:').pack(side="right")
        FileopenRow.pack(side="top")        

    def add_cell_row(self):

        self.supercell_X = tk.IntVar(value=2)
        self.supercell_Y = tk.IntVar(value=2)
        self.supercell_Z = tk.IntVar(value=2)
        self.unitcell_X = tk.DoubleVar(value=0.0)
        self.unitcell_Y = tk.DoubleVar(value=0.0)
        self.unitcell_Z = tk.DoubleVar(value=0.0)
        self.show_box = tk.BooleanVar(value=True)

        SupercellRow = tk.Frame(self.LeftFrame)
        tk.Label(SupercellRow, text='Supercell').pack(side="left")
        for field in self.supercell_X, self.supercell_Y, self.supercell_Z:
            tk.Entry(SupercellRow, textvariable=field, width=2).pack(side="left")
        tk.Label(SupercellRow, text='Bounding box location').pack(side="left")
        for field in self.unitcell_X, self.unitcell_Y, self.unitcell_Z:
            tk.Entry(SupercellRow, textvariable=field, width=3).pack(side="left")
        tk.Checkbutton(SupercellRow, text="Show box", variable=self.show_box).pack(side="right")
            
        SupercellRow.pack(side="top", expand="yes", fill="x")

    def add_appearance_row(self, padding=20):
        self.arrows = tk.BooleanVar(value=False)
        self.arrowsize = tk.DoubleVar(value=20.0)
        self.atomsize =  tk.DoubleVar(value=0.6)
        self.vibsize =  tk.DoubleVar(value=3.0)
        self.camera_rot = tk.DoubleVar(value=360)
        
        Appearance = tk.Frame(self.LeftFrame, borderwidth=3, relief="groove")
        tk.Label(Appearance, text="Appearance settings").pack(side="top", fill="x")

        AppearanceRow1 = tk.Frame(Appearance)
        tk.Entry(AppearanceRow1, textvariable=self.camera_rot, width=4).pack(side="right")
        tk.Label(AppearanceRow1, text="Camera tilt:").pack(side="right")
        tk.Checkbutton(AppearanceRow1, text="Show arrows", variable=self.arrows).pack(side="left")
        AppearanceRow1.pack(side="top", fill="x", expand="yes")

        AppearanceScales = tk.Frame(Appearance)
        for label, param in (('Arrow size:', self.arrowsize),
                                      ('Vib size:', self.vibsize),
                                      ('Atom scale:', self.atomsize)):
            tk.Label(AppearanceScales, text=label).pack(side="left")
            tk.Entry(AppearanceScales, textvariable=param, width=3).pack(side="left")
        AppearanceScales.pack(side="top")

        Appearance.pack(side="top", padx=padding, pady=padding)


    def add_frame_row(self):
        self.start_frame = tk.IntVar(value=0)
        self.end_frame = tk.IntVar(value=29)
        self.n_frames = tk.IntVar(value=30)
        self.gif = tk.BooleanVar(value=True)
        
        FrameRow = tk.Frame(self.LeftFrame)
        tk.Label(FrameRow, text='Frame range').pack(side="left")
        tk.Entry(FrameRow, textvariable=self.start_frame, width=3).pack(side="left")
        tk.Entry(FrameRow, textvariable=self.end_frame, width=3).pack(side="left")
        tk.Label(FrameRow, text='Frames/cycle').pack(side="left")
        tk.Entry(FrameRow, textvariable=self.n_frames, width=3).pack(side="left")
        tk.Checkbutton(FrameRow, text="Make .gif", variable=self.gif).pack(side="left")
        tk.Button(FrameRow, text='Launch Blender', command=self.launch_blender).pack(side="right", **self.button_defaults)
        FrameRow.pack(side="top", expand="yes", fill="x")

    def add_render_row(self):
        self.RenderRow = tk.Frame(self.LeftFrame)
        tk.Button(self.RenderRow, text='Output file', command=self.askoutputfilename).pack(side="left", **self.button_defaults)
        self.output_file_entry = tk.Entry(self.RenderRow, textvariable=self.output_file).pack(side="left", expand="yes", fill="x")
        tk.Button(self.RenderRow, text='Render', command=self.render).pack(side="right", **self.button_defaults)
        tk.Button(self.RenderRow, text='Preview', command=self.preview).pack(side="right", **self.button_defaults)            
        self.RenderRow.pack(side=tk.TOP, expand="yes", fill="x")

    def add_preview_panel(self):
        # Setup preview panel
        self.preview_label = tk.Label(self.RightFrame)        
        self.preview_placeholder_pil = ImageTk.Image.open(preview_placeholder)
        self.preview_placeholder_tk = ImageTk.PhotoImage(self.preview_placeholder_pil)
        self.preview_label.configure(image=self.preview_placeholder_tk)        
        self.preview_label.pack(padx=10)
                

    def askinputfilename(self):
        """Set the input .ASCII file with a native system dialogue"""
        self.input_file = filedialog.askopenfilename(defaultextension='.ascii',
                                                     filetypes=[('all files','.*'),
                                                                ('v_sim','.ascii')])

    def askoutputfilename(self):
        """Set the output file path and root with a native system dialogue"""
        output_file = filedialog.asksaveasfilename()
        self.output_file.set(output_file)
        

    def update_args(self):
        self.call_blender_args.update({
            'start_frame': self.start_frame.get(),
            'end_frame': self.end_frame.get(),
            'n_frames': self.n_frames.get(),
            'output_file': self.output_file.get(),
            'supercell': (self.supercell_X.get(),self.supercell_Y.get(),self.supercell_Z.get()),
            'bbox_offset': (self.unitcell_X.get(),self.unitcell_Y.get(),self.unitcell_Z.get()),
            'bbox': self.show_box.get(),
            'vectors': self.arrows.get(),
            'camera_rot': self.camera_rot.get(),
            'scale_factor': self.atomsize.get(),
            'vib_magnitude': self.vibsize.get(),
            'arrow_magnitude': self.arrowsize.get(),
            'gif':self.gif.get(),
            'mode_index':self.mode.get()
            }) 
        return self.call_blender_args

    def render(self):
        self.update_args()
        if self.input_file == '' or isdir(self.input_file):
            self.message.set('Please open a .ascii input file')
        else:
            ascii_phonons.call_blender(self.input_file, **self.call_blender_args)
            self.message.set('Rendering complete')

    def preview(self):
        kwargs = self.update_args().copy()
        kwargs.update({'preview':self.preview_file, 'gif':False})
        ascii_phonons.call_blender(self.input_file,  **kwargs)

        # Pack the preview image into the right frame
        self.preview_pil = ImageTk.Image.open(self.preview_file + '.png')
        self.preview_tk = ImageTk.PhotoImage(self.preview_pil)
        self.preview_label.configure(image=self.preview_tk)
        
        self.message.set('Preview complete')

    def launch_blender(self):
        kwargs = self.update_args().copy()
        kwargs.update({'output_file':False, 'gui':True})
        ascii_phonons.call_blender(self.input_file, **kwargs)
                
if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("ascii-phonons")
    top = Application(root)
    root.mainloop()
