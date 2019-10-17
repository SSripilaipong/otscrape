import functools
import typing
import abc


class Page(abc.ABC):
    fields_meta = []
    skip_error = False

    def __init__(self, meta=None, parent=None):
        self.parent = parent  # type: PageReference

        meta = meta or {}
        assert set(meta.keys()) == set(self.fields_meta)
        self.meta = meta  # type: dict

    @property
    def reference(self):
        raise NotImplementedError()

    def _backtrack(self, reference):
        try:
            return self.backtrack(reference)
        except Exception as e:
            if not self.skip_error:
                raise e

    @staticmethod
    def backtrack(reference):
        return None  # type: PageReference


class ContentPage(Page, abc.ABC):
    def __init__(self, *args, **kwargs):
        super(ContentPage, self).__init__(*args, **kwargs)

        self.fields_data = self.get_fields()
        self._data = dict()

    def get_fields(self) -> tuple:
        fields = []
        for attr in dir(self):
            if attr.startswith('data_'):
                fields.append(attr[5:])
        return tuple(fields)

    @staticmethod
    def dtype(dtype_, default):
        def dec(func):
            @functools.wraps(func)
            def wraps(*args, **kwargs):
                result = func(*args, **kwargs)
                try:
                    result = dtype_(result)
                    return result
                except ValueError:
                    return default
            return wraps
        return dec

    @property
    def reference(self):
        return PageReference(self)

    @property
    def data(self) -> dict:
        if self._data:
            return self._data

        for field in self.fields_data:
            if field not in self._data:
                try:
                    d = self.__getattribute__(f'data_{field}')()
                except Exception as e:
                    if not self.skip_error:
                        raise e
                    d = None
                self._data[field] = d
        return self._data


class ListingPage(Page, abc.ABC):
    def __init__(self, *args, **kwargs):
        super(ListingPage, self).__init__(*args, **kwargs)

        self._state = {}
        self.buffer = []

    @property
    def reference(self):
        return PageReference(self, state=self._state.copy())

    @property
    def state_init(self):
        raise NotImplementedError()

    def _on_start(self):
        return self.on_start()

    def on_start(self):
        pass

    def _check_stop(self, state):
        try:
            stop = self.check_stop(state)
        except Exception as e:
            if not self.skip_error:
                raise e
            stop = False

        if stop:
            try:
                self._on_stop()
            except Exception as e:
                if not self.skip_error:
                    raise e
            raise StopIteration()

    def check_stop(self, state) -> bool:
        return False

    def _get_children(self, state) -> typing.List[Page]:
        try:
            children = self.get_children(state)
        except Exception as e:
            if not self.skip_error:
                raise e
            children = []
        for child in children:
            child.parent = self.reference
        return children

    def get_children(self, state) -> typing.List[Page]:
        raise NotImplementedError()

    def _update_state(self, state) -> dict:
        try:
            return self._update_state(state)
        except Exception as e:
            if not self.skip_error:
                raise e
            return state

    def update_state(self, state) -> dict:
        raise NotImplementedError()

    def _on_update(self, old, new):
        try:
            self.on_update(old, new)
            self._check_stop(new)
        except Exception as e:
            if not self.skip_error:
                raise e

    def on_update(self, old, new):
        pass

    def _on_stop(self):
        try:
            self.on_stop()
        except Exception as e:
            if not self.skip_error:
                raise e

    def on_stop(self):
        pass

    def load_buffer(self):
        results = self.get_children(self._state)
        self.buffer = list(results)

    def __iter__(self):
        self._state = self.state_init
        try:
            self._check_stop(self._state)
        except StopIteration:
            return iter(())

        self.buffer = []
        self._on_start()

        self.load_buffer()
        return self

    def __next__(self):
        if not self.buffer:
            old = self._state
            self._state = self._update_state(self._state)
            self._on_update(old, self._state)
            self.load_buffer()

        first = self.buffer[0]
        self.buffer = self.buffer[1:]
        return first


class PageReference:
    def __init__(self, page: Page, state: dict = None):
        self.meta = page.meta
        self.state = state

        self.object_id = id(page)

        if page.parent is not None:
            self.parent = page.parent
        else:
            self.parent = None
