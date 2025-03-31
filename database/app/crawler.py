import wikipediaapi

def fetch_wikipedia_page(title):
    wiki_wiki = wikipediaapi.Wikipedia(user_agent="Bradley's Wikipedia Crawler", language="en")
    page = wiki_wiki.page(title)

    if not page.exists():
        print(f"Page '{title}' does not exist.")
        return None

    return page.text

def save_text_to_file(title, content):
    filename = f"{title.replace(' ', '_')}.txt"
    with open(filename, "w", encoding="utf-8") as file:
        file.write(content)
    print(f"Saved content to {filename}")

if __name__ == "__main__":
    page_title = "Google"
    content = fetch_wikipedia_page(page_title)

    if content:
        save_text_to_file(page_title, content)
