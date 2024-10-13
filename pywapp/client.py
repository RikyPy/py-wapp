import os
import asyncio
from typing import Callable, Dict, List
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from time import sleep
from .utils import generateQR, MyThread
from .pywapp import Session, Messages
from .constants import SESSIONDIR, UNREAD_CONVERSATIONS
from .exceptions import GetDataError, NotLoggedInError, UnknownError, InvalidEventError, StaleElementReferenceError

async def check(driver: Chrome, canvasb64):
    # show img
    generateQR(canvasb64)
    while True:
        try:
            parent_div = driver.find_element(By.CSS_SELECTOR, '._ak96')
            child_div = parent_div.find_element(By.CSS_SELECTOR, '._akau')
            data_ref_value = child_div.get_attribute('data-ref')
        except:
            break # login page disappeared
        canvasb64new = data_ref_value
        if canvasb64 != canvasb64new:
            canvasb64 = canvasb64new
            try:
                os.remove('qrcode.png')
            except:
                pass
            #show img
            generateQR(canvasb64new)
        sleep(5)

class WhatsAppClient:

    global driver

    _callbacks: Dict[str, Callable] = {
        "on_ready": None,
        "on_message": None
    }

    _threads: Dict[str, MyThread] = {
        "on_message": None
    }

    def __init__(self, headless: bool, saveSession: bool) -> None:
        self.headless = headless
        self.saveSession = saveSession
    
    def start(self):
        global driver
        opt = ChromeOptions()
        opt.add_experimental_option("detach", True)
        opt.add_argument("--ignore-certificate-errors")
        opt.add_argument('--disable-proxy-certificate-handler')
        opt.add_argument('--ignore-certificate-errors-spki-list')
        opt.add_argument('--ignore-ssl-errors')
        if self.headless:
            opt.add_argument('--headless')
        if self.saveSession:
            opt.add_argument(f'user-data-dir={SESSIONDIR}')
        chrome_driver = ChromeDriverManager().install()
        driver = Chrome(service=Service(chrome_driver), options=opt)
        # driver.maximize_window()
        driver.get('https://web.whatsapp.com')

        try:
            # wait qrcode load
            for _ in range(5):
                sleep(2)
                try:
                    parent_div = driver.find_element(By.CSS_SELECTOR, "._ak96")
                    child_div = parent_div.find_element(By.CSS_SELECTOR, '._akau')
                    data_ref_value = child_div.get_attribute('data-ref')
                except:
                    data_ref_value = None
            if not data_ref_value:
                # Check if already logged in
                if Session.isLoggedIn(SESSIONDIR, driver):
                    pass
                else:
                    raise GetDataError('Error: unable to get qrcode data.')
            else:
                # show img
                asyncio.run(check(driver=driver, canvasb64=data_ref_value))

        except ValueError as e:
            raise UnknownError(e)
        
        self._add_thread("on_ready", self._on_ready)
        self._add_thread("on_message", self._on_message)

        # Start the threads
        for thread in self._threads.values():
            thread.start()

    @property
    def unread_messages(self) -> List[UnreadMessage]:
        """Returns the list of unread messages in the conversations page.

        #### Returns
            * List[UnreadMessage]: List of unread messages.
        """

        return [UnreadMessage(self, element) for element in driver.find_elements(By.CSS_SELECTOR, UNREAD_CONVERSATIONS)]

    def send_message(self, number, message):
        if not Session.isLoggedIn(SESSIONDIR, driver):
            raise NotLoggedInError('Before sending a message you need to log in.')
        safeNumber = str(number).replace(' ', '').replace('+', '').replace('-', '').replace('@c.us', '')
        driver.get(f'https://web.whatsapp.com/send?phone={safeNumber}')

        Messages.sendMessage(message, driver)
    
    def event(self, func: Callable):
        if func.__name__ not in self._callbacks.keys():
            raise InvalidEventError(f"Invalid event: {func.__name__}")

        self._callbacks[func.__name__] = func

    def _add_thread(self, name: str, target: Callable, daemon: bool = True) -> None:
        self._threads[name] = MyThread(target=target, daemon=daemon)

    def _start_thread(self, name: str) -> None:
        self._threads[name].start()

    def _stop_thread(self, name: str) -> None:
        self._threads[name].stop()
        self._threads.pop(name)

    def _on_ready(self) -> None:
        """Calls the on_ready callback when the page is loaded."""

        if not self._callbacks["on_ready"]:
            return

        self._callbacks["on_ready"]()

    def _on_message(self) -> None:
        """Checks for new messages and calls the on_message callback"""

        last_check = self.unread_messages

        while True:
            if self._threads["on_message"].stopped():
                break

            if not self._callbacks["on_message"]:
                continue

            try:
                unread = self.unread_messages
            except StaleElementReferenceError:
                continue

            for chat in unread:
                if chat not in last_check and chat.message is not None:
                    self._callbacks["on_message"](chat)

            last_check = unread
            sleep(1) # Wait 1 second before checking again