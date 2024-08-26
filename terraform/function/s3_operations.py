from google.cloud import storage

class GCSJoinedGiveawaysHandler:
    """ We use a GCS bucket to hold the log file with the id's of the giveaway posts that have already been joined.
    This class provides methods to read and append to the file in the GCS bucket.
    """

    def __init__(self, bucket_name, file_name):
        self.bucket_name = bucket_name
        self.file_name = file_name

        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(self.bucket_name)
        self.blob = self.bucket.blob(self.file_name)

    def log_joined_giveaway(self, append_text):
        """
        Append a line to a file in a GCS bucket.
        """
        try:
            # First, read the existing content
            existing_content = self.get_joined_giveaways()
            if existing_content is None:
                existing_content = ""

            # Append the new line
            updated_content = existing_content + "\n" + append_text

            # Upload the updated content back to GCS
            self.blob.upload_from_string(updated_content)
            print("Successfully appended to the file in GCS")
        except Exception as e:
            raise Exception(
                f"Error appending to the file in GCS: {str(e)}"
            )

    def get_joined_giveaways(self):
        try:
            if self.blob.exists():
                file_content = self.blob.download_as_text()
                return file_content
            else:
                print(f"File {self.file_name} does not exist in GCS bucket {self.bucket_name}.")
                return None
        except Exception as e:
            print(f"Error reading file from GCS: {str(e)}")
            return None

    def check_if_giveaway_joined(self, post_id):
        """
        Check if a giveaway post has already been joined.
        """
        try:
            existing_content = self.get_joined_giveaways()
            if existing_content is None:
                raise Exception("Error reading file from GCS")

            return post_id in [line.strip() for line in existing_content.split("\n")]
        except Exception as e:
            raise Exception(
                f"Error checking if giveaway post has been joined: {str(e)}")


if __name__ == "__main__":
    # Test the GCSJoinedGiveawaysHandler class
    store_handler = GCSJoinedGiveawaysHandler(
        "reddit-giveaways-giveaway-data", "giveaway_log.txt"
    )

    store_handler.log_joined_giveaway("test1")
    file_content = store_handler.get_joined_giveaways()
    print([line.strip() for line in file_content.split("\n")])
    print(file_content)
