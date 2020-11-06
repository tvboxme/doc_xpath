# doc_xpath

```python
# doc_xpath:
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

# doc_xpath_dict_map
>>> a = {'a1': {'b1': {'c1': 'd1'}}, 'a2': {'b3': '3'}}
>>> xpath_dict = {'alpha': 'a1.b1.c1', 'beta': ('a2.b3', int)}
>>> doc_xpath_dict_map(a, xpath_dict)
{'alpha': 'd1', 'beta': 3}
```
