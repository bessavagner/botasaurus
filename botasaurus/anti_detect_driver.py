from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import  StaleElementReferenceException

from bs4 import BeautifulSoup
from datetime import datetime
from random import uniform
from time import sleep
from traceback import print_exc

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from lxml import etree

from .output import is_slash_not_in_filename


from .decorators_utils import  create_directory_if_not_exists
from .beep_utils import beep_input
from .local_storage_driver import LocalStorage
from .opponent import Opponent
from .utils import (
    read_file,
    relative_path,
    sleep_for_n_seconds,
    sleep_forever,
    document_query_selector,
    document_query_selector_all,
    is_display,
    Key,
    ATTR_SELECTOR,
    DISPATCH_ENTER,
    DISPATCH_ENTER_SELECTOR
)
from .wait import Wait
from .driver_about import AboutBrowser
from .accept_google_cookies import accept_google_cookies

                  

class AntiDetectDriver(webdriver.Chrome):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.about: AboutBrowser = None
        self.is_network_enabled = False
        self.close_proxy = False

    def get_by_current_page_referrer(self, link, wait=None):

        # selenium.common.exceptions.WebDriverException
        
        currenturl = self.current_url
        self.execute_script(f"""
                window.location.href = "{link}";
            """)
        
        # cleaned = link.replace("https://", "").replace("http://", "")
        changed = False
        while not changed:
            if currenturl != self.current_url:
                changed = True
            sleep(0.1)

        if wait is not None and wait != 0:
            sleep(wait)

    def js_click(self, element):
        self.execute_script("arguments[0].click();",  element)
    def get_elements_or_none_by_xpath(self: WebDriver, xpath,wait=Wait.SHORT):
        try:
            if wait is None:
                return self.find_elements(By.XPATH, xpath)
            else:
                WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))

                return self.find_elements(By.XPATH, xpath)
        except:
            return None



    def sleep(self, n):
        sleep_for_n_seconds(n)

    def prompt(self, text="Press Enter To Continue..."):
        if self.about:
            bp = self.about.beep
        else:
            bp = True

        return beep_input(text, bp)

    def short_random_sleep(self):
        sleep_for_n_seconds(uniform(2, 4))

    def long_random_sleep(self):
        sleep_for_n_seconds(uniform(6, 9))

    def sleep_forever(self):
        sleep_forever()

    def bs4(self) -> BeautifulSoup:
        return BeautifulSoup(self.page_source, 'html.parser')

    def get_bot_detected_by(self):

        pmx = self.get_element_or_none(
            "//*[text()='Please verify you are a human']", None)

        if pmx is not None:
            return Opponent.PERIMETER_X

        clf = self.get_element_or_none_by_selector("#challenge-running", None)
        if clf is not None:
            return Opponent.CLOUDFLARE

        return None

    def is_bot_detected(self):
        return self.get_bot_detected_by() is not None

    def get_element_or_none(self, xpath, wait=Wait.SHORT) -> WebElement:
        try:
            if wait is None:
                return self.find_element(By.XPATH, xpath)
            else:
                return WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.XPATH, xpath)))
        except:
            return None

    def get_element_or_none_by_selector(self: WebDriver, selector, wait=Wait.SHORT) -> WebElement:
        try:
            if wait is None:
                return self.find_element(By.CSS_SELECTOR, selector)
            else:
                return WebDriverWait(self, wait).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
        except:
            return None

    def get_element_by_id(self, id: str, wait=Wait.SHORT):
        cleaned = id.lstrip('#')
        return self.get_element_or_none_by_selector(f'[id="{cleaned}"]', wait)

    def get_element_or_none_by_text_contains(self, text, wait=Wait.SHORT):
        text = f'//*[contains(text(), "{text}")]'
        return self.get_element_or_none(text, wait)

    def get_element_or_none_by_text(self, text,wait=Wait.SHORT):
        text = f'//*[text()="{text}"]'

        return self.get_element_or_none(text, wait)

    def get_element_parent(element):
        return element.find_element(By.XPATH, "./..")

    def get_elements_or_none_by_selector(self: WebDriver, selector,wait=Wait.SHORT):
        try:
            if wait is None:
                return self.find_elements(By.CSS_SELECTOR, selector)
            else:
                WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

                return self.find_elements(By.CSS_SELECTOR, selector)
        except:
            return None


    
    def text(self: WebDriver, selector: str,   wait=Wait.SHORT):
        
        try:
            el = self.get_element_or_none_by_selector(
                    selector, wait)
            if el is None:
                return None

            return el.text
        except StaleElementReferenceException:
            return self.text(selector,wait)

    def text_xpath(self: WebDriver, xpath: str,   wait=Wait.SHORT):
        el = self.get_element_or_none(
                xpath, wait)
        if el is None:
            # print(f'Element with selector: "{selector}" not found')
            return None

        return el.text

    def link(self: WebDriver, selector: str,   wait=Wait.SHORT):
        el = self.get_element_or_none_by_selector(
                selector, wait)

        if el is None:
            # print(f'Element with selector: "{selector}" not found')

            return None

        return el.get_attribute("href")


    def exists(self: WebDriver, selector: str,   wait=Wait.SHORT):
        el = self.get_element_or_none_by_selector(
                selector, wait)

        if el is None:
            # print(f'Element with selector: "{selector}" not found')

            return False

        return True

    def scroll(self, selector: str,   wait=Wait.SHORT):
        element = self.get_element_or_none_by_selector(
                selector, wait)

        if (element) is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")

        if self.can_element_be_scrolled(element):
            self.execute_script("arguments[0].scrollBy(0, 10000)", element)
            return True
        else:
            return False

    def links(self: WebDriver, selector: str,   wait=Wait.SHORT):
        els = self.get_elements_or_none_by_selector(
                selector, wait)

        if els is None:
            # print(f'Element with selector: "{selector}" not found')
            return []
        
        def extract_links(elements):
                    def extract_link(el):
                            return el.get_attribute("href")

                    return list(map(extract_link, elements))

        links = extract_links(els)

        return links

    def type(self: WebDriver, selector: str, text: str,  wait=Wait.SHORT):
        input_el = self.get_element_or_none_by_selector(
                selector, wait)
        
        if input_el is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")
        
        input_el.send_keys(text)

    def click(self: WebDriver, selector, wait=Wait.SHORT):
        el = self.get_element_or_none_by_selector(
                selector, wait)
        
        if el is None:
            raise NoSuchElementException(f"Cannot locate element with selector: {selector}")
        
        self.js_click(el)

    
    def get_element_text(self, element):
        return element.get_attribute('innerText')

    def get_innerhtml(self, element):
        return element.get_attribute("innerHTML")

    def get_element_or_none_by_name(self, selector, wait=Wait.SHORT):
        try:
            if wait is None:
                return self.find_element(By.NAME, selector)
            else:
                return WebDriverWait(self, wait).until(
                    EC.presence_of_element_located((By.NAME, selector)))
        except:
            return None

    def scroll_site(self):
        self.execute_script(""" 
window.scrollBy(0, 10000);
""")

    def can_element_be_scrolled(self, element):
        # <=3 is a fix to handle floating point numbers
        result = not (self.execute_script(
            "return Math.abs(arguments[0].scrollTop - (arguments[0].scrollHeight - arguments[0].offsetHeight)) <= 3", element))
        return result

    def scroll_into_view(self, element):
        return self.execute_script("arguments[0].scrollIntoView()", element)

    def scroll_element(self, element):
        if self.can_element_be_scrolled(element):
            self.execute_script("arguments[0].scrollBy(0, 10000)", element)
            return True
        else:
            return False


    def get_cookies_dict(self):
        all_cookies = self.get_cookies()
        cookies_dict = {}
        for cookie in all_cookies:
            cookies_dict[cookie['name']] = cookie['value']
        return cookies_dict

    def get_local_storage_dict(self):
        storage = LocalStorage(self)
        return storage.items()

    def get_cookies_and_local_storage_dict(self):
        cookies = self.get_cookies_dict()
        local_storage = self.get_local_storage_dict()

        return {"cookies": cookies, "local_storage": local_storage}

    def add_cookies_dict(self, cookies):
        for key in cookies:
            self.add_cookie({"name": key, "value": cookies[key]})

    def add_local_storage_dict(self, local_storage):
        storage = LocalStorage(self)
        for key in local_storage:
            storage.set_item(key, local_storage[key])

    def add_cookies_and_local_storage_dict(self, site_data):
        cookies = site_data["cookies"]
        local_storage = site_data["local_storage"]
        self.add_cookies_dict(cookies)
        self.add_local_storage_dict(local_storage)

    def delete_cookies_dict(self):
        self.delete_all_cookies()

    def delete_local_storage_dict(self):
        self.execute_script("window.localStorage.clear();")
        self.execute_script("window.sessionStorage.clear();")

    def delete_cookies_and_local_storage_dict(self):
        self.delete_cookies_dict()
        self.delete_local_storage_dict()

    def organic_get(self, link,  wait=None, accept_cookies=False):
        return self.google_get(link, wait, accept_cookies)

    def google_get(self, link,  wait=None, accept_cookies=False):
        self.get("https://www.google.com/")
        if accept_cookies:
            accept_google_cookies(self)
        return self.get_by_current_page_referrer(link, wait)

    def get_google(self, accept_cookies=False):
        self.get("https://www.google.com/")
        if accept_cookies:
            accept_google_cookies(self)
        # self.get_element_or_none_by_selector('input[role="combobox"]', Wait.VERY_LONG)

    @property
    def local_storage(self):
        return LocalStorage(self)

    def get_links(self, search=None, wait=Wait.SHORT):

        def extract_links(elements):
            def extract_link(el):
                return el.get_attribute("href")

            return list(map(extract_link, elements))

        els = self.get_elements_or_none_by_selector("a", wait)

        links = extract_links(els)

        def is_not_none(link):
            return link is not None

        def is_starts_with(link):
            if search == None:
                return True
            return search in link

        return list(filter(is_starts_with, filter(is_not_none, links)))


    def execute_file(self, filename, *args):
        if not filename.endswith(".js"):
            filename = filename + ".js"
        content = read_file(filename)
        return self.execute_script(content, *args)
    def get_images(self, search=None, wait=Wait.SHORT):

        def extract_links(elements):
            def extract_link(el):
                return el.get_attribute("src")

            return list(map(extract_link, elements))

        els = self.get_elements_or_none_by_selector("img", wait)

        links = extract_links(els)

        def is_not_none(link):
            return link is not None

        def is_starts_with(link):
            if search == None:
                return True
            return search in link

        return list(filter(is_starts_with, filter(is_not_none, links)))

    def is_in_page(self, target, wait=None, raise_exception=False):

        def check_page(driver, target):
            if isinstance(target, str):
                return target in driver.current_url
            else:
                for x in target:
                    if x in driver.current_url:
                        return True
                return False

        if wait is None:
            return check_page(self, target)
        else:
            time = 0
            while time < wait:
                if check_page(self, target):
                    return True

                sleep_time = 0.2
                time += sleep_time
                sleep(sleep_time)

        if raise_exception:
            raise Exception(f"Page {target} not found")
        return False

    def save_screenshot(self, filename=datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + ".png"):
        try:

            if not filename.endswith(".png"):
                filename = filename + ".png"

            if is_slash_not_in_filename(filename):
                create_directory_if_not_exists("output/screenshots/")
                filename = f'output/screenshots/{filename}'
            filename = relative_path(
                    filename, 0)
            self.get_screenshot_as_file(
                filename)
            # print('Saved screenshot at {0}'.format(final_path))
        except:
            print_exc()
            print('Failed to save screenshot')
    
    def prompt_to_solve_captcha(self, more_rules=[]):
        print('')
        print('   __ _ _ _    _                          _       _           ')
        print('  / _(_) | |  (_)                        | |     | |          ')
        print(' | |_ _| | |   _ _ __      ___ __ _ _ __ | |_ ___| |__   __ _ ')
        print(r' |  _| | | |  | | `_ \    / __/ _` | `_ \| __/ __| `_ \ / _` |')
        print(' | | | | | |  | | | | |  | (_| (_| | |_) | || (__| | | | (_| |')
        print(r' |_| |_|_|_|  |_|_| |_|   \___\__,_| .__/ \__\___|_| |_|\__,_|')
        print('                                   | |                        ')
        print('                                   |_|                        ')
        print('')

        # print('General Rules of Captcha Solving')
        # print(' - Solve it Fast')

        # for t in more_rules:
        #     print(t)
        # print('- Solve it Fast')
        # print('1. If')

        return beep_input('Press fill in the captcha, the faster the less detectable, then press enter to continue ...', self.about.beep)

        # return beep_input('Press fill in the captcha and press enter to continue ...', self.about.beep)

    
    def _enable_network(self) -> None:
        if not self.is_network_enabled:
            self.is_network_enabled = True
            self.execute_cdp_cmd('Network.enable', {})

    def quit(self) -> None:
        if hasattr(self, 'close_proxy') and callable(self.close_proxy):
          self.close_proxy()
        super().quit()

        if hasattr(self, 'kill_chrome_by_pid') and callable(self.kill_chrome_by_pid):
          self.kill_chrome_by_pid()


