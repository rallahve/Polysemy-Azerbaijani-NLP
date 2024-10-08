# -*- coding: utf-8 -*-
"""qmul_final_project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kbqSoIR01QeIy-7X6259cjlpZUV7rtn8
"""

# This is the start of the project. Make sure to include these files:
# "60words_annotated.csv"
# "top_60_nouns.csv"
# "requirements.txt"
# "functions.py"

from huggingface_hub import notebook_login
# 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 (token for login)
notebook_login()

!pip install datasets
from datasets import load_dataset
dataset = load_dataset("azcorpus/azcorpus_v0")

# Run this section to import all dependencies
import requests
from bs4 import BeautifulSoup
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
from google.colab import files
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import numpy as np
import csv

BASE_URL = "https://obastan.com"
session = requests.Session()

def remove_em_tags(text):
    """Remove content within <em> tags."""
    return re.sub(r"<em>.*?</em>", "", text)

def get_text_without_tags(html_content):
    """Convert HTML content to text and remove leading/trailing whitespace."""
    return BeautifulSoup(html_content, "html.parser").get_text().strip()

def extract_meaning_and_usage(clean_text):
    """Split the clean text into actual meaning and usage examples."""
    sentences = re.split(r"(?<=[.!?]) +", clean_text)
    actual_meaning = (
        re.sub(r"^\w+\s?(I|II|III|IV|V|VI|VII|VIII|IX|X)\s", "", sentences[0])
        if sentences
        else ""
    )
    usage_examples = " ".join(sentences[1:]) if len(sentences) > 1 else ""
    return actual_meaning, usage_examples

def clean_meaning(meaning):
    """Clean the meaning text by removing unwanted characters."""
    return re.sub(r"\[\s*]", "", meaning).strip()

def scrape_word_details(href_link):
    """Scrape the details of a word from its individual page using the session."""
    full_url = f"{BASE_URL}{href_link}"
    response = session.get(full_url)
    soup = BeautifulSoup(response.content, "html.parser")
    details = []
    for p in soup.find("div", itemprop="articleBody").find_all("p", recursive=False):
        part_of_speech = p.find("em").text if p.find("em") else None
        origin_match = re.search(r"\[\s*<em>(.*?)<\/em>\s*\]", str(p))
        origin = origin_match.group(1) if origin_match else None
        clean_p_text = get_text_without_tags(remove_em_tags(str(p)))
        actual_meaning, usage_examples = extract_meaning_and_usage(clean_p_text)
        details.append(
            {
                "part_of_speech": part_of_speech,
                "origin": origin,
                "meaning": clean_meaning(actual_meaning),
                "usage": usage_examples,
            }
        )
    return details

def scrape_main_list(page_number):
    """Scrape the main list of words from the given page number."""
    page_url = f"{BASE_URL}/azerbaycan-dilinin-omonimler-lugeti/?l=az&p={page_number}"
    response = session.get(page_url)
    soup = BeautifulSoup(response.content, "html.parser")
    words = [
        {
            "word": li.find("h3", class_="wli-title").text.strip(),
            "link": li.find("a", class_="wli-link")["href"].strip(),
        }
        for li in soup.find_all("li", class_="wli")
    ]
    return words

def scrape_details_concurrently(word_infos):
    """Function to scrape details in parallel."""
    all_details = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        future_to_word_info = {
            executor.submit(scrape_word_details, word_info["link"]): word_info
            for word_info in word_infos
        }
        for future in as_completed(future_to_word_info):
            details = future.result()

            for detail in details:
                detail["word"] = future_to_word_info[future][
                    "word"
                ]
                all_details.append(detail)
    return all_details

def main_scrape(max_page_to_scrape = None):
    all_words_info = []
    page = 0
    while True:
        page += 1
        print(f"Scraping page {page}...")
        words_list = scrape_main_list(page)
        if not words_list:
            print(f"No words found on page {page}. Stopping page scrape.")
            break
        all_words_info.extend(words_list)
        if max_page_to_scrape and page >= max_page_to_scrape:
            print(f"Reached maximum page limit of {max_page_to_scrape}. Stopping page scrape.")
            break


    data = scrape_details_concurrently(all_words_info)
    print(f"Scraping done. Total words details scraped: {len(data)}")
    return data

