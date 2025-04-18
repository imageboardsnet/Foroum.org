from bs4 import BeautifulSoup

def parse_village(html_content):
    """
    Parse the HTML content of https://village.cx/village
    and return a list of topics in a uniform JSON structure.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    topics_divs = soup.select('div.row-center.bg-base-0')  # Each topic container

    print(f"[DEBUG] Found {len(topics_divs)} topics in village.cx")

    topics = []
    for topic_div in topics_divs:
        try:
            # Get the main link element which contains most of the data
            link_element = topic_div.select_one('a[href^="/village/"].row-center')
            if not link_element:
                continue

            # Find title and replies within the first span
            title_container = link_element.select_one('div span.font-medium')
            if title_container:
                title_span = title_container.select_one('span.topic-title')
                replies_span = title_container.select_one('span.text-sm i.far.fa-message-lines')
                
                title = title_span.get_text(strip=True) if title_span else ''
                replies = '0'
                if replies_span and replies_span.parent:
                    replies = replies_span.parent.get_text(strip=True)

            # Get topic URL
            topic_url = f"https://village.cx{link_element['href']}"
            
            # Username is in a span with text-sm class within the link
            username_span = link_element.select_one('span.row-center.text-sm span')
            username = username_span.get_text(strip=True) if username_span else 'Unknown'
            
            # Last activity time is in the last span
            last_activity_span = link_element.select_one('span.ml-auto.mr-2')
            last_activity = last_activity_span.get_text(strip=True).replace(' ', '') if last_activity_span else None

            topic_info = {
                'title': title,
                'topic_url': topic_url,
                'username': username,
                'replies': replies,
                'last_activity': last_activity
            }
            print(f"[DEBUG] Extracted topic: {topic_info}")
            topics.append(topic_info)
        except Exception as e:
            print(f"[ERROR] Failed to parse topic: {e}")
            continue

    return topics