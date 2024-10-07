from django.test import TestCase
from django.urls import reverse
import urllib.request


class UksiViewIntegrationTests(TestCase):

    def test_fetch_uksi_data_success(self):
        """
        Test successful fetching of real XML data and rendering of the response.
        """
        
        response = self.client.get(reverse('fetch_uksi_data'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'uksi/contents.html')
        self.assertContains(response, "The Power to Award Degrees etc.")
        self.assertContains(response, "Citation and commencement")

    def test_fetch_uksi_data_failure(self):
        """
        Test the failure case where the URL returns a non-200 status code.
        """
        bad_url = "https://www.legislation.gov.uk/invalid-url"
        try:
            response = urllib.request.urlopen(bad_url)
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 404)
        else:
            self.fail("Expected HTTPError for invalid URL, but got success")

        response = self.client.get(reverse('fetch_uksi_data'))
        self.assertEqual(response.status_code, 200)

    def test_fetch_uksi_data_real_content(self):
        """
        Ensure real XML content is fetched and parsed correctly.
        """
        url = "https://www.legislation.gov.uk/uksi/2024/979/contents/made/data.xml"
        response = urllib.request.urlopen(url)
        self.assertEqual(response.status, 200)

        xml_data = response.read()
        self.assertIn(b"The Power to Award Degrees etc.", xml_data)