scraped_data = main_scrape()

df = pd.DataFrame(scraped_data)


df['origin'] = df['origin'].astype('category')
df['part_of_speech'] = df['part_of_speech'].astype('category')
df['word'] = df['word'].astype('category')

origin_id_map = {origin: i for i, origin in enumerate(df['origin'].cat.categories)}
part_of_speech_id_map = {pos: i for i, pos in enumerate(df['part_of_speech'].cat.categories)}
word_id_map = {word: i for i, word in enumerate(df['word'].cat.categories)}

df['origin_id'] = df['origin'].map(origin_id_map)
df['part_of_speech_id'] = df['part_of_speech'].map(part_of_speech_id_map)
df['word_id'] = df['word'].map(word_id_map)

df = df[['word_id', 'origin_id', 'part_of_speech_id', 'meaning', 'usage']]

origin_df = pd.DataFrame(list(origin_id_map.items()), columns=['origin', 'origin_id'])
part_of_speech_df = pd.DataFrame(list(part_of_speech_id_map.items()), columns=['part_of_speech', 'part_of_speech_id'])
word_df = pd.DataFrame(list(word_id_map.items()), columns=['word', 'word_id'])

df.to_csv('scraped_data_with_mappings.csv', index=False, encoding='utf-8-sig')
files.download('scraped_data_with_mappings.csv')

az_korpus_df = pd.DataFrame(dataset['train'][:90000])

word_list = word_df['word'].tolist()
total_words = len(word_list)

az_korpus_df['text'] = az_korpus_df['text'].str.lower()

word_counts = {word: 0 for word in word_list}

for index, word in enumerate(word_list, start=1):
    percentage = (index / total_words) * 100
    print(f"Analyzing: {word} {percentage:.2f}%")

    word_counts[word] = az_korpus_df['text'].str.count(f"\\b{word.lower()}\\b").sum()

word_counts_df = pd.DataFrame(list(word_counts.items()), columns=['word', 'count'])

word_counts_df = word_df.merge(word_counts_df, on='word', how='left')

word_counts_df = word_counts_df.sort_values(by='count', ascending=False)

print(word_counts_df)
print("Word counting process completed.")

word_counts_df.to_csv('scraped_homonym_counts_50k.csv', index=False, encoding='utf-8-sig')
files.download('scraped_homonym_counts_50k.csv')

word_counts_df_60 = pd.read_csv("/content/top_60_nouns.csv", header = 1)
word_counts_df_60

# This section collects sentences per word from the corpus
top_words = word_counts_df_60.head(60)


sampled_sentences = []

corpus_sentences = sum(az_korpus_df['text'].apply(lambda x: x.split('.')).tolist(), [])

for word in top_words['word']:
    regex_pattern = r'\b' + re.escape(word.lower()) + r'\b'
    sentences_with_word = [sentence for sentence in corpus_sentences if re.search(regex_pattern, sentence.lower())]

    if sentences_with_word:
        sampled = np.random.choice(sentences_with_word, size=min(len(sentences_with_word), 1000), replace=False)

        for sentence in sampled:
            sampled_sentences.append({'word': word, 'sentence': sentence.strip()})

sampled_sentences_df = pd.DataFrame(sampled_sentences)

sampled_sentences_df

sampled_sentences_df.to_csv("60x1000_annotated.csv", index=False, encoding="utf-8-sig")
files.download('60x1000_annotated.csv')

# Below is the plotting part.
# Make sure "requirements.txt", "functions.py", "60words_annotated.csv" are included in the files section.

!pip install -r requirements.txt

# Import the necessary functions from the functions.py file
from functions import WordTransformer, format_sentences, project_group_and_scatter_plot_embeddings
from sklearn.metrics import f1_score

df = pd.read_csv("60words_annotated.csv")


