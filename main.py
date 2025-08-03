import re
from graphviz import Digraph

# Clase para nodos del AST
class Nodo:
    def __init__(self, valor, izquierda=None, derecha=None):
        self.valor = valor
        self.izquierda = izquierda
        self.derecha = derecha

# Precedencia y asociatividad de operadores
precedence = {
    '*': 4,
    '+': 4,
    '?': 4,
    '.': 3,  # Concatenación implícita
    '|': 2,  # OR
    '(': 1
}

right_associative = {'*', '+', '?'}

# Transforma extensiones (+ y ?) a formas básicas
def preprocesar_regex(expresion):
    expresion = re.sub(r'(\w)\+', r'\1\1*', expresion)  # a+ → aa*
    expresion = re.sub(r'(\w)\?', r'(\1|ε)', expresion)  # a? → (a|ε)
    return expresion

# Inserta concatenaciones explícitas con '.'
def insert_concatenation(exp):
    output = []
    for i in range(len(exp)):
        c = exp[i]
        output.append(c)
        if i + 1 < len(exp):
            next_c = exp[i + 1]
            # Casos donde se necesita concatenación: ab → a.b, )a → ).a, *a → *.a
            if (c not in {'(', '|'} and next_c not in {'|', ')', '*', '+', '?', '.'}) or \
               (c in {'*', '+', '?', ')'} and next_c not in {'|', ')', '*', '+', '?', '.'}):
                output.append('.')
    return ''.join(output)

# Algoritmo de Shunting Yard para regex
def shunting_yard(regex):
    output = []
    stack = []
    i = 0
    while i < len(regex):
        c = regex[i]
        if c == '\\':  # Carácter escapado (ej: \*)
            if i + 1 < len(regex):
                output.append(c + regex[i + 1])
                i += 1
        elif c == '(':
            stack.append(c)
        elif c == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Eliminar '('
        elif c in precedence:
            while (stack and stack[-1] != '(' and
                   precedence[c] <= precedence[stack[-1]]):
                output.append(stack.pop())
            stack.append(c)
        else:  # Operando (a, b, ε, etc.)
            output.append(c)
        i += 1

    while stack:
        output.append(stack.pop())

    return ''.join(output)

# Construye el AST desde postfix
def postfix_a_ast(postfix):
    pila = []
    for c in postfix:
        if c in {'*', '+', '?'}:  # Operadores unarios
            nodo = pila.pop()
            pila.append(Nodo(c, nodo))
        elif c in {'|', '.'}:  # Operadores binarios
            derecha = pila.pop()
            izquierda = pila.pop()
            pila.append(Nodo(c, izquierda, derecha))
        else:  # Operando (hoja)
            pila.append(Nodo(c))
    return pila[0] if pila else None

# Visualiza el AST con Graphviz
def dibujar_ast(nodo, filename='ast'):
    dot = Digraph()
    def agregar_nodos(nodo):
        if nodo:
            nodo_id = str(id(nodo))
            dot.node(nodo_id, label=nodo.valor)
            if nodo.izquierda:
                dot.edge(nodo_id, str(id(nodo.izquierda)))
                agregar_nodos(nodo.izquierda)
            if nodo.derecha:
                dot.edge(nodo_id, str(id(nodo.derecha)))
                agregar_nodos(nodo.derecha)
    agregar_nodos(nodo)
    dot.render(filename, format='png', cleanup=True)
    print(f"Árbol guardado como {filename}.png")

# Procesa el archivo de expresiones
def procesar_archivo(nombre_archivo):
    with open(nombre_archivo, 'r') as archivo:
        lineas = archivo.readlines()
        for idx, linea in enumerate(lineas, 1):
            expresion = linea.strip()
            print(f"\n--- Expresión {idx}: {expresion} ---")
            
            # Paso 1: Preprocesar (+ → aa*, ? → a|ε)
            expresion_pp = preprocesar_regex(expresion)
            print(f"Preprocesada: {expresion_pp}")
            
            # Paso 2: Insertar concatenaciones explícitas
            expresion_concat = insert_concatenation(expresion_pp)
            print(f"Con concatenación: {expresion_concat}")
            
            # Paso 3: Convertir a postfix
            postfix = shunting_yard(expresion_concat)
            print(f"Postfix: {postfix}")
            
            # Paso 4: Construir AST
            ast = postfix_a_ast(postfix)
            dibujar_ast(ast, f'ast_expresion_{idx}')

# Ejecución principal
if __name__ == "__main__":
    archivo = "expresiones.txt"  # Archivo con una expresión por línea
    procesar_archivo(archivo)