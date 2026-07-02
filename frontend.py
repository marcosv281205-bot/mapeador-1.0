import backend
import webbrowser
import os

def gerar_interface_grafica():
    print("🎨 FRONTEND: A iniciar a aplicação e a solicitar dados ao Backend...")
    
    # O Backend chama a janela do Windows para a escolha do ficheiro
    dados_limpos = backend.extrair_dados_switch()
    
    if not dados_limpos:
        print("⚠️ FRONTEND: O backend não devolveu dados válidos. O dashboard não será gerado.")
        return

    print("🎨 FRONTEND: A construir a arquitetura do Dashboard Moderno (Com Funcionalidades Profissionais)...")

    # 1. Montamos a lista de Nós (Nodes) - Usando ícones reais!
    nos_javascript = [
        "{ id: 'SWITCH_CENTRAL', label: 'SWITCH PRINCIPAL', shape: 'image', image: 'https://img.icons8.com/fluency/96/switch.png', size: 45, font: {color: '#ffffff', size: 16, bold: true, face: 'Segoe UI'}, level: 0, tipo: 'switch' }"
    ]
    
    conexoes_javascript = []

    # 2. Varremos os dados para criar as máquinas e os cabos
    for dispositivo in dados_limpos:
        mac = dispositivo['MAC']
        porta = dispositivo['Porta']
        vlan = dispositivo['VLAN']
        
        # Criação da Máquina (PC) com formato de Imagem
        card_pc = f"""{{ 
            id: '{mac}', 
            label: '{mac}', 
            shape: 'image', 
            image: 'https://img.icons8.com/fluency/96/workstation.png',
            size: 30,
            font: {{color: '#e2e8f0', size: 13, face: 'monospace'}}, 
            level: 1, 
            tipo: 'pc',
            porta: '{porta}',
            vlan: '{vlan}'
        }}"""
        nos_javascript.append(card_pc)
        
        # Cabo de rede (Cinza prateado, brilha a azul ao clicar)
        cabo = f"{{ from: 'SWITCH_CENTRAL', to: '{mac}', label: 'Porta {porta}', font: {{align: 'horizontal', color: '#cbd5e1', size: 11, background: '#000000', strokeWidth: 0}}, color: {{color: '#334155', highlight: '#38bdf8'}}, arrows: 'to' }}"
        conexoes_javascript.append(cabo)

    # Conta o total de dispositivos extraídos (para injetar na UI)
    total_maquinas = len(dados_limpos)

    # Junta tudo
    texto_nos = ",\n        ".join(nos_javascript)
    texto_conexoes = ",\n        ".join(conexoes_javascript)

    # 3. TEMPLATE HTML/CSS (Estilo Corporativo com Busca e Resumo)
    html_dashboard = f"""<!DOCTYPE html>
<html lang="pt-PT">
<head>
    <meta charset="UTF-8">
    <title>Painel de Mapeamento de Rede - SEAP</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    
    <style>
        body {{
            margin: 0; padding: 0;
            font-family: 'Segoe UI', system-ui, sans-serif;
            background-color: #000000;
            background-image: radial-gradient(circle at 50% 0%, #111827 0%, #000000 60%),
                              linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
                              linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
            background-size: 100% 100%, 30px 30px, 30px 30px;
            color: #f8fafc;
            display: flex; height: 100vh; overflow: hidden;
        }}
        #mapa-container {{ flex: 1; height: 100%; position: relative; }}
        
        #sidebar {{
            width: 340px; background: rgba(10, 10, 10, 0.85);
            backdrop-filter: blur(12px);
            border-left: 1px solid rgba(255, 255, 255, 0.05); 
            padding: 30px 25px; display: flex; flex-direction: column;
            box-shadow: -15px 0 30px rgba(0,0,0,0.8);
            transition: all 0.3s ease; z-index: 10;
        }}
        
        h2 {{
            color: #f8fafc; margin-top: 0; font-size: 20px; font-weight: 600;
            border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 16px;
            display: flex; align-items: center; gap: 10px;
        }}
        h2 span {{ color: #38bdf8; }}
        
        .status-badge {{
            background: rgba(56, 189, 248, 0.1); color: #38bdf8; 
            border: 1px solid rgba(56, 189, 248, 0.3);
            padding: 4px 12px; border-radius: 20px; font-size: 11px; font-weight: bold;
            display: inline-block; margin-bottom: 20px; text-transform: uppercase;
        }}
        
        .campo-detalhe {{
            background: rgba(255, 255, 255, 0.03); padding: 14px; border-radius: 10px;
            margin-bottom: 16px; border-left: 3px solid #38bdf8;
            transition: background 0.2s;
        }}
        .campo-detalhe:hover {{ background: rgba(255, 255, 255, 0.06); }}
        .campo-detalhe.switch {{ border-left-color: #10b981; }}
        
        .rotulo {{
            font-size: 11px; color: #64748b; text-transform: uppercase;
            font-weight: 600; letter-spacing: 1px; margin-bottom: 6px;
        }}
        .valor {{ font-size: 15px; font-weight: 400; color: #f1f5f9; }}
        
        /* NOVOS ESTILOS: Busca e Estatísticas */
        .search-box {{
            display: flex; gap: 8px; margin-bottom: 25px;
        }}
        .search-box input {{
            flex: 1; padding: 10px 14px; border-radius: 6px;
            background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1);
            color: white; font-family: 'Segoe UI'; outline: none; transition: border 0.3s;
        }}
        .search-box input:focus {{ border-color: #38bdf8; }}
        .search-box button {{
            background: #38bdf8; color: #000; border: none; border-radius: 6px;
            padding: 0 15px; cursor: pointer; font-weight: bold; transition: background 0.3s;
        }}
        .search-box button:hover {{ background: #7dd3fc; }}

        .stats-grid {{
            display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 25px;
        }}
        .stat-card {{
            background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.05);
            padding: 15px; border-radius: 8px; text-align: center;
        }}
        .stat-number {{ font-size: 24px; font-weight: bold; color: #10b981; margin-bottom: 5px; }}
        .stat-text {{ font-size: 11px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-number.blue {{ color: #38bdf8; }}

        .logo-area {{
            margin-top: auto; text-align: center; color: #475569; font-size: 12px;
            padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.05);
        }}
    </style>
</head>
<body>

    <div id="mapa-container">
        <div id="rede-canvas" style="width: 100%; height: 100%;"></div>
    </div>

    <div id="sidebar">
        <h2><span>📊</span> Painel de Rede</h2>
        <div id="conteudo-painel">
            <!-- Este é o resumo que aparece inicialmente -->
            <div id="visao-geral">
                <div class="search-box">
                    <input type="text" id="busca-input" placeholder="Buscar MAC ou Porta..." onkeypress="verificarEnter(event)">
                    <button onclick="buscarDispositivo()">🔍</button>
                </div>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number">{total_maquinas}</div>
                        <div class="stat-text">Dispositivos</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number blue">1</div>
                        <div class="stat-text">Switch</div>
                    </div>
                </div>
                
                <div style="color: #64748b; font-size: 13px; text-align: center; line-height: 1.5; margin-top: 10px;">
                    Clica em qualquer ícone no mapa para ver os dados detalhados ou usa a barra de busca acima para localizar rapidamente uma máquina.
                </div>
            </div>
        </div>
        <div class="logo-area">
            MAPEADOR DE REDE V1.5<br>Sistema Automático - SEAP
        </div>
    </div>

    <script type="text/javascript">
        var nodes = new vis.DataSet([{texto_nos}]);
        var edges = new vis.DataSet([{texto_conexoes}]);

        var container = document.getElementById('rede-canvas');
        var data = {{ nodes: nodes, edges: edges }};
        
        var options = {{
            layout: {{
                hierarchical: {{
                    enabled: true, direction: 'UD', sortMethod: 'directed',
                    levelSeparation: 220, nodeDistance: 240
                }}
            }},
            physics: {{
                hierarchicalRepulsion: {{ nodeDistance: 240, centralGravity: 0.0 }},
                solver: 'hierarchicalRepulsion'
            }},
            interaction: {{ hover: true }}
        }};

        var network = new vis.Network(container, data, options);

        // Guarda o HTML original do painel para podermos voltar a ele
        var htmlVisaoGeral = document.getElementById('visao-geral').outerHTML;

        // Função do Clique
        network.on("click", function (params) {{
            var painel = document.getElementById('conteudo-painel');
            
            if (params.nodes.length > 0) {{
                var idSelecionado = params.nodes[0];
                var dadosNo = nodes.get(idSelecionado);
                
                if (dadosNo.tipo === 'switch') {{
                    painel.innerHTML = `
                        <div style="margin-bottom: 20px;"><button onclick="voltarResumo()" style="background:transparent; border:none; color:#94a3b8; cursor:pointer; font-size:13px;">← Voltar ao Resumo</button></div>
                        <span class="status-badge" style="color: #34d399; background: rgba(16, 185, 129, 0.1); border-color: rgba(16, 185, 129, 0.3);">🟢 ONLINE</span>
                        <div class="campo-detalhe switch">
                            <div class="rotulo">Equipamento</div><div class="valor">Switch Principal de Acesso</div>
                        </div>
                        <div class="campo-detalhe switch">
                            <div class="rotulo">Status da Rede</div><div class="valor">Distribuição Ativa</div>
                        </div>
                    `;
                }} else {{
                    painel.innerHTML = `
                        <div style="margin-bottom: 20px;"><button onclick="voltarResumo()" style="background:transparent; border:none; color:#94a3b8; cursor:pointer; font-size:13px;">← Voltar ao Resumo</button></div>
                        <span class="status-badge">🔗 CONECTADO</span>
                        <div class="campo-detalhe">
                            <div class="rotulo">Endereço MAC do Host</div>
                            <div class="valor" style="font-family: 'Courier New', monospace; letter-spacing: 1px;">${{dadosNo.id}}</div>
                        </div>
                        <div class="campo-detalhe">
                            <div class="rotulo">Porta Física no Switch</div>
                            <div class="valor" style="color: #7dd3fc; font-weight: 600; font-size: 17px;">${{dadosNo.porta}}</div>
                        </div>
                        <div class="campo-detalhe">
                            <div class="rotulo">VLAN Designada</div>
                            <div class="valor">VLAN ${{dadosNo.vlan}}</div>
                        </div>
                    `;
                }}
            }} else {{
                voltarResumo(); // Se clicar no vazio, volta para a visão geral
            }}
        }});

        function voltarResumo() {{
            document.getElementById('conteudo-painel').innerHTML = htmlVisaoGeral;
        }}

        function verificarEnter(e) {{
            if (e.key === 'Enter') buscarDispositivo();
        }}

        function buscarDispositivo() {{
            var termo = document.getElementById('busca-input').value.trim().toUpperCase();
            if (!termo) return;

            var todosOsNos = nodes.get();
            var noEncontrado = null;

            // Procura o termo no ID (MAC) ou na Porta
            for (var i = 0; i < todosOsNos.length; i++) {{
                var n = todosOsNos[i];
                if (n.id.toUpperCase().includes(termo) || (n.porta && n.porta.toUpperCase() === termo)) {{
                    noEncontrado = n;
                    break;
                }}
            }}

            if (noEncontrado) {{
                // Faz a animação de Zoom no dispositivo encontrado
                network.focus(noEncontrado.id, {{
                    scale: 1.5,
                    animation: {{ duration: 1000, easingFunction: 'easeInOutQuad' }}
                }});
                
                // Simula um clique para abrir os detalhes na barra lateral
                network.selectNodes([noEncontrado.id]);
                network.emit('click', {{ nodes: [noEncontrado.id] }});
            }} else {{
                alert("Dispositivo ou Porta não encontrada na topologia atual.");
            }}
        }}
    </script>
</body>
</html>
"""

    # 4. Grava o ficheiro
    nome_html = 'Mapa_da_Rede_SEAP.html'
    caminho_completo = os.path.abspath(nome_html)
    
    with open(caminho_completo, 'w', encoding='utf-8') as f:
        f.write(html_dashboard)
        
    print(f"✅ FRONTEND: Dashboard Profissional gerado com sucesso!")
    
    # 5. Abre automaticamente no navegador padrão
    print("🚀 A abrir o mapa no navegador...")
    webbrowser.open(f'file://{caminho_completo}')

if __name__ == '__main__':
    gerar_interface_grafica()