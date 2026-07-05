import tkinter as tk
from tkinter import filedialog
import os
import re

def selecionar_arquivo_windows():
    root = tk.Tk()
    root.withdraw() 
    root.attributes('-topmost', True)
    print("⚙️ BACKEND: A aguardar seleção do ficheiro TXT...")
    caminho_arquivo = filedialog.askopenfilename(
        title="Selecione o log do Switch (.txt)",
        filetypes=[("Ficheiros de Texto", "*.txt"), ("Todos os Ficheiros", "*.*")]
    )
    root.destroy()
    return caminho_arquivo

def ler_dados_de_qualquer_switch(linhas):
    dados = []
    macs_vistos = set() # 🟢 CORREÇÃO 1: Impede que MACs repetidos quebrem o frontend!
    
    # 🟢 CORREÇÃO 2: Padrão turbinado! Apanha formatos como:
    # 00:11:22:33:44:55 | 00-11-22-33-44-55 | 0011.2233.4455 | 0011-2233-4455
    padrao_mac = re.compile(r'(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}|(?:[0-9A-Fa-f]{4}[.-]){2}[0-9A-Fa-f]{4}')
    
    for linha in linhas:
        mac_encontrado = padrao_mac.search(linha)
        
        if mac_encontrado:
            partes = linha.split()
            mac = mac_encontrado.group().upper()
            
            # Só adicionamos se o dispositivo ainda não existir na nossa lista
            if mac not in macs_vistos:
                macs_vistos.add(mac)
                
                # Prevenção extra caso a linha de log não tenha a porta no fim
                porta = partes[-1] if len(partes) > 1 else "Desconhecida"
                vlan = partes[0] if partes[0].isdigit() else "N/A"
                
                dados.append({'VLAN': vlan, 'MAC': mac, 'Porta': porta})
                
    return dados

def extrair_dados_switch():
    caminho_arquivo = selecionar_arquivo_windows()
    
    if not caminho_arquivo: 
        print("⚠️ BACKEND: Nenhum ficheiro selecionado. Operação cancelada.")
        return None 
        
    nome_do_arquivo = os.path.basename(caminho_arquivo)
    print(f"⚙️ BACKEND: A analisar o ficheiro -> {nome_do_arquivo}")
    
    dados_mapeados = []
    try:
        with open(caminho_arquivo, 'r', encoding='utf-8', errors='replace') as arquivo:
            linhas = arquivo.readlines()
            dados_mapeados = ler_dados_de_qualquer_switch(linhas)
            
    except Exception as erro:
        print(f"❌ BACKEND Erro crítico ao processar o ficheiro: {erro}")
        return None
        
    if not dados_mapeados:
        print("⚠️ BACKEND: Nenhum dispositivo/MAC encontrado neste ficheiro.")
        return None

    print(f"⚙️ BACKEND: Sucesso! {len(dados_mapeados)} dispositivos únicos detetados.")
    return dados_mapeados

if __name__ == "__main__":
    resultado = extrair_dados_switch()
    if resultado:
        print("\n--- Primeiros 5 resultados extraídos para teste ---")
        for item in resultado[:5]:
            print(item)