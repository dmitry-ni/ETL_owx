import unittest
from owlready2 import *
import types


DATA_FILE = 'file://./data/auto_part_fin.owx'

class TestOwlready2(unittest.TestCase):
  def test_read_ontology(self):
    onto = get_ontology(DATA_FILE).load()
    print(list(onto.classes()))
    print(list(onto.individuals()))

    with onto:
      class url(DataProperty): ...

      #class AutoManufacturer(Thing): pass
      #NewClass = types.new_class("NewClassName", (AutoManufacturer,))
      #types.new_class("NewClassName", (AutoManufacturer,))
      AutoManufacturer = types.new_class("AutoManufacturer", (Thing,))
      print(list(AutoManufacturer.subclasses()))
      Auto = types.new_class("ВАЗ", (AutoManufacturer,))
      m = Auto("test_model")
      m.price = 1000
      m.url = "test"
      

    #print(list(onto.classes()))                             
    onto.save(file = "./data/auto_part_tmp.owx", format = "rdfxml")

if __name__ == "__main__":
  unittest.main()