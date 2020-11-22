import builtins

HAS_IPYTHON = True

try:
    from IPython.core.magic import register_cell_magic
    from IPython.core.magics.osm import OSMagics
except ModuleNotFoundError:
    HAS_IPYTHON = False


if HAS_IPYTHON:
    try:
        @register_cell_magic('pagefile')
        def pagefile(line, cell):
            from importlib import reload

            args = line.split()

            file_path = args[0]

            OSMagics().writefile(file_path, cell)

            import_path = '.'.join(file_path.split('.')[0].split('/'))
            mod = __import__(import_path)

            reload(mod)

            for attr in args[1:]:
                value = getattr(mod, attr)
                setattr(builtins, attr, value)

    except NameError:
        pass
