# library imports
from haystack import Pipeline
from haystack.nodes import PreProcessor, DensePassageRetriever
from haystack import Document

import pandas as pd
import os
import texthero as hero
import logging

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

from helper_functions import get_elasticsearch_document_store

def main():

    # get the host where Elasticsearch is running, default to localhost
    host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    document_store_reddit = get_elasticsearch_document_store(host, "document_reddit")

    # load data
    data = pd.read_pickle("../data/reddit/nutrition.pkl")

    # clean data
    data["concat"] = data["Thread Title"] + " " + data["Comment Body"]
    data["url"] = "https://www.reddit.com/r/nutrition/comments/" + data["Thread ID"] + "/comment/" + data["Comment ID"] + "/"

    custom_pipeline = [hero.preprocessing.lowercase,
                    hero.preprocessing.remove_whitespace,
                    hero.preprocessing.remove_angle_brackets,
                    hero.preprocessing.remove_html_tags,
                    hero.preprocessing.remove_urls]

    data['concat_clean'] = hero.clean(data['concat'], custom_pipeline)

    data_list = []
    for body, title, url in zip(list(data["concat_clean"]), list(data["Thread Title"]), list(data["url"])):
        doc = Document(body, meta={"title": title, "url": url})
        data_list.append(doc)

    # initialize indexing pipeline for document store
    indexing_pipeline = Pipeline()

    # initialize haystack preprocessor
    preprocessor = PreProcessor(
        clean_whitespace=True,
        clean_header_footer=True,
        clean_empty_lines=True
    )

    # add nodes to pipeline
    indexing_pipeline.add_node(component=preprocessor, name="PreProcessor", inputs=["Query"])
    indexing_pipeline.add_node(component=document_store_reddit, name="DocumentStore", inputs=["PreProcessor"])

    # run the indexing pipeline
    indexing_pipeline.run_batch(documents=data_list)

    # initialize retriever model
    retriever = DensePassageRetriever(
        document_store=document_store_reddit,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
    )

    # update embeddings of documents in the document store using the retriever model
    document_store_reddit.update_embeddings(retriever)

if __name__ == "__main__":
    main()