import boto3


class S3JoinedGiveawaysHandler:
    """ We use an s3 bucket to hold the log file with the id's of the giveaway posts that have already been joined.
    This class provides methods to read and append to the file in the s3 bucket.
    """

    def __init__(self, bucket_name, file_name):
        self.bucket_name = bucket_name
        self.file_name = file_name

        self.s3 = boto3.client('s3')

    def log_joined_giveaway(self, append_text):
        """
        Append a line to a file in an S3 bucket.
        """
        try:
            # First, read the existing content
            existing_content = self.get_joined_giveaways()
            if existing_content is None:
                existing_content = ""

            # Append the new line
            updated_content = existing_content + "\n" + append_text

            # Upload the updated content back to S3
            self.s3.put_object(Bucket=self.bucket_name, Key=self.file_name,
                               Body=updated_content)
            print("Successfully appended to the file in S3")
        except Exception as e:
            raise Exception(
                f"Error appending to the file in S3: {str(e)}"
            )

    def get_joined_giveaways(self):
        try:
            response = self.s3.get_object(
                Bucket=self.bucket_name, Key=self.file_name)
            file_content = response['Body'].read().decode('utf-8')
            return file_content
        except Exception as e:
            print(f"Error reading file from S3: {str(e)}")
            return None

    def check_if_giveaway_joined(self, post_id):
        """
        Check if a giveaway post has already been joined.
        """
        try:
            existing_content = self.get_joined_giveaways()
            if existing_content is None:
                raise Exception("Error reading file from S3")

            return post_id in [line.strip() for line in existing_content.split("\n")]
        except Exception as e:
            raise Exception(
                f"Error checking if giveaway post has been joined: {str(e)}")


if __name__ == "__main__":
    # Test the S3StoreHandler class
    store_handler = S3JoinedGiveawaysHandler(
        "reddit-giveaway-bot-data-store", "RedditCommenter giveaways.txt")

    store_handler.log_joined_giveaway("test1")
    file_content = store_handler.get_joined_giveaways()
    print([line.strip() for line in file_content.split("\n")])
    print(file_content)
