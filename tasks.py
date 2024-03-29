from celery import Celery, Task
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import requests


app = Celery('myapp', backend='redis://localhost:6379', broker='redis://localhost:6379')
app.conf.update(
    CELERY_ALWAYS_EAGER=True
)

headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.129 Safari/537.36',
    }


class LinkCollectionTask(Task):
    """Задача для сбора ссылок на печатные формы с нужной страницы"""
    name = 'link_collection_task'

    def run(self, url, page_num):
        """Собираем в список адреса печатных xml-форм"""
        list_urls_xml = []
        params = {'fz44': 'on', 'pageNumber': {page_num}}
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            # выбираем блоки, включающие ссылки на формы
            printed_forms = soup.find_all(
                'div',
                class_='w-space-nowrap ml-auto registry-entry__header-top__icon'
            )
            # проходимся по блокам, выбираем ссылки и добавляем в список
            for elem in printed_forms:
                a_elements = elem.find_all('a')
                # редактируем ссылки для получения xml форм
                link = a_elements[1].get('href').replace('view.html',
                                                         'viewXml.html')
                list_urls_xml.append('https://zakupki.gov.ru' + link)
            return list_urls_xml
        else:
            return f'Ошибка при выполнении запроса. Код состояния: {response.status_code}'


class ParseFormTask(Task):
    """Задача для парсинга печатных xml-форм и выбора даты публикации"""
    name = 'parse_form_task'

    def run(self, form_url):
        """Собираем в строку ссылку на форму и дату её публикации"""
        response = requests.get(form_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'xml')
            tree = ET.ElementTree(ET.fromstring(str(soup)))
            root = tree.getroot()
            namespaces = {
                'ns7': 'http://zakupki.gov.ru/oos/printform/1',
                'ns': 'http://zakupki.gov.ru/oos/EPtypes/1'
            }
            # парсим поле publishDTInEIS
            publish_dt_in_eis = root.find(
                'ns:commonInfo/ns:publishDTInEIS',
                namespaces=namespaces)
            if publish_dt_in_eis is not None:
                return f'"{form_url}" - "{publish_dt_in_eis.text}"'
            else:
                return f'"{form_url}" - "None"'
        else:
            print('Ошибка при выполнении запроса 2. Код состояния:',
                  response.status_code)


# регистрируем задачи
app.register_task(LinkCollectionTask())
app.register_task(ParseFormTask())
