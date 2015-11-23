import xml.etree.ElementTree as ET
import random
import uuid
import urllib2

class ValueType:
    Single = 1 # A single number
    Choice = 2 # A set of choices
    Range = 3  # A pair of min and max values


def CreateElementFromList(parentElement, elementName, valueType, valueList):
    e = ET.SubElement(parentElement, "Value")
    e.attrib["Name"] = elementName
    e.attrib["ValueType"] = str(valueType)
    if (len(valueList) == 1 ):
        e.text = str(valueList[0])
    else:
        e.text = ",".join(map(str, valueList))

class PropertyCreator(object):
    def __init__(self, *args, **kwargs):

        self.env_range_data_mapping = {"size": [-10,10],
                                       "pos": [-10,10],
                                       "mass": [-10,10],
                                       "roughness": [-10,10],
                                       "height": [-10,10],
                                       "length": [-10,10]}

        self.property_range_data_mapping = {"speed": [-10,10],
                                            "force": [-10,10]}

        self.choice_data_mapping = {"action": ["Move", "Climb", "Push", "Pull",
                                               "Click", "Press", "TakePhoto", "LookAt",
                                               "Break", "Swing", "Punch", "Wave"],
                                    "direction": ["F", "B", "L", "R"]}
        return super(PropertyCreator, self).__init__(*args, **kwargs)

    @staticmethod
    def CreateRange(parent, name, min = 0, max = 10):
        e = ET.SubElement(parent, "Value")
        e.attrib["Name"] = name
        e.attrib["ValueType"] = str(ValueType.Range)
        num1 = random.randrange(min, 0, 2)
        num2 = random.randrange(0, max, 2)
        e.text = "{},{}".format(num1, num2)

    @staticmethod
    def CreateChoice(parent, name, choices, num):
        e = ET.SubElement(parent, "Value")
        e.attrib["Name"] = name
        e.attrib["ValueType"] = str(ValueType.Choice)
        item_list = random.sample(choices, num)
        e.text = ",".join(item_list)

class LibraryCreator(object):
    def __init__(self, *args, **kwargs):
        super(LibraryCreator, self).__init__(*args, **kwargs)
        self.library = ET.Element("Library")
        self.property_creator = PropertyCreator()

        self.LoadNames()

    def CreateLibrary(self):
        num_of_entries = 600
        for i in xrange(num_of_entries):
            self.RandomEntry()

    def LoadNames(self):
        word_site = "https://svnweb.freebsd.org/csrg/share/dict/words?view=co"

        response = urllib2.urlopen(word_site)
        txt = response.read()
        self.words = txt.splitlines()

    def RandomName(self):
        return random.choice(self.words)

    def RandomEntry(self):
        entry = ET.SubElement(self.library, "Entry")
        entry.attrib["ID"] = str(uuid.uuid4())

        conf = ET.SubElement(entry, "Configuration")
        conf.attrib["Name"] = self.RandomName()+"Bot"

        for x in xrange(random.randint(1,5)):
            behavior = ET.SubElement(entry, "Behavior")
            behavior.attrib["Name"] = self.RandomName()

        environment = ET.SubElement(entry, "Environment")
        environment.attrib["Name"] = self.RandomName()

        name_list = self.property_creator.env_range_data_mapping.keys()
        candidates = random.sample(name_list, random.randint(1,len(name_list)))
        if ("size" in candidates) and ("mass" not in candidates):
            candidates.append("mass") 
        for name in candidates:
            if name in ["size", "pos"]:
                for suffix in ["X","Y","Z"]:
                    PropertyCreator.CreateRange(environment, name+suffix,
                                                self.property_creator.env_range_data_mapping[name][0],
                                                self.property_creator.env_range_data_mapping[name][1])
            else:
                PropertyCreator.CreateRange(environment, name,
                                            self.property_creator.env_range_data_mapping[name][0],
                                            self.property_creator.env_range_data_mapping[name][1])

        properties = ET.SubElement(entry, "Property")
        name_list = self.property_creator.choice_data_mapping["action"]
        candidates = random.sample(name_list, random.randint(1,len(name_list)))
        PropertyCreator.CreateChoice(properties, "action", candidates, len(candidates))
        if "Move" in candidates:
            PropertyCreator.CreateChoice(properties, "direction",
                                         self.property_creator.choice_data_mapping["direction"],
                                         random.randint(1,4))
            PropertyCreator.CreateRange(properties, "speed",
                                        self.property_creator.property_range_data_mapping["speed"][0],
                                        self.property_creator.property_range_data_mapping["speed"][1])

    def SaveLibrary(self):
        tree = ET.ElementTree(self.library)
        with open("Library.xml","wb") as file_handle:
            tree.write(file_handle, encoding="utf-8", xml_declaration=True)


#library = ET.Element("Library")

