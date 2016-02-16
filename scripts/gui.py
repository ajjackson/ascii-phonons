#! /usr/bin/env python

from __future__ import print_function
import ascii_phonons
from os.path import isdir

from sys import version_info
if version_info.major > 2:
    import tkinter as tk
    import tkinter.filedialog as filedialog
else:
    import Tkinter as tk
    import tkFileDialog as filedialog

from PIL import ImageTk, Image


class Application(tk.Frame):
    
    def __init__(self, master):
        button_defaults={'fill': "x", 'padx': 10, 'pady': 10}

        self.input_file = ''
        self.call_blender_args = {}

        self.output_file = tk.StringVar(value='phonon')

        self.start_frame = tk.IntVar(value=0)
        self.end_frame = tk.IntVar(value=29)
        self.n_frames = tk.IntVar(value=30)
        
        tk.Frame.__init__(self, master)


        self.message = tk.StringVar(value='Messages')
        MessageRow = tk.Frame(self).pack(side="bottom")
        tk.Label(MessageRow, textvariable=self.message, height=1).pack(side="bottom", expand="yes", fill=tk.X)


        self.LeftRightFrames = tk.Frame(self)
        self.LeftFrame = tk.Frame(self.LeftRightFrames, borderwidth=2, bg="red")
        self.RightFrame = tk.Frame(self.LeftRightFrames, borderwidth=2, bg="green")
        tk.Label(self.LeftFrame, text="Left frame").pack(side="top")
        tk.Label(self.RightFrame, text="Right frame").pack(side="top")

        tk.Button(self.LeftFrame, text='Open ASCII file',
                  command=self.askinputfilename).pack(side="top", **button_defaults)

        FrameRow = tk.Frame(self.LeftFrame)
        tk.Label(FrameRow, text='Frame range').pack(side="left")
        tk.Entry(FrameRow, textvariable=self.start_frame, width=3).pack(side="left")
        tk.Entry(FrameRow, textvariable=self.end_frame, width=3).pack(side="left")
        tk.Label(FrameRow, text='Frames/cycle').pack(side="left")
        tk.Entry(FrameRow, textvariable=self.n_frames, width=3).pack(side="left")
        FrameRow.pack(side="top")

        self.RenderRow = tk.Frame(self.LeftFrame)
        tk.Button(self.RenderRow, text='Output file', command=self.askoutputfilename).pack(side="left", **button_defaults)
        self.output_file_entry = tk.Entry(self.RenderRow, textvariable=self.output_file).pack(side="left", expand="yes", fill="x")
        tk.Button(self.RenderRow, text='Render', command=self.render).pack(side="right", **button_defaults)
        self.RenderRow.pack(side=tk.TOP, expand="yes", fill="x")

        self.LeftRightFrames.pack(side="top", expand="yes", fill="x")
        self.LeftFrame.pack(side="left", expand="yes", fill="x")
        self.RightFrame.pack(side="right")

        self.pack(side=tk.TOP, expand="yes", fill="both")

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
            'output_file': self.output_file.get()
            })

    def render(self):
        self.update_args()
        if self.input_file == '' or isdir(self.input_file):
            self.message.set('Please open a .ascii input file')
        else:
            ascii_phonons.call_blender(self.input_file, **self.call_blender_args)
            self.message.set('Rendering complete')


if __name__ == "__main__":
    root = tk.Tk()
    root.wm_title("ascii-phonons")
    top = Application(root)
    root.mainloop()
