
escapes = {eval(f"'\{c}'") : f"\\{c}" for c in 'bfnr"\\'}

def format_string(s):
    return re.sub('['+''.join(escapes.keys())+']', lambda m:escapes[m.group(0)], s)


def format_literal(obj, indent="    "):
    if isinstance(obj, bool):
        return "true" if obj else "false"
    elif isinstance(obj, (int, float)):
        return str(obj)
    elif isinstance(obj, str):
        return format_string(obj)
    elif isinstance(obj, (list, tuple)):
        return '[' + (",\n"+indent).join(format_literal(o, indent=indent+"    ")
                                            for o in obj) + ']'
    elif isinstance(obj, dict):
        return '{' + (",\n"+indent).join(format_string(k) + " = "
                                            + format_literal(v, indent=indent+"    ")
                                            for k,v in obj.items()) + '}'
    else:
        raise TypeError(f"Object of type '{type(obj).__qualname__}' is not TOML serializable")

def totoml(obj, name="toml"):
    res = []
    tables = {k:v for k, v in obj.items() if isinstance(v, dict)}
    literals = {k:v for k, v in obj.items() if not isinstance(v, dict)}
    for k, v in literals.items():
        res.append(f"{format_string(k)} = {format_literal(v)}")
    for k, v in tables.items():
        res.append(f"\n[{name}.{k}]\n")
        for a, b in v.items():
            res.append(f"{format_string(a)} = {format_literal(b)}")
    return "\n".join(res)
