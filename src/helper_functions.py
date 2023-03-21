# library imports
from google.cloud import storage

from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import PDFToTextConverter

import pandas as pd

from pathlib import Path
from tqdm import tqdm

def download_all_pdfs(cloud_storage_bucket_name, cloud_storage_prefix, local_storage_path):
    '''
    Downloads all pdfs from a cloud storage bucket to a local directory.

    Args:
        cloud_storage_bucket_name (str): Name of the cloud storage bucket.
        cloud_storage_prefix (str): Prefix of the cloud storage bucket.
        local_storage_path (str): Path to the local directory where the pdfs should be downloaded to.

    Returns:
        None
    '''
    # create storage client
    storage_client = storage.Client()

    # create bucket object
    bucket = storage_client.bucket(cloud_storage_bucket_name)

    # get list of all blobs in bucket with prefix "all_pdfs/"
    file_iter = bucket.list_blobs(prefix=cloud_storage_prefix)

    for file in tqdm(file_iter):
        file.download_to_filename(file.name.replace(cloud_storage_prefix, local_storage_path))

def get_elasticsearch_document_store(host, username="", password="", index="document"):
    
    '''
    Returns an ElasticsearchDocumentStore object.

    Args:
        host (str): Hostname of the Elasticsearch instance.
        username (str): Username of the Elasticsearch instance.
        password (str): Password of the Elasticsearch instance.
        index (str): Name of the Elasticsearch document index.

    Returns:
        ElasticsearchDocumentStore: ElasticsearchDocumentStore object.
    '''

    # create ElasticsearchDocumentStore
    document_store = ElasticsearchDocumentStore(
        host=host,
        username=username,
        password=password,
        index=index,
        similarity="dot_product",
        embedding_dim=768,
    )
    
    return document_store

def convert_research_papers(pdfs_to_index, pdf_dir_local):
    '''
    Converts a list of pdfs to a Pandas dataframe.

    Args:
        pdfs_to_index (list): List of pdfs to be converted.
        pdf_dir_local (str): Path to the local directory where the pdfs are stored.

    Returns:
        all_pdfs_df (pd.DataFrame): Pandas dataframe containing the pdfs.
    '''

    all_pdfs_df = pd.DataFrame(columns=["content", "doi"])

    # create PDFToTextConverter
    pdf_text_converter = PDFToTextConverter(
        remove_numeric_tables=True,
        valid_languages=["en"]
    )

    # convert pdfs to dataframe
    for pdf in tqdm(pdfs_to_index):
        meta = {"doi": pdf.replace(pdf_dir_local+"/", "").replace(".pdf", "").replace("_", "/")}
        doc = pdf_text_converter.convert(file_path=Path(pdf), meta=meta)
        rp_df = pd.DataFrame({"content": doc[0].to_dict()["content"], "doi": doc[0].to_dict()["meta"]["doi"]}, index=[0])
        all_pdfs_df = pd.concat([all_pdfs_df, rp_df], axis=0)

    return all_pdfs_df