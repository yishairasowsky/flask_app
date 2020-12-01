import spacy
import random
import pandas as pd
import requests
import wikipedia

from bs4 import BeautifulSoup
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():

    to_display = ''
    
    name = request.args['name']

    HELLO_HTML = """
    <html><body>
    The time is {1}.
    <h1>Hello, {0}!</h1>
    <hr>
    </body></html>"""

    to_display += HELLO_HTML.format(name, str(datetime.now()))

    # url = 'http://www.sefaria.org/api/texts/Berakot.2a.10-13'

    # research_item = 'Rashi'
    research_item = 'Rambam'

    url = f'https://en.wikipedia.org/api/rest_v1/page/summary/{research_item}'

    r = requests.get(url)
    obj = r.json()


    key = 'extract'
    content = obj[key]

    html_str = content
    soup = BeautifulSoup(html_str,features="html.parser")
    text = soup.get_text()

    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    
    ents_dict = {
        'word':[ent.text for ent in doc.ents],
        'label':[ent.label_ for ent in doc.ents],
    }

    ents_df = pd.DataFrame(ents_dict)
    ents_df

    unique_ents_df = ents_df.drop_duplicates()
    unique_ents_dict = {}
    
    for row in unique_ents_df.itertuples():
        unique_ents_dict[row[1]] = row[2]


    to_display += '<h1>Material to Learn:</h1> '
    to_display += text

    to_display += '<hr>'
    to_display += '<hr>'
    to_display += '<h1>Study Questions:</h1> '
    to_display += '<h3>(#1) Wh- questions:</h3> '


    idx = 1
    
    for token,label in unique_ents_dict.items():
    
        to_display+=f"({idx}) "
    
        if label in {'ORG','PRODUCT'}:
            to_display+=f"What is meant by {token}?<br>"
    
        elif label in {'PERSON',''}:
            to_display+=f"Who is {token}?<br>"
    
        elif label=='DATE':
            to_display+=f"What occurred at the time of {token}?<br>"
    
        elif label in {'LOC','GPE'}:
            to_display+=f"What occurred in {token}?<br>"
        
        else:
            to_display+=f"<b>*</b> No question generated for: <b>{token}</b><br>"

        idx += 1

    text_with_blanks = text
    for ent in doc.ents:
        text_with_blanks = f'{text_with_blanks[:ent.start_char]}{"_"*(ent.end_char-ent.start_char)}{text_with_blanks[ent.end_char:]}'



    to_display += '<hr>'
    to_display += '<h3>(#2) Fill in the blank:</h3> '
    to_display += text_with_blanks
    

    true_sents = []
    false_sents = []

    words_to_replace = {'not','is','was'}

    for sent in doc.sents:

        sent_text_true = sent.text
        sent_text_false = 'NA'

        if any(word_to_replace in sent_text_true for word_to_replace in words_to_replace):
        
            sent_text_false = sent_text_true.replace('not ',' ',1)
            sent_text_false = sent_text_true.replace('is','is not',1)
            sent_text_false = sent_text_true.replace('was','was not',1)

            true_sents.append(sent_text_true)
            false_sents.append(sent_text_false)

    tf_dict = {
        'true':true_sents,
        'false':false_sents,
    }

    tf_df = pd.DataFrame(tf_dict)

    tf_dict = {}
    tf_dict['true'] = []
    tf_dict['false'] = []
    for row in tf_df.itertuples():
        tf_dict['true'].append( row[1])
        tf_dict['false'].append( row[2])

    tf_df = pd.DataFrame(tf_dict)

    t_or_f_lst = []
    for idx,row in enumerate(tf_df.itertuples()):
        t_or_f = random.choice([1,2])
        t_or_f_lst.append(f'<br>({idx + 1}) {row[t_or_f]}')

    t_or_f_str = '<br>'.join(t_or_f_lst)
    
    to_display += '<hr>'
    to_display += '<h3>(#3) True or False:</h3> '
    to_display += t_or_f_str

    # to_display = ''
    return to_display

if __name__ == '__main__':
    app.run(debug=True, port=5000) #run app in debug mode on port 5000
