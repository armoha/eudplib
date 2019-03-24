reimport eudplib
import types

module_to_doc = eudplib

exclude_types = [dict, str, types.ModuleType]
eudftypes = [eudplib.EUDFuncN]
allowed_type = eudftypes + [type, types.FunctionType]
exclude_names = ['__loader__', '__path__', '__spec__']
section_header_charr = ['=', '-', '\'', '~', '^']


print('Collecting list of documentation-needed structures')
doc_needed_functions = set()
doc_needed_classes = set()


# Document module
for name, value in module_to_doc.__dict__.items():
    # Exclude list
    if name in exclude_names or type(value) in exclude_types:
        continue

    if not any(isinstance(value, t) for t in allowed_type):
        continue

    if (
        isinstance(value, types.FunctionType) or
        isinstance(value, eudplib.EUDFuncN)
    ):
        # Get function prototype
        while isinstance(value, eudplib.EUDFuncN):
            value = value._bodyfunc

        args = value.__code__.co_varnames[:value.__code__.co_argcount]
        name = ('%s(%s)' % (name, ', '.join(args)))
        doc_needed_functions.add(name)

    elif isinstance(value, type):
        if name != 'EPError':
            args = value.__init__.__code__.co_varnames[1:value.__init__.__code__.co_argcount]
            name = ('%s(%s)' % (name, ', '.join(args)))
        else:
            name = 'EPError(msg)'  # EPError는 Exception의 일종이라 __init__를 못 얻는다.
        doc_needed_classes.add(name)

print('\n==================================\n')


# Summary
print('Current entries:')
for k in sorted(doc_needed_functions):
    print('%s' % k)
print('==================================')
for k in sorted(doc_needed_classes):
    print('%s' % k)
print('==================================')
