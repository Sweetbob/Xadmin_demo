from django.apps import AppConfig
from django.db.models import Q
from django.forms import ModelForm
from django.shortcuts import render, redirect
from django.utils.module_loading import autodiscover_modules
from django.urls import path, reverse
from django.http import HttpResponse
from django.utils.safestring import mark_safe
from xadmin.utils.page import Pagination
from django.db.models import ManyToManyField, ForeignKey


class XadminConfig(AppConfig):
    name = 'xadmin'

    def ready(self):
        autodiscover_modules("Xadmin")


class TemplateDecorationAdmin():
    display_list = ["__str__", ]
    display_link_list = []
    model_form = None
    search_field_list = []
    action_list = []
    filter_list = []

    def __init__(self, model):
        self.model = model

    def batch_delete(self, questset):
        questset.delete()

    batch_delete.shortcup_desciption = "batch_delete"


    def get_action_info_list(self):
        action_info_list = []
        action_info_list.append({
            "func_name": self.batch_delete.__name__,
            "func_desc": self.batch_delete.shortcup_desciption
        })
        for a in self.action_list:
            action_info_list.append({
                "func_name": a,
                "func_desc": getattr(self, a).shortcup_desciption
            })
        return action_info_list

    def check_box(self, obj=None, is_header=False):
        if is_header:
            return mark_safe("<input id='check_box_father' type='checkbox'>")
        return mark_safe("<input class='check_box_son' name='pk_check_box' value='{}' type='checkbox'>".format(obj.pk))

    def change(self, obj=None, is_header=False):
        if is_header:
            return "Operation"
        _url = reverse(viewname="{}_{}_change_url".format(self.model._meta.app_label, self.model._meta.model_name),
                       args=(obj.pk,), current_app=obj._meta.app_label)
        return mark_safe("<a href='{}'>Change</a>".format(_url))

    def delete(self, obj=None, is_header=False):
        if is_header:
            return "Operation"
        _url = reverse(viewname="{}_{}_delete_url".format(self.model._meta.app_label, self.model._meta.model_name),
                       args=(obj.pk,))
        return mark_safe(
            """
<!-- Button trigger modal -->
<button type='button' class='btn btn-primary' data-toggle="modal" data-target='#obj_{}'>
  Delete
</button>

<!-- Modal -->
<div class='modal fade' id='obj_{}' tabindex='-1' role='dialog' aria-labelledby='exampleModalLabel' aria-hidden='true'>
  <div class="modal-dialog" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title" id="exampleModalLabel">Warning!</h5>
        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
          <span aria-hidden="true">&times;</span>
        </button>
      </div>
      <div class="modal-body">
        This action can not rollback! Are you sure delete is?
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
        <a href='{}' type="button" class="btn btn-primary">Delete</a>
      </div>
    </div>
  </div>
</div>"""
                .format(obj.pk, obj.pk, _url))

    def get_new_display_list(self):
        temp = []
        temp.append(TemplateDecorationAdmin.check_box)
        temp.extend(self.display_list)
        if not self.display_link_list:
            temp.append(TemplateDecorationAdmin.change)
        temp.append(TemplateDecorationAdmin.delete)
        return temp

    """
    视图
    """
    def list_view(self, request):
        if request.method == "POST":
            action = getattr(self, request.POST.get("action_name"))
            print(request.POST.getlist("pk_check_box"))
            queryset = self.model.objects.filter(pk__in=request.POST.getlist("pk_check_box"))
            # 执行action函数 getattr已经指明了self了，所以不用再指明self
            action(queryset)

        # 搜索条件的过滤开始
        query_keyword = request.GET.get("query_keyword", "")
        search_Q = Q()
        if query_keyword:
            # 设置成 或 模式
            search_Q.connector = "or"
            for search_field in self.search_field_list:
                # 添加搜索字段元组（用这种方法可以把key设置成字符串，传统的方法Q(title='')不能设置字符串）
                search_Q.children.append((search_field + "__contains", query_keyword))
        # 搜索条件的过滤的结束

        # filter的过滤的开始
        filter_Q = Q()
        # 循环所有参数，如果参数在filter_list中，所有这是一个过滤器的参数
        for single_param_name, single_param_val in  request.GET.items():
            if single_param_name in self.filter_list:
                filter_Q.children.append((single_param_name, single_param_val))
        # filter的过滤的结束get_filter

        # 添加搜索的过滤条件 和 filter过滤的条件
        data_list = self.model.objects.all().filter(search_Q).filter(filter_Q)
        show_case = ShowCase(template_decoration_admin_instance=self, data_list=data_list, request=request)
        add_url = reverse(viewname="{}_{}_add_url".format(self.model._meta.app_label, self.model._meta.model_name))
        # local() 把本地的变量都传过去
        return render(request, "xadmin/list_view.html", locals())

    def get_list_view_url(self):
        return reverse(viewname="{}_{}_list_url".format(self.model._meta.app_label, self.model._meta.model_name))

    def get_model_form(self):
        """
        获取模型类
        :return: 模型类
        """
        if self.model_form == None:
            class ModelFormTemp(ModelForm):
                # 在Meta 中设置模型类和字段
                class Meta():
                    model = self.model
                    fields = "__all__"

            return ModelFormTemp
        else:
            return self.model_form

    def add_view(self, request):
        model_form = self.get_model_form()
        if request.method == "POST":
            form_obj = model_form(request.POST)
            if form_obj.is_valid():
                # 如果验证通过
                saved_obj = form_obj.save()
                # 这里的pop_id就是下面传的标志参数，如果有pop_id，就是通过弹出窗口的方式打开的
                pop_id = request.GET.get("pop_id","")
                if pop_id:
                    return render(request, "xadmin/pop.html", {"element_id": pop_id, "pk": saved_obj.pk, "text": str(saved_obj)})
                else:
                    return redirect(to=self.get_list_view_url())
        from django.forms import ModelChoiceField
        # 此时f并不是一个一个的form字段，二十用BlundField包装的，.field就是一个一个的form字段对象了
        form = model_form()
        for f in form:
            # 如果是ModelChoiceField的子类，就是一对一和一对多的字段（这里的字段类型是ModelForm里面的字段类型）
            if isinstance(f.field, ModelChoiceField):
                f.is_pop = True
                # 取得该字段对应的模型，根据模型名和app名字来反向解析url
                model_name = f.field.queryset.model._meta.model_name
                app_label = f.field.queryset.model._meta.app_label
                # 该url是页面上的 + 的herf值, 在后面添加一个识别码
                f.url = reverse("{}_{}_add_url".format(app_label, model_name)) + "?pop_id=id_" + f.name
        return render(request, "xadmin/add_view.html", {"model_form": form})

    def delete_view(self, request, id):
        try:
            self.model.objects.filter(pk=id).delete()
            return redirect(to=self.get_list_view_url())
        except Exception as e:
            return redirect(to=self.get_list_view_url())

    def change_view(self, request, id):
        form_model = self.get_model_form()
        edit_obj = self.model.objects.filter(pk=id).first()
        if request.method == "POST":
            model_form = form_model(request.POST, instance=edit_obj)
            if model_form.is_valid():
                model_form.save()
                return redirect(to=self.get_list_view_url())
        model_form = form_model(instance=edit_obj)
        return render(request, "xadmin/change_view.html", {"model_form": model_form})

    def get_urls_2(self):
        urls_2 = []
        urls_2.append(path("", self.list_view,
                           name='{}_{}_list_url'.format(self.model._meta.app_label, self.model._meta.model_name)))
        urls_2.append(path("<int:id>/delete", self.delete_view,
                           name='{}_{}_delete_url'.format(self.model._meta.app_label, self.model._meta.model_name)))
        urls_2.append(path("<int:id>/change", self.change_view,
                           name='{}_{}_change_url'.format(self.model._meta.app_label, self.model._meta.model_name)))
        urls_2.append(path("add", self.add_view,
                           name='{}_{}_add_url'.format(self.model._meta.app_label, self.model._meta.model_name)))
        return urls_2, None, None


