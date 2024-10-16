import platform
import subprocess

from .waobject import WaObject
from .constants import *

class Session(WaObject):
    def __init__(self, sessiondir=None, driver=None):
        super().__init__(driver)
        self.sessiondir = sessiondir
        if sessiondir == None:
            self.sessiondir = SESSIONDIR

    def generate_session(self, sessionfilename=None, shouldclosedriver=False,
                         shouldshowfilelocation=True, _shouldoutput=True):
        os.makedirs(self.sessiondir, exist_ok=True)
        if sessionfilename == None:
            sessionfilename = self._create_valid_session_file_name(self.sessiondir)
        else:
            sessionfilename = self._add_file_extension(sessionfilename)
        if True: # _shouldoutput and DEFAULT_SHOULD_OUTPUT
            print("Waiting for QR code scan", end="... ")
        self._wait_for_presence_of_an_element(SELECTORS.MAIN_SEARCH_BAR__SEARCH_ICON)
        if True: # _shouldoutput and DEFAULT_SHOULD_OUTPUT
            print(f'{STRINGS.CHECK_CHAR} Done')
        session = self.driver.execute_script(GET_SESSION)
        sessionfilelocation = os.path.realpath(os.path.join(self.sessiondir, sessionfilename))
        with open(sessionfilelocation, 'w',
                  encoding='utf-8') as sessionfile:
            sessionfile.write(str(session))
        if True: # _shouldoutput and DEFAULT_SHOULD_OUTPUT
            print('Your session file is saved to: ' + sessionfilelocation)
        if True: # shouldshowfilelocation
            self._show_file_location(self.sessiondir)
        if shouldclosedriver:
            self.driver.quit()

    def open_session(self, sessionfilename=None, wait=True, _shouldoutput=True):
        if sessionfilename == None:
            sessionfilename = self._get_last_created_session_file(self.sessiondir)
        else:
            sessionfilename = self._validate_session_file(sessionfilename, self.sessiondir)
        session = None
        with open(sessionfilename, "r", encoding="utf-8") as sessionfile:
            try:
                session = sessionfile.read()
            except:
                raise IOError('"' + sessionfilename + '" is invalid file.')
        if _shouldoutput and DEFAULT_SHOULD_OUTPUT:
            print("Injecting session", end="... ")
        self._wait_for_presence_of_an_element(SELECTORS.QR_CODE)
        self.driver.execute_script(
            PUT_SESSION,
            session,
        )
        self.driver.refresh()
        if wait:
            self._wait_for_presence_of_an_element(SELECTORS.MAIN_SEARCH_BAR)
        if _shouldoutput and DEFAULT_SHOULD_OUTPUT:
            print(f'{STRINGS.CHECK_CHAR} Done')

    def _add_file_extension(self, sessionfilename):
        return sessionfilename + ".wa" if sessionfilename[-3:] != ".wa" else sessionfilename

    def _create_valid_session_file_name(self, sessiondir):
        n = len(os.listdir(sessiondir))
        sessionfilename = "%02d" % n + ".wa"
        while os.path.exists(sessionfilename):
            n += 1
            sessionfilename = "%02d" % n + ".wa"
        sessionfilename = self._add_file_extension(sessionfilename)

        return sessionfilename

    def _get_last_created_session_file(self, sessiondir):
        if not os.path.exists(sessiondir):
            raise IOError('No session file is exists. Generate session file by using generate_session().')
        files = os.listdir(sessiondir)
        paths = [os.path.join(sessiondir, basename) for basename in files]
        sessionfilename = max(paths, key=os.path.getctime)
        if not os.path.exists(sessionfilename):
            raise IOError('No session file is exists. Generate session file by using generate_session().')
        return sessionfilename

    def _validate_session_file(self, sessionfilename, sessiondir):
        if sessionfilename[-3:] != ".wa":
            sessionfilename += ".wa"
        possible_paths = [
            os.path.join(sessiondir, sessionfilename), sessionfilename
        ]
        possibleSessionfilePath = None
        for path in possible_paths:
            if os.path.exists(path):
                possibleSessionfilePath = path
        if possibleSessionfilePath == None:
            raise IOError(
                f'Session file "{sessionfilename}" is not exist. Generate that session file by using generate_session(\'{sessionfilename}\')')
        return possibleSessionfilePath

    def _show_file_location(self, path):
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])

    def _is_logged_in(self):
        d = os.listdir(SESSIONDIR + "\\Default\\IndexedDB\\")
        found = False
        for dir in d:
            if dir.__contains__('web.whatsapp.com'):
                found = True
                break
        return found

    def _wait_util_logged_in(self):
        self._wait_for_presence_of_an_element(SELECTORS.MAIN_SEARCH_BAR__SEARCH_ICON)
        return True