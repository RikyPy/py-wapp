from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from .client import WhatsAppClient
from .constants import UNREAD_BADGE, UNREAD_CONVERSATIONS, UNREAD_LAST_MESSAGE, UNREAD_TITLE


@dataclass(init=False)
class UnreadMessage:
    # TODO: Create pywapp.unread_messages
    """An unread chat. Should not be initialized directly, use `pywapp.unread_messages` instead.

    #### Properties
        * name (str): The name of the unread chat.
        * count (int): The count of the unread chat.
        * message (str): The last message of the unread chat.
    """

    _whatsapp: WhatsAppClient = field(repr=False)
    _element: WebElement = field(repr=False)
    
    name: str
    count: int
    message: str

    def __init__(self, _whatsapp: WhatsAppClient, _element: WebElement) -> None:
        self._whatsapp = _whatsapp
        self._element = _element

        self.name = _element.find_element(By.CSS_SELECTOR, UNREAD_TITLE).get_attribute("title")
        self.count = int(_element.find_element(By.CSS_SELECTOR, UNREAD_BADGE).text) or 1

        try:
            self.message = _element.find_element(By.CSS_SELECTOR, .UNREAD_LAST_MESSAGE).get_attribute("title")
            self.message = self.message[1:-1]
        except NoSuchElementException:
            self.message = None

    def reply(self, 
              message: str, 
              attatchments: List[str] = None, 
              type: Literal["auto", "document", "midia", "contact"] = "auto"
        ) -> chat.Chat | chat.Group:
        """Reply to the unread chat.

        #### Arguments
            * message (str): The message to reply with.
            * attatchments (List[str], optional): The attatchments to reply with. Defaults to None.
            * type (Literal["auto", "document", "midia", "contact"], optional): The type of the attatchments. Defaults to "auto".

        #### Returns
            * Chat | Group: The chat or group that the message was sent to.
        """

        chat = self._whatsapp.open(self.name)
        chat.send(message, attatchments, type)

        return chat