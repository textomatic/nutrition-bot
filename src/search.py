from fastapi import FastAPI
from haystack.document_stores import ElasticsearchDocumentStore
from haystack import Pipeline
from haystack.nodes import FARMReader
from haystack.nodes import DensePassageRetriever
from haystack.utils import print_answers
from haystack import Document
from pathlib import Path

import pandas as pd
import os
from pprint import pprint
import logging

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

host = os.environ.get("ELASTICSEARCH_HOST", "localhost")

document_store_reddit = ElasticsearchDocumentStore(
    host=host,
    username="",
    password="",
    index="document_research",
    similarity="dot_product",
    embedding_dim=768
)

retriever = DensePassageRetriever(
    document_store=document_store_reddit,
    query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
    passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
)
reader = FARMReader(model_name_or_path="deepset/roberta-base-squad2", use_gpu=True)

querying_pipeline = Pipeline()
querying_pipeline.add_node(component=retriever, name="Retriever", inputs=["Query"])
querying_pipeline.add_node(component=reader, name="Reader", inputs=["Retriever"])

app = FastAPI()

@app.get("/search/{query}")
async def search(query: str):
    prediction = querying_pipeline.run(
        query=query,
        params={
        "Retriever": {"top_k": 10},
        "Reader": {"top_k": 5}
        })
    answers = pd.DataFrame([i.to_dict() for i in prediction["answers"]])
    answers['document_ids'] = answers['document_ids'].apply(lambda x: x[0])
    documents = pd.DataFrame([i.to_dict() for i in prediction["documents"]])
    merge = pd.merge(documents, answers, left_on="id", right_on="document_ids", how="inner")
    results = merge[["content", "answer", "score_y"]].sort_values(by="score_y", ascending=False).to_dict(orient="records")
    return results
    #return {"message": "Hello World"}
