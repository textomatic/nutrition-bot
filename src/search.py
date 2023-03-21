from fastapi import FastAPI, Request
from starlette.responses import JSONResponse

from haystack.document_stores import ElasticsearchDocumentStore
from haystack import Pipeline
from haystack.nodes import FARMReader
from haystack.nodes import DensePassageRetriever

import pandas as pd
import os
import logging

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

host = os.environ.get("ELASTICSEARCH_HOST", "localhost")

document_store_reddit = ElasticsearchDocumentStore(
    host=host,
    username="",
    password="",
    index="document_reddit",
    similarity="cosine",
    embedding_dim=768
)

document_store_research = ElasticsearchDocumentStore(
    host=host,
    username="",
    password="",
    index="document_research",
    similarity="cosine",
    embedding_dim=768
)

retriever_reddit = DensePassageRetriever(
    document_store=document_store_reddit,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
)

retriever_research_papers = DensePassageRetriever(
    document_store=document_store_research,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
)

reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

querying_pipeline_reddit = Pipeline()
querying_pipeline_reddit.add_node(component=retriever_reddit, name="Retriever", inputs=["Query"])
querying_pipeline_reddit.add_node(component=reader, name="Reader", inputs=["Retriever"])

querying_pipeline_research_papers = Pipeline()
querying_pipeline_research_papers.add_node(component=retriever_research_papers, name="Retriever", inputs=["Query"])
querying_pipeline_research_papers.add_node(component=reader, name="Reader", inputs=["Retriever"])

app = FastAPI()

@app.middleware("http")
async def authentication(request: Request, call_next):

    if request.headers.get('api-key') == "2866fe43-6267-4245-a519-4809ebe14368":
        response = await call_next(request)

    else:
        response = JSONResponse(
            content={"message": "unauthorized access"}, status_code=401
        )
    return response

@app.get("/search/{query}")
async def search(query: str):
    reddit_results = search_reddit_posts(query)
    research_paper_results = search_research_papers(query)
    return {"reddit_results": reddit_results, "research_paper_results": research_paper_results}

def search_reddit_posts(query):
    prediction = querying_pipeline_reddit.run(
        query=query,
        params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })
    
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    answers["thread_link"] = answers['meta'].apply(lambda x: x["url"])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")
    merge = merge[merge["score_y"] >= 0.1]
    results = merge[["content", "answer", "score_y", "thread_link"]].sort_values(by="score_y", ascending=False).to_dict(orient="records")
    return results

def search_research_papers(query):
    prediction = querying_pipeline_research_papers.run(
        query=query,
        params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })
    
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    answers["doi_link"] = "https://doi.org/" + answers['meta'].apply(lambda x: x["doi"])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")
    merge = merge[merge["score_y"] >= 0.1]
    results = merge[["content", "answer", "score_y", "doi_link"]].sort_values(by="score_y", ascending=False).to_dict(orient="records")
    return results