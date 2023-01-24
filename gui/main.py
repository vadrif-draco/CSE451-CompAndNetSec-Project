from tkinter import StringVar, filedialog
from typing import Callable
import threading
import numpy as np
import ttkbootstrap as ttkb
from ftp import ftp_client
from crypto import round_robin_crypto, util, aes_for_master_key

# Master Key to be used for encrypting/decrypting the keys used for RoundRobinCrypto
MASTER_KEY: bytes = None

# Root window
WIDTH = 1280
HEIGHT = 360
ROOT = ttkb.Window(themename="darkly", title="RoundRobinCrypt", size=[WIDTH, HEIGHT])
ROOT.config(cursor="left_ptr")
ROOT.resizable(False, False)

# The main pages in the notebook of the root window (So far)
UPLOAD_PAGE: ttkb.Frame = None
DOWNLOAD_PAGE: ttkb.Frame = None

# These imports HAVE TO come after the ROOT window assignment, otherwise it opens a new window
# The appended comments stop VS Code (and other editors) from auto-sorting it to the top
from gui.styles.buttons import stylize_btn  # noqa nopep8 isort:skip
from gui.styles.entries import stylize_entry  # noqa nopep8 isort:skip

# StringVars for filepaths; must be created after root window as well
UPLOAD_FILEPATH: StringVar = StringVar()
DOWNLOAD_FILEPATH: StringVar = StringVar()


def __create_filepath_browse_frame(master, entry_tvar, width=80) -> ttkb.Frame:
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
        width=width,
        font=("Consolas", 12),
        style=stylize_entry("dark"),
        textvariable=entry_tvar
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
        command=__browse,
    )
    browse_btn.pack(side=ttkb.RIGHT, padx=5, pady=[8, 0])

    return frame


def __create_upload_buttons_frame(master) -> ttkb.Frame:

    frame = ttkb.Frame(master)

    secure_upload_btn = ttkb.Button(
        frame,
        width=32,
        cursor="hand1",
        text="Secure Upload",
        style=stylize_btn("success.Outline"),
        command=__secure_upload
    )
    secure_upload_btn.pack(side=ttkb.LEFT, padx=5)

    unsecure_upload_btn = ttkb.Button(
        frame,
        width=32,
        cursor="hand1",
        text="Unsecure Upload (for testing only!)",
        style=stylize_btn("warning.Outline"),
        command=__unsecure_upload
    )
    unsecure_upload_btn.pack(side=ttkb.RIGHT, padx=5)

    return frame


def __browse() -> str:
    """
    Opens file browse dialog and returns filepath selected
    """
    global UPLOAD_FILEPATH
    filepath = filedialog.askopenfilename()
    if filepath != "":
        UPLOAD_FILEPATH.set(filepath)


def __encrypt_data(original_file: util.File, meter: ttkb.Meter, next_fn: Callable):

    # Encrypted files to be uploaded
    encrypted_files: list[util.File] = []

    # The keys in bits
    key_des = np.array(np.random.choice([0, 1], (64,)), dtype=np.uint8)
    key_aes128 = np.array(np.random.choice([0, 1], (128,)), dtype=np.uint8)
    key_custom = np.array(np.random.choice([0, 1], (128,)), dtype=np.uint8)

    def encrypt_all():

        meter.configure(subtext="Encrypting data", amountused=0)
        encrypted_files.append(
            round_robin_crypto.encrypt_file(
                input_file=original_file,
                output_file_path=original_file.file_path_no_ext + "-encrypted" + original_file.file_ext,
                key_des=key_des,
                key_aes128=key_aes128,
                key_custom=key_custom,
                progress_update_hook=lambda e: meter.configure(amountused=e)
            )
        )

        concatenated_keys = np.array(np.concatenate((key_des, key_aes128, key_custom))).tobytes()
        meter.configure(subtext="Encrypting keys")
        encrypted_files.append(
            util.File.create_file(
                original_file.file_path_no_ext + "-encrypted.keys",
                np.frombuffer(aes_for_master_key.encrypt(concatenated_keys, MASTER_KEY), dtype=np.uint8)
            )
        )

    encryption_thread = threading.Thread(target=encrypt_all)
    encryption_thread.start()

    def encryption_thread_checker():
        if not encryption_thread.is_alive():
            next_fn(encrypted_files, meter)
        else:
            ROOT.after(2000, encryption_thread_checker)

    print("\nEncrypting...\n")
    encryption_thread_checker()


