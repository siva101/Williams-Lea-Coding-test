# uksi/views.py
import urllib.request
import xml.etree.ElementTree as ET
from django.shortcuts import render

NAMESPACES = {
    'leg': 'http://www.legislation.gov.uk/namespaces/legislation',
    'ukm': 'http://www.legislation.gov.uk/namespaces/metadata',
    'dc': 'http://purl.org/dc/elements/1.1/',
}


class UksiDataFetcher:
    """
    Responsible for fetching UKSI XML data from a given URL.
    """
    def __init__(self, url):
        self.url = url

    def fetch(self):
        """
        Fetch XML data from the URL with appropriate headers.
        """
        req = urllib.request.Request(self.url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:106.0) Gecko/20100101 Firefox/106.0')
        req.add_header('Accept', 'application/xml')

        try:
            with urllib.request.urlopen(req) as response:
                return response.read()
        except urllib.error.URLError as e:
            raise Exception(f"Failed to fetch data: {e}")


class UksiDataParser:
    """
    Responsible for parsing XML data and extracting relevant information.
    """
    def __init__(self, xml_data):
        self.root = ET.fromstring(xml_data)

    def parse_metadata(self):
        """
        Extract metadata like title, description, and important dates.
        """
        title = self.root.find('.//dc:title', NAMESPACES).text
        description = self.root.find('.//dc:description', NAMESPACES).text
        made_date = self.root.find('.//ukm:Made', NAMESPACES).attrib['Date']
        coming_into_force = self.root.find('.//ukm:DateTime', NAMESPACES).attrib['Date']
        return {
            'title': title,
            'description': description,
            'made_date': made_date,
            'coming_into_force': coming_into_force,
        }

    def parse_articles(self):
        """
        Extract articles (contents) with their number, title, and link.
        """
        articles = []
        for item in self.root.findall('.//leg:ContentsItem', NAMESPACES):
            content_number = item.find('leg:ContentsNumber', NAMESPACES).text
            content_title = item.find('leg:ContentsTitle', NAMESPACES).text
            document_uri = item.attrib.get('DocumentURI')  # Get the link to the article
            articles.append({
                'number': content_number,
                'title': content_title,
                'link': document_uri
            })
        return articles


class UksiRenderer:
    """
    Responsible for rendering the UKSI data to the template.
    """
    def __init__(self, request):
        self.request = request

    def render(self, metadata, articles):
        """
        Render the fetched and parsed data to the template.
        """
        context = {
            'title': metadata['title'],
            'description': metadata['description'],
            'made_date': metadata['made_date'],
            'coming_into_force': metadata['coming_into_force'],
            'articles': articles
        }
        return render(self.request, 'uksi/contents.html', context)


def fetch_uksi_data(request):
    """
    Main Django view that uses other classes to fetch, parse, and render UKSI data.
    """
    url = "https://www.legislation.gov.uk/uksi/2024/979/contents/made/data.xml"

    
    fetcher = UksiDataFetcher(url)
    try:
        xml_data = fetcher.fetch()
    except Exception as e:
        return render(request, 'uksi/error.html', {'message': str(e)})

    parser = UksiDataParser(xml_data)
    metadata = parser.parse_metadata()
    articles = parser.parse_articles()

    renderer = UksiRenderer(request)
    return renderer.render(metadata, articles)
