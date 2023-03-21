# library imports
from google.cloud import storage

from haystack.document_stores import ElasticsearchDocumentStore
from haystack.nodes import PDFToTextConverter

import pandas as pd

from pathlib import Path
from tqdm import tqdm

def download_all_pdfs(cloud_storage_bucket_name, cloud_storage_prefix, local_storage_path):
    # create storage client
    storage_client = storage.Client()

    # create bucket object
    bucket = storage_client.bucket(cloud_storage_bucket_name)

    # get list of all blobs in bucket with prefix "all_pdfs/"
    file_iter = bucket.list_blobs(prefix=cloud_storage_prefix)

    for file in tqdm(file_iter):
        file.download_to_filename(file.name.replace(cloud_storage_prefix, local_storage_path))

def get_elasticsearch_document_store(host, username="", password="", index="document"):
    
    # create ElasticsearchDocumentStore
    document_store = ElasticsearchDocumentStore(
        host=host,
        username=username,
        password=password,
        index=index,
        similarity="cosine",
        embedding_dim=768,
    )
    
    return document_store

def convert_research_papers(pdfs_to_index, pdf_dir_local):
    
    all_pdfs_df = pd.DataFrame(columns=["content", "doi"])

    pdf_text_converter = PDFToTextConverter(
        remove_numeric_tables=True,
        valid_languages=["en"]
    )

    for pdf in tqdm(pdfs_to_index):
        meta = {"doi": pdf.replace(pdf_dir_local+"/", "").replace(".pdf", "").replace("_", "/")}
        doc = pdf_text_converter.convert(file_path=Path(pdf), meta=meta)
        rp_df = pd.DataFrame({"content": doc[0].to_dict()["content"], "doi": doc[0].to_dict()["meta"]["doi"]}, index=[0])
        all_pdfs_df = pd.concat([all_pdfs_df, rp_df], axis=0)

    return all_pdfs_df