# 🔍 Швидкий довідник по AST та parser.out

## 🚀 Швидкі команди

```bash
# Запустити компілятор та згенерувати AST
python main.py

# Переглянути AST в терміналі
python inspect_ast.py

# Показати дерево AST
python inspect_ast.py --tree

# Детальний аналіз AST
python inspect_ast.py --detailed

# Переглянути JSON
cat ast.json | python -m json.tool | less

# Відкрити візуалізацію в браузері
xdg-open index.html

# Переглянути parser.out
less parser.out
```

## 📋 Що таке parser.out?

**Автоматично генерується PLY** при першому запуску парсера.

### Містить:
- ✅ Всі правила граматики (52 правила)
- ✅ Таблицю термінальних символів (tokens)
- ✅ Таблицю нетермінальних символів
- ✅ Стани LALR-автомата (100+ станів)
- ⚠️ **Конфлікти** (у нас 1 shift/reduce для ELSE - це нормально!)

### Як читати:
```
Rule 30: selection_statement -> IF LPAREN expression RPAREN statement ELSE statement

state 96
    IF LPAREN expression RPAREN statement . ELSE statement
    
    ELSE    shift and go to state 99  ← "shift" означає: читай ELSE
    ELSE    reduce using rule 29      ← конфлікт! але shift має пріоритет
```

## 🌳 Структура AST

### Кореневий вузол:
```json
{
  "type": "Program",
  "body": [список функцій]
}
```

### Типи вузлів:

| Тип | Використання | Поля |
|-----|-------------|------|
| `Program` | Корінь AST | `body` - список функцій |
| `FunctionDef` | Оголошення функції | `name`, `returnType`, `params`, `body` |
| `VarDecl` | Змінна | `name`, `dataType`, `init` |
| `Assignment` | Присвоєння | `target`, `value` |
| `If` | Умова | `test`, `consequent`, `alternate` |
| `While` | Цикл | `test`, `body` |
| `BinaryOp` | Операція | `op`, `left`, `right` |
| `Call` | Виклик функції | `callee`, `args` |
| `Identifier` | Ідентифікатор | `name` |
| `Literal` | Константа | `value` |
| `Return` | Повернення | `value` |
| `Print` | Вивід | `value` |
| `Block` | Блок коду | `body` - список statements |

## 🔄 Де використовується AST в коді?

### 1. **Створення** (Parsing)
```python
# main.py, функції p_* 
def p_function(p):
    'function : type_specifier ID LPAREN param_list RPAREN LBRACE block_item_list RBRACE'
    p[0] = {'type': 'FunctionDef', ...}  # ← СТВОРЮЄМО ВУЗОЛ
```

### 2. **Семантичний аналіз** (Semantic Analysis)
```python
# main.py, клас SemanticAnalyzer
def visit_FunctionDef(self, node):  # ← ОБРОБЛЯЄМО ВУЗОЛ З AST
    for param in node['params']:    # ← ЧИТАЄМО ДАНІ З AST
        self.symbol_table.add(param['name'], ...)
```

### 3. **Генерація коду** (Code Generation)
```python
# main.py, функція generate()
def generate(node, indent=0):
    ntype = node['type']  # ← ЧИТАЄМО ТИП З AST
    if ntype == 'FunctionDef':
        params = [p['name'] for p in node['params']]  # ← ДАНІ З AST
        code = f"def {node['name']}({', '.join(params)}):\n"
```

### 4. **Збереження** (JSON Export)
```python
# main.py, функція test_code()
with open('ast.json', 'w') as f:
    json.dump(ast, f, indent=2)  # ← ЗБЕРІГАЄМО ДЛЯ ВІЗУАЛІЗАЦІЇ
```

### 5. **Візуалізація** (D3.js в index.html)
```javascript
d3.json("ast.json").then(function(rawData) {
    const treeData = transformData(rawData);  // ← ЧИТАЄМО AST
    // ... малюємо дерево
});
```

## ✅ Як перевірити що AST працює?

### Метод 1: Автоматичні тести
```bash
python main.py
# Якщо всі 5 тестів ✓ PASS → AST працює правильно!
```

### Метод 2: Інспектор
```bash
python inspect_ast.py --detailed
# Перевірте статистику вузлів
```

### Метод 3: Візуалізація
```bash
xdg-open index.html
# Перевірте структуру дерева візуально
```

### Метод 4: Перегляд JSON
```bash
cat ast.json | python -m json.tool
# Перевірте структуру вручну
```

### Метод 5: Додайте debug
```python
def test_code(code, name):
    ast = parser.parse(code, lexer=lexer.clone())
    print(json.dumps(ast, indent=2))  # ← DEBUG
```

## 🎯 Приклад: від коду до AST

### Вхідний код:
```c
int add(int a, int b) {
    return a + b;
}
```

### AST (спрощено):
```
Program
└── FunctionDef [add]
    ├── returnType: "int"
    ├── params: [
    │     {name: "a", type: "int"},
    │     {name: "b", type: "int"}
    │   ]
    └── body: [
          Return
          └── value: BinaryOp [+]
              ├── left: Identifier [a]
              └── right: Identifier [b]
        ]
```

### Згенерований Python:
```python
def add(a, b):
    return (a + b)
```

## 🐛 Типові помилки AST

### ❌ Проблема: ast.json порожній
```bash
# Рішення:
python main.py  # Запустіть щоб згенерувати AST
```

### ❌ Проблема: Помилка в структурі AST
```python
# Перевірте що кожен p_* функція повертає словник з 'type':
def p_statement(p):
    p[0] = {'type': 'Statement', ...}  # ✓ Правильно
    p[0] = ['Statement', ...]          # ✗ Неправильно!
```

### ❌ Проблема: Візуалізація не працює
```bash
# Перевірте що ast.json існує і валідний:
python -m json.tool ast.json
```

## 📚 Корисні посилання

- **PLY документація:** https://www.dabeaz.com/ply/
- **D3.js дерева:** https://observablehq.com/@d3/tree
- **LALR парсери:** https://en.wikipedia.org/wiki/LALR_parser

## 💡 Підказки

1. **parser.out** - читайте коли є помилки в граматиці
2. **ast.json** - перевіряйте структуру AST
3. **inspect_ast.py** - швидкий аналіз в терміналі
4. **index.html** - зручна візуалізація в браузері
5. **Тести в main.py** - найкращий спосіб перевірити що все працює

---

**Автор:** Студентська лабораторна робота  
**Версія:** 1.0  
**Дата:** Листопад 2024

