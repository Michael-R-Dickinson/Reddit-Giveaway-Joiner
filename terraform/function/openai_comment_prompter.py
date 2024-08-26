from openai import OpenAI
import logging
import os


def generate_comment_text_with_openai(post_text, pinned_comments_text, context_comments_text):
    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
    )

    # Prepare the prompt for OpenAI
    prompt = f"""
    Post text: {post_text}
    Op's comments: {pinned_comments_text}
    Context comments: {context_comments_text}
    Based on the post & comments, generate a short comment to join this giveaway. Do not generate any text that is not to be included in the comment. ONLY generate the comment text and nothing else.
    Not too flowery, no emojis, no exclamation marks, keep it casual.
    If the post asks for a color or type of item, copy the idea (but not message exactly) from one of the context comments.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates comments for giveaway posts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )

        # Extract the generated comment from the API response
        generated_comment = response.choices[0].message.content.strip()

        return generated_comment

    except Exception as e:
        logging.error(f"Error generating comment: {str(e)}")
        return "Thanks for the giveaway! I'd love to participate."  # Fallback comment


if __name__ == "__main__":
    post_text = "I'm giving away a brand new mechanical keyboard! To enter, simply comment below and tell me your favorite keyboard switch."
    pinned_comments_text = "This is a pinned comment with additional information about the giveaway rules and end date."

    generated_comment = generate_comment_text_with_openai(
        post_text, pinned_comments_text, '')
    print(generated_comment)
