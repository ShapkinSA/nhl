"""
    Служебный класс для создания селективных сущностей
"""
class Reflection:

    @staticmethod
    def get_class(fullClassName, *args):
        parts = fullClassName.split('.')
        moduleName = ".".join(parts[:-1])
        module = __import__(moduleName)
        inst = None
        for clasName in parts[1:-1]:
            obj = getattr(getattr(module, clasName), clasName)
            inst = obj.createObjByArgs(args)
        return inst



