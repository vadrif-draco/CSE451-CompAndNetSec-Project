from tkinter import StringVar, filedialog
import ttkbootstrap as ttkb
import threading
from ftp import ftp_client
from crypto import round_robin_crypto, util

# Root window
WIDTH = 1280
HEIGHT = 360
ROOT = ttkb.Window(themename="darkly", title="RoundRobinCrypt", size=[WIDTH, HEIGHT])
ROOT.config(cursor="left_ptr")
ROOT.resizable(False, False)

# These imports HAVE TO come after the ROOT window assignment, otherwise it opens a new window
# The appended comments stop VS Code (and other editors) from auto-sorting it to the top
from gui.styles.buttons import stylize_btn  # noqa nopep8 isort:skip
from gui.styles.entries import stylize_entry  # noqa nopep8 isort:skip

# StringVar for filepath; must be created after root window as well
FILEPATH: StringVar = StringVar()


def create_filepath_browse_frame(master) -> ttkb.Frame:
    """
    Creates the visuals for the filepath browse dialog area
    """
    frame = ttkb.Frame(master)

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


def create_upload_buttons_frame(master) -> ttkb.Frame:

    frame = ttkb.Frame(master)

    secure_upload_btn = ttkb.Button(
        frame,
        width=32,
        cursor="hand1",
        text="Secure Upload",
        style=stylize_btn("success.Outline"),
        command=secure_upload
    )
    secure_upload_btn.pack(side=ttkb.LEFT, padx=5)

    unsecure_upload_btn = ttkb.Button(
        frame,
        width=32,
        cursor="hand1",
        text="Unsecure Upload (for testing only!)",
        style=stylize_btn("warning.Outline"),
        command=unsecure_upload
    )
    unsecure_upload_btn.pack(side=ttkb.RIGHT, padx=5)

    return frame


def browse() -> str:
    """
    Opens file browse dialog and returns filepath selected
    """
    global FILEPATH
    filepath = filedialog.askopenfilename()
    if filepath != "":
        FILEPATH.set(filepath)


def secure_upload():
    import numpy as np
    ROOT.withdraw()
    encrypted_data = []
    meter_window, meter = create_meter_window("Encrypting", "success")
    encryption_thread = threading.Thread(
        target=lambda: encrypted_data.append(round_robin_crypto.encrypt_file(
            input_file=util.File(FILEPATH.get()),
            key_des=np.array([0] * 64),
            key_aes128=np.zeros((128,), dtype=np.uint8),
            key_custom=np.zeros((128,), dtype=np.uint8),
            progress_update_hook=lambda e: meter.configure(amountused=e)
        ))
    )
    encryption_thread.start()

    def encryption_thread_checker():
        if not encryption_thread.is_alive():
            meter.configure(subtext="Uploading", amountused=0)
            upload_thread = threading.Thread(
                target=ftp_client.upload_binary,
                args=(
                    FILEPATH.get(),
                    encrypted_data[0],
                    lambda e: meter.configure(amountused=e)
                )
            )
            upload_thread.start()

            def upload_thread_checker():
                if not upload_thread.is_alive():
                    meter_window.destroy()
                    ROOT.deiconify()
                else: ROOT.after(1000, upload_thread_checker)

        else: ROOT.after(1000, encryption_thread_checker)

    encryption_thread_checker()


def unsecure_upload():
    ROOT.withdraw()
    upload_meter_page, meter = create_meter_window("Uploading", "warning")
    ftp_client.upload(FILEPATH.get(), meter.step)
    upload_meter_page.destroy()
    ROOT.deiconify()


def create_meter_window(label, bootstyle):
    meter_page = ttkb.Toplevel(title=f"RoundRobinCrypt | {label}", size=[HEIGHT, HEIGHT])
    meter_page.resizable(False, False)
    meter = ttkb.Meter(
        master=meter_page,
        amountused=0,
        stripethickness=10,
        subtext=label,
        bootstyle=bootstyle
    )
    meter.pack(fill="none", expand=True)
    return meter_page, meter


def start():
    """
    Packs the base frames/widgets and starts the main loop of the GUI
    """

    notebook = ttkb.Notebook(master=ROOT, width=WIDTH, height=HEIGHT)

    upload_page = ttkb.Frame(master=notebook)
    create_filepath_browse_frame(master=upload_page).pack(pady=[100, 20])
    create_upload_buttons_frame(master=upload_page).pack(pady=[20, 100])
    notebook.add(upload_page, text='Upload')

    download_page = ttkb.Frame(master=notebook)
    create_filepath_browse_frame(master=download_page).pack(pady=[100, 20])
    notebook.add(download_page, text='Download')

    notebook.pack()
    ROOT.mainloop()
