import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
from crewai.tools import BaseTool


class PubMedSearchTool(BaseTool):
    name: str = "PubMed Biomedical Search"
    description: str = (
        "Search PubMed for peer-reviewed biomedical and life sciences research articles. "
        "Use this for topics in medicine, biology, pharmacology, neuroscience, genetics, public health, and clinical research. "
        "Input should be a search query string. "
        "Returns article titles, authors, journal names, publication dates, abstracts, and PubMed URLs."
    )
    max_results: int = 5

    def _fetch_ids(self, query: str) -> list:
        """Step 1: Use ESearch to get PubMed IDs for a query."""
        encoded_query = urllib.parse.quote(query)
        url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?"
            f"db=pubmed&term={encoded_query}&retmax={self.max_results}"
            f"&sort=relevance&retmode=json"
        )
        with urllib.request.urlopen(url, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
        return data.get("esearchresult", {}).get("idlist", [])

    def _fetch_details(self, ids: list) -> str:
        """Step 2: Use EFetch to get full article details for a list of IDs."""
        ids_str = ",".join(ids)
        url = (
            f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?"
            f"db=pubmed&id={ids_str}&retmode=xml"
        )
        with urllib.request.urlopen(url, timeout=15) as response:
            return response.read().decode("utf-8")

    def _parse_articles(self, xml_data: str) -> list:
        """Parse PubMed XML into structured article dicts."""
        root = ET.fromstring(xml_data)
        articles = []

        for article in root.findall(".//PubmedArticle"):
            # Title
            title_el = article.find(".//ArticleTitle")
            title = title_el.text if title_el is not None else "N/A"
            title = (title or "N/A").strip()

            # Authors
            author_els = article.findall(".//Author")
            authors = []
            for a in author_els[:3]:
                last = a.find("LastName")
                first = a.find("ForeName")
                if last is not None:
                    name = last.text
                    if first is not None:
                        name += f" {first.text}"
                    authors.append(name)
            authors_str = ", ".join(authors) if authors else "N/A"

            # Journal
            journal_el = article.find(".//Journal/Title")
            journal = journal_el.text if journal_el is not None else "N/A"

            # Publication date
            year_el = article.find(".//PubDate/Year")
            month_el = article.find(".//PubDate/Month")
            year = year_el.text if year_el is not None else ""
            month = month_el.text if month_el is not None else ""
            pub_date = f"{month} {year}".strip() if month else year or "N/A"

            # Abstract
            abstract_els = article.findall(".//AbstractText")
            abstract_parts = []
            for ab in abstract_els:
                label = ab.get("Label", "")
                text = ab.text or ""
                if label:
                    abstract_parts.append(f"{label}: {text}")
                else:
                    abstract_parts.append(text)
            abstract = " ".join(abstract_parts)[:400] + "..." if abstract_parts else "No abstract available."

            # PMID / URL
            pmid_el = article.find(".//PMID")
            pmid = pmid_el.text if pmid_el is not None else None
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else "N/A"

            articles.append({
                "title": title,
                "authors": authors_str,
                "journal": journal,
                "date": pub_date,
                "abstract": abstract,
                "url": url,
            })

        return articles

    def _run(self, query: str) -> str:
        try:
            ids = self._fetch_ids(query)
            if not ids:
                return f"No PubMed articles found for query: '{query}'"

            xml_data = self._fetch_details(ids)
            articles = self._parse_articles(xml_data)

            if not articles:
                return f"Could not parse PubMed results for query: '{query}'"

            results = []
            for art in articles:
                results.append(
                    f"📄 Title: {art['title']}\n"
                    f"👥 Authors: {art['authors']}\n"
                    f"📰 Journal: {art['journal']}\n"
                    f"📅 Published: {art['date']}\n"
                    f"🔗 URL: {art['url']}\n"
                    f"📝 Abstract: {art['abstract']}"
                )

            return "\n\n---\n\n".join(results)

        except Exception as e:
            return f"PubMed search failed for '{query}': {str(e)}"


def get_pubmed_tool() -> PubMedSearchTool:
    """Returns a CrewAI-compatible PubMed search tool. No API key required."""
    return PubMedSearchTool()