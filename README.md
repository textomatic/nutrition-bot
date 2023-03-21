# Nutrition Bot
**Duke AIPI 540 Natural Language Processing Module Project by Yilun Wu, Shen Juin Lee, Shrey Gupta**

## Project Description
For most people, especially for people who are interested in body healthcare, *nutrition* is a well-acquainted term. By definition,nutrition is the study of how food and drink affects our bodies with special regard to the essential nutrients necessary to support human health. It looks at the physiological and biochemical processes involved in nourishment and how substances in food provide energy or are converted into body tissues. Nutrition is a critical part of health and development. Better nutrition is related to improved infant, child and maternal health, stronger immune systems, safer pregnancy and childbirth, lower risk of non-communicable diseases (such as diabetes and cardiovascular disease), and longevity. Therefore, nutrition is a popular topic among the world. 

*Reddit*, one of the largest online communities in the United States, has a wide-range of posts and discussions on nutrition related topics as it should be. Reddit contains many subreddits dedicated to nutrition topics, making it a great platform for anyone interested in learning more about healthy eating, dietary advice, and related discussions. Nonetheless, not every nutrition question from every user are approprately answered or solved--there still exists several problems of Reddit posts & discussions on nutrition topic: 

- Lack of context: some Reddit posts may not contain enough information due to the character limit or formatting limit of the Reddit platform

- Lack of moderation: some Reddit users may encounter irrelevant or even offensive comments (or trolls /spams)

- **Lack of scientific evidence support**: some replies from certain users to a specific nutrition related problem are quite meaningful and beneficial, yet still not convincing enough since the lack of scientific evidence 

Our project mainly focuses on solving the third problem: the lack of scientific evidence support. To be more specific, our project builds up a Q&A query system that allows users to input questions related to nutrition and find approprate answers based on scientific research papers and answers from reddit posts. 

## Data Sources
As discussed before, our project aims to solve the problem of lack of scientific evidence support and try to provide answers to each nutrition related problems from both scientific research papers and reddit posts & replies. Therefore, our datasets mainly contains two parts: scientific research papers in .pdf format and contents of reddit posts and discussions in .csv format.

