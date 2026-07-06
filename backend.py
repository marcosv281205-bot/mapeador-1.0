import tkinter as tk
from tkinter import filedialog
import os
from collections import defaultdict

def mac_curto(mac):
    partes = mac.replace('-', ':').split(':')
    if len(partes) == 6:
        return ':'.join(partes[3:6]).upper()
    return mac

def extrair_dados_rede():
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    print("⚙️ BACKEND: A aguardar seleção dos ficheiros .txt...")
    caminhos = filedialog.askopenfilenames(
        title="Selecione os arquivos .txt dos switches",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )
    root.destroy()

    if not caminhos:
        print("⚠️ BACKEND: Nenhum ficheiro selecionado. Operação cancelada.")
        return None

    # Estruturas de dados
    switch_portas = defaultdict(lambda: defaultdict(list))
    mac_aparicoes = defaultdict(list)

    # Leitura dos arquivos
    for caminho in caminhos:
        nome_switch = os.path.basename(caminho).replace('.txt', '')
        try:
            with open(caminho, 'r', encoding='utf-8') as f:
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
    mac_home = {}
    hosts = []
    for mac, aparicoes in mac_aparicoes.items():
        # Encontra a porta com o menor número de MACs para ser a casa do host
        melhor = min(aparicoes, key=lambda x: portas_count[x[0]].get(x[1], 9999))
        sw, porta = melhor
        mac_home[mac] = sw
        hosts.append({
            'MAC': mac,
            'mac_maquina': mac_curto(mac),
            'switch': sw,
            'porta': porta
        })

    # 2. Descobrir quais Switches cada porta consegue "enxergar"
    port_home_counts = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
    for sw in switches:
        for port, macs in switch_portas[sw].items():
            for mac in macs:
                home = mac_home[mac]
                if home != sw: # Se o MAC mora noutro switch, contabilizamos
                    port_home_counts[sw][port][home] += 1

    # 3. Inferir Trunks (Uplinks) usando a Regra de Interseção FDB
    uplinks = []
    for i in range(len(switches)):
        for j in range(i + 1, len(switches)):
            sw1 = switches[i]
            sw2 = switches[j]

            # Portas no sw1 que enxergam equipamentos cuja casa é o sw2
            ports1 = [p for p, targets in port_home_counts[sw1].items() if sw2 in targets]
            # Portas no sw2 que enxergam equipamentos cuja casa é o sw1
            ports2 = [p for p, targets in port_home_counts[sw2].items() if sw1 in targets]

            best_pair = None
            best_score = -999999

            # Avaliar cada combinação de portas entre os dois switches
            for p1 in ports1:
                for p2 in ports2:
                    macs1 = set(switch_portas[sw1][p1])
                    macs2 = set(switch_portas[sw2][p2])

                    # Regra de Ouro: Uma ligação direta NÃO partilha MACs nas duas portas
                    intersection = len(macs1.intersection(macs2))
                    coverage = len(macs1) + len(macs2)
                    
                    # Penalidade altíssima se houver MACs em comum
                    score = coverage - (intersection * 100)

                    if score > best_score:
                        best_score = score
                        best_pair = (p1, p2)

            # Validação final do link direto
            if best_pair:
                p1, p2 = best_pair
                macs1 = set(switch_portas[sw1][p1])
                macs2 = set(switch_portas[sw2][p2])
                intersecao = len(macs1.intersection(macs2))
                
                # Tolerância de segurança: Num cabo direto a interseção deve ser 0.
                # Permitimos até 5 MACs partilhados para compensar ruído de rede (flapping, BPDUs, etc.)
                if intersecao <= 5:
                    uplinks.append({
                        'origem': sw1,
                        'destino': sw2,
                        'porta_origem': p1,
                        'porta_destino': p2
                    })

    # Relatório Final
    print(f"\n⚙️ BACKEND: Topologia concluída!")
    print(f"📡 Switches processados: {len(switches)}")
    print(f"💻 Hosts finais identificados: {len(hosts)}")
    print(f"🔗 Cabos diretos (Trunks) deduzidos: {len(uplinks)}")
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