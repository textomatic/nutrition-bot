# library imports
from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from haystack import Pipeline
from haystack.nodes import FARMReader
from haystack.nodes import DensePassageRetriever

import pandas as pd
import os
import logging
import json

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

from helper_functions import get_elasticsearch_document_store

def initialize():
    '''
    Function to initialize elasticsearch document store objects, retrievers, reader and qna pipelines.

    Args:
        None

    Returns:
        querying_pipeline_reddit (haystack.Pipeline): Qna pipeline for reddit posts.
        querying_pipeline_research_papers (haystack.Pipeline): Qna pipeline for research papers.
        api_key (str): API key for authentication.
    '''

    config = json.load(open("../config.json"))
    api_key = config["api-key"]

    # get the host where Elasticsearch is running, default to localhost
    host = os.environ.get("ELASTICSEARCH_HOST", "localhost")

    # initialize elasticsearch document store objects for reddit posts and research papers
    document_store_reddit = get_elasticsearch_document_store(host, index = "document_reddit")
    document_store_research = get_elasticsearch_document_store(host, index = "document_research")

    # initialize retriever for running qna pipeline on reddit posts
    retriever_reddit = DensePassageRetriever(
        document_store=document_store_reddit,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
    )

    # initialize retriever for running qna pipeline on research papers
    retriever_research_papers = DensePassageRetriever(
        document_store=document_store_research,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
    )

    # initialize reader for running qna pipeline
    reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

    # initialize qna pipeline for reddit posts
    querying_pipeline_reddit = Pipeline()
    querying_pipeline_reddit.add_node(component=retriever_reddit, name="Retriever", inputs=["Query"])
    querying_pipeline_reddit.add_node(component=reader, name="Reader", inputs=["Retriever"])

    # initialize qna pipeline for research papers
    querying_pipeline_research_papers = Pipeline()
    querying_pipeline_research_papers.add_node(component=retriever_research_papers, name="Retriever", inputs=["Query"])
    querying_pipeline_research_papers.add_node(component=reader, name="Reader", inputs=["Retriever"])

    return querying_pipeline_reddit, querying_pipeline_research_papers, api_key

# initialize the search pipeline
querying_pipeline_reddit, querying_pipeline_research_papers, api_key = initialize()

# initialize fastapi app
app = FastAPI()

# define middleware for authentication
@app.middleware("http")
async def authentication(request: Request, call_next):
    '''
    Middleware for authentication.

    Args:
        request (Request): Request object.
        call_next (function): Function to call next.

    Returns:
        JSONResponse: JSON response object.
    '''
    if request.headers.get('api-key') == api_key:
        response = await call_next(request)

    else:
        response = JSONResponse(
            content={"message": "unauthorized access"}, status_code=401
        )
    return response

# define search endpoint
@app.get("/search/{query}")
async def search(query: str):
    '''
    Search endpoint for searching reddit posts and research papers.

    Args:
        query (str): Query string.

    Returns:
        dict: Dictionary containing search results.
    '''

    # run qna pipeline on reddit posts
    reddit_results = search_reddit_posts(query)

    # run qna pipeline on research papers
    research_paper_results = search_research_papers(query)

    # return search results
    return {"reddit_results": reddit_results, "research_paper_results": research_paper_results}

def search_reddit_posts(query):
    '''
    Function to run qna pipeline on reddit posts.

    Args:
        query (str): Query string.

    Returns:
        list: List of dictionaries containing search results.
    '''

    # run qna pipeline
    prediction = querying_pipeline_reddit.run(
        query=query,
        params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })

    # process results
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    answers["thread_link"] = answers['meta'].apply(lambda x: x["url"])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")

    # filter results
    merge = merge[merge["score_y"] >= 0.1]
    results = merge[["content", "answer", "score_y", "thread_link"]].sort_values(by="score_y", ascending=False).to_dict(orient="records")
    
    return results

def search_research_papers(query):
    '''
    Function to run qna pipeline on research papers.
    
    Args:
        query (str): Query string.
        
    Returns:
        list: List of dictionaries containing search results.
    '''

    # run qna pipeline
    prediction = querying_pipeline_research_papers.run(
        query=query,
        params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })
    
    # process results
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    answers["doi_link"] = "https://doi.org/" + answers['meta'].apply(lambda x: x["doi"])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")
    
    # filter results
    merge = merge[merge["score_y"] >= 0.1]
    results = merge[["content", "answer", "score_y", "doi_link"]].sort_values(by="score_y", ascending=False).to_dict(orient="records")
    
    return results