# Nutrition Bot
**Duke AIPI 540 Natural Language Processing Module Project by Yilun Wu, Shen Juin Lee, Shrey Gupta**

## Project Description
For most people, especially for people who are interested in body healthcare, *nutrition* is a well-acquainted term. By definition,nutrition is the study of how food and drink affects our bodies with special regard to the essential nutrients necessary to support human health. It looks at the physiological and biochemical processes involved in nourishment and how substances in food provide energy or are converted into body tissues. Nutrition is a critical part of health and development. Better nutrition is related to improved infant, child and maternal health, stronger immune systems, safer pregnancy and childbirth, lower risk of non-communicable diseases (such as diabetes and cardiovascular disease), and longevity. Therefore, nutrition is a popular topic among the world. 

*Reddit*, one of the largest online communities in the United States, has a wide-range of posts and discussions on nutrition related topics as it should be. Reddit contains many subreddits dedicated to nutrition topics, making it a great platform for anyone interested in learning more about healthy eating, dietary advice, and related discussions. Nonetheless, not every nutrition question from every user are approprately answered or solved--there still exists several problems of Reddit posts & discussions on nutrition topic: 

- **Lack of context**: some Reddit posts may not contain enough information due to the character limit or formatting limit of the Reddit platform

- **Lack of moderation**: some Reddit users may encounter irrelevant or even offensive comments (or trolls /spams)

- **Lack of scientific evidence support**: some replies from certain users to a specific nutrition related problem are quite meaningful and beneficial, yet still not convincing enough since the lack of scientific evidence 

Our project mainly focuses on solving the third problem: the lack of scientific evidence support. To be more specific, our project builds up a Q&A query system that allows users to input questions related to nutrition and find approprate answers based on scientific research papers and answers from reddit posts. 

## Data Sources
As discussed before, our project aims to solve the problem of lack of scientific evidence support and try to provide answers to each nutrition related problems from both scientific research papers and reddit posts & replies. Therefore, our datasets mainly contains two parts: scientific research papers in .pdf format and contents of reddit posts and discussions in .csv format.

### Scientific Research Papers
The scientific research papers on topics about nutrition are collected both manually and automatically with the support of web scraping python scripts. To be more specific, we manually downloaded ~200 most recent & most relevant scientific research papers on top questions about nutrition posted on Reddit, and automatically scraped more than 2000 academic research papers from *PubMed*, *ScienceDirect*, etc. The total number of scientific research papers downloaded is 2480, and we uploaded them to a Google Cloud Storage Bucket.

### Reddit Posts & Replies
The posts & replies on various topics about nutrition are collected using python scripts. To be more specific, we extracted reddit posts & comments from the nutrition subreddit (`r/nutrition`) using the Python Reddit API Wrapper (PRAW) package. The total number of posts extracted is 163 and the total number of comments & replies extracted is 25,286. Only posts with an upvote count higher than 50 were downloaded. The collected dataset is stored as `nutrition.csv` and also as a pickled file under the folder `/data/reddit/`.

## Setting up Elasticsearch Document Store

Elasticsearch is a distributed, open source search and analytics engine for all types of data, including textual, numerical, geospatial, structured, and unstructured. It allows us to store, search, and analyze big volumes of data quickly and in near real time. It is generally used as the underlying engine/technology that powers applications that have complex search features and requirements. In our project, we use Elasticsearch as the document store to store the research papers and reddit posts & replies.

It can be setup on your local machine using docker. The following steps can be followed to setup Elasticsearch on your local machine:

**1. Install Docker:** 
```bash
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io
```
**2. Pull the Elasticsearch docker image:** 
```bash
docker pull docker.elastic.co/elasticsearch/elasticsearch:7.17.6
```
**3. Create a volume to store the Elasticsearch data:** 
```bash
docker volume create es_v1
```

**4. Run the Elasticsearch docker image:** 
```bash
docker run -d -p 9200:9200 -e 'discovery.type=single-node' --name es_v1 --mount type=volume,src=es_v1,target=/usr/share/elasticsearch/ elasticsearch:7.17.6
```

