from django import template
from menu.models import Menu, MenuItem
from django.urls import resolve

register = template.Library()

@register.inclusion_tag('menu/menu.html', takes_context=True)
def draw_menu(context, menu_name):
    request = context['request']
    current_url = resolve(request.path_info).url_name
    menu = Menu.objects.get(name=menu_name)
    items = menu.items.select_related('parent').all()

    menu_tree = build_menu_tree(items)
    mark_active(menu_tree, current_url)

    return {'menu_tree': menu_tree, 'request': request}

def build_menu_tree(items):
    tree = []
    items_dict = {item.id: item for item in items}
    for item in items:
        if item.parent_id:
            parent = items_dict[item.parent_id]
            if not hasattr(parent, 'children'):
                parent.children = []
            parent.children.append(item)
        else:
            tree.append(item)
    return tree

def mark_active(items, current_url):
    for item in items:
        item.active = item.get_url() == current_url
        if hasattr(item, 'children'):
            children = item.children.all()
            mark_active(children, current_url)
            if any(child.active for child in children):
                item.expanded = True
