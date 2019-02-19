# Register your models here.
from django.utils.safestring import mark_safe

from xadmin.apps import xadmin, TemplateDecorationAdmin
from app02.models import *


class BookDecorationAdmin(TemplateDecorationAdmin):


    display_list = ["title", "price"]
    display_link_list = ["title"]

# register models to Xadmin
xadmin.registration(Book, BookDecorationAdmin)



print("=" * 100 , xadmin.registry)

