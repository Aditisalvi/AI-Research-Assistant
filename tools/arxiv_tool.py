import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from crewai.tools import BaseTool


class ArxivSearchTool(BaseTool):
    name: str = "ArXiv Academic Search"
    description: str = (
        "Search ArXiv for peer-reviewed academic papers and preprints on any scientific topic. "
        "Use this for topics in physics, mathematics, computer science, AI/ML, biology, finance, and more. "
        "Input should be a search query string. "
        "Returns paper titles, authors, abstracts, publication dates, and ArXiv URLs."
    )
    max_results: int = 5

    def _run(self, query: str) -> str:
        try:
            encoded_query = urllib.parse.quote(query)
            url = (
                f"http://export.arxiv.org/api/query?"
                f"search_query=all:{encoded_query}"
                f"&start=0&max_results={self.max_results}"
                f"&sortBy=relevance&sortOrder=descending"
            )

            with urllib.request.urlopen(url, timeout=15) as response:
                xml_data = response.read().decode("utf-8")

            root = ET.fromstring(xml_data)
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            entries = root.findall("atom:entry", ns)

            if not entries:
                return f"No ArXiv papers found for query: '{query}'"

            results = []
            for entry in entries:
                title = entry.find("atom:title", ns)
                summary = entry.find("atom:summary", ns)
                published = entry.find("atom:published", ns)
                arxiv_id = entry.find("atom:id", ns)

                authors = entry.findall("atom:author", ns)
                author_names = [
                    a.find("atom:name", ns).text
                    for a in authors[:3]
                    if a.find("atom:name", ns) is not None
                ]

                title_text = title.text.strip().replace("\n", " ") if title is not None else "N/A"
                summary_text = summary.text.strip().replace("\n", " ")[:400] + "..." if summary is not None else "N/A"
                published_text = published.text[:10] if published is not None else "N/A"
                url_text = arxiv_id.text.strip() if arxiv_id is not None else "N/A"
                authors_text = ", ".join(author_names) if author_names else "N/A"

                results.append(
                    f"📄 Title: {title_text}\n"
                    f"👥 Authors: {authors_text}\n"
                    f"📅 Published: {published_text}\n"
                    f"🔗 URL: {url_text}\n"
                    f"📝 Abstract: {summary_text}"
                )

            return "\n\n---\n\n".join(results)

        except Exception as e:
            return f"ArXiv search failed for '{query}': {str(e)}"


def get_arxiv_tool() -> ArxivSearchTool:
    """Returns a CrewAI-compatible ArXiv search tool. No API key required."""
    return ArxivSearchTool()