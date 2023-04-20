import ply.lex as lex
from ply import yacc
from cProfile import label
import tkinter as tk #Biblioteca para interfaces gráficas
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import filedialog as fd

reserved = {
    'IFSULDEMINAS': 'IFSULDEMINAS',
    'INICIO': 'INICIO',
    'COMPILADORES': 'COMPILADORES',
    'FIM': 'FIM',
    'se': 'se',
    'senao': 'senao',
    'enquanto': 'enquanto',
    'para': 'para',
    'interrompa': 'interrompa',
    'continue': 'continue',
    'retorne': 'retorne',
    'em': 'em',
    'define': 'define',
    'classe': 'classe',
    'leia': 'leia',
    'escreva': 'escreva',
}

tokens = [
    'OP_ARIT', #'+', '-', '/', '*'
    'OP_REL', #'<', '>', '<>', '<=', '>=', '=='
    'OP_ATRIBUI', #':='
    'ABRE_CH', #'{'
    'FECHA_CH', #'}'
    'ABRE_CLT', #'['
    'FECHA_CLT', #']'
    'ABRE_P', #'('
    'FECHA_P', #')'
    'COMENT', #'**...'
    'COMENTS', #'***...***']
    'VIRGULA', #','
    'PONTO_E_VIRGULA', ';'
    'DELIMITADOR', #'$'
    'tipo_var',
    'valor_numint',
    'valor_texto',
    'valor_letra',
    'valor_numdec',
    'booleano',
    
#Verificação de compatibilidade com o ply (biblioteca utilizada)
'ignore', #ignorar tabulação e espaços
'numero_mf', #número mal formado
'texto_mf', #string mal formada
'variavel_mf', #variável mal formada
] + list(reserved.values()) #Concatenação com as palavras reservadas

t_OP_ARIT = r'\+|-|/|*'
t_OP_MOD = r'\%'
t_PONTO_E_VIRGULA = r'\;'
t_VIRGULA = r'\,'
t_ASPAS = r'\"'
t_COMENT = r'\**'
t_COMENTS = r'\*\*\*[a-zA-Z]+\*\*\*'
t_booleano = r'\b(verdadeiro|falso)\b'

t_IFSULDEMINAS = r'IFSULDEMINAS'
t_INICIO = r'INICIO'
t_COMPILADORES = r'COMPILADORES'
t_FIM = r'FIM'
t_se = r'se'
t_senao = r'senao'
t_enquanto = r'enquanto'
t_para = r'para'
t_interrompa = r'interrompa'
t_prossiga = r'prossiga'
t_retorne = r'retorne'
t_em = r'em'
t_define = r'define'
t_classe = r'classe'
t_escreva = r'escreva'
t_leia = r'leia'

t_OP_REL = r'[-+]=?|==|<>'
t_OP_ATRIBUI = r'\:='
t_OP_LOGICO = r'\b(e|ou)\b'
t_ABRE_P = r'\('
t_FECHA_P = r'\)'
t_ABRE_CH = r'\{'
t_FECHA_CH = r'\}'
t_ABRE_CLT = r'\['
t_FECHA_CLT = r'\]'
t_ignore = ' \t' #Ignora espaços e tabulações

def t_valor_texto(t):
    r'("[^"]*")'
    return t

def t_texto_mf(t):
    r'("[^"]*)'
    return t

def t_variavel_mf(t):
    r'([0-9]+[a-z]+)|([@!#$%&*]+[a-z]+|[a-z]+\.[0-9]+|[a-z]+[@!#$%&*]+)'
    return t

def t_numero_mf(t):
    r'([0-9]+\.[a-z]+[0-9]+)|([0-9]+\.[a-z]+)|([0-9]+\.[0-9]+[a-z]+)'
    return t

def t_valor_numdec(t):
    r'([0-9]+\.[0-9]+)|([0-9]+\.[0-9]+)'
    return t

def t_valor_numint(t):
    r'\d+'
    t.value = int(t.value)
    return t

def t_valor_letra(t):
    r'[a-z][a-z_0-9]*'
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_DELIMITADOR(t):
    r'\$'
    return t
    t.lexer.lineno += len(t.value)

#Regras para tratamento de erros
erroslexicos = []
def t_error(t):
    erroslexicos.append(t)
    t.lexer.skip(1)

root = tk.Tk()
class Application():
    def __init__(self):
        self.root = root
        self.tela()
        self.frames_da_tela()
        self.botoes()
        self.Menus()
        root.mainloop()

    def limpa_telaentrada(self):
        self.codigo_entry.delete(1.0, END)
        for i in self.saida.get_children():
            self.saida.delete(1)
        saidas.clear()
        erroslexicos.clear()
        errossintaticos.clear()
        global erros
        erros = 0
        self.frame_1.update()
        self.frame_2.update()
        root.update()

    def tela(self):
        self.root.title("Compilador")
        self.root.configure(background = "white")
        self.root.geometry("700x500")
        self.root.resizable(True, True)
        self.root.minsize(width = 500, height = 350)

    def frames_da_tela(self):
        self.frame_1 = Frame(self.root, bd = 4, bg = "#DCDCDC", highlightbackground = "grey", highlightthickness = 3)
        self.frame_1.place(relx = 0.02, rely = 0.07, relwidth = 0.96, relheight = .55)
        self.frame_2 = Frame(self.root, bd = 4, bg = "#DCDCDC", highlightbackground = "grey", highlightthickness = 3)
        self.frame_2.place(relx = 0.02, rely = 0.70, relwidth = 0.96, relheight = 0.20)

    def chama_analisador(self):
        columns = ('linha', 'posicao', 'token', 'lexema', 'notificacao')
        self.saida = ttk.Treeview(self.frame_2, height = 5, columns = columns, show = 'headings')
        self.saida.heading("linha", text = 'Linha')
        self.saida.heading("posicao", text = 'Posição referente ao início da entrada')
        self.saida.heading("token", text = 'Token')
        self.saida.heading("notificacao", text = 'Notificação')

        data = self.codigo_entry.get(1.0, "end-1c")
        data.lower()
        lexer = lex.lex()
        lexer.input(data)

        #Tokenizar a entrada para passar para o analisar léxico
        for tok in lexer:
            global erros
            if tok.type == "texto_mf":
                erros += 1
                add_lista_saida(tok, f"Ops... String mal formada!")
            elif tok.type == "variavel_mf":
                erros += 1
                add_lista_saida(tok, f"Ops... Variável mal formada!")