class AntiDetectCrawler(AntiDetectDriver):

    def __init__(self, *args, timeout=20, **kwargs):
        super().__init__(*args, **kwargs)
        self.soup = None
        self.dom = None
        self.timeout = timeout

    def find(
        self,
        value: str,
        by: str = "id",
        expected_condition=EC.presence_of_element_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> WebElement:
        """
        Finds an element on the web page using the specified locator strategy
        and waits until the element is present.

        Parameters
        ----------
        value : str
            The value to search for, such as the ID, name, or XPath of the
            element.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition : Callable, default EC.presence_of_element_located
            The expected condition to wait for, such as the presence of the
            element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElement
            The first matching element found.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        if timeout is None:
            timeout = self.timeout
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        result = wait.until(expected_condition((ATTR_SELECTOR[by], value)))
        return result

    def find_all(
        self,
        value: str,
        by: str = "id",
        expected_condition=EC.presence_of_all_elements_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> list[WebElement]:
        """
        Finds all elements on the web page that match the specified locator
        strategy and waits until at least one element is present.


        Parameters
        ----------
        value : str
            The value to search for, such as the ID, name, or XPath of the
            elements.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition : Callable, default
        EC.presence_of_all_elements_located
            The expected condition to wait for, such as the presence of the
            elements.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        list[WebElement]
            A list of all matching elements found.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        return self.find(
            value,
            by,
            expected_condition,
            timeout,
            poll_frequency,
            ignored_exceptions
        )

    def xpath(
        self,
        value: str,
        expected_condition=EC.presence_of_all_elements_located,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ) -> list[WebElement]:
        """
        Finds all elements on the web page that match the specified XPath and
        waits until at least one element is present.


        Parameters
        ----------
        value : str
            The XPath expression to search for.
        expected_condition : Callable, default EC.presence_of_all_elements_located  # noqa E501
            The expected condition to wait for, such as the presence of the
            elements.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        list[WebElement]
            A list of all matching elements found.
        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        return self.find_all(
            value,
            "xpath",
            expected_condition,
            timeout,
            poll_frequency,
            ignored_exceptions
        )

    def send_to(
        self,
        element: WebElement,
        key: str | Key,
        expected_condition=EC.element_to_be_clickable,
        enter=False,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Sends a key to the specified web element and optionally presses the
        Enter key.


        Parameters
        ----------
        element : WebElement
            The web element to send the key to.
        key : str | Key
            The key or text to send to the element.
        expected_condition : Callable, default EC.element_to_be_clickable
            The expected condition to wait for before sending the key.
        enter : bool, default False
            Whether to press the Enter key after sending the key.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElement
            The element to which the key was sent.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element)).send_keys(key)
        if enter:
            element.send_keys(Key.enter)

    def send(
        self,
        element: WebElement,
        value: str,
        key: str | Key,
        by="id",
        expected_condition_element=EC.presence_of_element_located,
        expected_condition_send=EC.element_to_be_clickable,
        enter=False,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        element = self.find(
            value=value,
            by=by,
            expected_condition=expected_condition_element,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        self.send_to(
            element,
            key,
            expected_condition=expected_condition_send,
            enter=enter,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    def child(
        self,
        element: WebElement,
        value: str,
        by="id",
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds a child element of the specified web element using the specified
        locator strategy and waits until the element is visible.

        Parameters
        ----------
        element : WebElement
            The parent web element to find the child element within.
        value : str
            The value to search for, such as the ID, name, or XPath of the
            child element.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition : Callable, default EC.visibility_of
            The expected condition to wait for, such as the visibility of the
            child element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElement
            The first matching child element found.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        descendant = wait.until(
            lambda elem: element.find_element(ATTR_SELECTOR[by], value)
        )
        return descendant

    def child_by_class_name(
        self,
        element: WebElement,
        value: str,
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds a child element of the specified web element by class name and
        waits until the element is visible.

        Parameters
        ----------
        element : WebElement
            The parent web element to find the child element within.
        value : str
            The class name to search for.
        expected_condition : Callable, default EC.visibility_of
            The expected condition to wait for, such as the visibility of the
            child element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebElement
            The first matching child element found by class name.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        descendant = wait.until(
            lambda elem: element.find_element(
                ATTR_SELECTOR['class name'], value)
        )
        return descendant

    def children(
        self,
        element: WebElement,
        value: str,
        by="id",
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds all child elements of the specified web element using the
        specified locator strategy and waits until at least one element is
        visible.

        Parameters
        ----------
        element : WebElement
            The parent web element to find the child elements within.
        value : str
            The value to search for, such as the ID, name, or XPath of the
            child elements.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition : Callable, default EC.visibility_of
            The expected condition to wait for, such as the visibility of the
            child elements.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        list[WebElement]
            A list of all matching child elements found.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        offspring = wait.until(
            lambda elem: element.find_elements(ATTR_SELECTOR[by], value)
        )
        return offspring

    def children_by_class_name(
        self,
        element: WebElement,
        value: str,
        expected_condition=EC.visibility_of,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds all child elements of the specified web element by class name and
        waits until at least one element is visible.

        Parameters
        ----------
        element : WebElement
            The parent web element to find the child elements within.
        value : str
            The class name to search for.
        expected_condition : Callable, default EC.visibility_of
            The expected condition to wait for, such as the visibility of the
            child elements.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        list[WebElement]
            A list of all matching child elements found by class name.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element))
        offspring = wait.until(
            lambda elem: element.find_elements(
                ATTR_SELECTOR['class name'], value)
        )
        return offspring

    def click_element(
        self,
        element: WebElement,
        expected_condition=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Clicks on the specified web element after waiting for it to be
        clickable.

        Parameters
        ----------
        element : WebElement
            The web element to click on.
        expected_condition : Callable, default EC.element_to_be_clickable
            The expected condition to wait for before clicking the element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        wait.until(expected_condition(element)).click()

    def click(
        self,
        value: str,
        by="id",
        expected_condition_element=EC.presence_of_element_located,
        expected_condition_click=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Finds an element on the web page using the specified locator strategy
        and waits until the element is present, then clicks on it.

        Parameters
        ----------
        value : str
            The value to search for, such as the ID, name, or XPath of the
            element.
        by : str, default "id"
            The locator strategy to use, such as "id", "name", "xpath", etc.
        expected_condition_element : Callable, default EC.presence_of_element_located  #noqa E501
            The expected condition to wait for, such as the presence of the
            element.
        expected_condition_click : Callable, default EC.element_to_be_clickable
            The expected condition to wait for before clicking the element.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        element = self.find(
            value=value,
            by=by,
            expected_condition=expected_condition_element,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )
        self.click_element(
            element,
            expected_condition=expected_condition_click,
            timeout=timeout,
            poll_frequency=poll_frequency,
            ignored_exceptions=ignored_exceptions
        )

    def arrow_down_element(
        self,
        element: WebElement,
        n_times: int = 1,
        enter=False,
        expected_condition=EC.element_to_be_clickable,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException,)
    ):
        """
        Sends the down arrow key to the specified web element the specified
        number of times and optionally presses the Enter key.

        Parameters
        ----------
        element : WebElement
            The web element to send the down arrow key to.
        n_times : int, default 1
            The number of times to send the down arrow key.
        enter : bool, default False
            Whether to press the Enter key after sending the down arrow key.
        expected_condition : Callable, default EC.element_to_be_clickable
            The expected condition to wait for before sending the keys.
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Raises
        ------
        TimeoutException
            If the condition is not met within the specified timeout.
        """
        wait = self.wait(timeout, poll_frequency, ignored_exceptions)
        for _ in range(n_times):
            wait.until(expected_condition(element)).send_keys(Key.down)
        if enter:
            wait.until(expected_condition(element)).send_keys(Key.enter)

    def soup_of(
        self,
        element: WebElement,
        parser="html.parser",
        features="lxml",
        outer=True,
        **kwargs
    ):
        """
        Parses the inner or outer HTML of the specified web element using
        BeautifulSoup.

        Parameters
        ----------
        element : WebElement
            The web element to parse.
        parser : str, default "html.parser"
            The parser to use for parsing the HTML.
        features : str, default "lxml"
            The features to use for parsing the HTML.
        outer : bool, default True
            Whether to parse the outer HTML of the element. If False, the inner
            HTML is parsed.
        **kwargs : dict
            Additional keyword arguments to pass to the BeautifulSoup
            constructor.

        Returns
        -------
        BeautifulSoup
            A BeautifulSoup object representing the parsed HTML of the element.
        """
        type_attribute = "innerHTML"
        if outer:
            type_attribute = "outerHTML"

        return BeautifulSoup(
            element.get_attribute(type_attribute),
            parser=parser,
            features=features,
            **kwargs
        )

    def run(self, script, *args):
        """
        Executes the specified JavaScript script on the web page.

        Parameters
        ----------
        script : str
            The JavaScript script to execute.
        *args : tuple
            Arguments to pass to the JavaScript script.

        Returns
        -------
        Any
            The result of the script execution.
        """
        return self.execute_script(script, *args)

    def query_selector(self, selector: str):
        """
        Executes a JavaScript query selector on the web page and returns the
        first matching element.

        Parameters
        ----------
        selector : str
            The CSS selector to use for querying the web page.

        Returns
        -------
        WebElement
            The first matching element found by the query selector.
        """
        script = document_query_selector(selector)
        return self.run(script)

    def query_selector_all(self, selector: str):
        """
        Executes a JavaScript query selector on the web page and returns all
        matching elements.

        Parameters
        ----------
        selector : str
            The CSS selector to use for querying the web page.

        Returns
        -------
        list[WebElement]
            A list of all matching elements found by the query selector.
        """
        script = document_query_selector_all(selector)
        return self.run(script)

    def dispatch_enter(self, element: WebElement):
        """
        Dispatches an 'Enter' key event to the specified web element.

        Parameters
        ----------
        element : WebElement
            The web element to dispatch the 'Enter' key event to.

        Returns
        -------
        Any
            The result of the dispatched event.
        """
        return self.run(DISPATCH_ENTER, element)

    def dispatch_enter_selector(self, selector: str):
        """
        Dispatches an 'Enter' key event to the first element matching the
        specified CSS selector.

        Parameters
        ----------
        selector : str
            The CSS selector to use for querying the web page.

        Returns
        -------
        Any
            The result of the dispatched event.
        """
        return self.run(DISPATCH_ENTER_SELECTOR.format(selector))

    def make_soup(self, parser="html.parser", **kwargs):
        """
        Parses the current page source using BeautifulSoup with the specified
        parser.

        Parameters
        ----------
        parser : str, default "html.parser"
            The parser to use for parsing the HTML.
        **kwargs : dict
            Additional keyword arguments to pass to the BeautifulSoup
            constructor.

        Returns
        -------
        BeautifulSoup
            A BeautifulSoup object representing the parsed HTML of the current
            page.
        """
        return BeautifulSoup(self.page_source, parser=parser, **kwargs)

    def make_dom(self, soup_parser="html.parser", **kwargs):
        """
        Parses the current page source using lxml with the specified parser and
        returns an ElementTree object.

        Parameters
        ----------
        soup_parser : str, default "html.parser"
            The parser to use for parsing the HTML.
        **kwargs : dict
            Additional keyword arguments to pass to the lxml HTML constructor.

        Returns
        -------
        etree.ElementTree
            An ElementTree object representing the parsed HTML of the current
            page.
        """
        self.soup = self.make_soup(parser=soup_parser)
        self.dom = etree.HTML(str(self.soup), **kwargs)
        return self.dom

    def is_display(self, element: WebElement, value: str):
        """
        Checks if the specified web element is displayed with the given display
        value.

        Parameters
        ----------
        element : WebElement
            The web element to check the display property of.
        value : str
            The display value to check against, such as "block", "none", etc.

        Returns
        -------
        bool
            True if the element is displayed with the given value, False
            otherwise.
        """
        script = is_display(value)
        return self.run(script, element)

    def wait(
        self,
        timeout=None,
        poll_frequency=0.5,
        ignored_exceptions=(NoSuchElementException, )
    ):
        """
        Returns a WebDriverWait object that can be used to wait for a condition
        to be met.

        Parameters
        ----------
        timeout : int, optional
            The maximum time to wait for the condition to be met. If not
            specified, the default timeout is used.
        poll_frequency : float, default 0.5
            The frequency at which the condition is checked, in seconds.
        ignored_exceptions : tuple, default (NoSuchElementException,)
            Exceptions to ignore while waiting for the condition.

        Returns
        -------
        WebDriverWait
            A WebDriverWait object configured with the specified parameters.
        """
        if timeout is None:
            timeout = self.timeout
        return WebDriverWait(
            self, timeout, poll_frequency, ignored_exceptions
        )

    def switch_to_frame(self, value: str, by='id'):
        """
        Switches the web driver's focus to the frame specified by the given
        value and locator strategy.

        Parameters
        ----------
        value : str
            The value to search for, such as the ID, name, or XPath of the frame.  # noqa E501
        by : str, default 'id'
            The locator strategy to use, such as "id", "name", "xpath", etc.

        Raises
        ------
        TimeoutException
            If the frame is not found within the specified timeout.
        """
        self.wait().until(
            EC.frame_to_be_available_and_switch_to_it(
                (by, value)
            )
        )