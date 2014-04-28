class Stack:
    def __init__(self):
        self.stack = []

    def __str__(self):
        return '[' + ', '.join(str(e) for e in self.stack) + ']'

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        try:
            to_return = self.stack[len(self.stack)-1]
            del self.stack[len(self.stack)-1]
            return to_return
        except IndexError:
            return 'Stack is empty.'
        
    def top(self):
        try:
            return self.stack[len(self.stack)-1]
        except IndexError:
            return 'There is no top; the stack is empty.'


if __name__ == '__main__':
    a = Stack()
    
    # pushes
    a.push(1)
    a.push(2)
    a.push(3)
    print a
    
    # pops
    print a.pop()
    print a.pop()

    # top
    print a.top()
    
    
