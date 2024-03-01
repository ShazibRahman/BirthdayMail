import plyer
import pathlib
import os 


os.environ["DISPLAY"] = ":0"

pwd = pathlib.Path(__file__).parent.parent.resolve()

class DesktopNotification:
    icon_path = pwd.joinpath("data", "image", "icon.png").resolve().as_posix()

    def __init__(self, title: str, message: str):
        plyer.notification.notify(
            title=title,
            message=message,
            app_name="Birthday",
            timeout=10,
            ticker="Happy Birthday",
            toast=True,
            app_icon=self.icon_path,
        )


if __name__ == "__main__":
    DesktopNotification("test", "test")
