from otscrape.core.base.page import Page


def ensure_dict(page):
    if isinstance(page, Page):
        data = page.get_data()
    elif isinstance(page, dict):
        data = page
    else:
        raise TypeError(f'type {type(page)} is not supported')

    return data
