import re
import shlex
from node import *

class InputError(Exception):
    pass

class QueryParser(object):
    """A factory to construct nodes from a query"""

    default_categories = {
            "o" : "oracle_text",
            "t" : "type_line",
            "c" : "colors",
            "ci" : "color_identity",
            "pow" : "power",
            "tou" : "toughness",
            "loy" : "loyalty", }

    def __init__(self, default_field="name", short_categories=None):
        self.node = None
        self.tokens = None
        self.query = None
        self.basic_regex = re.compile("(-?)([a-z_]*)([:><=]+)([^<=>]*)")
        self.default_field = default_field
        self.short_categories = short_categories
        if self.short_categories == None:
            self.short_categories = self.default_categories

    def parse(self, query):
        """Takes in a query, and outputs an equivalent node structure"""
        query = query.strip()
        self.node = AndNode()
        self.query = query.lower()
        try:
            self.tokens = self.tokenize()
            if len(self.tokens) == 0:
                self.node = Node()
                return
            return self.list_interpret(self.tokens)
        except Exception as e:
            print("Invalid input: {}\n{}".format(query, e))
            return ErrorNode()
    
    def tokenize(self):
        split = shlex.split(self.query)
        res = []
        lists = [res]
        while len(split) > 0:
            s = split.pop(0)
            if '(' in s or ')' in s:
                indices = [s.find('('), s.find(')')]
                index = min([x for x in indices if x != -1])
                pre = s[:index]
                post = s[index+1:] 
                if len(pre) > 0:
                    lists[-1].append(pre)
                if s[index] == '(':
                    lists.append([])
                else:
                    complete = lists.pop()
                    lists[-1].append(complete)
                if len(post) > 0:
                    split.insert(0, post)
            else:
                lists[-1].append(s)
        return res

    def string_interpret(self, string):
        # Base case - returns a node for the input token string
        m = self.basic_regex.match(string)
        if not m:
            res = ContainsNode(self.default_field, string)
        else:
            key = self.short_categories.get(m.group(2), m.group(2))
            if key in [ 'colors' ]:
                res = ColorNode(key, m.group(3), m.group(4))
            elif key in [ 'color_identity' ]:
                res = ColorIdentityNode(key, m.group(3), m.group(4))
            elif m.group(3) == "=":
                res = EqualsNode(key, m.group(4))
            elif m.group(3) == "<":
                res = LessThanNode(key, m.group(4))
            elif m.group(3) == "<=":
                res = OrNode()
                res.add_node(LessThanNode(key, m.group(4)))
                res.add_node(EqualsNode(key, m.group(4)))
            elif m.group(3) == ">":
                res = GreaterThanNode(key, m.group(4))
            elif m.group(3) == ">=":
                res = OrNode()
                res.add_node(GreaterThanNode(key, m.group(4)))
                res.add_node(EqualsNode(key, m.group(4)))
            else:
                res = ContainsNode(key, m.group(4))
        if string[0] == "-":
            res = NotNode([res])
        return res

    def list_interpret(self, ts):
        # Recursive case - returns a node for the input token string
        if not type(ts) == list:
            return self.string_interpret(ts)
        res_list = []
        while len(ts) > 0:
            if "or" in ts:
                index = ts.index("or")
                node = OrNode()
                node.add_node(self.list_interpret(ts[:index]))
                node.add_node(self.list_interpret(ts[index+1:]))
                res_list.append(node)
                ts = []
            elif ts[0] == "-":
                ts.pop(0)
                node = NotNode()
                node.add_node(self.list_interpret(ts.pop(0)))
                res_list.append(node)
            else:
                res_list.append(self.list_interpret(ts.pop(0)))
        return AndNode(res_list)
