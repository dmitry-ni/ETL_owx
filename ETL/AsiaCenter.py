import pandas as pd
import openpyxl
from dataclasses import dataclass
from owlready2 import *
import types
import re
from openai import OpenAI
import time


IN_ONTO_FILE = './data/auto_part_fin.owx'
OUT_ONTO_FILE = './data/auto_part_fill.owx'

AUTO_PART_LIMIT = 2

@dataclass
class Frame:
  name: str
  df: pd.DataFrame
  
@dataclass(frozen=True)
class AutoModel:
  name: str
  manufacturer: str

@dataclass(frozen=True)
class AutoPart:
  name: str
  sku: str
  price: str
  url: str 
  category: str

@dataclass(frozen=True)
class AutoPartManufacturer:
  name: str
  
  
AP_CATEGORIES = [
  'Тормозная система',
  'Запчасти двигателя',
  'Подвеска',
  'Коробка передач',
  'Охлаждение и отопление',
  'Электрика',
  'Кузов',
  'Смазки и жидкости',
  'Система выхлопа',
  'Рулевое управление',
  'Освещение',
]

class AutoPartCategorization:
  def __init__(self):
    api_key = os.environ["OPENAI_KEY"]
    self.openai_client = OpenAI(api_key=api_key)
    
    self.openai_assistant = self.openai_client.beta.assistants.create(
      instructions=f"Выбрать категорию автомобильной запчасти из следующего списка: {','.join(AP_CATEGORIES)}",
      model="gpt-3.5-turbo-0613",
      tools=[{"type": "code_interpreter"}]
    )
    
    self.openai_thread = self.openai_client.beta.threads.create()
    
    
  def get_category(self, auto_part: str)->str:
    #time.sleep(2) #for prevent request limit
    thread_message = self.openai_client.beta.threads.messages.create(
      thread_id=self.openai_thread.id,
      role="user",
      content=f"верни только категорию без лишних слов - {auto_part}",
    )
    
    run = self.openai_client.beta.threads.runs.create(
      thread_id=self.openai_thread.id,
      assistant_id=self.openai_assistant.id,
    )
    category = ''
    
    while run.status in ["queued", "in_progress"]:
      keep_retrieving_run = self.openai_client.beta.threads.runs.retrieve(
        thread_id=self.openai_thread.id,
        run_id=run.id
      )
      
      if keep_retrieving_run.status == "completed":
        all_messages = self.openai_client.beta.threads.messages.list(
          thread_id= self.openai_thread.id
        )

        #print(f"User: {thread_message.content[0].text.value}")
        #print(f"Assistant: {all_messages.data[0].content[0].text.value}")

        category = all_messages.data[0].content[0].text.value
        break
      elif keep_retrieving_run.status == "queued" or keep_retrieving_run.status == "in_progress":
        pass
      else:
        print(f"Run status: {keep_retrieving_run.status} - {keep_retrieving_run}")
        break
    
    return category



class Extractor:

  def __init__(self):
    self.frames: list[Frame] = []

  def run(self, file_path: str): 
    wb=openpyxl.load_workbook(file_path)
    for sheet in wb:
      data_rows = []
      for row in sheet.iter_rows(min_row=8, max_col=6):
        data_rows.append([cell.value for cell in row])
      self.frames.append(Frame(sheet.title, pd.DataFrame(data_rows)))
  

class Transformer:
  def __init__(self):
    self.auto_models: set[AutoModel] = set()
    self.auto_part_manufacturer: set[AutoPartManufacturer] = set()
    self.auto_parts: set[AutoPart] = set()
    
  def run(self, e: Extractor):
    
    def clean_str(s: str):
      s = re.sub(r"\s+", '_', s)
      s = re.sub(r"\-+", '_', s)
      s = re.sub(r"\"+", '', s)
      s.strip()
      return s
    
    a_p_c = AutoPartCategorization()
    
    for f in e.frames:
      auto_part_counter = 0
      for _, row in f.df.iterrows():
        if row.iloc[0]:
          a_m = AutoModel(name= clean_str(row.iloc[0]), manufacturer=clean_str(f.name))
          self.auto_models.add(a_m)
          
        if row.iloc[2]:
          a_p_m = AutoPartManufacturer(name= f"APM:{clean_str(row.iloc[2])}" )
          self.auto_part_manufacturer.add(a_p_m)

        if row.iloc[3] and auto_part_counter < AUTO_PART_LIMIT:
          category = a_p_c.get_category(row.iloc[3])
          print(f"Detail: {row.iloc[3]} - {category}")
          a_p = AutoPart(
            name=clean_str(row.iloc[3]),
            sku=clean_str(row.iloc[1]),
            price=clean_str(str(row.iloc[4])),
            url=clean_str(row.iloc[5]),
            category=clean_str(category)                           
          )
          self.auto_parts.add(a_p)
          
        auto_part_counter+=1
    
    print(f"Auto models: {len(self.auto_models)}")
    print(f"Auto part manufacturer: {len(self.auto_part_manufacturer)}")
        
    

class Loader:
  def run(self, t: Transformer):
    onto = get_ontology(IN_ONTO_FILE).load()
    with onto:
      class AutoManufacturer(Thing): pass
      class AutoPartManufacturer(Thing): pass
      class AutoPart(Thing): pass
      
      for a_m in t.auto_models:
        AutoModel = types.new_class(a_m.manufacturer, (AutoManufacturer,))
        auto_model = AutoModel(a_m.name)
        
      for a_p_m in t.auto_part_manufacturer:
        auto_part_manufacturer = AutoPartManufacturer(a_p_m.name)
        
      for a_p in t.auto_parts:
        AutoPartCategory = types.new_class(a_p.category, (AutoPart,))
        auto_part = AutoPartCategory(a_p.name)
        auto_part.sku = a_p.sku
        auto_part.price = a_p.price
        auto_part.url = a_p.url
                
    onto.save(file = OUT_ONTO_FILE, format = "rdfxml")