### Scientific Research Papers
The scientific research papers on topics about nutrition are collected both manually and automatically with the support of web scraping python scripts. To be more specific, we manually downloaded ~200 most recent & most relevant scientific research papers on top questions about nutrition posted on Reddit, and automatically scraped more than 2000 academic research papers from *PubMed*, *ScienceDirect*, etc. The total number of scientific research papers downloaded is 2480, and we uploaded them to Google Cloud Bucket which can be accessed [here](https://console.cloud.google.com/storage/browser/aipi540_nlp_nutrition).

### Reddit Posts & Replies
The posts & replies on various topics about nutrition are collected using python scripts. To be more specific, we extracted reddit posts & comments using web scraping; the total number of posts extracted is 163 and the total number of comments & replies extracted is 25,286. The entire scraped dataset is stored as `nutrition.csv` also with a picked file under folder `/data/reddit`.

## Data Processing (TODO)
Once the images were downloaded using the URLs, we wrote a python script to do the following:
- Remove corrupt images
- Remove duplicate images
- Resave the images after optimizing the quality to 80%

The processed data on which the models were trained can either be downloaded directly using the links above or the scripts to download and optimize the dataset can be found in the `scripts` folder and can be run as follows:

**1. Create a new conda environment and activate it:** 
```
conda create --name cv python=3.8
conda activate cv
```
**2. Install python package requirements:** 
```
pip install -r requirements.txt 
```
**3. Run the data download script:** 
```
python scripts/dataset/make_dataset.py
```
**4. Run the data optimize script:** 
```
python scripts/dataset/optimize_dataset.py
```

## Project Structure
The project data and codes are arranged in the following manner:

```
├── README.md                           <- description of project and how to set up and run it
├── requirements.yaml                   <- requirements file to document dependencies
├── src                                 <- directory for data processing, modelling and utility scripts
├── models                              <- directory for trained models
├── data                                <- directory for project data
    ├── all_pdfs                        <- directory to store all research papers (should be removed?)
    ├── reddit                          <- directory to store all reddit posts & replies
        ├── nutrition.csv
        ├── nutrition.pkl
        ├── top_questions.csv
├── notebooks                           <- directory to store any exploration notebooks used
├── .gitignore                          <- git ignore file
```

&nbsp;
## Model Training and Evaluation (TODO)
A non deep learning and a deep learning modelling approach were used to accurately identify and categorize social media images based on their content. The non deep learning approach used Random Forest and SVM models whereas the deep learning approach used VGG and Resnet model architectures.
### Non-Deep Learning Models

### SVM
To avoid the bottle neck of being able to train the model on a small dataset, a SVM (Support Vector Machine) model was trained. The PyTorch implementation of SVM was used to be able to use the whole dataset to train the model.

But due to the high dimensionality of the image data, the SVM model was not able to perform well. The model was able to achieve an accuracy of 40% on the test set. This is because SVMs are linear classifiers and are not able to capture non-linear relationships in the data. This is where deep learning models come in handy.

Following are the steps to run the code and train a SVM model:

**1. Create a new conda environment and activate it:** 
```
conda create --name cv python=3.8
conda activate cv
```
**2. Install python package requirements:** 
```
pip install -r requirements.txt 
```

**3. Tweak the model parameters [OPTIONAL]:** 
```
nano scripts/svm/svm_config.json
```

**4. Run the training script:** 
```
python scripts/svm/svm_training.py
```
&nbsp;
### Deep Learning Models
### VGG
A VGG19 model was trained on the dataset. Transfer learning was performed on the model in 2 ways:
- Case 1: VGG19_bn with all layers trainable
- Case 2: VGG19_bn with just the last fully connected layer trainable

The model was trained for 10 epochs in both the cases and the training and validation loss and accuracy were plotted. The model in case 1 was able to achieve an accuracy of 74% on the test set while the model in case 2 achieved 89%.

Following are the steps to run the code and train a VGG model:

**1. Create a new conda environment and activate it:** 
```
conda create --name cv python=3.8
conda activate cv
```
**2. Install python package requirements:** 
```
pip install -r requirements.txt 
```

**3. Tweak the model parameters [OPTIONAL]:** 
```
nano scripts/vgg/vgg_config.json
```

**4. Run the training script:** 
```
python scripts/vgg/vgg_transfer_learning.py
```
### Resnet

The SOTA model in image classification - Resnet was trained on the dataset in the following variations:
- Case 1: Resnet18 with all layers trainable
- Case 2: Resnet18 with just the last fully connected layer trainable
- Case 3: Resnet50 with all layers trainable
- Case 4: Resnet50 with just the last fully connected layer trainable
- Case 5: Resnet152 with all layers trainable
- Case 6: Resnet152 with just the last fully connected layer trainable

We trained three models for comparison. We started with a simple image classifier - Resnet18. The labelled images were split into train and test datasets and loaded in Pytorch Dataset Objects. A pretrained Resnet18 model was loaded and its fully connected head was stripped off to perform transfer learning. The new trasnfer learned resnet takes in input images of size 640x640 and gives the predicted probability of presence of each class in the image.

The results of the model were as follows:
| Model     | Mode             | Accuracy (Test) |
| --------- | ---------------- | :-------------: |
| Resnet18  | Train all layers | 85%             |
| Resnet18  | Train FC layer   | 84%             |
| Resnet50  | Train all layers | 87%             |
| Resnet50  | Train FC layer   | 88%             |
| Resnet152 | Train all layers | 89%             |
| Resnet152 | Train FC layer   | 91%             |

Following are the steps to run the code and train a Resnet model:

**1. Create a new conda environment and activate it:** 
```
conda create --name cv python=3.8
conda activate cv
```
**2. Install python package requirements:** 
```
pip install -r requirements.txt 
```

**3. Tweak the model parameters [OPTIONAL]:** 
```
nano scripts/resnet/resnet_config.json
```

**4. Run the training script:** 
```
python scripts/resnet/resnet_transfer_learning.py
```


## Content Moderation Application (Streamlit): (TODO)
* Refer to the [README.md](https://github.com/guptashrey/Content-Moderation-for-Social-Media/blob/st/README.md) at this link to run the streamlit based web application or access it [here](https://guptashrey-content-moderation-for-1--content-moderation-5y11hh.streamlit.app/).
* You can find the code for the stremalit web-app [here](https://github.com/guptashrey/Content-Moderation-for-Social-Media/tree/st)