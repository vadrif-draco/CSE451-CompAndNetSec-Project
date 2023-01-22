import ftplib

__FTP_HOST = "172.174.106.14"
__FTP_PORT = 6060
__FTP_USER = "test"
__FTP_PASS = "password"


def upload(file_path, file_name):
    # file_name: the name of file you want to upload to the FTP server

    # connect to the FTP server
    ftp = ftplib.FTP()
    ftp.connect(__FTP_HOST)
    ftp.login(__FTP_USER, __FTP_PASS)

    # force UTF-8 encoding
    ftp.encoding = "utf-8"

    with open(file_path, "rb") as file:
        # use FTP's STOR command to upload the file
        ftp.storbinary(f"STOR {file_name}", file)

    # quit and close the connection
    ftp.quit()


def download(file_path, file_name):
    # file_name: the name of file you want to download from the FTP server

    # connect to the FTP server
    ftp = ftplib.FTP()
    ftp.connect(__FTP_HOST)
    ftp.login(__FTP_USER, __FTP_PASS)

    # force UTF-8 encoding
    ftp.encoding = "utf-8"

    with open(file_path, "wb") as file:
        # use FTP's RETR command to download the file
        ftp.retrbinary(f"RETR {file_name}", file.write)

    # quit and close the connection
    ftp.quit()
