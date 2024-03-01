import streamlit as st
import requests
from transformers import pipeline
from transformers import AutoTokenizer
from googletrans import Translator
from gensim.summarization import keywords
from gensim.summarization.textcleaner import tokenize_by_word
from gensim.utils import simple_tokenize
from PIL import Image

def fetch_news_data():
    url = 'https://newsdata.io/api/1/news?country=sg&apikey=pub_36339f1061da1cd614f8c7343e8bbb75e6a04'
    response = requests.get(url)
    json_data = response.json()
    return json_data.get('results', [])

def extract_keywords(text, num_keywords):
    keywords_list = keywords(text, words=num_keywords, lemmatize=True, split=True)
    return keywords_list

def detect_lang(text):
    translator = Translator()
    lang = translator.detect(text).lang
    return lang

def translate(text):
    translator = Translator()
    translation = translator.translate(text, src=detect_lang(text), dest='en')
    return translation.text

def tokenize_text(text):
    return list(simple_tokenize(text))

def determine_feasible_len(description):
    if len(description) >= 50:
        return 40
    elif 40 <= len(description) < 50:
        return 30
    elif 30 <= len(description) < 40:
        return 20
    elif 20 <= len(description) < 30:
        return 10
    else:
        return 5

default_image = Image.new('RGB', (200, 200), color='grey')
def show_image(st,image,default_image):
    if image == None:
        image = default_image
        st.image(image,width =400)
    else:
        st.image(image, width=400)

def main():
    st.set_page_config(page_title="The Sing Times - Top Headlines", page_icon="📰")
    st.title("The Singapore Times - Top Headlines📰")

    results = fetch_news_data()
    # print(results)

    summarizer = pipeline("summarization")

    for article in results:
        title = article.get('title', '')
        description = article.get('description', '')
        category = article.get('category', '')
        image = article.get('image_url',"")
        url = article.get('link', '')

        if description is None:
            description = "None provided."
            summary = "None provided."
        else:
            feasible_len = determine_feasible_len(description)
            tokens = tokenize_text(description)
            feasible_len = min(feasible_len, len(tokens))
            # print(len(description))
            # print(tokens)
            # print(feasible_len)

            summary = summarizer(description, max_length=feasible_len, min_length=3, length_penalty=2.0, num_beams=3, temperature=0.5)
            summary = summary[0]['summary_text']
            # print(summary)

        detect_lang_title = detect_lang(title)
        if detect_lang_title != 'en': # or detect_lang_title is None
            title = translate(title)
            description = translate(description)

        st.write(f"### {title}")
        # show image
        show_image(st,image,default_image)
        st.write(f"**Description:** {description}")
        # print(summary)
        st.write(f"**Summary:** {summary}")
        st.write(f"**Category:** {category}")
        st.markdown(f"[Read more]({url})")

if __name__ == "__main__":
    main()
