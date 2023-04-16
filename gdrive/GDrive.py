import os
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


class GDrive:
    def __init__(self):
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
        self.file.SetContentFile(FILE_PATH)
        self.file.Upload()

        print(f"File '{self.file_title}' uploaded to Google Drive.")

    def download(self):
        self.file.GetContentFile(FILE_PATH)

        while os.path.exists(FILE_PATH):
            break

        print(f"File '{self.file_title}' downloaded from Google Drive.")
