__all__ = ["Chats"]

from .constants import *
from .waobject import WaObject
from selenium.webdriver.common.keys import Keys

class Chat(WaObject):
    def __init__(self, driver=None):
        super().__init__(driver)

    def open_chat_to(self, number, _shouldoutput=(True, True)):
        if _shouldoutput[0] and DEFAULT_SHOULD_OUTPUT:
            print(f'Opening chatroom to "{number}"', end="... ")
        self._search_and_open_chat_by_number(number)
        if _shouldoutput[1] and DEFAULT_SHOULD_OUTPUT:
            print(f'{STRINGS.CHECK_CHAR} Done')

    def send_message_to(self, number, message, _shouldoutput=(True, True), open=False):
        if _shouldoutput[0] and DEFAULT_SHOULD_OUTPUT:
            print(f'Sending message "{message}" to "{number}"...', end="... ")
        if open:
            self.open_chat_to(number)
        self._send_message(message)
        if _shouldoutput[1] and DEFAULT_SHOULD_OUTPUT:
            print(f'{STRINGS.CHECK_CHAR} Done')
    
    def _send_message(self, message):
        self._wait_for_an_element_to_be_clickable(SELECTORS.MESSAGE_INPUT_BOX).send_keys(message + Keys.ENTER)