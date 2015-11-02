import xml.etree.ElementTree as ET

class ValueType:
    Single = 1 # A single number
    Choice = 2 # A set of choices
    Range = 3  # A pair of min and max values

class Configuration(object):
    def __init__(self, *args, **kwargs):
        super(Configuration, self).__init__(*args, **kwargs)
        self.name = ""

    def __str__(self):
        return "Configuration: {}".format(self.name)

class Behavior(object):
    def __init__(self, *args, **kwargs):
        super(Behavior, self).__init__(*args, **kwargs)
        self.name = ""

    def __str__(self):
        return "Behavior: {}".format(self.name)

class Environment(object):
    def __init__(self, *args, **kwargs):
        super(Environment, self).__init__(*args, **kwargs)
        self.name = ""
        self.value_list = []
        
    """
    For each value v1 in the given environment,
    there must exist at least one value v2 in this environment
    that satisfies v1
    """
    def satifies(self, otherEnv):
        for v1 in otherEnv.value_list:
            sat = False
            for v2 in self.value_list:
                b = v2.satifies(v1)
                if b:
                    sat = True
                    break
            if not sat:
                return False
        return True

    def __str__(self):
        return "Enviornment: {}\n{}".format(self.name,"\n".join(map(str,self.value_list)))

class Property(object):
    def __init__(self, *args, **kwargs):
        super(Property, self).__init__(*args, **kwargs)
        self.value_list = []

    """
    For each value v1 in the given property,
    there must exist at least one value v2 in this property
    that satisfies v1
    """
    def satifies(self, otherProperty):
        for v1 in otherProperty.value_list:
            sat = False
            for v2 in self.value_list:
                if v2.satifies(v1):
                     sat = True
                     break
            if not sat:
                return False
        return True

    def __str__(self):
        return "Property:\n" + "\n".join(map(str,self.value_list))

class Value(object):
    def __init__(self, *args, **kwargs):
        super(Value, self).__init__(*args, **kwargs)
        self.name = ""
        self.value_type = None
        self.value = None

    """
    Check if this value satisfies the given value
    To satisfy, this value needs to be a superset of the given value
    """
    def satifies(self, otherValue):
        if self.name == otherValue.name:
            if otherValue.value_type == ValueType.Single:
                if self.value_type == ValueType.Single:
                    return self.value[0] == otherValue.value[0]
                if self.value_type == ValueType.Range:
                    return ((self.value[0] <= otherValue.value[0]) & (self.value[1] >= otherValue.value[0]))
                if self.value_type == ValueType.Choice:
                    return otherValue.value[0] in self.value
                return False
            elif otherValue.value_type == ValueType.Choice:
                if self.value_type == ValueType.Choice:
                    for v in otherValue.value:
                        if v not in self.value:
                            return False
                else:
                    return False
            elif otherValue.value_type == ValueType.Range:
                if self.value_type == ValueType.Range:
                    if self.value[0] > otherValue.value[0]:
                        return False
                    if self.value[1] < otherValue.value[1]:
                        return False
                else:
                    return False

            return True

    def __str__(self):
        if (len(self.value) == 1):
            text = str(self.value[0])
        else:
            text = ",".join(map(str, self.value))
        return "Value: {} -- {} -- {}".format(self.name, self.value_type, text)

class LibraryEntry(object):
    def __init__(self, *args, **kwargs):
        super(LibraryEntry, self).__init__(*args, **kwargs)
        self.ID = ""
        self.conf = None
        self.behavior_list = []
        self.environment_list = []
        self.property = None

    """
    For each environment e1 in the given proposition,
    there must exist at least one environment e2 in this entry
    that satisfies e1
    For each property p1 in the given proposition,
    there must exist at least one property p2 in this entry
    that satisfies p1
    """
    def satifies(self, prop):
        for e1 in prop.environment_list:
            sat = False
            for e2 in self.environment_list:
                if e2.satifies(e1):
                    sat = True
                    break
            if not sat:
                return False

        return self.property.satifies(prop.property)

