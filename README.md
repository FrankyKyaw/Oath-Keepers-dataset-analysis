# Oath Keepers Dataset Analysis Dashboard

This repository contains code for analyzing and visualizing text messages and emails from the Oath Keepers dataset. The Oath Keepers dataset consists of chat messages and email communications from members 
of the Oath Keepers, a far-right anti-government militia organization in the United States. \
Click [here](https://ddosecrets.com/wiki/Oath_Keepers) to download dataset and for more info. \
\
The analysis is performed using Python and Streamlit which provides insights into common words and message counts by users.

## Installation 
Clone the repository
```
$ git clone https://github.com/FrankyKyaw/Oath-Keepers-dataset-analysis.git
$ cd oathkeepers-analysis
```
Install the required packages:
```
$ pip install -r requirements.txt
```
Download nltk stopwords
```
import nltk
nltk.download('stopwords')
```

## Usage
Place the Oath Keepers.sbd in the directory and run the Streamlit app:
```
streamlit run extract.py
```

![](https://github.com/FrankyKyaw/Oath-Keepers-dataset-analysis/blob/master/images/screenshot-1.png)
![](https://github.com/FrankyKyaw/Oath-Keepers-dataset-analysis/blob/master/images/screenshot-3.png)
![](https://github.com/FrankyKyaw/Oath-Keepers-dataset-analysis/blob/master/images/screenshot-2.png)
