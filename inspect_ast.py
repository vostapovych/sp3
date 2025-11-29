#!/usr/bin/env python3
"""
🔍 Інспектор AST - інструмент для перевірки Abstract Syntax Tree

Використання:
    python inspect_ast.py                    # Показує ast.json
    python inspect_ast.py --detailed         # Детальний аналіз
    python inspect_ast.py --tree             # Текстове дерево
"""

import json
import sys
from pathlib import Path

def load_ast():
    """Завантажує AST з файлу"""
    ast_file = Path(__file__).parent / 'ast.json'
    if not ast_file.exists():
        print("❌ Файл ast.json не знайдено!")
        print("💡 Спочатку запустіть: python main.py")
        sys.exit(1)
    
    with open(ast_file, 'r') as f:
        return json.load(f)

def count_nodes(node, counts=None):
    """Підраховує кількість вузлів кожного типу"""
    if counts is None:
        counts = {}
    
    if isinstance(node, dict) and 'type' in node:
        node_type = node['type']
        counts[node_type] = counts.get(node_type, 0) + 1
        
        # Рекурсивно обходимо всі значення
        for key, value in node.items():
            if key != 'type':
                if isinstance(value, list):
                    for item in value:
                        count_nodes(item, counts)
                elif isinstance(value, dict):
                    count_nodes(value, counts)
    
    return counts

def print_tree(node, indent=0, prefix="", is_last=True):
    """Виводить AST у вигляді текстового дерева"""
    if node is None:
        return
    
    # Символи для дерева
    connector = "└── " if is_last else "├── "
    extension = "    " if is_last else "│   "
    
    if isinstance(node, dict):
        if 'type' in node:
            # Основна інформація про вузол
            node_info = f"{node['type']}"
            
            # Додаткова інформація
            if node['type'] == 'FunctionDef':
                node_info += f" [{node['name']}]"
            elif node['type'] == 'Identifier':
                node_info += f" [{node['name']}]"
            elif node['type'] == 'Literal':
                node_info += f" [{node['value']}]"
            elif node['type'] == 'BinaryOp':
                node_info += f" [{node['op']}]"
            elif node['type'] == 'VarDecl':
                node_info += f" [{node['name']}: {node['dataType']}]"
            
            print(f"{prefix}{connector}{node_info}")
            
            # Обходимо дочірні вузли
            children = []
            for key, value in node.items():
                if key != 'type' and value is not None:
                    if isinstance(value, list) and value:
                        children.append((key, value))
                    elif isinstance(value, dict):
                        children.append((key, value))
            
            for i, (key, child) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                child_prefix = prefix + extension
                
                if isinstance(child, list):
                    print(f"{child_prefix}{'└── ' if is_last_child else '├── '}{key}:")
                    for j, item in enumerate(child):
                        print_tree(item, indent + 2, child_prefix + ("    " if is_last_child else "│   "), j == len(child) - 1)
                else:
                    print(f"{child_prefix}{'└── ' if is_last_child else '├── '}{key}:")
                    print_tree(child, indent + 1, child_prefix + ("    " if is_last_child else "│   "), True)
    
    elif isinstance(node, list):
        for i, item in enumerate(node):
            print_tree(item, indent, prefix, i == len(node) - 1)

def analyze_ast(ast):
    """Аналізує AST та виводить статистику"""
    print("\n" + "="*60)
    print("📊 АНАЛІЗ ABSTRACT SYNTAX TREE")
    print("="*60)
    
    # Підрахунок вузлів
    counts = count_nodes(ast)
    total_nodes = sum(counts.values())
    
    print(f"\n📈 Загальна статистика:")
    print(f"   Всього вузлів: {total_nodes}")
    print(f"   Типів вузлів: {len(counts)}")
    
    print(f"\n🔢 Розподіл вузлів за типами:")
    for node_type, count in sorted(counts.items(), key=lambda x: -x[1]):
        bar = "█" * min(count, 30)
        print(f"   {node_type:20s} {count:3d} {bar}")
    
    # Аналіз функцій
    if ast['type'] == 'Program':
        functions = [f for f in ast['body'] if f['type'] == 'FunctionDef']
        print(f"\n🔧 Функції ({len(functions)}):")
        for func in functions:
            params_str = ", ".join([f"{p['dataType']} {p['name']}" for p in func['params']])
            print(f"   {func['returnType']} {func['name']}({params_str})")
            print(f"      Statements: {len(func['body'])}")

def main():
    """Основна функція"""
    args = sys.argv[1:]
    
    # Завантажуємо AST
    try:
        ast = load_ast()
    except Exception as e:
        print(f"❌ Помилка при завантаженні AST: {e}")
        sys.exit(1)
    
    # Виводимо залежно від параметрів
    if '--tree' in args:
        print("\n🌳 Структура AST (текстове дерево):\n")
        print_tree(ast)
    elif '--detailed' in args:
        analyze_ast(ast)
        print("\n🌳 Структура AST:\n")
        print_tree(ast)
    else:
        analyze_ast(ast)
    
    print("\n" + "="*60)
    print("💡 Підказки:")
    print("   python inspect_ast.py --tree      # Текстове дерево")
    print("   python inspect_ast.py --detailed  # Детальний аналіз")
    print("   cat ast.json | python -m json.tool # JSON з відступами")
    print("   xdg-open index.html                # Візуалізація в браузері")
    print("="*60 + "\n")

if __name__ == '__main__':
    main()

