import os
import ftplib

__FTP_HOST = "172.174.106.14"
# __FTP_PORT = 6060
__FTP_USER = "test"
__FTP_PASS = "password"


def ftp_init() -> ftplib.FTP:
    ftp = ftplib.FTP()
    ftp.encoding = "utf-8"
    # ftp.set_debuglevel(2)
    ftp.connect(__FTP_HOST)
    ftp.login(__FTP_USER, __FTP_PASS)
    print(f"\n\nConnected...\n{ftp.getwelcome()}\n\n")
    return ftp


def get_file_list():
    ftp = ftp_init()
    file_list = ftp.nlst()
    return file_list


def upload(file_path, progress_update_hook=None):

    # connect to the FTP server
    ftp = ftp_init()

    # force UTF-8 encoding
    ftp.encoding = "utf-8"

    with open(file_path, "rb") as file:
        # use FTP's STOR command to upload the file
        if progress_update_hook:
            progress_update_hook(50)
        ftp.storbinary(f"STOR {os.path.basename(file_path)}", file)
        if progress_update_hook:
            progress_update_hook(80)

    if progress_update_hook:
        progress_update_hook(100)
    # quit and close the connection
    ftp.quit()


def download(save_file_path, target_file_name):
    # file_name: the name of file you want to download from the FTP server

    # connect to the FTP server
    ftp = ftp_init()

    with open(save_file_path, "wb") as file:
        # use FTP's RETR command to download the file
        ftp.retrbinary(f"RETR {target_file_name}", file.write)

    # quit and close the connection
    ftp.quit()
