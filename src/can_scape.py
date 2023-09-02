import requests


def can_scrape(url, user_agent="*"):
    """
    Check if a URL can be scraped based on its robots.txt
    """
    # Extract base URL and get robots.txt
    if not url.startswith("http"):
        url = "http://" + url
    if not url.endswith("/"):
        url += "/"
    robots_url = url + "robots.txt"

    try:
        response = requests.get(robots_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        lines = response.text.strip().split("\n")
        disallow_list = []
        user_agent_list = []
        current_user_agent = None

        for line in lines:
            line = line.strip().lower()
            if line.startswith("user-agent:"):
                current_user_agent = line.split(":")[1].strip()
                user_agent_list.append(current_user_agent)
            elif line.startswith("disallow:") and current_user_agent:
                disallowed_path = line.split(":")[1].strip()
                disallow_list.append(disallowed_path)

        # Check if given user_agent is allowed to scrape
        if user_agent in user_agent_list:
            for path in disallow_list:
                if url.endswith(path):
                    return False
        return True

    except requests.RequestException as e:
        print(f"Error checking robots.txt: {e}")
        return False
