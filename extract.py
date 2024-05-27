import json
import re
from email.parser import BytesParser
from email import policy
import nltk
from nltk.corpus import stopwords
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import os
from collections import Counter
import streamlit as st
import pandas as pd
import csv

def extract_data(file_path):
    with open(file_path, 'r', encoding='utf8') as file:
        data = json.load(file)
    return data

# Add commas between each JSON object in the file 
def fix_json(file_path):
    with open(file_path, 'r', encoding='utf8') as file:
        content = file.read()
        
    content = content.replace('}\n{', '},\n{')
    content = f'[{content}]'
    with open(file_path, 'w', encoding='utf8') as file:
        file.write(content)

# fix_json(file_path)
file_path = "messages.json"



def extract_messages(file_path, output_path='output.txt'):
    data = extract_data(file_path)
    for obj in data: 
        if 'msg' in obj and len(obj['msg'].split()) > 1:
            with open(output_path, 'a', encoding='utf8') as file:
                file.write(obj['msg'] + '\n')

def extract_username_messages_count(file_path, output_path='username_messages_count.txt'):
    data = extract_data(file_path)
    dic = {}
    for obj in data:
        if 'msg' in obj and obj['u']['username'] and len(obj['msg'].split()) > 1:
            username = obj['u']['username']
            dic[username] = dic.get(username, 0) + 1
    return dic
    
def create_username_bar_chart(dictionary):
    df = pd.DataFrame(dictionary.items(), columns=['Username', 'Message Count'])
    df = df[df['Message Count'] > 100]
    fig, ax = plt.subplots()
    ax.barh(df['Username'], df['Message Count'])
    ax.set_ylabel('Username')
    ax.set_xlabel('Message Count')
    st.pyplot(fig)
    
def parse_email(file_path, output_dir, sender_dict):
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        
    base_name = os.path.basename(file_path)
    output_file_name = base_name + '.txt'
    output_path = os.path.join(output_dir, output_file_name)
    
    emails = raw_data.split(b'\nFrom ')

    with open(output_path, 'w', encoding='utf8') as file:
        for i, email in enumerate(emails):
            if i > 0:
                email = b'From ' + email
            email_msg = BytesParser(policy=policy.default).parsebytes(email)
            
            subject = email_msg.get('subject', 'No subject')
            if any(keyword in subject for keyword in ['Returned mail', 'Fwd:']):
                continue
            file.write(f"Subject line: + {subject} + \n")
            file.write(f"From: {email_msg.get('from', 'No from')}\n")
            
            sender = email_msg.get('from', 'No from')
            sender_dict[sender] = sender_dict.get(sender, 0) + 1
            
            file.write(f"To: {email_msg.get('to', 'No to')}\n")
            if email_msg.is_multipart():
                for part in email_msg.walk():
                    if part.get_content_type() == 'text/plain':
                        file.write(part.get_payload(decode=True).decode('utf8', errors='ignore'))
                        file.write('\n')
            else:
                content_type = email_msg.get_content_type()
                if content_type == 'text/plain':
                    file.write(email_msg.get_payload(decode=True).decode('utf8', errors='ignore'))
                    file.write('\n')
            file.write('-' * 30 + '\n' + '\n')
    return sender_dict

def parse_all_emails(file_dir, output_dir):
    sender_dict = {}
    for file_name in os.listdir(file_dir):
        file_path = os.path.join(file_dir, file_name)
        sender_dict = parse_email(file_path, output_dir, sender_dict)
    return sender_dict
# nltk.download('stopwords')

