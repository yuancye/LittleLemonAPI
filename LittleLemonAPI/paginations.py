from rest_framework.pagination import PageNumberPagination

class MenuItemPagination(PageNumberPagination):
   page_size = 2
   page_size_query_param = 'perpage'
   max_page_size = 10
   page_query_param = 'page'