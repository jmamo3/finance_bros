import feedparser
import re

def get_reddit_sentiment(ticker: str):
    url = f"https://www.reddit.com/search.rss?q={ticker}&sort=relevance&limit=10&restrict_sr=0"
    
    feed = feedparser.parse(url)
    
    if not feed.entries:
        return {"error": f"No Reddit posts found for {ticker}"}
    
    posts = []
    for entry in feed.entries:
        title = entry.get("title", "")
        content = re.sub(r'<[^>]+>', '', entry.get("summary", ""))
        subreddit = entry.get("tags", [{}])[0].get("term", "unknown") if entry.get("tags") else "unknown"
        
        posts.append({
            "title": title,
            "content": content.strip(),
            "subreddit": subreddit,
            "url": entry.get("link", "")
        })
    
    return {
        "ticker": ticker,
        "posts": posts
    }

if __name__ == "__main__":
    ticker = input("Enter ticker symbol: ").upper()
    result = get_reddit_sentiment(ticker)
    for post in result["posts"]:
        print(post["title"])
        print(post["subreddit"])
        # print(post["content"][:200])  # first 200 chars of content (TESTING PURPOSES)
        print()