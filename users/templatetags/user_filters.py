import pymorphy2
from django import template

morph = pymorphy2.MorphAnalyzer()

register = template.Library()


@register.filter()
def addclass(field, css):
    return field.as_widget(attrs={'class': css})

@register.simple_tag
def declension(count, word):
    zero_word = morph.parse(word)[0]
    return zero_word.make_agree_with_number(count).word
