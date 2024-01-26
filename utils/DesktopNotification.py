import plyer


class DesktopNotification:
    def __init__(self, title: str, message: str):
        plyer.notification.notify(title=title, message=message,app_name="Birthday",timeout=10,ticker="Happy Birthday",toast=True)




if __name__ == "__main__":
    DesktopNotification("test", "test")