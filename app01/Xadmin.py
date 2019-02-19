# Register your models here.
from xadmin.apps import xadmin
from app01.models import *
from xadmin.apps import xadmin, TemplateDecorationAdmin


class CityDecorationAdmin(TemplateDecorationAdmin):
    display_list = ["city_name", "population", "rank", "province"]
    search_field_list = ["city_name", "rank"]
    action_list=["update_population_action"]
    filter_list = ["city_name", "province"]

    def update_population_action(self, questset):
        questset.update(population=325454)

    update_population_action.shortcup_desciption = "update_population"

xadmin.registration(City, CityDecorationAdmin)
xadmin.registration(Province)

