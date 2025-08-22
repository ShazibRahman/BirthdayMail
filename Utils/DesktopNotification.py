import subprocess
import pathlib
import os

os.environ["DISPLAY"] = ":0"
os.environ["DBUS_SESSION_BUS_ADDRESS"] = "unix:path=/run/user/1000/bus"  # Adjust UID if needed

pwd = pathlib.Path(__file__).parent.parent.resolve()


class DesktopNotification:
    icon_path = pwd.joinpath("data", "image", "icon.png").resolve().as_posix()

    def __init__(self, title: str, message: str):
        """
        Initializes a notification with the given title and message.

        Parameters:
            title (str): The title of the notification.
            message (str): The message body of the notification.
        """
        try:
            subprocess.run(["notify-send", title, message, "-i", self.icon_path, "-t", "10000"])
        except Exception as e:
            print(f"Error sending notification: {e}")


if __name__ == "__main__":
    DesktopNotification("test", "test")
    print("done")
