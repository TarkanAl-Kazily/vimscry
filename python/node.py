import re
import math

def strToNum(s):
    try:
        val = float(s)
        if abs(val - int(val)) < 0.25:
            return int(s)
        return val
    except:
        return 0

class Node(object):
    """A trait that must be true"""

    def __init__(self):
        pass

    def verify(self, card):
        return True

    def __repr__(self):
        return "True"

    def __str__(self):
        return self.__repr__()

class ErrorNode(Node):
    """Always false"""
    def verify(self, card):
        return False

    def __repr__(self):
        return "False"

class ContainsNode(Node):

    parens_regex = re.compile(r"\([^)]*\)")

    def __init__(self, field, trait):
        self.field = field
        self.trait = trait

    def __repr__(self):
        res = "<{} Contains {}>".format(self.field, self.trait)
        return res

    def verify(self, card):
        c_field = card.get(self.field, None)
        if c_field is None:
            c_faces = card.get("card_faces", None)
            if c_faces is None:
                return False
            c_field = ""
            for face in c_faces:
                c_field += face.get(self.field, "")
        # Remove reminder text
        c_field, count = self.parens_regex.subn('', c_field)
        return self.trait in c_field.lower()

class AndNode(Node):
    """A set of nodes that all must be true"""

    def __init__(self, nodes=None):
        self.nodes = nodes
        if self.nodes is None:
            self.nodes = []

    def __repr__(self):
        if len(self.nodes) == 0:
            return "True"
        if len(self.nodes) == 1:
            return str(self.nodes[0])
        res = "And" + str(self.nodes)
        return res

    def add_node(self, node):
        self.nodes.append(node)

    def add_nodes(self, nodes):
        self.nodes += nodes

    def verify(self, card):
        for n in self.nodes:
            if not n.verify(card):
                return False
        return True

class OrNode(Node):
    """A set of nodes that at least one must be true"""

    def __init__(self, nodes=None):
        self.nodes = nodes
        if self.nodes is None:
            self.nodes = []

    def __repr__(self):
        if len(self.nodes) == 0:
            return "True"
        if len(self.nodes) == 1:
            return str(self.nodes[0])
        res = "Or" + str(self.nodes)
        return res

    def add_node(self, node):
        self.nodes.append(node)

    def add_nodes(self, nodes):
        self.nodes += nodes

    def verify(self, card):
        for n in self.nodes:
            if n.verify(card):
                return True
        return len(self.nodes) == 0

class NotNode(Node):
    """A modifier of a node that requires everything in it to be false"""

    def __init__(self, nodes=None):
        self.nodes = nodes
        if self.nodes is None:
            self.nodes = []

    def __repr__(self):
        res = "Not" + str(self.nodes)
        return res

    def add_node(self, node):
        self.nodes.append(node)

    def add_nodes(self, nodes):
        self.nodes += nodes

    def verify(self, card):
        for n in self.nodes:
            if n.verify(card):
                return False
        return True

class HasFieldNode(Node):
    """A node that is true as long as the card has the field"""

    def __init__(self, field):
        self.field = field

    def __repr__(self):
        res = "<HasField {}>".format(self.field)
        return res

    def verify(self, card):
        c_field = card.get(self.field, None)
        if c_field:
            return True
        c_faces = card.get("card_faces", None)
        if c_faces:
            for f in c_faces:
                if f.get(self.field, None):
                    return True
        return False

class LessThanNode(Node):
    """A node that checks that the field is less than a number"""

    def __init__(self, field, value):
        self.field = field
        self.value = strToNum(value)

    def __repr__(self):
        res = "<{} LessThan {}>".format(self.field, self.value)
        return res

    def verify(self, card):
        c_field = card.get(self.field, None)
        if c_field:
            return strToNum(c_field) < self.value
        c_faces = card.get("card_faces", None)
        if c_faces is None:
            return False
        c_fields = []
        for face in c_faces:
            c_field = face.get(self.field, None)
            if c_field:
                c_fields.append(c_field)
        for f in c_fields:
            if strToNum(f) < self.value:
                return True
        return False