**5. Check if Elasticsearch is running:** 
```bash
curl -X GET "localhost:9200/"
```

## Data Processing
### Research Papers

The research papers were downloaded in .pdf format from the google cloud storage bucket in the `data/all_pdfs folder`. Then, a python script was run to convert them into text, preprocess them, chunk them into sentences, and index them into the elasticsearch document store. The python script can be found in the `scripts` folder and can be run as follows:

**1. Create a new conda environment and activate it:** 
```
conda create --name haystack python=3.8
conda activate cv
```
**2. Install python package requirements:** 
```
pip install -r requirements.txt 
```
**3. Install xpdf:** 
```bash
wget --no-check-certificate https://dl.xpdfreader.com/xpdf-tools-linux-4.04.tar.gz
tar -xvf xpdf-tools-linux-4.04.tar.gz
sudo cp xpdf-tools-linux-4.04/bin64/pdftotext /usr/local/bin
```
**4. Run the data download script:** 
```
python scripts/process_research_papers.py
```

### Reddit Posts & Replies

The Reddit posts and comments were downloaded using the PRAW library. You will need to register for a Reddit account and create a new app in your user profile to obtain a client ID and client secret. Those will be the credentials needed for downloading data using PRAW. Save those credentials in the following format as `praw.ini` in the root folder:
```ini
client_id=<your_client_id>
client_secret=<your_client_secret>
user_agent=<your_custom_defined_user_agent_string>
```

Assuming you are in the same conda environment as the previous step:

**1. Run the following script to download data from the `r/nutrition` subreddit:** 
```
python scripts/reddit_download.py
```

The data would be available as CSV and PKL in the `/data/reddit/` directory.


## Running the QnA Pipeline Server
The QnA pipeline server is a FastAPI server that allows us to query the elasticsearch document store using a REST API.

The pipeline has the following steps:
1. Get the query from the user
2. Embed the query using Dense Passage Retrieval (DPR) model (`facebook/dpr-question_encoder-single-nq-base`)
3. Retrieve the top 10 relevant documents from the elasticsearch document store using the query embedding
4. Run the retrieved documents through the reader model (`deepset/roberta-base-squad2`) to top 5 answers
5. Filter the answers based on the score
6. Return the answers as a JSON response

The server can be run as follows:

**1. Create a new conda environment and activate it:** 
```
conda create --name haystack python=3.8
conda activate haystack
```
**2. Install python package requirements:** 
```
pip install -r requirements.txt 
```
**3. Change directory:** 
```
cd src
```
**3. Start the server:** 
```
uvicorn search:app --reload --host 0.0.0.0 --port 8060
```

## Project Structure
The project data and codes are arranged in the following manner:

```
├── data                                <- directory for project data
    ├── all_pdfs                        <- placeholder directory to store all research papers
    ├── reddit                          <- directory to store all reddit posts & replies
        ├── nutrition.csv
        ├── nutrition.pkl
        ├── top_questions.csv
├── notebooks                           <- directory to store any exploration notebooks used
├── src                                 <- directory for data processing and QnA pipeline server scripts
    ├── helper_functions.py             <- script to store helper functions
    ├── process_reddit_posts.py         <- script to process the reddit posts
    ├── process_research_papers.py      <- script to process the research papers
    ├── reddit_download.py               <- script to download reddit posts
    ├── search.py                       <- script to run the QnA pipeline server
├── .gitignore                          <- git ignore file
├── README.md                           <- description of project and how to set up and run it
├── requirements.txt                    <- requirements file to document dependencies
```
&nbsp;
## Nutrition Bot (Streamlit):
* Refer to the [README.md](https://github.com/textomatic/nutrition-bot/blob/st/README.md) at this link to run the Streamlit-based web application or access it [here](https://nutrition-bot.streamlit.app).
* You can find the code for the Streamlit web-app [here](https://github.com/textomatic/nutrition-bot/tree/st)