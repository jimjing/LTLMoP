import xml.etree.ElementTree as ET
import uuid

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


library = ET.Element("Library")

entry = ET.SubElement(library, "Entry")
entry.attrib["ID"] = str(uuid.uuid4())
conf = ET.SubElement(entry, "Configuration")
conf.attrib["Name"] = "LoopBot"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "Forward"
environment = ET.SubElement(entry, "Environment")
environment.attrib["Name"] = "Door"
CreateElementFromList(environment, "sizeX", ValueType.Range, [1,5])
CreateElementFromList(environment, "sizeY", ValueType.Range, [1,5])
CreateElementFromList(environment, "sizeZ", ValueType.Range, [1,1])
CreateElementFromList(environment, "mass", ValueType.Range, [0,10])
properties = ET.SubElement(entry, "Property")
CreateElementFromList(properties, "action", ValueType.Choice, ["Move", "Push"])
CreateElementFromList(properties, "speed", ValueType.Range, [3,5.5])
CreateElementFromList(properties, "direction", ValueType.Choice, ["F"])

entry = ET.SubElement(library, "Entry")
entry.attrib["ID"] = str(uuid.uuid4())
conf = ET.SubElement(entry, "Configuration")
conf.attrib["Name"] = "LoopBot"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "Forward"
environment = ET.SubElement(entry, "Environment")
environment.attrib["Name"] = "Stairs"
CreateElementFromList(environment, "sizeX", ValueType.Range, [4,5])
CreateElementFromList(environment, "sizeY", ValueType.Range, [1,5])
CreateElementFromList(environment, "sizeZ", ValueType.Range, [1,1])
properties = ET.SubElement(entry, "Property")
CreateElementFromList(properties, "action", ValueType.Choice, ["Move"])
CreateElementFromList(properties, "speed", ValueType.Range, [1,2])
CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "B"])

entry = ET.SubElement(library, "Entry")
entry.attrib["ID"] = str(uuid.uuid4())
conf = ET.SubElement(entry, "Configuration")
conf.attrib["Name"] = "SimpleCar"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "Forward"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "TurnRight"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "TurnLeft"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "Backward"
environment = ET.SubElement(entry, "Environment")
environment.attrib["Name"] = "Floor"
CreateElementFromList(environment, "roughness", ValueType.Range, [0,0])
properties = ET.SubElement(entry, "Property")
CreateElementFromList(properties, "action", ValueType.Choice, ["Move"])
CreateElementFromList(properties, "speed", ValueType.Range, [2,10])
CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "L", "R", "B"])

entry = ET.SubElement(library, "Entry")
entry.attrib["ID"] = str(uuid.uuid4())
conf = ET.SubElement(entry, "Configuration")
conf.attrib["Name"] = "SwimBot"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "Forward"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "TurnRight"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "TurnLeft"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "Backward"
environment = ET.SubElement(entry, "Environment")
environment.attrib["Name"] = "Floor"
CreateElementFromList(environment, "roughness", ValueType.Range, [0,0])
environment = ET.SubElement(entry, "Environment")
environment.attrib["Name"] = "Ceiling"
CreateElementFromList(environment, "height", ValueType.Range, [5,10])
properties = ET.SubElement(entry, "Property")
CreateElementFromList(properties, "action", ValueType.Choice, ["Move"])
CreateElementFromList(properties, "speed", ValueType.Range, [2,3])
CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "L", "R", "B"])

entry = ET.SubElement(library, "Entry")
entry.attrib["ID"] = str(uuid.uuid4())
conf = ET.SubElement(entry, "Configuration")
conf.attrib["Name"] = "PhotoBot"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "TakePhoto"
environment = ET.SubElement(entry, "Environment")
environment.attrib["Name"] = "Target"
CreateElementFromList(environment, "posX", ValueType.Range, [1,10])
CreateElementFromList(environment, "posY", ValueType.Range, [-2,2])
CreateElementFromList(environment, "posZ", ValueType.Range, [4,6])
properties = ET.SubElement(entry, "Property")
CreateElementFromList(properties, "action", ValueType.Choice, ["TakePhoto", "LookAt"])

entry = ET.SubElement(library, "Entry")
entry.attrib["ID"] = str(uuid.uuid4())
conf = ET.SubElement(entry, "Configuration")
conf.attrib["Name"] = "ClickBot"
behavior = ET.SubElement(entry, "Behavior")
behavior.attrib["Name"] = "Click"
environment = ET.SubElement(entry, "Environment")
environment.attrib["Name"] = "Target"
CreateElementFromList(environment, "posX", ValueType.Range, [1,3])
CreateElementFromList(environment, "posY", ValueType.Range, [-2,2])
CreateElementFromList(environment, "posZ", ValueType.Range, [0,1])
properties = ET.SubElement(entry, "Property")
CreateElementFromList(properties, "action", ValueType.Choice, ["Press", "Click"])





tree = ET.ElementTree(library)

with open("Library.xml","wb") as file_handle:
    tree.write(file_handle, encoding="utf-8", xml_declaration=True)

print "Created new library"


