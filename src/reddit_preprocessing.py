import pandas as pd

# Define constants
_CSV_FILE_PATH = "../data/reddit/nutrition.csv"
_PICKLE_FILE_PATH = "../data/reddit/nutrition.pkl"


def main():
    """
    Read in downloaded Reddit threads and comments as Pandas dataframe, group dataframe by thread title, sort by descending order of upvotes, and save them as pickle.
    
    Args:
        None

    Return:
        None
    """

    # Read in downloaded threads and comments as dataframe
    df = pd.read_csv(_CSV_FILE_PATH, index_col=False)
    # Group dataframe by Thread Title and sort rows according to the highest thread upvotes and comment upvotes
    df_group = df.groupby(by=['Thread Title'])['Thread Title', 'Thread Upvotes', 'Thread ID', 'Thread URL', 'Thread Body', 'Number of Comments', 'Comment ID', 'Comment Link', 'Comment Upvotes','Comment Body'].apply(lambda x: x).sort_values(by=["Thread Upvotes", "Comment Upvotes"], ascending=False).reset_index(drop=True)
    # Add a new column to record approximate word count of each comment
    df_group['Comment Word Count'] = df_group['Comment Body'].apply(lambda x: len(x.split(" ")))
    # Save dataframe as pickle for ease of ingestion by ElasticSearch document store
    df_group.to_pickle('../data/reddit/nutrition.pkl')


if __name__ == '__main__':
    main()