class Proposition(object):
    def __init__(self, *args, **kwargs):
        super(Proposition, self).__init__(*args, **kwargs)
        self.name = ""
        self.environment_list = []
        self.property = None

class MappingInterface(object):
    def __init__(self, mapping_path = "Mapping.xml", *args, **kwargs):
        super(MappingInterface, self).__init__(*args, **kwargs)
        self.mapping_ET_tree = ET.parse(mapping_path)
        self.prop_list = []

    def unpackMapping(self):
        mapping_ET = self.mapping_ET_tree.getroot()

        for prop_ET in mapping_ET:
            prop = Proposition()
            prop.name = prop_ET.attrib["Name"]

            for child in prop_ET:
                if child.tag == "Environment":
                    prop.environment_list.append(LibraryInterface.parseEnvironment(child))
                elif child.tag == "Property":
                    prop.property = LibraryInterface.parseProperty(child)

            self.prop_list.append(prop)
   
class LibraryInterface(object):
    def __init__(self, library_path="Library.xml", *args, **kwargs):
        super(LibraryInterface, self).__init__(*args, **kwargs)
        self.library_ET_tree = ET.parse(library_path)
        self.entry_list = []

    def unpackLibrary(self):
        library_ET = self.library_ET_tree.getroot()

        for entry_ET in library_ET:
            entry = LibraryEntry()
            entry.ID = entry_ET.attrib["ID"]

            for child in entry_ET:
                if child.tag == "Configuration":
                    entry.conf = LibraryInterface.parseConfiguraion(child)
                elif child.tag == "Behavior":
                    entry.behavior_list.append(LibraryInterface.parseBehavior(child))
                elif child.tag == "Environment":
                    entry.environment_list.append(LibraryInterface.parseEnvironment(child))
                elif child.tag == "Property":
                    entry.property = LibraryInterface.parseProperty(child)

            self.entry_list.append(entry)

    def printLibrary(self):
        for entry in self.entry_list:
            print entry.conf
            for b in entry.behavior_list:
                print b
            for e in entry.environment_list:
                print e
            print entry.property
            print

    @staticmethod
    def parseConfiguraion(data_ET):
        conf = Configuration()
        conf.name = data_ET.attrib["Name"]
        return conf

    @staticmethod
    def parseBehavior(data_ET):
        behavior = Behavior()
        behavior.name = data_ET.attrib["Name"]
        return behavior

    @staticmethod
    def parseEnvironment(data_ET):
        env = Environment()
        env.name = data_ET.attrib["Name"]
        for child in data_ET:
            env.value_list.append(LibraryInterface.parseValue(child))
        return env

    @staticmethod
    def parseProperty(data_ET):
        property = Property()
        for child in data_ET:
            property.value_list.append(LibraryInterface.parseValue(child))
        return property

    @staticmethod
    def parseValue(data_ET):
        value = Value()
        value.name = data_ET.attrib["Name"]
        value.value_type = int(data_ET.attrib["ValueType"])
        if value.value_type == ValueType.Choice:
            value.value = data_ET.text.split(',')
        elif value.value_type == ValueType.Single:
            try:
                value.value = [float(data_ET.text)]
            except ValueError:
                value.value = [data_ET.text]
        else:
            value.value = map(float, data_ET.text.split(','))
        return value

    def findEntryListWithPropMapping(self, prop):
        entry_list = []
        for entry in self.entry_list:
            if entry.satifies(prop):
                entry_list.append(entry)
        return entry_list






if __name__ == "__main__":
    LI = LibraryInterface()
    LI.unpackLibrary()
    MI = MappingInterface()
    MI.unpackMapping()

    for prop in MI.prop_list:
        print prop.name
        print LI.findEntryListWithPropMapping(prop)





