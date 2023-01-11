from tkinter import StringVar, filedialog
import ttkbootstrap as ttkb

# Root window
ROOT = ttkb.Window(themename="darkly", title="ShroofianSalamanderCrypt", size=[1280, 360])
ROOT.config(cursor="left_ptr")

# These imports HAVE TO come after the ROOT window assignment, otherwise it opens a new window
# The appended comments stop VS Code (and other editors) from auto-sorting it to the top
from gui.styles.buttons import stylize_btn  # noqa nopep8 isort:skip
from gui.styles.entries import stylize_entry  # noqa nopep8 isort:skip

# StringVar for filepath; must be created after root window as well
FILEPATH: StringVar = StringVar()


def create_filepath_browse_frame() -> ttkb.Frame:
    """
    Creates the visuals for the filepath browse dialog area
    """
    frame = ttkb.Frame()

    filepath_entry_frame = ttkb.Labelframe(
        frame,
        text="File path",
        cursor="xterm",
        style="light",
    )
    filepath_entry_frame.pack(side=ttkb.LEFT, padx=5)

    filepath_entry = ttkb.Entry(
        filepath_entry_frame,
        width=80,
        font=("Consolas", 12),
        style=stylize_entry("dark"),
        textvariable=FILEPATH
    )
    filepath_entry.pack()

    # Focus entry field if the entry frame was clicked (the entry field doesn't fill it completely)
    filepath_entry_frame.bind("<Button-1>", lambda event: filepath_entry.focus_set())

    browse_btn = ttkb.Button(
        frame,
        width=16,
        text="Browse",
        cursor="hand1",
        style=stylize_btn("light", font_size=16),
        command=browse,
    )
    browse_btn.pack(side=ttkb.RIGHT, padx=5, pady=[8, 0])

    return frame


def create_upload_buttons_frame() -> ttkb.Frame:

    frame = ttkb.Frame()

    secure_upload_btn = ttkb.Button(
        frame,
        width=32,
        cursor="hand1",
        text="Secure Upload",
        style=stylize_btn("success.Outline"),
    )
    secure_upload_btn.pack(side=ttkb.LEFT, padx=5)

    unsecure_upload_btn = ttkb.Button(
        frame,
        width=32,
        cursor="hand1",
        text="Unsecure Upload (for testing only!)",
        style=stylize_btn("warning.Outline"),
    )
    unsecure_upload_btn.pack(side=ttkb.RIGHT, padx=5)

    return frame


def browse() -> str:
    """
    Opens file browse dialog and returns filepath selected
    """
    global FILEPATH
    filename = filedialog.askopenfilename()
    if filename != "":
        FILEPATH.set(filename)


def start():
    """
    Starts the main loop of the GUI
    """

    create_filepath_browse_frame().pack(pady=[100, 20])
    create_upload_buttons_frame().pack(pady=[20, 100])

    ROOT.mainloop()


# TODO: Use meter for progress
# TODO: Use notebook for tabs (send/receive)
