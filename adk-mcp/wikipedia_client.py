# Placeholder for WikipediaClient
# This file is needed to allow the ADK agent to load the tool definitions.
# The methods are mocks and do not perform real Wikipedia lookups.

import logging

logger = logging.getLogger(__name__)

class WikipediaClient:
    def __init__(self, language="en"):
        logger.warning(f"Initializing MOCK WikipediaClient for language: {language}")
        self.language = language

    def search(self, query, limit=10):
        logger.warning(f"MOCK SEARCH: {query}, limit: {limit}")
        return [{"title": f"Mock Search Result for '{query}'", "pageid": 12345}]

    def get_article(self, title):
        logger.warning(f"MOCK GET_ARTICLE: {title}")
        return {"title": title, "content": f"This is the mock content for the article titled '{title}'.", "url": f"https://{self.language}.wikipedia.org/wiki/{title.replace(' ', '_')}"}

    def get_summary(self, title):
        logger.warning(f"MOCK GET_SUMMARY: {title}")
        return f"This is a mock summary for the article titled '{title}'."

    def summarize_for_query(self, title, query, max_length=250):
        logger.warning(f"MOCK SUMMARIZE_FOR_QUERY: {title}, query: {query}")
        return f"This is a mock query-focused summary for '{title}' regarding '{query}'."

    def summarize_section(self, title, section_title, max_length=150):
        logger.warning(f"MOCK SUMMARIZE_SECTION: {title}, section: {section_title}")
        return f"This is a mock summary for the section '{section_title}' in the article '{title}'."

    def extract_facts(self, title, topic_within_article, count=5):
        logger.warning(f"MOCK EXTRACT_FACTS: {title}, topic: {topic_within_article}")
        return [f"Mock fact {i+1} about {topic_within_article or title}" for i in range(count)]

    def get_related_topics(self, title, limit=10):
        logger.warning(f"MOCK GET_RELATED_TOPICS: {title}")
        return [f"Mock Related Topic {i+1}" for i in range(limit)]

    def get_sections(self, title):
        logger.warning(f"MOCK GET_SECTIONS: {title}")
        return ["Introduction", "History", "Mock Section 3"]

    def get_links(self, title):
        logger.warning(f"MOCK GET_LINKS: {title}")
        return ["https://en.wikipedia.org/wiki/Mock_Link_1", "https://en.wikipedia.org/wiki/Mock_Link_2"]
