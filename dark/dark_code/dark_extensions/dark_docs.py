# Copyright 2026 Dark.Tehno
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------
# В разработке!
# --------------------------------

template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Docs for {file_name}</title>
    <link rel="stylesheet" href="css/main.css">
</head>
<body>
    <header>
        <h1>Docs for {file_name}</h1>
    </header>
    <main>
        <section id="variables">
            <h2>Variables</h2>
            {variables}
        </section>
        <section id="functions">
            <h2>Functions</h2>
            {functions}
        </section>
        <section id="classes">
            <h2>Classes</h2>
            {classes}
        </section>
    </main>
</body>
</html>
"""


variable_template = """<div class="variable-item"><h3>`{name}` ({type})(Строчка - {line})</h3><p>{description}</p></div>"""

functions_template = """<div class="function-item"><h3>`{name}({args})` (Строчки - {line_start}-{line_end})</h3><p>{description}</p><h4>Returns:</h4><ul>{returns}</ul></div>"""
return_template = """<li>({type}): {description}</li>"""

classes_template = """<div class="class-item"><h3>`{name}`</h3><p>{description}</p><h4>Methods:</h4><ul>{methods}</ul></div>"""
method_template = """<li>`{name}({args})`: {description}</li>"""


def docs_variable(code, line, ast_code):
    name = ''
    type = ''
    description = ''
    
    name = ast_code[1]
    type = ast_code[2][0]
    description = code.split('# ')
    if len(description) <= 1:
        description = ''
    else:
        description = description[1]

    return variable_template.format(name=name, type=type, line=line, description=description)

def docs_function(code, line_start, line_end, ast_code):
    name = ''
    args = ''
    description = ''
    description_return = ''
    returns = ''
        
    lines = code.split('\n')    
    name = ast_code[1]
    args = ', '.join(ast_code[2])
    if ast_code[3][0][0] == 'expr':
        description = ast_code[3][0][1][1]
    for ast in ast_code[3]:
        if ast[0] == 'return':
            line = ast[2]
            description_return = lines[line-1].split('# ')
            if len(description_return) <= 1:
                description_return = 'Описание отсутствует'
            else:
                description_return = description_return[1]
            returns += return_template.format(type=ast[1][0], description=description_return)
    return functions_template.format(name=name, args=args, line_start=line_start, line_end=line_end, description=description, returns=returns)


def docs_class(ast_code):
    methods = ''
    for ast_method in ast_code[3]:
        if ast_method[0] == 'func_def':
            method_name = ast_method[1]
            method_args = ', '.join(ast_method[2])
            method_description = ''
            for item in ast_method[3]:
                if item[0] == 'expr' and item[1][0] == 'str':
                    method_description = item[1][1]
                    break
            methods += method_template.format(name=method_name, args=method_args, description=method_description)
    description = ast_code[2][1][1] if ast_code[2] else ''
    return classes_template.format(name=ast_code[1], description=description, methods=methods)


def native_docs_create(args):
    from dark_code.dark_lang import Parser, lex, run 

    if len(args) != 1:
        raise TypeError("create() принимает 1 аргумент (code)")
    code = args[0]

    lines = code.split('\n')
    tokens = lex(code)
    parser = Parser(tokens)
    ast = parser.parse()
    variables = ''
    functions = ''
    classes = ''
    for i, line in enumerate(ast[1]):
        if line[0] == 'assign':
            variables = docs_variable(lines[i], line[3], line)
        elif line[0] == 'func_def':
            line_start = line[4]
            line_end = line[3][-1][2] + 1
            code_func = '\n'.join(lines[line_start-1:line_end])
            functions = docs_function(code_func, line_start, line_end, line)
        elif line[0] == 'class_def':
            classes = docs_class(line)
    output = template.format(file_name='test.dark', variables=variables, functions=functions, classes=classes)
    return output

if __name__ == '__main__':
    from dark_code.dark_lang import Parser, lex, run 
    code = """person = {"name": "Alex", "age": 30}

# Через квадратные скобки
println(person["name"]) # Выведет "Alex"

# Через точку (если ключ - валидный идентификатор)
println(person.age) # Выведет 30

function check_age(age) do
    if age < 18 then
        println("Доступ запрещен.")
        return # Досрочный выход из функции
    end
    println("Доступ разрешен.")
end

class Animal do
    function __main__(object, name) do
        object.name = name # Создание и инициализация атрибута 'name'
    end
end
"""
    lines = code.split('\n')
    tokens = lex(code)
    parser = Parser(tokens)
    ast = parser.parse()
    variables = ''
    functions = ''
    classes = ''
    for i, line in enumerate(ast[1]):
        if line[0] == 'assign':
            variables = docs_variable(lines[i], line[3], line)
        elif line[0] == 'func_def':
            line_start = line[4]
            line_end = line[3][-1][2] + 1
            code_func = '\n'.join(lines[line_start-1:line_end])
            functions = docs_function(code_func, line_start, line_end, line)
        elif line[0] == 'class_def':
            classes = docs_class(line)
    output = template.format(file_name='test.dark', variables=variables, functions=functions, classes=classes)
    print(output)