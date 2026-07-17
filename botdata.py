class Record():
    def __init__(self, id, recordType: str = None, **kwargs):
        if not recordType:
            recordType = 'default'
        self.__id = str(id)
        self.__type = recordType
        self.__data = kwargs
    @property
    def key(self):
        return f'{self.__id}:{self.__type}'
    @property
    def value(self):
        return self.__data
    @value.setter
    def value(self, kwargs):
        self.__data = kwargs
class Memory():
    def __init__(self, *args: list[Record]):
        self.__value = {}
        for r in args:
            self.write(r)
    def __len__(self): return len(self.__value)
    def write(self, record: Record):
        self.__value[record.key] = record.value
    def read(self, record: Record):
        return self.__value[record.key]
    def pop(self, item: Record):
        self.__value.pop(item.key)
    def records(self, id):
        id = str(id)
        records = list()
        for k, v in self.__value:
            i = k.index(':')
            type = k[i+1:]
            records.append(Record(id, type, v))
        return self.records
    def __contains__(self, item: Record):
        return item.key in self.__value.keys()