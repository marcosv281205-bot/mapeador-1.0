import tkinter as tk
from tkinter import filedialog
import os

def selecionar_arquivo_windows():
    """Abre a janela nativa do Windows para o utilizador escolher o ficheiro"""
    root = tk.Tk()
    root.withdraw() # Oculta a janela principal
    
    # CORREÇÃO 1: Força a janela a aparecer por cima (evita que fique escondida atrás do VS Code)
    root.attributes('-topmost', True)
    
    print("⚙️ BACKEND: A aguardar seleção do ficheiro TXT...")
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione o log do Switch (.txt)",
        filetypes=[("Ficheiros de Texto", "*.txt"), ("Todos os Ficheiros", "*.*")]
    )
    
    # CORREÇÃO 2: Destrói a janela oculta para o programa não ficar bloqueado (congelado) em segundo plano
    root.destroy()
    
    return caminho_arquivo

def identificar_marca_switch(linhas):
    """Analisa o começo do ficheiro para descobrir a marca"""
    for linha in linhas[:20]:
        if "Legend: Mac Address" in linha or "-------+-------------------+" in linha:
            return "ALCATEL"
        
        # Substitua pela palavra-chave real que aparece no cabeçalho da Intelbras
        elif "PALAVRA_CHAVE_INTELBRAS" in linha: 
            return "INTELBRAS"
            
    return "DESCONHECIDO"

def ler_padrao_alcatel(linhas):
    """Régua de Corte para Alcatel"""
    dados = []
    for linha in linhas:
        partes = linha.split() 
        if len(partes) >= 5 and ':' in partes[1]:
            vlan = partes[0]
            mac = partes[1].upper() 
            porta = partes[-1]      
            if '/' in porta or any(char.isdigit() for char in porta):
                dados.append({'VLAN': vlan, 'MAC': mac, 'Porta': porta})
    return dados

def ler_padrao_intelbras(linhas):
    """Régua de Corte Genérica para Intelbras"""
    dados = []
    for linha in linhas:
        partes = linha.split() 
        
        # Verifica se a linha tem informações suficientes e se parece um MAC
        if len(partes) >= 3 and ('-' in partes[0] or ':' in partes[0]):
            # Adapta as posições [0], [1], [-1] consoante o teu log real da Intelbras
            mac = partes[0].upper() 
            vlan = partes[1]        
            porta = partes[-1]      
            
            dados.append({'VLAN': vlan, 'MAC': mac, 'Porta': porta})
            
    return dados

def extrair_dados_switch():
    """Gere todo o processo de extração e devolve os dados limpos."""
    caminho_arquivo = selecionar_arquivo_windows()
    
    if not caminho_arquivo: 
        print("⚠️ BACKEND: Nenhum ficheiro selecionado. Operação cancelada.")
        return None 
        
    nome_do_arquivo = os.path.basename(caminho_arquivo)
    print(f"⚙️ BACKEND: A analisar o ficheiro -> {nome_do_arquivo}")
    
    dados_mapeados = []
    try:
        # CORREÇÃO 3: errors='replace' evita que o programa dê erro caso o TXT tenha caracteres especiais estranhos
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='replace') as arquivo:
            linhas = arquivo.readlines()
            
            marca = identificar_marca_switch(linhas)
            print(f"⚙️ BACKEND: Marca detetada -> {marca}")
            
            if marca == "ALCATEL":
                dados_mapeados = ler_padrao_alcatel(linhas)
            elif marca == "INTELBRAS":
                dados_mapeados = ler_padrao_intelbras(linhas)
            else:
                print("❌ BACKEND Erro: Formato não reconhecido. Certifique-se de que é um log do Alcatel ou Intelbras.")
                return None
                
    except Exception as erro:
        print(f"❌ BACKEND Erro crítico ao processar o ficheiro: {erro}")
        return None
        
    print(f"⚙️ BACKEND: Sucesso! {len(dados_mapeados)} dispositivos encontrados.")
    return dados_mapeados

# Bloco de Teste: Permite testar o backend clicando no "Play" apenas neste ficheiro
if __name__ == "__main__":
    resultado = extrair_dados_switch()
    if resultado:
        print("Primeiros 3 resultados extraídos para teste:")
        print(resultado[:3])