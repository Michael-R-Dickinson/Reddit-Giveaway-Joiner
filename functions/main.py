import praw
import time
import datetime
from datetime import datetime, timedelta
from pytz import timezone
import pytz
import logging
from praw.models import MoreComments
from openai_comment_prompter import generate_comment_text_with_openai
import os


CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USERNAME = os.getenv("REDDIT_USERNAME")
PASSWORD = os.getenv("REDDIT_PASSWORD")

FAKE_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'

TARGET_SUBREDDIT = "MechanicalKeyboards"
GIVEAWAY_TAG = "Giveaway"

TIME_THRESHOLD = timedelta(hours=24)

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

my_timezone = timezone('US/Pacific')
time_format = "%B %d, %Y at %I:%M %p"


def create_comment_text(post):
    post_text = post.selftext

    authors_comments_text = ""
    context_comments_text = ""
    for i, comment in enumerate(post.comments):
        if isinstance(comment, MoreComments):
            continue
        if comment.author == post.author:
            authors_comments_text += comment.body + "\n\n"
        if 5 < i < 7:
            context_comments_text += comment.body + "\n"

    return generate_comment_text_with_openai(post_text, authors_comments_text, context_comments_text)


def check_for_existing_comment(post):
    with open('joined_giveaways.txt', 'r') as file:
        return post.id in [line.strip() for line in file]


def post_within_timeframe(submission, time_threshold):
    current_time_utc = datetime.now(pytz.utc)
    post_time_utc = datetime.fromtimestamp(submission.created_utc, pytz.utc)

    return current_time_utc - post_time_utc <= time_threshold


def get_giveaway_posts_in_timespan(reddit, target_subreddit, giveaway_tag, timespan):
    target_sub = reddit.subreddit(target_subreddit)
    giveaway_posts = target_sub.search(
        f'flair:{giveaway_tag}', sort='new', time_filter='day')
    giveaway_posts_in_timeframe = [
        post for post in giveaway_posts if post_within_timeframe(post, timespan)]

    return giveaway_posts_in_timeframe


def join_giveaways(reddit):
    current_local_time = datetime.now(pytz.utc).astimezone(my_timezone)
    active_giveaway_posts = get_giveaway_posts_in_timespan(
        reddit, TARGET_SUBREDDIT, GIVEAWAY_TAG, TIME_THRESHOLD)

    logging.info("Checked For Posts at {}".format(
        current_local_time.strftime(time_format)))
    print("Checked For Posts at {}".format(
        current_local_time.strftime(time_format)
    ))

    for post in active_giveaway_posts:
        has_already_commented = check_for_existing_comment(post)
        if not has_already_commented:
            comment_text = create_comment_text(post)
            print({
                "title": post.title,
                "comment": comment_text
            })
            post.reply(comment_text)

            with open('joined_giveaways.txt', 'a') as file:
                file.write(post.id + '\n')

            logging.info("Commented on post: {} at {}".format(
                post.title, current_local_time.strftime(time_format)))
        else:
            logging.info(f"Already commented on post: {post.title}")


def main():
    reddit = praw.Reddit(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        user_agent=FAKE_USER_AGENT,
        username=USERNAME,
        password=PASSWORD
    )

    while True:
        join_giveaways(reddit)
        time.sleep(3)


if __name__ == "__main__":
    main()