def calculate_accuracy(y_pred, y_true):
  if (len(y_pred) != len(y_true)):
    return 0

  correct_pred = 0

  for i in range(len(y_pred)):
    if (y_pred[i] == y_true[i]):
      correct_pred += 1

  accuracy = correct_pred / len(y_pred)

  return accuracy

model = WordTransformer('pierluigic/xl-lexeme')
f1_array = []
accuracy_array = []
for word in df["word"].unique():
  df_word = df[df['word']==word] # where word is your word of choice
  word_sentences = df_word['sentence'].to_list()
  y_true = df_word['true_label'].to_list()
  # This is to check inverse of true labels
  # for i in range(len(y_true)):
  #   y_true[i] = 1 - y_true[i]

  word_sentences = [sentence for sentence in word_sentences if len(sentence) < 450]
  words = [word]*len(word_sentences)
  formatted_sentences = format_sentences(word_sentences, words)

# Generate the embeddings by encoding the formatted sentences
  word_embeddings = model.encode(formatted_sentences)

# Project the embeddings to 2D and plot them
  y_pred = project_group_and_scatter_plot_embeddings(word_embeddings, word_sentences, words, n_clusters=2, dim_reducer='pca')


  f1 = -1
  pred_length = len(y_pred)
  # if (len(y_pred) == 18):
  f1 = f1_score(y_true[:pred_length], y_pred, average='weighted')
  accuracy = calculate_accuracy(y_pred, y_true[:pred_length])

  f1_array.append(f1)
  accuracy_array.append(accuracy)


  print("true_label: ", y_true)
  print("y_pred: ", y_pred)
  print("f1 score: ", f1)
  print("accuracy: ", accuracy)
  print("length of true: ", len(y_true))
  print("length of pred: ", len(y_pred))

# This downloads all F1 scores as a CSV file
import csv
from google.colab import files

filename = 'f1.csv'

# Writing to the CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Writing the header
    writer.writerow(["f1 scores"])
    # Writing the data
    for score in f1_array:
        writer.writerow([score])

files.download('f1.csv')

# This downloads all accuracy scores as a CSV file
filename = 'accuracy.csv'

# Writing to the CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Writing the header
    writer.writerow(["accuracy scores"])
    # Writing the data
    for score in accuracy_array:
        writer.writerow([score])

files.download('accuracy.csv')

# This code gets the starting and ending indices of word in the sentence
df = pd.read_csv("60words_annotated.csv")

start_index_array = []
end_index_array = []

for i in range(len(df["word"])):
  current_word = df["word"][i].lower()
  current_sentence = df["sentence"][i].lower()
  pattern = r'\b\w*' + re.escape(current_word) + r'\w*\b'

  match = re.search(pattern, current_sentence)
  if match:
      start_index_array.append(match.start())
      end_index_array.append(match.end() - 1)  # Subtract 1 because end is exclusive in Python
  else:
      start_index_array.append("NOT FOUND")
      end_index_array.append("NOT FOUND")



filename = 'start_indices.csv'

# Writing to the CSV file
with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Writing the header
    writer.writerow(["Start Index"])
    # Writing the data
    for index in start_index_array:
        writer.writerow([index])

files.download('start_indices.csv')

filename = 'end_indices.csv'

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Writing the header
    writer.writerow(["End Index"])
    # Writing the data
    for index in end_index_array:
        writer.writerow([index])

files.download('end_indices.csv')

# This is for Google Translation
pip install googletrans==4.0.0rc1

# This is Google Translator to translate top_60_nouns.csv
import time
import googletrans
from googletrans import Translator

df = pd.read_csv("data.csv")

translator = Translator()
translated_words = []
for i in df["word"]:
  word_eng = (translator.translate(i, dest="en", src="az")).text
  translated_words.append(word_eng)

filename = 'translations.csv'

with open(filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    # Writing the header
    writer.writerow(["translation"])
    # Writing the data
    for i in translated_words:
        writer.writerow([i])

files.download('translations.csv')

