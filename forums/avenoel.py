from bs4 import BeautifulSoup
from sutils import convert_to_relative_time

def parse_avenoel(html_content):
    """
    Parse the HTML content of https://avenoel.org/forum and return a list of topics in a uniform JSON structure.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    topics_rows = soup.select('tr')  # Each forum topic is contained in a <tr> element

    topics = []
    for row in topics_rows:
        # Initialize title to avoid referencing it before assignment
        title = None

        # Topic title
        title_tag = row.select_one('td.topics-title a')
        if title_tag:
            title = title_tag.get_text(strip=True)
            if title.endswith(')') and '(' in title:
                title = title[:title.rfind('(')].strip()

        # URL to the topic
        topic_url = title_tag.get('href') if title_tag else None

        # Username
        user_tag = row.select_one('td.topics-author a')
        username = user_tag.get_text(strip=True) if user_tag else None

        # Number of replies
        replies_tag = row.select_one('td.topics-amount')
        replies = replies_tag.get_text(strip=True) if replies_tag else '0'

        # Last activity
        last_activity_tag = row.select_one('td.topics-date')
        last_activity_raw = last_activity_tag.get_text(strip=True) if last_activity_tag else None

        # Convert last_activity to relative time (e.g., "43s", "5m", "2h")
        last_activity = convert_to_relative_time(last_activity_raw)

        if title in ["Topic de modération", "🟣 Discord d'AVN (nouveau lien)"]:
            print(f"[DEBUG] Skipping topic with title: {title}")
            continue

        if title and topic_url:
            topic_info = {
                'title': title,
                'topic_url': topic_url,
                'username': username,
                'replies': int(replies),
                'last_activity': last_activity
            }
            topics.append(topic_info)

    return topics