from playwright.sync_api import sync_playwright

_playwright = None
_browser = None


def get_browser():
    global _playwright, _browser

    if _browser is None:
        _playwright = sync_playwright().start()
        _browser = _playwright.chromium.launch(headless=True)

    return _browser