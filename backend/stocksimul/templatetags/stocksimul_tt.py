from django import template

# To be a valid tag library, the module must contain a module-level variable named register that is a template.
# Library instance, in which all the tags and filters are registered.
# So, near the top of your module, put the following:
register = template.Library()


@register.filter
def get_value(dictionary, key):
    value = dictionary[key]
    print('template get_value=',value)
    return value
