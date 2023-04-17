import os
import logging
from datetime import datetime
try:
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive
except ImportError:
    if os.name == "nt":
        os.system("pip install -r requirement.txt")
    else:
        os.system("pip3 install -r requirement.txt")
    from pydrive.auth import GoogleAuth
    from pydrive.drive import GoogleDrive

CRED_FILE = os.path.join(os.path.dirname(__file__), "credentials.json")
FILE_PATH = os.path.join(os.path.dirname(__file__), "..", 'dates.json')
CLIENT_SECRET = os.path.join(os.path.dirname(__file__), "client_secrets.json")
logger_path = os.path.join(os.path.dirname(__file__), "..",  "logger.log")

logging.basicConfig(
    filename=logger_path,
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)

class GDrive:
    def  intiate(self):
        self.gauth = GoogleAuth()
        self.gauth.settings['client_config_file'] = CLIENT_SECRET
        if os.path.exists(CRED_FILE):
            self.gauth.LoadCredentialsFile(CRED_FILE)
        else:
            self.gauth.LocalWebserverAuth()
            self.gauth.SaveCredentialsFile(CRED_FILE)
        if self.gauth.credentials is None:
            self.gauth.LocalWebserverAuth()
            self.gauth.SaveCredentialsFile(CRED_FILE)
        if self.gauth.access_token_expired:
            self.gauth.Refresh()
            self.gauth.SaveCredentialsFile(CRED_FILE)

        self.drive = GoogleDrive(self.gauth)

        self.file_title = 'dates.json'

        self.file_list = self.drive.ListFile(
            {'q': f"title='{self.file_title}' and trashed=false"}).GetList()
        if len(self.file_list) == 0:
            self.file = self.drive.CreateFile({'title': self.file_title})
        else:
            self.file = self.file_list[0]

    def upload(self):
        if os.path.exists(FILE_PATH):
            local_file_modified_time = os.path.getmtime(FILE_PATH)
            remote_file_mod_time_str = self.file['modifiedDate']
            remote_file_modified_time = datetime.strptime(remote_file_mod_time_str, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
            logging.info(f"Local file modified time: {local_file_modified_time} during upload process.Remote file modified time: {remote_file_modified_time} during upload process.")
            if local_file_modified_time <= remote_file_modified_time:
                logging.info(f"File '{self.file_title}' is up to date on Google Drive. skipping upload.")
                return
        self.file.SetContentFile(FILE_PATH)
        self.file.Upload()

        logging.info(f"File '{self.file_title}' uploaded to Google Drive.")
        logging.info(f"Modified time of file on google drive after upload: { datetime.fromisoformat(self.file['modifiedDate'][:-1]).timestamp()} ")

    def download(self):
        self.intiate()
        if os.path.exists(FILE_PATH):
            local_file_modified_time = os.path.getmtime(FILE_PATH)
            remote_file_mod_time_str = self.file['modifiedDate']
            remote_file_modified_time = datetime.strptime(remote_file_mod_time_str, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp()
            logging.info(f"Local file modified time: {local_file_modified_time} during download process.Remote file modified time: {remote_file_modified_time} during download process.")
            if local_file_modified_time >= remote_file_modified_time:
                logging.info(f"File '{self.file_title}' is up to date on local. skipping download.")
                return False
        self.file.GetContentFile(FILE_PATH)

        while os.path.exists(FILE_PATH):
            break

        logging.info(f"File '{self.file_title}' downloaded from Google Drive.")
        return True
