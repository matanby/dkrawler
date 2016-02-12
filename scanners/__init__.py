__all__ = ['dnskey']

# Going over each scanner and saving its scan function
scan_functions = []
for scanner in __all__:
    scan_script = __import__("scanners.%s" % scanner, globals(), locals(), ['scan'])
    scan_functions.append(scan_script.scan)
