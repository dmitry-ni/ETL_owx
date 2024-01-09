
from ETL import AsiaCenter as AC

DATA_FILE = './data/asiacentr.com.ua_pricelist.xlsx'

if __name__ == '__main__':
  #extract data
  extract = AC.Extractor()
  extract.run(DATA_FILE)

  #transform data
  transformer = AC.Transformer()
  transformer.run(extract)

  #load data
  load = AC.Loader()
  load.run(transformer)
  

