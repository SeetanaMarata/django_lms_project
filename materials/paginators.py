from rest_framework.pagination import PageNumberPagination


class MaterialsPagination(PageNumberPagination):
    """
    Пагинатор для курсов и уроков.
    """

    page_size = 5  # по умолчанию 5 элементов на странице
    page_size_query_param = "page_size"  # параметр для изменения размера страницы
    max_page_size = 50  # максимум 50 элементов на странице
