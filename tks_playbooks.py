from notion_client import Client
import re
import json

from pymongo import MongoClient

# Replace with your actual connection string
client = MongoClient("mongodb+srv://pranavmenon:Kceawhf6123...@serverlessinstance0.pgxo6w3.mongodb.net/?retryWrites=true&w=majority")
db = client.gpt_playbook
collection = db.playbook

notion = Client(auth="secret_oElIIAJoGfU0lbUh8OEWfbFcXYhXWqRRYYYOL9xV8Zx")

# Define a function to create unique identifiers based on the content
def create_unique_identifier(content):
    # You can customize this function to create a unique identifier based on the content
    # For simplicity, we'll use a hash of the content as the unique identifier
    import hashlib
    unique_id = hashlib.sha256(content.encode()).hexdigest()
    return unique_id

def find_page_id_from_url(notion_url):
    # Regular expression to extract the page ID from the URL
    match = re.search(r"([a-z0-9]{32})", notion_url)
    if match:
        return match.group(1)
    else:
        return None

def extract_text_from_block(block):
    """Extract text from a given block based on its type."""
    text_content = ""
    if block.get("type") in ["paragraph", "heading_1", "heading_2", "heading_3"]:
        for text_segment in block[block["type"]]["rich_text"]:
            text_content += text_segment.get("plain_text", "")
    return text_content

def extract_content_from_child_pages(parent_page_id):
    parent_blocks = notion.blocks.children.list(block_id=parent_page_id)["results"]
    all_text_content = []

    for block in parent_blocks:
        if block["type"] == "child_page":
            child_page_id = block["id"]
            child_blocks = notion.blocks.children.list(block_id=child_page_id)["results"]

            for child_block in child_blocks:
                text_content = extract_text_from_block(child_block)
                if text_content:
                    all_text_content.append(text_content)

    return all_text_content



def update_mongodb(text_content):
    for item in text_content:
        unique_identifier = create_unique_identifier(item)
        try:
            collection.update_one(
                {"unique_identifier": unique_identifier},
                {"$set": {"content": item}},
                upsert=True
            )
        except Exception as e:
            print(f"Error updating MongoDB: {e}")

# Main execution
def main():
    notion_webpage_url = "https://www.notion.so/Test-Page-2f7d41f4dba24d6aa6c1255bce0fec85?pvs=4"
    parent_page_id = find_page_id_from_url(notion_webpage_url)

    if parent_page_id:
        text_content = extract_content_from_child_pages(parent_page_id)
        print("Extracted Text Content:", "\n".join(text_content))
        update_mongodb(text_content)
    else:
        print("Page ID not found.")

if __name__ == "__main__":
    main()