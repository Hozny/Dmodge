import shelve

class MicroDB():
    def __init__(self, file_name):
        self._file_name = file_name

    def get(self, key):
        with shelve.open(self._file_name, 'c') as shelf:
            if key in shelf:
                return shelf[key]
        return None
    
    def set(self, key, value):
        with shelve.open(self._file_name, 'c') as shelf:
            shelf[key] = value

    def get_all(self):
        """
        :returns: read-only copy of DB, writes to this will not persist
        """
        with shelve.open(self._file_name, 'c') as shelf:
            return dict(shelf)


