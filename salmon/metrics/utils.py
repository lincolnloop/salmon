import ast
import operator as op


class Transform(object):
    "Parse and evaluate un-trusted expression from string"
    # Lots of help from http://stackoverflow.com/a/9558001/116042
    # supported operators
    operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
                 ast.Div: op.truediv}

    def __init__(self, expr, value, timedelta):
        self.expr = expr
        self.value = value
        self.timedelta = timedelta

    def replace_variable(self, variable):
        """Substitute variables with numeric values"""
        if variable == 'x':
            return self.value
        if variable == 't':
            return self.timedelta
        raise ValueError("Invalid variable %s", variable)

    def result(self):
        """Evaluate expression and return result"""
        # Module(body=[Expr(value=...)])
        return self.eval_(ast.parse(self.expr).body[0].value)

    def eval_(self, node):
        if isinstance(node, ast.Name):
            # <variable>
            return self.replace_variable(node.id)
        if isinstance(node, ast.Num):
            # <number>
            return node.n
        if isinstance(node, ast.operator) and type(node) in self.operators:
            # <operator>
            return self.operators[type(node)]
        if isinstance(node, ast.BinOp):
            # <left> <operator> <right>
            return self.eval_(node.op)(self.eval_(node.left),
                                       self.eval_(node.right))
        raise TypeError(node)

