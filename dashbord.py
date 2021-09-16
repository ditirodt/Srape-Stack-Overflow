# -*- coding: utf-8 -*-
"""
Created on Mon May 20 09:27:58 2021

@author: Ditiro
"""

import streamlit as st
import pandas as pd
import requests
from requests_html import HTML
import time


base_url = 'https://stackoverflow.com/questions/tagged/'
tag = "java"
query_filter = "Votes"
url = f"{base_url}{tag}?tab={query_filter}"

r = requests.get(url)
html_str = r.text
html = HTML(html=html_str) #use HTML library to parse through page

question_summaries = html.find(".question-summary")
#columns = ['votes', 'vote_title', 'num_answers', 'views', 'question', 'short_desc', 'tags', 'date', 'user', 'user_details']

key_names = ['question', 'votes', 'tags']
classes_needed = ['.question-hyperlink', '.vote', '.tags']
#this_question_element = question_summaries[0]
#this_question_element.find('.question-hyperlink', first=True).text #look for classes that have .question hyperlink
#this_question_element.find('.vote', first=True).text.replace('\nvotes', '')#remove \nvotes to only have a number

def clean_scraped_data(text, keyname=None): #remove \nvotes to only have a number
    if keyname == 'votes':
        return text.replace('\nvotes', '')
    return text

datas = []

#in question summary,find classes needed,only scrape from a single page
for q_el in question_summaries:
    question_data = {} #give the question data a dictionary
    for i, _class in enumerate(classes_needed): #give element values,assign keysname to classes_needed using enumarate
        sub_el = q_el.find(_class, first=True)
        keyname = key_names[i]#ppend data to variable keyname
        question_data[keyname] = clean_scraped_data(sub_el.text, keyname=keyname)
    datas.append(question_data)

#scrape from multiple pagess
def parse_tagged_page(html):#pass actual page html
    question_summaries = html.find(".question-summary")
    key_names = ['question', 'votes', 'tags']
    classes_needed = ['.question-hyperlink', '.vote', '.tags']
    datas = []
    for q_el in question_summaries:
        question_data = {}
        for i, _class in enumerate(classes_needed):
            sub_el = q_el.find(_class, first=True)
            keyname = key_names[i]
            question_data[keyname] = clean_scraped_data(sub_el.text, keyname=keyname)
        datas.append(question_data)
    return datas

def extract_data_from_url(url):#extract data from the url
    r = requests.get(url)
    if r.status_code not in range(200, 299):#if Client request successful,this range means request is succesful
        return []     #if request is unsuccesful return an empty string
    html_str = r.text
    html = HTML(html=html_str)#use HTML library to parse through page
    datas = parse_tagged_page(html)
    return datas

def scrape_tag(tag = None, query_filter = "Votes", max_pages=50, pagesize=25):
    base_url = 'https://stackoverflow.com/questions/tagged/'
    datas = []
    for p in range(max_pages):
        page_num = p + 1
        url = f"{base_url}{tag}?tab={query_filter}&page={page_num}&pagesize={pagesize}"#scrape only 50 pages with a pagesize of 25 questions
        datas += extract_data_from_url(url)
        time.sleep(1.2)#aoid being blocked from the website,dont hammer people's websites
    return datas  

datas = scrape_tag(tag='python')
df = pd.DataFrame(datas)


header = st.beta_container()
body = st.beta_container()

with header:
    st.title("Stackr Overflow dashboard")
    
with body:
    st.write(df.head(25))

st.sidebar.title("Interact with the dashboard")
    
st.sidebar.markdown("Select the Tags accordingly")
select = st.sidebar.selectbox(
        label = "select Tag",
        options =['select','Java','Javascript','Python']
        )
if select =="Python":
    datas = scrape_tag(tag='python')
    df = pd.DataFrame(datas)
if select =="Java":
    datas = scrape_tag(tag='java')
    df = pd.DataFrame(datas)
    
if select =="Javascript":
    datas = scrape_tag(tag='javascript')
    df = pd.DataFrame(datas)

"""
* Possible uses
  *get popular questions for learning
  *build reputation for job opportunities
  *help to make bootcamps or online questions
"""
