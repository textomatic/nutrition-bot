from haystack.nodes import PreProcessor, DensePassageRetriever
from haystack import Document
import texthero as hero

import os
import logging

logging.basicConfig(format="%(levelname)s - %(name)s -  %(message)s", level=logging.WARNING)
logging.getLogger("haystack").setLevel(logging.INFO)

from helper_functions import download_all_pdfs, get_elasticsearch_document_store, convert_research_papers

# initialize constants
pdf_dir_local = "../data/all_pdfs/"
cloud_storage_bucket_name = "aipi540_nlp_nutrition"
cloud_storage_folder = "all_pdfs/"

def main():
    '''
    Download research papers from google cloud storage, process them, and index them in Elasticsearch.
    
    Args:
        None

    Return:
        None
    '''
    # get the host where Elasticsearch is running, default to localhost
    host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
    document_store_research = get_elasticsearch_document_store(host, "document_research")

    # download all research papers from google cloud storage
    download_all_pdfs(cloud_storage_bucket_name, cloud_storage_folder, pdf_dir_local)
    pdfs_to_index = [pdf_dir_local + "/" + f for f in os.listdir(pdf_dir_local)]

    # convert research papers to dataframe
    research_papers_df = convert_research_papers(pdfs_to_index, pdf_dir_local)

    # clean the content of the research papers using texthero
    custom_pipeline = [hero.preprocessing.remove_whitespace,
                    hero.preprocessing.remove_angle_brackets,
                    hero.preprocessing.remove_html_tags,
                    hero.preprocessing.remove_urls,
                    hero.preprocessing.remove_square_brackets]

    research_papers_df['content_clean'] = hero.clean(research_papers_df['content'], custom_pipeline)

    data_list = []
    for content, doi in zip(list(research_papers_df["content_clean"]), list(research_papers_df["doi"])):
        doc = Document(content, meta={"doi": doi})
        data_list.append(doc)

    # create preprocessor to split documents into smaller chunks
    preprocessor = PreProcessor(
        clean_whitespace=True,
        clean_header_footer=True,
        clean_empty_lines=True,
        split_by="word",
        split_length=150,
        split_overlap=10,
        split_respect_sentence_boundary=True,
    )

    # split documents into smaller chunks
    preprocessed_docs = preprocessor.process(documents=data_list)

    # write documents to document store
    document_store_research.write_documents(preprocessed_docs)

    # intialize DensePassageRetriever
    retriever = DensePassageRetriever(
        document_store=document_store_research,
        query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
        passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base"
    )

    # update embeddings
    document_store_research.update_embeddings(retriever)

if __name__ == "__main__":
    main()