# !pip install pdfplumber
import pdfplumber
import re
import pandas as pd
import os
import numpy as np

os.chdir('/content/drive/MyDrive/Python/Projetos/BD/Política Internacional')
book_path = 'Cronologia das Relações Internacionais do Brasil.pdf'
text_path = 'cronologia_raw.txt'

def process_text(book_path: str) -> str:
  raw_text = ""
  with pdfplumber.open(book_path) as pdf:
      for i in range(9, 253):
        page = pdf.pages[i]
        raw_text += (page.extract_text(layout=True) or '')
  text = re.sub(r' +', ' ', raw_text)

  with open(text_path, "w") as file:
      file.write(text)

def read_text_file(text_path: str) -> str:
  with open(text_path, 'r', encoding = 'utf-8') as file:
    text = file.read()
  return text

def get_yearly_data(text: str) -> list:
  pattern = re.compile(r'[\n ]{4}\d{4}\s')
  matched_indices = [match.start() for match in re.finditer(pattern, text)]

  yearly_data = []
  for i, idx in enumerate(matched_indices):
    if i == 0:
      yearly_data.append(text[:idx])
    if (i != len(matched_indices) - 1):
      yearly_data.append(text[idx:matched_indices[i+1]])
    else:
      yearly_data.append(text[idx:])
  return yearly_data

def get_event_data(year_data: list, year_event: dict) -> dict:
  pattern = re.compile(r'[. ]\n \n ')
  matched_indices = [match.start() for match in re.finditer(pattern, year_data)]

  event_data = []
  for i, idx in enumerate(matched_indices):
    if i == 0:
      txt = year_data[:idx].replace('\n ',' ').strip().replace('  ',' ').strip()
      if len(txt) >= 4:
        year = txt[:5]
        event_data.append(txt[5:])
    if (i != len(matched_indices) - 1):
      txt = year_data[idx:matched_indices[i+1]].replace('\n ',' ').strip().replace('  ',' ').strip()
      if len(txt) >=4:
        event_data.append(txt)
    else:
      txt = year_data[idx:].replace('\n ',' ').strip().replace('  ',' ').strip()
      if len(txt) >= 4:
        event_data.append(txt)

  if len(event_data) == 0:
    txt = year_data.replace('\n ',' ').strip().replace('  ',' ').strip()
    year = txt[:5].strip()
    event_data.append(txt[5:])

  try:
    year_event[int(year)] = event_data
  except:
    pass
  return year_event

def make_dataframe(text: str) -> pd.DataFrame:
  yearly_data = get_yearly_data(text)
  year_event = {}
  for year_data in yearly_data:
    year_event = get_event_data(year_data, year_event)

  df = pd.DataFrame()
  for year, events in year_event.items():
    year_df = pd.DataFrame({'ano': len(events)*[(year)],
                            'evento': events})
    df = pd.concat([df, year_df])
  return df.reset_index(drop=True)

def adjust_dataframe(df: pd.DataFrame) -> pd.DataFrame:
  mask = df['evento'].str.startswith('.')
  if mask.any():
    df.loc[mask, 'evento'] = df.loc[mask, 'evento'].str[1:].str.strip()

  mask = ~df['evento'].str.endswith('.')
  if mask.any():
    df.loc[mask, 'evento'] = df.loc[mask, 'evento'] + "."
  return df

# process_text(book_path)
text = read_text_file(text_path)
df = make_dataframe(text)
df = adjust_dataframe(df)
