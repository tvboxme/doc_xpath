#!/usr/bin/env python
# encoding: utf-8
# author: 04


def doc_xpath(doc, xpath, allow_empty=False):
    """
    Xpath for document
    >>> a = {'a': [{'b': {'c': ['d', 'f']}}, {'b': {'c': ['g', 'h']}}]}
    >>> doc_xpath(a, 'a.b.c')
    Traceback (most recent call last):
       ...
    ValueError: Xpath <a.b.c> failed at <b>.
    [{'b': {'c': ['d', 'f']}}, {'b': {'c': ['g', 'h']}}]
    >>> doc_xpath(a, 'a.[].b.c')
    [['d', 'f'], ['g', 'h']]
    >>> doc_xpath(a, 'a.[].b.c.[]')
    ['d', 'f', 'g', 'h']
    """
    check_points = [doc]
    for word in xpath.split('.'):
        new_points = []
        for point in check_points[:]:
            try:
                if word == '[]':
                    if not isinstance(point, list):
                        raise ValueError()
                    new_points.extend(point)
                else:
                    if point.get(word) is None:
                        if not allow_empty:
                            raise ValueError()
                        else:
                            continue
                    new_points.append(point.get(word))
            except Exception:
                raise ValueError('Xpath <%s> failed at <%s>.\n%s' % (xpath, word, point))
        check_points = new_points
    return check_points


def doc_xpath_dict_map(doc, xpath_dict, default=''):
    """
    Xpath with dict
    >>> a = {'a1': {'b1': {'c1': 'd1'}}, 'a2': {'b3': 'c3'}}
    >>> xpath_dict = {'alpha': 'a1.b1.c1', 'beta': 'a2.b3'}
    >>> doc_xpath_dict_map(a, xpath_dict)
    {'alpha': 'd1', 'beta': 'c3'}
    """
    output = {}
    for key, value in xpath_dict.items():
        if isinstance(value, tuple):
            value, func = value
            if not callable(func):
                raise ValueError('%s should be callable.' % repr(func))
        else:
            func = None
        if isinstance(value, dict):
            output[key] = doc_xpath_dict_map(doc, value)
        elif isinstance(value, (basestring, unicode)):
            step_value = doc_xpath(doc, value, allow_empty=True)
            if len(step_value) == 1:
                step_value = step_value[0]
            elif len(step_value) == 0:
                step_value = default
            output[key] = step_value
        else:
            raise NotImplementedError('Not prepared for this type: %s' % type(value))
        if func:
            output[key] = func(output[key])
    return output


if __name__ == "__main__":
    import doctest
    doctest.testmod()