class GreaterThanNode(Node):
    """A node that checks that the field is greater than a number"""

    def __init__(self, field, value):
        self.field = field
        self.value = strToNum(value)

    def __repr__(self):
        res = "<{} GreaterThan {}>".format(self.field, self.value)
        return res

    def verify(self, card):
        c_field = card.get(self.field, None)
        if c_field:
            return strToNum(c_field) > self.value
        c_faces = card.get("card_faces", None)
        if c_faces is None:
            return False
        c_fields = []
        for face in c_faces:
            c_field = face.get(self.field, None)
            if c_field:
                c_fields.append(c_field)
        for f in c_fields:
            if strToNum(f) > self.value:
                return True
        return False

class EqualsNode(Node):
    """A node that checks that the field is equal to a number"""

    def __init__(self, field, value):
        self.field = field
        self.value = strToNum(value)

    def __repr__(self):
        res = "<{} Equals {}>".format(self.field, self.value)
        return res

    def verify(self, card):
        c_field = card.get(self.field, None)
        if c_field:
            val = strToNum(c_field)
            return math.isclose(val, self.value, rel_tol=0.1)
        c_faces = card.get("card_faces", None)
        if c_faces is None:
            return False
        c_fields = []
        for face in c_faces:
            c_field = face.get(self.field, None)
            if c_field:
                val = strToNum(c_field)
                if math.isclose(val, self.value, rel_tol=0.1):
                    return True
        return False

class ColorNode(Node):
    """A node with special functionality for checking colors"""

    all_colors = "WUBRG"
    colorless = "C"

    def __init__(self, field, operator, value):
        self.field = field
        self.operator = operator
        self.value = value.upper()
        if self.value == self.colorless:
            self.value = ""

    def __repr__(self):
        res = "<{} Color {} {}>".format(self.field, self.operator, self.value)
        return res

    def verify(self, card):
        c_field = card.get(self.field, None)
        if not c_field is None:
            if self.operator == '<':
                return self._less(c_field)
            elif self.operator == '=':
                return self._equal(c_field)
            elif self.operator == '>':
                return self._greater(c_field)
            elif self.operator == '<=':
                return self._less(c_field) or self._equal(c_field)
            elif self.operator == '>=' or self.operator == ':':
                return self._greater(c_field) or self._equal(c_field)
        faces = card.get("card_faces", None)
        if faces is None:
            return False
        for f in faces:
            if self.verify(f):
                return True
        return False

    def _less(self, c_field):
        colors_present = []
        for c in c_field:
            if not c in self.value:
                return False
            colors_present.append(c)
        return len(colors_present) < len(self.value)

    def _equal(self, c_field):
        colors_present = []
        for c in c_field:
            if not c in self.value:
                return False
            colors_present.append(c)
        return len(colors_present) == len(self.value)

    def _greater(self, c_field):
        extra_colors = c_field
        for c in self.value:
            if not c in extra_colors:
                return False
            extra_colors.remove(c)
        return extra_colors > 0

class ColorIdentityNode(ColorNode):
    """A node with special functionality for checking color identity"""

    def __repr__(self):
        res = "<{} ColorIdentity {} {}>".format(self.field, self.operator, self.value)
        return res

    def verify(self, card):
        c_field = card.get(self.field, None)
        if not c_field is None:
            if self.operator == '<':
                return self._less(c_field)
            elif self.operator == '=':
                return self._equal(c_field)
            elif self.operator == '>':
                return self._greater(c_field)
            elif self.operator == '<=' or self.operator == ':':
                return self._less(c_field) or self._equal(c_field)
            elif self.operator == '>=':
                return self._greater(c_field) or self._equal(c_field)
        return False
