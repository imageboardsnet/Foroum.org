from bs4 import BeautifulSoup
from sutils import relative_time_to_epoch

def parse_onche(html_content):
    """
    Parse the HTML content of https://onche.org/forum/1/blabla-general
    and return a list of topics in a uniform JSON structure.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    topics_divs = soup.select('div.topic')  # Each forum topic is contained in <div class="topic ...>

    print(f"[DEBUG] Found {len(topics_divs)} topics in onche.org")

    topics = []
    for topic_div in topics_divs:
        # Topic title
        title_tag = topic_div.select_one('a.topic-subject.link span')
        title = title_tag.get_text(strip=True) if title_tag else None

        # URL to the topic
        link_tag = topic_div.select_one('a.topic-subject.link')
        topic_url = link_tag.get('href') if link_tag else None

        # Number of replies / posts
        replies_tag = topic_div.select_one('span.topic-nb')
        replies = replies_tag.get_text(strip=True) if replies_tag else '0'

        # Username
        user_tag = topic_div.select_one('div.topic-username')
        username = user_tag.get_text(strip=True) if user_tag else None

        # Last activity
        right_tag = topic_div.select_one('a.right span')
        last_activity = relative_time_to_epoch(right_tag.get_text(strip=True)) if right_tag else None

        # Skip specific titles
        if title in ["Topic de la modération", "[À LIRE] Règles du forum"]:
            print(f"[DEBUG] Skipping topic with title: {title}")
            continue

        if title and topic_url:
            topic_info = {
                'title': title,
                'topic_url': topic_url,
                'username': username,
                'replies': replies,
                'last_activity': last_activity
            }
            print(f"[DEBUG] Extracted topic: {topic_info}")
            topics.append(topic_info)

    return topics