def __upload(files: list[util.File], meter: ttkb.Meter):

    # TODO: Upload master key??
    num_of_files = len(files)
    subtext_postfixes = ["data", "keys"]

    def upload_files():
        meter.configure(amountused=0)
        for i, file in enumerate(files):
            meter.configure(subtext=f'Uploading {subtext_postfixes[i]}')
            ftp_client.upload(file.file_path, lambda e: meter.step(e // num_of_files))

    upload_thread = threading.Thread(target=upload_files)
    upload_thread.start()

    def upload_thread_checker():
        if not upload_thread.is_alive():
            for child in UPLOAD_PAGE.winfo_children():
                child.destroy()
            create_upload_page()
        else:
            ROOT.after(2000, upload_thread_checker)

    print("\nUploading...\n")
    upload_thread_checker()


def __secure_upload():
    # TODO: Also check if file exists
    if UPLOAD_FILEPATH.get() != "":
        for child in UPLOAD_PAGE.winfo_children():
            child.destroy()
        original_file = util.File(UPLOAD_FILEPATH.get())
        meter = __create_meter("Encrypting data", "success")
        __encrypt_data(original_file, meter, next_fn=__upload)


def __unsecure_upload():
    # TODO: Also check if file exists
    if UPLOAD_FILEPATH.get() != "":
        for child in UPLOAD_PAGE.winfo_children():
            child.destroy()
        file = util.File(UPLOAD_FILEPATH.get())
        meter = __create_meter("Uploading data", "warning")
        __upload(file, meter)


def __create_meter(label, bootstyle):
    meter = ttkb.Meter(
        master=UPLOAD_PAGE,
        amountused=0,
        stripethickness=10,
        subtext=label,
        bootstyle=bootstyle
    )
    meter.pack(fill="none", expand=True)
    return meter


def __create_missing_master_key_prompt():
    prompt = ttkb.Frame()

    ttkb.Label(
        master=prompt,
        text="It seems like you forgot to provide your master key file, or it is malformed...",
        font=("Helvetica", 16),
        style="danger"
    ).pack(pady=(64, 16))

    ttkb.Label(
        master=prompt,
        text="Please double-check your 256-bit master key file \"MASTER_KEY\" in the app's root directory.",
        font=("Helvetica", 16),
        style="danger"
    ).pack(pady=(16, 16))

    key_creation_prompt_frame = ttkb.Frame(master=prompt)

    ttkb.Label(
        master=key_creation_prompt_frame,
        text="Would you like me to create one for you?",
        font=("Helvetica", 16),
        style="light"
    ).pack(side=ttkb.LEFT, padx=(16, 32))

    ttkb.Button(
        master=key_creation_prompt_frame,
        text="No, I'll do it myself.",
        cursor="hand1",
        style=stylize_btn("light.Outline", font_size=14),
        command=ROOT.destroy
    ).pack(side=ttkb.RIGHT, padx=(8, 16))

    def generate_master_key_and_restart():
        master_key = np.random.bytes(32)
        with open("MASTER_KEY", "wb") as file:
            file.write(master_key)
        prompt.destroy()
        start(master_key)

    ttkb.Button(
        master=key_creation_prompt_frame,
        text="Yes, please!",
        cursor="hand1",
        style=stylize_btn("info.Outline", font_size=14),
        command=generate_master_key_and_restart
    ).pack(side=ttkb.RIGHT, padx=(16, 8))

    key_creation_prompt_frame.pack(pady=(64, 64))

    prompt.pack(fill="none", expand=True)


def create_upload_page():
    global UPLOAD_PAGE
    __create_filepath_browse_frame(master=UPLOAD_PAGE, entry_tvar=UPLOAD_FILEPATH).pack(pady=[100, 20])
    __create_upload_buttons_frame(master=UPLOAD_PAGE).pack(pady=[20, 100])


def create_download_page():
    global DOWNLOAD_PAGE
    browse_and_download_frame = ttkb.Frame(master=DOWNLOAD_PAGE)

    __create_filepath_browse_frame(
        master=browse_and_download_frame,
        entry_tvar=DOWNLOAD_FILEPATH,
        width=60
    ).pack(side=ttkb.TOP, pady=20)

    download_btn = ttkb.Button(
        browse_and_download_frame,
        width=24,
        cursor="hand1",
        text="Download Selected File",
        style=stylize_btn("success.Outline")
    )
    download_btn.pack(side=ttkb.BOTTOM, pady=20)

    browse_and_download_frame.pack(expand=True, side=ttkb.LEFT, padx=20)

    file_list_frame = ttkb.Frame(master=DOWNLOAD_PAGE)

    tree_view_frame = ttkb.Frame(master=file_list_frame)

    tree_view_scrollbar = ttkb.Scrollbar(master=tree_view_frame)
    tree_view_scrollbar.pack(side=ttkb.RIGHT, fill=ttkb.Y)

    tree_view = ttkb.Treeview(
        master=tree_view_frame,
        selectmode="browse",
        yscrollcommand=tree_view_scrollbar.set
    )
    tree_view['columns'] = ["Files"]
    tree_view.column("#0", width=0, minwidth=0, stretch=ttkb.NO)
    tree_view.heading("#0", text="")
    tree_view.column("Files", anchor=ttkb.W, width=360, minwidth=360)
    tree_view.heading("Files", anchor=ttkb.W, text="Files")
    tree_view.pack(side=ttkb.LEFT)

    tree_view_scrollbar.configure(command=tree_view.yview)

    tree_view_frame.pack(side=ttkb.TOP, pady=20)

    def populate_file_list():
        refresh_list_btn['state'] = ttkb.DISABLED
        refresh_list_btn.configure(style=stylize_btn("dark", font_size=14))
        tree_view.delete(*tree_view.get_children())
        files = ftp_client.get_file_list()
        for i, file in enumerate(files):
            tree_view.insert(parent='', index='end', iid=i, text='', values=file)
        refresh_list_btn.configure(style=stylize_btn("info.Outline", font_size=14))
        refresh_list_btn['state'] = ttkb.NORMAL

    refresh_list_btn = ttkb.Button(
        master=file_list_frame,
        cursor="hand1",
        width=24,
        text="Refresh List",
        style=stylize_btn("info.Outline", font_size=14),
        command=lambda: threading.Thread(target=populate_file_list).start()
    )
    refresh_list_btn.pack(side=ttkb.BOTTOM, pady=20)

    def get_selected_item():
        selected_item_index = tree_view.selection()
        if len(selected_item_index) != 0:
            return tree_view.item(selected_item_index)['values'][0]

    download_btn.configure(command=lambda: print(get_selected_item()))

    file_list_frame.pack(side=ttkb.RIGHT, expand=True, fill="none", padx=20)
    threading.Thread(target=populate_file_list).start()


def start(master_key: np.ndarray):
    """
    Packs the base frames/widgets and starts the main loop of the GUI
    """

    if master_key is None:
        __create_missing_master_key_prompt()

    else:
        global MASTER_KEY, UPLOAD_PAGE, DOWNLOAD_PAGE
        MASTER_KEY = master_key
        notebook = ttkb.Notebook(master=ROOT, width=WIDTH, height=HEIGHT)
        UPLOAD_PAGE = ttkb.Frame(master=notebook)
        DOWNLOAD_PAGE = ttkb.Frame(master=notebook)
        create_upload_page()
        create_download_page()
        notebook.add(UPLOAD_PAGE, text='Upload')
        notebook.add(DOWNLOAD_PAGE, text='Download')
        notebook.pack()

    ROOT.mainloop()

# TODO: Modularize this monolothic disasterpiece
