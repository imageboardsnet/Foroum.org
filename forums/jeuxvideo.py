from bs4 import BeautifulSoup
from sutils import convert_to_relative_time

def parse_jeuxvideo(html_content):
    """
    Parse the HTML content of https://www.jeuxvideo.com/forums/0-51-0-1-0-1-0-blabla-18-25-ans.htm
    and return a list of topics in a uniform JSON structure.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    topics_list = soup.select('ul.topic-list > li[data-id]')  # Select all topic rows with a data-id attribute

    topics = []
    for topic in topics_list:
        # Topic title
        title_tag = topic.select_one('a.topic-title')
        title = title_tag.get_text(strip=True) if title_tag else None

        # URL to the topic
        topic_url = f"https://www.jeuxvideo.com{title_tag.get('href')}" if title_tag else None

        # Username
        user_tag = topic.select_one('a.topic-author')
        username = user_tag.get_text(strip=True) if user_tag else None

        # Number of replies
        replies_tag = topic.select_one('span.topic-count')
        replies = int(replies_tag.get_text(strip=True)) if replies_tag else 0

        # Last activity
        last_activity_tag = topic.select_one('span.topic-date a')
        last_activity = convert_to_relative_time(last_activity_tag.get_text(strip=True)) if last_activity_tag else None

        if title in ["Modération ultime= pas nous", "Règles du forum"]:
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
            topics.append(topic_info)

    return topics