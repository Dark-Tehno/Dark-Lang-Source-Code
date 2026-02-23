import std/json, sequtils, strutils, tables
from ../dark/exceptions import DarkRuntimeError, formatError


proc dark_range*(start: auto, stop: auto): seq[int] =
    when start is int and stop is int:
        result = newSeq[int](0)
        var i = int(start)
        while i < stop:
            result.add(i)
            i += 1
        return result
    else:
        var message = "ошибка вызова нативной функции: Аргументами для stdlib.range() должны быть числа"
        var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
        echo formatError(err, "DarkRuntimeError")
        quit() 

proc dark_list_contains*(haystack: seq[auto], needle: auto): bool =
    return needle in haystack

proc dark_list_join*[T](items: seq[T], separator: string): string =
    return map(items, proc(x: T): string = $x).join(separator)

proc dark_dict_get*[K, V](d: openArray[(K, V)], key: K, default_val: V): V =
    let table = d.toTable
    return table.getOrDefault(key, default_val)

proc dark_clamp*(value: auto, min_val: auto, max_val: auto): auto =
    return max(min_val, min(value, max_val))

proc dark_json_decode*(json_string: string): JsonNode =
    try:
        return parseJson(json_string)
    except JsonParsingError as e:
        var message = "неверный формат JSON: " & e.msg
        var err: DarkRuntimeError = DarkRuntimeError(message: message, line: 0, col: 0, filename: "<script>")
        echo formatError(err, "DarkRuntimeError")
        quit()

proc dark_str_split*(s: string, sep: string): seq[string] =
  return s.split(sep)

proc dark_str_upper*(s: string): string =
    return s.toUpper()

proc dark_str_lower*(s: string): string =
    return s.toLower()

proc dark_str_replace*(s: string, old: string, new_t: string): string =
    return s.replace(old, new_t)