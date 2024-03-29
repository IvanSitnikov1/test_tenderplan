from tasks import LinkCollectionTask, ParseFormTask


url = 'https://zakupki.gov.ru/epz/order/extendedsearch/results.html'


if __name__ == '__main__':
    # запускаем задачи для сбора ссылок с требуемых страниц
    task1 = LinkCollectionTask().apply_async(args=[url, 1])
    task2 = LinkCollectionTask().apply_async(args=[url, 2])

    # запускаем задачи парсинга для каждой формы и добавляем в список
    list_task = []
    for task in task1, task2:
        for form_url in task.get():
            list_task.append(ParseFormTask().apply_async(args=[form_url]))

    # выводим в консоль результат парсинга
    for task in list_task:
        print(task.get())
