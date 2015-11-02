import xml.etree.ElementTree as ET
from libraryToLTL import ValueType
from createMLibrary import CreateElementFromList 

def run():
    mapping = ET.Element("Mapping")

    prop = ET.SubElement(mapping, "Proposition")
    prop.attrib["Name"] = "_move"
    environment = ET.SubElement(prop, "Environment")
    environment.attrib["Name"] = "Floor"
    CreateElementFromList(environment, "roughness", ValueType.Range, [0,0])
    properties = ET.SubElement(prop, "Property")
    CreateElementFromList(properties, "action", ValueType.Choice, ["Move"])
    CreateElementFromList(properties, "speed", ValueType.Single, [3])
    CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "L", "R", "B"])

    prop = ET.SubElement(mapping, "Proposition")
    prop.attrib["Name"] = "push"
    environment = ET.SubElement(prop, "Environment")
    environment.attrib["Name"] = "Door"
    CreateElementFromList(environment, "sizeX", ValueType.Single, [3])
    CreateElementFromList(environment, "sizeY", ValueType.Single, [3])
    CreateElementFromList(environment, "sizeZ", ValueType.Single, [1])
    CreateElementFromList(environment, "mass", ValueType.Single, [5])
    properties = ET.SubElement(prop, "Property")
    CreateElementFromList(properties, "action", ValueType.Single, ["Push"])
    CreateElementFromList(properties, "direction", ValueType.Choice, ["F"])

    prop = ET.SubElement(mapping, "Proposition")
    prop.attrib["Name"] = "takePhoto"
    environment = ET.SubElement(prop, "Environment")
    environment.attrib["Name"] = "BookShelf"
    CreateElementFromList(environment, "posX", ValueType.Range, [3,7])
    CreateElementFromList(environment, "posY", ValueType.Range, [-1,1])
    CreateElementFromList(environment, "posZ", ValueType.Single, [5])
    properties = ET.SubElement(prop, "Property")
    CreateElementFromList(properties, "action", ValueType.Single, ["TakePhoto"])

    prop = ET.SubElement(mapping, "Proposition")
    prop.attrib["Name"] = "pressButton"
    environment = ET.SubElement(prop, "Environment")
    environment.attrib["Name"] = "Mouse"
    CreateElementFromList(environment, "posX", ValueType.Range, [1,2])
    CreateElementFromList(environment, "posY", ValueType.Range, [-1,1])
    CreateElementFromList(environment, "posZ", ValueType.Single, [1])
    properties = ET.SubElement(prop, "Property")
    CreateElementFromList(properties, "action", ValueType.Single, ["Press"])

    prop = ET.SubElement(mapping, "Proposition")
    prop.attrib["Name"] = "crawl"
    environment = ET.SubElement(prop, "Environment")
    environment.attrib["Name"] = "Ceiling"
    CreateElementFromList(environment, "height", ValueType.Single, [7])
    properties = ET.SubElement(prop, "Property")
    CreateElementFromList(properties, "action", ValueType.Single, ["Move"])
    CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "L", "R", "B"])

    prop = ET.SubElement(mapping, "Proposition")
    prop.attrib["Name"] = "climb"
    environment = ET.SubElement(prop, "Environment")
    environment.attrib["Name"] = "Stairs"
    CreateElementFromList(environment, "sizeX", ValueType.Single, [4])
    CreateElementFromList(environment, "sizeY", ValueType.Single, [3])
    CreateElementFromList(environment, "sizeZ", ValueType.Single, [1])
    properties = ET.SubElement(prop, "Property")
    CreateElementFromList(properties, "action", ValueType.Single, ["Move"])
    CreateElementFromList(properties, "direction", ValueType.Choice, ["F", "B"])



    tree = ET.ElementTree(mapping)

    with open("Mapping.xml","wb") as file_handle:
        tree.write(file_handle, encoding="utf-8", xml_declaration=True)
if __name__ == "__main__":
    run()
    print "Created new mapping"