from otscrape.core.base.page import Page


def ensure_dict(page):
    if isinstance(page, Page):
        data = page.get_data()
    elif isinstance(page, dict):
        data = page
    else:
        raise TypeError(f'type {type(page)} is not supported')

    return data


def ensure_page_iter(p):
    if isinstance(p, (list, tuple, set)):
        if all(isinstance(x, Page) for x in p):
            return p
        else:
            raise TypeError('All elements in the collection must be of type Page.')
    elif isinstance(p, Page):
        return [p]
    elif hasattr(p, '__iter__'):
        return p
    else:
        raise TypeError(f'Page of type {type(p)} is unexpected.')
