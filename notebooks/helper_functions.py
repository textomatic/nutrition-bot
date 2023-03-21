# library imports
from google.cloud import storage
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