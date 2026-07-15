import tkinter as tk
from tkinter import filedialog
import os
from collections import defaultdict

def mac_curto(mac):
    partes = mac.replace('-', ':').split(':')
    if len(partes) == 6:
        return ':'.join(partes[3:6]).upper()
    return mac


def extrair_arquivos_txt():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    print("BACKEND: A aguardar seleção dos ficheiros .txt...")
    caminhos = filedialog.askopenfilenames(
        title="Selecione os arquivos .txt dos switches",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()
    return caminhos

def extrair_dados_rede():
    caminhos = extrair_arquivos_txt()


    if not caminhos:
        print("BACKEND: Nenhum ficheiro selecionado. Operação cancelada.")
        return None

    # Estruturas de dados
    switch_portas = defaultdict(lambda: defaultdict(list))
    mac_aparicoes = defaultdict(list)
    macs_por_switch = defaultdict(set) # NOVO: Guarda todos os MACs que passaram pelo switch

    # Leitura dos arquivos
    for caminho in caminhos:
        nome_switch = os.path.basename(caminho).replace('.txt', '')
        try:
            # errors='replace' evita crashes se o TXT vier com caracteres estranhos
            with open(caminho, 'r', encoding='utf-8', errors='replace') as f:
                for linha in f:
                    linha = linha.strip()
                    if not linha or ',' not in linha:
                        continue
                        
                    partes = linha.split(',', 1)
                    if len(partes) != 2:
                        continue
                        
                    mac = partes[0].strip().upper()
                    porta = partes[1].strip()
                    
                    if not mac or not porta:
                        continue
                        
                    switch_portas[nome_switch][porta].append(mac)
                    mac_aparicoes[mac].append((nome_switch, porta))
                    macs_por_switch[nome_switch].add(mac) # Regista o MAC na visão global do switch
                    
        except Exception as e:
            print(f"Erro ao ler {caminho}: {e}")

    if not mac_aparicoes:
        return None

    switches = list(switch_portas.keys())
    
    # Contar quantos MACs existem por porta (para encontrar a porta de Acesso)
    portas_count = {}
    for sw, portas in switch_portas.items():
        portas_count[sw] = {porta: len(macs) for porta, macs in portas.items()}

    # 1. Definir a "Casa" (Home) de cada MAC (porta com menos MACs = Access Port)
    hosts = []
    for mac, aparicoes in mac_aparicoes.items():
        # Encontra a porta com o menor número de MACs para ser a casa do host
        melhor = min(aparicoes, key=lambda x: portas_count[x[0]].get(x[1], 9999))
        sw, porta = melhor
        hosts.append({
            'MAC': mac,
            'mac_maquina': mac_curto(mac),
            'switch': sw,
            'porta': porta
        })

    # 2. Inferir Trunks (Uplinks) usando Score Global (Atualizado)
    uplinks = []
    portas_usadas = set() # Guarda as portas já mapeadas ex: (nome_switch, porta)
    candidatos = []

    for i in range(len(switches)):
        for j in range(i + 1, len(switches)):
            sw1 = switches[i]
            sw2 = switches[j]

            # Avaliar cada combinação de portas entre os dois switches
            for p1, macs_p1_list in switch_portas[sw1].items():
                macs1 = set(macs_p1_list)
                
                # Otimização: Se a porta tem menos de 2 MACs, dificilmente é um Trunk para outro switch
                if len(macs1) < 2:
                    continue
                    
                for p2, macs_p2_list in switch_portas[sw2].items():
                    macs2 = set(macs_p2_list)
                    
                    if len(macs2) < 2:
                        continue

                    # Regra de Ouro: Uma ligação direta NÃO partilha MACs nas duas portas
                    intersecao = len(macs1.intersection(macs2))
                    
                    # Tolerância para ruído de rede. Se passar de 5, é conexão indireta/loop!
                    if intersecao > 5:
                        continue

                    # NOVA MÉTRICA DE VISIBILIDADE GLOBAL:
                    # Quantos MACs que passam na porta p1 existem em *qualquer lugar* do Switch 2?
                    sw1_ve_sw2 = len(macs1.intersection(macs_por_switch[sw2]))
                    sw2_ve_sw1 = len(macs2.intersection(macs_por_switch[sw1]))
                    forca_mutua = sw1_ve_sw2 + sw2_ve_sw1

                    # Se os switches não trocam tráfego entre si nestas portas, descarta.
                    if forca_mutua == 0:
                        continue

                    cobertura = len(macs1) + len(macs2)
                    
                    # Cálculo do Score: Força Mútua é o fator mais importante
                    score = (forca_mutua * 10) + cobertura - (intersecao * 1000)

                    candidatos.append({
                        'score': score,
                        'sw1': sw1, 'p1': p1,
                        'sw2': sw2, 'p2': p2
                    })

    # Ordena a lista do maior Score para o menor
    candidatos.sort(key=lambda x: x['score'], reverse=True)

    # Validação final e criação dos links
    for cand in candidatos:
        sw1, p1 = cand['sw1'], cand['p1']
        sw2, p2 = cand['sw2'], cand['p2']

        # Se NENHUMA das portas estiver a ser usada noutro link, fechamos a ligação!
        if (sw1, p1) not in portas_usadas and (sw2, p2) not in portas_usadas:
            uplinks.append({
                'origem': sw1,
                'destino': sw2,
                'porta_origem': p1,
                'porta_destino': p2
            })
            portas_usadas.add((sw1, p1))
            portas_usadas.add((sw2, p2))

    # Relatório Final no Terminal
    print(f"\n BACKEND: Topologia concluída!")
    print(f" Switches processados: {len(switches)}")
    print(f" Hosts finais identificados: {len(hosts)}")
    print(f" Cabos diretos (Trunks) deduzidos: {len(uplinks)}")
    for ul in uplinks:
        print(f"   [{ul['origem']}] Porta {ul['porta_origem']} <====> [{ul['destino']}] Porta {ul['porta_destino']}")

    return {
        'switches': switches,
        'hosts': hosts,
        'uplinks': uplinks
    }

if __name__ == "__main__":
    dados = extrair_dados_rede()
    if not dados:
        print("Falha ao obter dados.")