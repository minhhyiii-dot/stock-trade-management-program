class HashTable:
    def __init__(self):
        self._capacity = 16
        self._size = 0
        self._buckets = []

        for i in range(self._capacity):
            self._buckets.append([])

    def _hash(self, key):
        if not isinstance(key, str):
            raise TypeError("HashTable key must be a string")

        index = 0

        for char in key:
            index = (index * 10 + ord(char)) % self._capacity

        return index

    def set(self, key, value):
        index = self._hash(key)
        bucket = self._buckets[index]

        for i in range(len(bucket)):
            if bucket[i][0] == key:
                bucket[i] = (key, value)
                return 
            
        bucket.append((key, value))
        self._size += 1 

        # for resizing the table
        load_factor = self._size / self._capacity
        if load_factor > 0.75:
            self._resize()
        

    def get(self, key, default=None):
        index = self._hash(key)
        bucket = self._buckets[index]

        for i in range(len(bucket)):
            if bucket[i][0] == key:
                return bucket[i][1]

        return default

    def __contains__(self, key):
        index = self._hash(key)
        bucket = self._buckets[index]

        for i in range(len(bucket)):
            if bucket[i][0] == key:
                return True
        return False

    def  __len__(self):
        return self._size

    def delete(self, key):
        index = self._hash(key)
        bucket = self._buckets[index]

        for i in range(len(bucket)):
            if bucket[i][0] == key:
                del bucket[i]
                self._size -= 1
                return
        raise KeyError(key)

    def items(self):
        for bucket in self._buckets:
            for pair in bucket:
                yield pair

    def values(self):
        for bucket in self._buckets:
            for pair in bucket:
                yield pair[1]

    # Resize HashTable 
    def _resize(self):
        old_buckets = self._buckets
        self._capacity = self._capacity * 2 
        self._buckets = []
        for i in range(self._capacity):
            self._buckets.append([])

        for old_bucket in old_buckets:
            for pair in old_bucket:
                index = self._hash(pair[0]) # re-calculate hash index
                bucket = self._buckets[index] # re-locate bucket posistion
                bucket.append(pair) # transfer data to new table

    @property
    def capacity(self):
        return self._capacity

    @property
    def load_factor(self):
        return self._size / self._capacity


