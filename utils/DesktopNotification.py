import plyer
import pathlib
import os
from decorators.sneaky_throws import sneaky_throws

os.environ["DISPLAY"] = ":0"

pwd = pathlib.Path(__file__).parent.parent.resolve()


class DesktopNotification:

    icon_path = pwd.joinpath("data", "image", "icon.png").resolve().as_posix()

    @sneaky_throws
    def __init__(self, title: str, message: str):
        """
        Initializes a Birthday notification with the given title and message.

        Parameters:
            title (str): The title of the notification.
            message (str): The message body of the notification.

        Returns:
            None
"""
        plyer.notification.notify(
            title=title,
            message=message,
            app_name="Birthday",
            timeout=10,
            ticker="Happy Birthday",
            toast=True,
            app_icon=self.icon_path,
        )

        # Not working cause of X11 and cron job issue have to add cron user name to group of either video or x11 dont know much about .. 


if __name__ == "__main__":
    DesktopNotification("test", "test")
    print("done")
