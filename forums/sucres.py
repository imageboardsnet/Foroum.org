from bs4 import BeautifulSoup
from sutils import convert_to_epoch

def parse_2sucres(html_content):
    """
    Parse the HTML content of https://2sucres.org/forums/1/1 and return a list of topics in a uniform JSON structure.
    """
    print("[DEBUG] Parsing HTML content for 2sucres.org")
    soup = BeautifulSoup(html_content, 'html.parser')
    topics_divs = soup.select('div.tbody > div > div.tr')  # Updated CSS selector

    if not topics_divs:
        print("[DEBUG] No topics found. Check the CSS selector or website structure.")
    
    topics = []
    for topic_div in topics_divs:
        # Topic title
        title_tag = topic_div.select_one('div.topicName a')
        title = title_tag.get_text(strip=True) if title_tag else None

        # URL to the topic
        topic_url = f"https://2sucres.org{title_tag.get('href')}" if title_tag else None

        # Username
        user_tag = topic_div.select_one('div.topicAuteur a')
        username = user_tag.get_text(strip=True) if user_tag else None

        # Number of replies
        replies_tag = topic_div.select_one('div.topicNb')
        replies = int(replies_tag.get_text(strip=True)) if replies_tag else 0

        # Last activity
        last_activity_tag = topic_div.select_one('div.topicDernier a')
        last_activity = convert_to_epoch(last_activity_tag.get_text(strip=True)) if last_activity_tag else None

        if title in ["Les bugs / éléments inconvenants sur 2Sucres", "[OFFICIEL] Bienvenue aux NOUVEAUX ! + TUTO","Secrétariat de 2S (Modération/Administration)","Feuille de route du développement de 2Sucres"]:
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
            print(f"[DEBUG] Found topic: {topic_info}")
            topics.append(topic_info)

    print(f"[DEBUG] Total topics parsed for 2sucres.org: {len(topics)}")
    return topics