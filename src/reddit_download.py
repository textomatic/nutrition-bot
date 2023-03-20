import os
import praw
import pandas as pd

# Define constants
_PRAW_INI_SECTION = "nutritionbot"
_SUBREDDIT_NAME = "nutrition"
_CSV_FILE_PATH = "../data/reddit/nutrition.csv"


def check_ini():
    """
    Checks for the presence of praw.ini - a file that contains credential for accessing Reddit programmatically.
    
    Args:
        None
    
    Return:
        None    
    """

    return os.path.exists(os.path.realpath(os.path.dirname(__file__)) + '/praw.ini')


def main():
    """
    Initialize Reddit instance using PRAW, download threads and comments from a subreddit, save them in a dataframe, and store them as a CSV file.

    Args:
        None
    
    Return:
        None    
    """

    # Throw exception if Reddit credential doesn't exist
    if not check_ini():
        raise Exception("INI file with Reddit credential not found! Please ensure praw.ini exists in the current directory.")

    # Initialize Reddit and nutrition subreddit instances
    reddit = praw.Reddit(_PRAW_INI_SECTION)
    subreddit = reddit.subreddit(_SUBREDDIT_NAME)
    print(f"Subreddit name: {subreddit.display_name}")

    # Store threads and comments as lists of list
    data = []
    post_count = 0
    comment_overall_count = 0

    for submission in subreddit.new(limit=1000000):
        if submission.score > 50: # only store threads with a upvote count higher than 50
            post_count += 1
            comment_count = 0
            submission.comments.replace_more(limit=None) # get all comments associated with the thread
            for comment in submission.comments.list():
                comment_count += 1
                row = [submission.title, submission.score, submission.id, submission.url, submission.selftext, submission.num_comments, comment.id, comment.link_id, comment.score, comment.body]
                data.append(row)
            comment_overall_count += comment_count
            print(f"Submission ID '{submission.id}', Comment Count: {comment_count}")

    print(f'Total posts: {post_count}')
    print(f'Total comments: {comment_overall_count}')

    # Store collected data as a dataframe
    df = pd.DataFrame(data=data, columns=['Thread Title', 'Thread Upvotes', 'Thread ID', 'Thread URL', 'Thread Body', 'Number of Comments', 'Comment ID', 'Comment Link', 'Comment Upvotes', 'Comment Body']).reset_index(drop=True)

    # Save dataframe as CSV file
    df.to_csv(_CSV_FILE_PATH, index=False)
    print(f"Data successfully saved to: {_CSV_FILE_PATH}")


if __name__ == '__main__':
    main()