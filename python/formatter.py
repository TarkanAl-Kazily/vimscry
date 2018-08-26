import textwrap

class FormatException(Exception):
    def __init__(self, message):
        self.message = message

class Formatter(object):
    """Provides functions to display error, list and card objects"""

    def __init__(self, obj, indent=4, width=70):
        self.obj = obj
        self.type = obj["object"]
        self.date = obj["date"]
        self.indent = ' ' * indent
        self.width = width

    def _str_error(self):
        res = "details: {} ".format(self.obj["details"])
        res += "({} {})".format(self.obj["status"], self.obj["code"])
        return res

    def _str_list(self):
        res = "query: {}\n".format(self.obj["query"])
        res += "total_cards: {}\n".format(self.obj["total_cards"])
        for c in self.obj["data"]:
            res += "{}{}\n".format(self.indent, c["name"])
        return res

    def _str_face(self, face):
        res = "{} {}\n".format(face["name"], face["mana_cost"])
        res += "{}\n".format(face["type_line"])
        oracle = face.get("oracle_text", None)
        if oracle:
            res += textwrap.fill(oracle, width=self.width)
            res += "\n"
        flavor = face.get("flavor_text", None)
        if flavor:
            res += '-' * (int(self.width/4)) + '\n'
            res += textwrap.fill(flavor, width=self.width)
            res += "\n"
        power = face.get("power", None)
        toughness = face.get("toughness", None)
        loyalty = face.get("loyalty", None)
        if power and toughness:
            res += "{}/{}\n".format(power, toughness)
        elif loyalty:
            res += "{}\n".format(loyalty)
        res += self.obj["scryfall_uri"] + "\n"
        return res

    def _str_card(self):
        res = None
        if "card_faces" in self.obj:
            res = self._str_face(self.obj["card_faces"][0])
            for face in self.obj["card_faces"][1:]:
                res += "-" * self.width + '\n'
                res += self._str_face(face)
        else:
            res = self._str_face(self.obj)
        return res

    def __str__(self):
        res = ""
        if self.type == "error":
            res = self._str_error()
        elif self.type == "list":
            res = self._str_list()
        elif self.type == "card":
            res = self._str_card()
        return res

    def __repr__(self):
        return self.obj.__repr__()

    def names(self):
        if self.type == "list":
            res = ""
            for card in self.obj["data"]:
                res += card["name"] + "\n"
            return res
        if self.type == "card":
            res = self.obj["name"] + "\n"
            return res
        raise FormatException("Must be a list or card")
