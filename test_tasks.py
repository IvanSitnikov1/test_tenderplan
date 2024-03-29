import unittest

from tasks import LinkCollectionTask, ParseFormTask


class TestCeleryTasks(unittest.TestCase):

    def test_link_collection_task(self):
        url = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html'
        result = LinkCollectionTask().apply_async(args=[url, 1]).get()
        self.assertEqual(len(result), 10)
        self.assertTrue(all(isinstance(item, str) for item in result))

    def test_parse_form_task(self):
        form_url = 'https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338300047924000069'
        result = ParseFormTask().apply_async(args=[form_url]).get()
        self.assertEqual(result, '"https://zakupki.gov.ru/epz/order/notice/printForm/viewXml.html?regNumber=0338300047924000069" - "2024-03-21T16:38:28.857+12:00"')


if __name__ == '__main__':
    unittest.main()