import customtkinter as ctk
import ctypes
import gc
from weakref import ref, proxy


def ref_count(address):
    return ctypes.c_long.from_address(address).value


def object_by_id(object_id):
    for obj in gc.get_objects():
        if id(obj) == object_id:
            return "Object exists"
    return "Not Found"


class testGUI(ctk.CTk):

    def __init__(self):
        super().__init__()
        self.frame = ctk.CTkFrame(self, fg_color='green')
        self.frame.pack(ipadx=10, ipady=10)
        self.label = ctk.CTkLabel(self, text='hallo')


def main():
    gui = testGUI()
    gui_id = id(gui)
    print(ref_count(gui_id))
    gui.destroy()
    del gui.label
    del gui
    gc.collect()
    print(ref_count(gui_id))


main()
