from . import session, chats

class Session:

    @staticmethod
    def generate_session(sessionfilename=None, sessiondir=None, driver=None, shouldclosebrowser=False,
                         shouldshowfilelocation=True) -> None:
        temp = session.Session(sessiondir, driver)
        temp.generate_session(sessionfilename, shouldclosebrowser, shouldshowfilelocation)

    @staticmethod
    def open_session(sessionfilename=None, sessiondir=None, driver=None, wait=True) -> None:
        temp = session.Session(sessiondir, driver)
        temp.open_session(sessionfilename, wait)

    @staticmethod
    def isLoggedIn(sessiondir, driver) -> bool:
        temp = session.Session(sessiondir, driver)
        return temp._is_logged_in()
    
class Messages:

    @staticmethod
    def sendMessage(message, driver):
        temp = chats.Chat(driver)
        temp._send_message(message)