#entry = ET.SubElement(library, "Entry")
#entry.attrib["ID"] = str(uuid.uuid4())
#conf = ET.SubElement(entry, "Configuration")
#conf.attrib["Name"] = "LoopBot"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "Forward"
#environment = ET.SubElement(entry, "Environment")
#environment.attrib["Name"] = "Door"
#CreateElementFromList(environment, "sizeX", ValueType.Range, [1,5])
#CreateElementFromList(environment, "sizeY", ValueType.Range, [1,5])
#CreateElementFromList(environment, "sizeZ", ValueType.Range, [1,1])
#CreateElementFromList(environment, "mass", ValueType.Range, [0,10])
#properties = ET.SubElement(entry, "Property")
#CreateElementFromList(properties, "action", ValueType.Choice, ["Move", "Push"])
#CreateElementFromList(properties, "speed", ValueType.Range, [3,5.5])
#CreateElementFromList(properties, "direction", ValueType.Choice, ["F"])

#entry = ET.SubElement(library, "Entry")
#entry.attrib["ID"] = str(uuid.uuid4())
#conf = ET.SubElement(entry, "Configuration")
#conf.attrib["Name"] = "LoopBot"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "Forward"
#environment = ET.SubElement(entry, "Environment")
#environment.attrib["Name"] = "Stairs"
#CreateElementFromList(environment, "sizeX", ValueType.Range, [4,5])
#CreateElementFromList(environment, "sizeY", ValueType.Range, [1,5])
#CreateElementFromList(environment, "sizeZ", ValueType.Range, [1,1])
#properties = ET.SubElement(entry, "Property")
#CreateElementFromList(properties, "action", ValueType.Choice, ["Move"])
#CreateElementFromList(properties, "speed", ValueType.Range, [1,2])
#CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "B"])

#entry = ET.SubElement(library, "Entry")
#entry.attrib["ID"] = str(uuid.uuid4())
#conf = ET.SubElement(entry, "Configuration")
#conf.attrib["Name"] = "SimpleCar"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "Forward"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "TurnRight"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "TurnLeft"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "Backward"
#environment = ET.SubElement(entry, "Environment")
#environment.attrib["Name"] = "Floor"
#CreateElementFromList(environment, "roughness", ValueType.Range, [0,0])
#properties = ET.SubElement(entry, "Property")
#CreateElementFromList(properties, "action", ValueType.Choice, ["Move"])
#CreateElementFromList(properties, "speed", ValueType.Range, [2,10])
#CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "L", "R", "B"])

#entry = ET.SubElement(library, "Entry")
#entry.attrib["ID"] = str(uuid.uuid4())
#conf = ET.SubElement(entry, "Configuration")
#conf.attrib["Name"] = "SwimBot"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "Forward"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "TurnRight"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "TurnLeft"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "Backward"
#environment = ET.SubElement(entry, "Environment")
#environment.attrib["Name"] = "Floor"
#CreateElementFromList(environment, "roughness", ValueType.Range, [0,0])
#environment = ET.SubElement(entry, "Environment")
#environment.attrib["Name"] = "Ceiling"
#CreateElementFromList(environment, "height", ValueType.Range, [5,10])
#properties = ET.SubElement(entry, "Property")
#CreateElementFromList(properties, "action", ValueType.Choice, ["Move"])
#CreateElementFromList(properties, "speed", ValueType.Range, [2,3])
#CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "L", "R", "B"])

#entry = ET.SubElement(library, "Entry")
#entry.attrib["ID"] = str(uuid.uuid4())
#conf = ET.SubElement(entry, "Configuration")
#conf.attrib["Name"] = "PhotoBot"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "TakePhoto"
#environment = ET.SubElement(entry, "Environment")
#environment.attrib["Name"] = "Target"
#CreateElementFromList(environment, "posX", ValueType.Range, [1,10])
#CreateElementFromList(environment, "posY", ValueType.Range, [-2,2])
#CreateElementFromList(environment, "posZ", ValueType.Range, [4,6])
#properties = ET.SubElement(entry, "Property")
#CreateElementFromList(properties, "action", ValueType.Choice, ["TakePhoto", "LookAt"])

#entry = ET.SubElement(library, "Entry")
#entry.attrib["ID"] = str(uuid.uuid4())
#conf = ET.SubElement(entry, "Configuration")
#conf.attrib["Name"] = "ClickBot"
#behavior = ET.SubElement(entry, "Behavior")
#behavior.attrib["Name"] = "Click"
#environment = ET.SubElement(entry, "Environment")
#environment.attrib["Name"] = "Target"
#CreateElementFromList(environment, "posX", ValueType.Range, [1,3])
#CreateElementFromList(environment, "posY", ValueType.Range, [-2,2])
#CreateElementFromList(environment, "posZ", ValueType.Range, [0,1])
#properties = ET.SubElement(entry, "Property")
#CreateElementFromList(properties, "action", ValueType.Choice, ["Press", "Click"])


if __name__ == "__main__":

    LC = LibraryCreator()


    print "Created new library"


