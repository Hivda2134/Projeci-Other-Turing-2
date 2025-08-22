class MyClass:
    """A simple example class."""
    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value

    def set_value(self, new_value):
        self.value = new_value

if __name__ == "__main__":
    obj = MyClass(10)
    print(obj.get_value())
    obj.set_value(20)
    print(obj.get_value())


