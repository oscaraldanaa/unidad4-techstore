class Specification:
    def is_satisfied_by(self, order):
        raise NotImplementedError

    def __and__(self, other):
        return AndSpec(self, other)
    def __or__(self, other):
        return OrSpec(self, other)
    def __invert__(self):
        return NotSpec(self)

class AndSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def is_satisfied_by(self, order):
        return (self.left.is_satisfied_by(order)
                and self.right.is_satisfied_by(order))

class OrSpec(Specification): 
    def __init__(self, left, right): 
        self.left, self.right = left, right
    def is_satisfied_by(self, order): 
        return (self.left.is_satisfied_by(order) 
                or self.right.is_satisfied_by(order))

class NotSpec(Specification): 
    def __init__(self, left): 
        self.left = left
    def is_satisfied_by(self, order): 
        return (not self.left.is_satisfied_by(order))