@st.cache_data
def parse_messages(messages_file):
    word_list = []
    stopwords_list = set(stopwords.words('english'))
    additional_stop_words = {'one', 'time', 'good', 'morning', 'need', 'know', 'people', 
                             'see', 'think', 'back', 'u', 'go', 'well', 'new', 'thing', 'got', 'right', 
                             'hey', 'anyone', 'us', 'way', 'thank', 'want', 'way', 'ok', 'ye', 'going', 's','yes', 'make',
                             'i\'m', 'get', 'would', 'like', '', 'could', 'also', 'sure', 'even', 'https', 'still',
                             'welcome', 'lol', 'hello', 'thanks', 'use', 'things', 'channel', 'server',
                             'working', 'group', 'work', 'channel', 'safelinks', 'org', 'oathkeepers', 'oksupport', 'error', 'codes', 'data', 'complaints',
                             'user', 'sdata', 'subject', 'line', 'outlook', 'protection', 'reserved', 'url', 'www', 'com', 'thee', 'http',
                             'look', 'come', 'much', 'great', 'say', 'take', 'day', 'really', 'let', 'may', 'say',
                             'chat', 'guy', 'getting', 'anything'}
    stopwords_list.update(additional_stop_words)
    
    with open(messages_file, 'r', encoding='utf8') as file:
        for line in file:
            words = line.split()
            words = re.findall(r'\b\w+\b', line.lower())
            filtered_words = [word for word in words if word not in stopwords_list and not any(char.isdigit() for char in word)]
            word_list.extend(filtered_words)
    return word_list

def generate_word_cloud(text):
    wordCloud = WordCloud(width=800, height=800, background_color='white', min_font_size=10).generate(text)
    fig, ax = plt.subplots()
    ax.imshow(wordCloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)


def main():
    input_path = r"Oath Keepers.sbd\Oath Keepers.sbd"
    output_dir = r"all_extracted_emails"
    sender_dict = parse_all_emails(input_path, output_dir)
    
    st.title("Oath Keepers Dataset Analysis Dashboard")
    
    # Common words in messages.json
    st.subheader("Most Common Words in messages.json")
    all_words = parse_messages('output.txt')
    word_counts = Counter(all_words)
    common_words = word_counts.most_common(20)
    st.table(pd.DataFrame(common_words, columns=['Word', 'Count']))
    
    st.subheader("Word Cloud of messages.json")
    generate_word_cloud(' '.join(all_words))
    
    st.markdown('''
            This data is from text messages extracted from the messages.json file. The messages.json file contains
            chat messaegs in the OathKeepers server. The most common words are cowboy which I is just an emoji since
            it is usually in the context of :cowboy:. There are words like "patriots" and "flag" which suggests
            that the users consider themselves defenders of the American flag and the country. 
                
            ''')
        
    # Message count by username
    file_path = 'messages.json'
    message_counter = extract_username_messages_count(file_path)
    st.subheader("Username Message Count")
    create_username_bar_chart(message_counter)
    
    st.markdown('''
            By analyzing chat messages by username, I found several interesting findings. One of the most active users
            "Lone Star Hog" has sent over 500 messages. They spread conspiracy theories through links to videos and messages 
            that support conspiracy theories. Some of these include Project Blue Beam, a theory that "NASA is attempting to 
            implement a New Age religion with the Antichrist at its head and start a New World Order, via a 
            technologically-simulated Second Coming." Another theory is that the COVID-19 vaccine causes mad cow disease
            with claims made by Jim Stone.
            ''')
    
    st.subheader("Most Common Words in Oath Keepers Support email address")
    all_words1 = parse_messages('all_extracted_emails\oksupport.txt')
    word_counts1 = Counter(all_words1)

    common_words1 = word_counts1.most_common(20)
    st.table(pd.DataFrame(common_words1, columns=['Word', 'Count']))
    st.subheader("Word Cloud of Oath Keepers Support email address")
    generate_word_cloud(' '.join(all_words1))
    
    # Description of data
    st.markdown('''
                This data is from all the communication in the the Oath Keepers support email address. These emails includes 
                inquiries about the organization, broadcast messages and communication between members. The most frequent word is Trump which is unsurprising 
                since the group is a far-right organization that supports Trump and the emails. 
                The words "deep" and "radical" likely refer to phrases like "deep state" and "radical left," suggesting a narrative focused on 
                conspiracy theories about the left and the government. 
                A surprising word that is common is "donate" which indicates active fundraising efforts and its reliance of financial support from its members.
                The frequent mention of "YouTube" suggests that the group actively uses the video sharing platform to share conspiracy theories. 
                Words such as "constitution,", "state," and "patriots" appear frequently as well emphasizing the group's focus on patriotism and defending 
                consitutional rights as part of their identity. 
                ''')
    

if __name__ == '__main__':
    main()