class ShowCase():
    def __init__(self, template_decoration_admin_instance, data_list, request):
        self.template_decoration_admin_instance = template_decoration_admin_instance
        self.data_list = data_list
        self.request = request
        # 分页
        current_page = int(self.request.GET.get("page", 1))
        all_count = self.data_list.count()
        base_url = self.request.path
        self.pagination = Pagination(current_page=current_page, all_count=all_count, base_url=base_url,
                                params=self.request.GET,
                                per_page_num=3, pager_count=3)

    def get_filter_list(self):
        """
        获取右边的过滤器的展示数据
        :return:
        """
        from copy import deepcopy
        display_data = {}
        for filter_item in self.template_decoration_admin_instance.filter_list:
            # 获取请求参数，方便拼接url的参数部分
            params = deepcopy(self.request.GET)

            a_links = []
            if filter_item in self.request.GET.keys():
                del params[filter_item]
                a_links.append("<a href='?{}'>All</a>".format(params.urlencode()))
            else:
                a_links.append("<a class='text-success' href='?{}'>All</a>".format(params.urlencode()))

            field = self.template_decoration_admin_instance.model._meta.get_field(filter_item)
            # 如果是关联的另一个类

            if isinstance(field, ManyToManyField) or isinstance(field, ForeignKey):
                foreign_model = field.remote_field.model
                # 取目前点击的id，下面生成a标签的时候进行匹配，分别渲染
                destination_pk = int(self.request.GET.get(filter_item, "0"))
                for foreign_obj in foreign_model.objects.all():
                    # 拼接类似 province=2
                    params[filter_item] = foreign_obj.pk
                    url = params.urlencode()
                    if destination_pk == foreign_obj.pk:
                        a_link = "<a class='text-success' href='?{}'>{}</a>".format(url, foreign_obj)
                    else:
                        a_link = "<a href='?{}'>{}</a>".format(url, foreign_obj)
                    a_links.append(a_link)
            else:
                # 是普通的字段
                obj_pk_and_field_value = self.template_decoration_admin_instance.model.objects.all().values("pk", filter_item)
                destination_value = self.request.GET.get(filter_item, "")
                for obj in obj_pk_and_field_value:
                    field_value = obj.get(filter_item)
                    params[filter_item] = field_value
                    if field_value == destination_value:
                        a_links.append("<a class='text-success' href='?{}'>{}</a>".format(params.urlencode(), field_value))
                    else:
                        a_links.append("<a href='?{}'>{}</a>".format(params.urlencode(), field_value))

            display_data[filter_item] = a_links
        return display_data

    def get_header_list(self):
        header_list = []
        for field in self.template_decoration_admin_instance.get_new_display_list():
            if isinstance(field, str):
                if field == "__str__":
                    header_list.append(self.template_decoration_admin_instance.model._meta.model_name.upper())
                else:
                    header_list.append(self.template_decoration_admin_instance.model._meta.get_field(field).verbose_name)
            else:
                header_list.append(field(self.template_decoration_admin_instance, is_header=True))
        return header_list

    def get_body_list(self):
        new_data_list = []
        # 取分页数据
        for data in self.data_list[self.pagination.start: self.pagination.end]:
            temp = []
            for field in self.template_decoration_admin_instance.get_new_display_list():

                if isinstance(field, str):
                    val = getattr(data, field)
                    if field in self.template_decoration_admin_instance.display_link_list:
                        _url = reverse(
                            viewname="{}_{}_change_url".format(
                                self.template_decoration_admin_instance.model._meta.app_label,
                                self.template_decoration_admin_instance.model._meta.model_name),
                            args=(data.pk,), current_app=data._meta.app_label)
                        val = mark_safe("<a href='{}'>{}</a>".format(_url, val))
                    temp.append(val)
                else:
                    temp.append(field(self.template_decoration_admin_instance, obj=data))
            new_data_list.append(temp)
        return new_data_list


class Xadmin():
    registry = {}

    def registration(self, model, decoration_admin=None):
        if not decoration_admin:
            Xadmin.registry[model] = TemplateDecorationAdmin(model)
        else:
            Xadmin.registry[model] = decoration_admin(model)

    @property
    def urls(self):
        urls_1 = []
        for model, decoration_class in Xadmin.registry.items():
            urls_1.append(
                path("{0}/{1}/".format(model._meta.app_label, model._meta.model_name, ), decoration_class.get_urls_2()))

        return urls_1, None, None


print("=" * 120, "xadmin 实例创建..")
xadmin = Xadmin()
