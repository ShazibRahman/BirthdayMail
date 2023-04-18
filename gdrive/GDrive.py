import os
import logging
from datetime import datetime
import pytz
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
FILE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", 'dates.json')
CLIENT_SECRET = os.path.join(os.path.dirname(__file__), "client_secrets.json")
LOCAL_DATE_TIMEZONE = pytz.timezone("Asia/Kolkata")
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "data.json")

logger_path = os.path.join(os.path.dirname(
    __file__), "..", "data", "logger.log")

if not os.path.exists(logger_path):
    open(logger_path, "w").close()

logging.basicConfig(
    filename=logger_path,
    filemode="a",
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    datefmt="%m/%d/%Y %I:%M:%S %p",
)


class GDrive:
    def intiate(self):
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

    def upload(self, file_path=FILE_PATH):
        if os.path.exists(file_path) and len(self.file_list) > 0:
            local_file_modified_time = os.path.getmtime(file_path)

            if local_file_modified_time <= self.get_remote_modified_timestamp():
                logging.info(
                    f"File '{self.file_title}' is up to date on Google Drive. skipping upload.")
                return

        self.file_title = os.path.basename(file_path)

        self.file.SetContentFile(file_path)
        self.file.Upload()

        logging.info(
            f"File '{self.file_title} and {file_path}' uploaded to Google Drive.")

    def get_remote_modified_timestamp(self):
        remote_file_modified_time = datetime.strptime(
            self.file['modifiedDate'], '%Y-%m-%dT%H:%M:%S.%fZ')
        remote_file_modified_time = remote_file_modified_time.replace(
            tzinfo=pytz.utc)
        remote_file_modified_time = remote_file_modified_time.astimezone(
            LOCAL_DATE_TIMEZONE)
        return remote_file_modified_time.timestamp()

    def download(self, file_path=FILE_PATH):
        self.intiate()
        self.file_title = os.path.basename(file_path)

        self.file_list = self.drive.ListFile(
            {'q': f"title='{self.file_title}' and trashed=false"}).GetList()
        if len(self.file_list) == 0:
            self.file = self.drive.CreateFile(
                {'title': self.file_title})
        else:
            self.file = self.file_list[0]

        if os.path.exists(FILE_PATH):
            local_file_modified_time = os.path.getmtime(FILE_PATH) + 10
        try:
            if local_file_modified_time >= self.get_remote_modified_timestamp():
                logging.info(
                    f"File '{self.file_title}' is up to date on local. skipping download.")
                return False
        except:
            logging.info(f"File '{self.file_title}' is not present on remote.")
            return False
        self.file.GetContentFile(file_path)

        while os.path.exists(file_path):
            break

        logging.info(f"File '{self.file_title}' downloaded from Google Drive.")
        return True

    def download_by_id_and_file_format(self, file_path, file_id, mimetype):
        self.intiate()
        file = self.drive.CreateFile({'id': file_id})
        file.GetContentFile(file_path, mimetype=mimetype)
        logging.info(f"File '{file_path}' downloaded from Google Drive.")

    def download_data_file(self):
        self.download(DATA_PATH)

    def upload_data_file(self):
        self.upload(file_path=DATA_PATH)
