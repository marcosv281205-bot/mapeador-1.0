import backend
import webbrowser
import os
import json

def gerar_html():
    dados = backend.extrair_dados_rede()
    
    if not dados:
        print("❌ Nenhum dado retornado.")
        html_erro = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Erro</title></head>
<body style="background:#0f172a;color:#f8fafc;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;">
<div style="text-align:center;"><h1>⚠️ Nenhum dado processado</h1><p>Selecione arquivos .txt válidos.</p></div>
</body></html>"""
        caminho = os.path.abspath('topologia.html')
        with open(caminho, 'w', encoding='utf-8') as f:
            f.write(html_erro)
        webbrowser.open(f'file://{caminho}')
        return

    nodes = []
    edges = []

    # 1. Processar Switches
    for sw in dados['switches']:
        nodes.append({
            "id": sw,
            "label": sw.upper(),
            "title": f"<div style='padding:5px;'><b>🔌 Switch:</b> {sw.upper()}</div>",
            "image": "https://img.icons8.com/fluency/96/switch.png",
            "size": 45,
            "tipo": "switch"
        })

    # 2. Processar Hosts
    for host in dados['hosts']:
        mac = host['MAC']
        mac_curto = host['mac_maquina']
        porta = host['porta']
        sw = host['switch']

        nodes.append({
            "id": mac,
            "label": mac_curto,
            "title": f"<div style='padding:5px;'><b>💻 Host:</b> {mac_curto}<br><b>MAC:</b> {mac}<br><b>Porta:</b> {porta}</div>",
            "image": "https://img.icons8.com/fluency/96/monitor.png",
            "size": 25,
            "tipo": "host",
            "porta": porta,
            "mac_completo": mac,
            "mac_maquina": mac_curto,
            "switch_pai": sw
        })

        # Cabo Host -> Switch (Agora Tracejado para diferenciar do Trunk)
        edges.append({
            "from": sw,
            "to": mac,
            "label": f"P: {porta}",
            "font": {"align": "middle", "color": "#94a3b8", "size": 10, "strokeWidth": 0},
            "color": {"color": "#475569", "highlight": "#38bdf8"},
            "width": 1.5,
            "length": 150,
            "dashes": [5, 5] # Efeito Tracejado
        })

    # 3. Processar Trunks (Uplinks) - Cabos principais
    for ul in dados['uplinks']:
        edges.append({
            "from": ul['origem'],
            "to": ul['destino'],
            "label": f"[{ul['porta_origem']}] ⟷ [{ul['porta_destino']}]",
            "font": {"align": "bottom", "color": "#10b981", "size": 13, "background": "rgba(15,23,42,0.8)", "bold": True},
            "color": {"color": "#10b981", "highlight": "#34d399"},
            "width": 4,
            "length": 350,
            "smooth": {"type": "curvedCW", "roundness": 0.2}
        })

    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)

    total_sw = len(dados['switches'])
    total_hosts = len(dados['hosts'])
    total_trunks = len(dados['uplinks'])

    # HTML Turbo - Design Glassmorphism & UI Moderna
    html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Topologia de Rede – SEAP</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background-color: #020617; /* Fundo base escuro */
            background-image: 
                radial-gradient(at 0% 0%, rgba(15, 23, 42, 1) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(15, 23, 42, 1) 0px, transparent 50%);
            font-family: 'Inter', sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
            color: #f8fafc;
        }}
        
        /* Toolbar Superior Estilo Glassmorphism */
        #toolbar {{
            background: rgba(15, 23, 42, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(16, 185, 129, 0.3);
            box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
            z-index: 10;
        }}
        .logo {{ font-size: 20px; font-weight: 600; letter-spacing: 0.5px; display: flex; align-items: center; gap: 10px; }}
        .logo span.highlight {{ color: #10b981; }}
        
        .stats {{ display: flex; gap: 15px; font-size: 13px; font-weight: 600; color: #cbd5e1; }}
        .stat-item {{ background: rgba(255,255,255,0.05); padding: 6px 16px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05); }}
        .stat-item b {{ color: #34d399; font-size: 14px; }}
        
        /* Barra de Pesquisa Redesenhada */
        .search-container {{ display: flex; align-items: center; gap: 8px; }}
        .search-box {{
            display: flex; align-items: center;
            background: rgba(0, 0, 0, 0.4);
            border: 1px solid rgba(148, 163, 184, 0.3);
            border-radius: 8px;
            padding: 4px 8px;
            transition: all 0.3s ease;
        }}
        .search-box:focus-within {{ border-color: #10b981; box-shadow: 0 0 10px rgba(16, 185, 129, 0.2); }}
        .search-box input {{ background: transparent; border: none; color: #fff; padding: 6px 8px; font-size: 13px; outline: none; width: 220px; font-family: 'Inter'; }}
        .search-box input::placeholder {{ color: #64748b; }}
        .btn-search {{ background: #10b981; color: #020617; border: none; padding: 6px 14px; border-radius: 6px; font-weight: 700; cursor: pointer; transition: 0.2s; }}
        .btn-search:hover {{ background: #34d399; transform: translateY(-1px); }}
        .btn-clear {{ background: transparent; color: #64748b; border: none; font-size: 18px; cursor: pointer; padding: 0 4px; }}
        .btn-clear:hover {{ color: #ef4444; }}

        .actions button {{
            background: rgba(255,255,255,0.05); color: #e2e8f0; border: 1px solid rgba(255,255,255,0.1);
            padding: 8px 16px; border-radius: 8px; font-weight: 600; font-size: 12px; cursor: pointer; transition: 0.3s;
        }}
        .actions button:hover {{ background: rgba(255,255,255,0.1); color: #fff; }}

        /* Área do Mapa e Painel */
        #main {{ position: relative; display: flex; flex: 1; overflow: hidden; }}
        #mapa {{ flex: 1; outline: none; cursor: grab; }}
        #mapa:active {{ cursor: grabbing; }}
        
        /* Painel Flutuante (Modernizado) */
        #painel {{
            position: absolute;
            right: -350px; /* Escondido por padrão */
            top: 20px;
            width: 320px;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(16, 185, 129, 0.4);
            border-radius: 12px;
            padding: 24px;
            box-shadow: -5px 10px 30px rgba(0,0,0,0.5);
            transition: right 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            display: flex; flex-direction: column;
            z-index: 100;
        }}
        #painel.ativo {{ right: 20px; }}
        
        #painel h3 {{ color: #34d399; font-size: 18px; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.1); }}
        .info-row {{ margin-bottom: 14px; }}
        .info-label {{ color: #94a3b8; font-size: 11px; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; margin-bottom: 4px; }}
        .info-value {{ color: #f8fafc; font-size: 14px; font-weight: 500; word-break: break-all; }}
        
        .btn-fechar {{ background: rgba(255,255,255,0.05); color: #cbd5e1; border: 1px solid rgba(255,255,255,0.1); padding: 8px; border-radius: 6px; cursor: pointer; margin-top: 20px; width: 100%; transition: 0.2s; font-weight: 600; }}
        .btn-fechar:hover {{ background: rgba(239, 68, 68, 0.2); color: #f87171; border-color: rgba(239, 68, 68, 0.4); }}

        /* Rodapé e Legenda Transparente */
        #legenda-container {{
            position: absolute; bottom: 20px; left: 20px;
            background: rgba(15, 23, 42, 0.7); backdrop-filter: blur(8px);
            padding: 12px 20px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.05);
            display: flex; gap: 20px; align-items: center;
            font-size: 12px; color: #cbd5e1; z-index: 10;
        }}
        .legenda-item {{ display: flex; align-items: center; gap: 8px; }}
        .linha-trunk {{ width: 24px; height: 4px; background: #10b981; border-radius: 2px; }}
        .linha-host {{ width: 24px; height: 2px; background: transparent; border-top: 2px dashed #475569; }}
        
        .vis-tooltip {{
            background: rgba(2, 6, 23, 0.95) !important; color: #f8fafc !important;
            border: 1px solid #10b981 !important; border-radius: 8px !important;
            padding: 12px !important; font-size: 13px !important; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            font-family: 'Inter', sans-serif !important;
        }}
    </style>
</head>
<body>
    <div id="toolbar">
        <div class="logo"><span class="highlight">🌐</span> SEAP Topologia</div>
        <div class="stats">
            <div class="stat-item"><b>{total_sw}</b> Switches</div>
            <div class="stat-item"><b>{total_hosts}</b> Hosts</div>
            <div class="stat-item"><b>{total_trunks}</b> Trunks</div>
        </div>
        <div class="search-container">
            <div class="search-box">
                <input type="text" id="pesquisaInput" placeholder="Buscar MAC, Porta ou Nome..." />
                <button class="btn-clear" onclick="limparBusca()">×</button>
            </div>
            <button class="btn-search" onclick="buscar()">Buscar</button>
        </div>
        <div class="actions">
            <button onclick="network.fit({{ animation: {{ duration: 800, easingFunction: 'easeInOutQuad' }} }})">🎯 Ver Tudo</button>
            <button onclick="exportarImagem()">📸 Exportar PNG</button>
        </div>
    </div>
    
    <div id="main">
        <div id="mapa"></div>
        
        <div id="painel">
            <h3>📋 Detalhes do Nó</h3>
            <div id="conteudo-painel"></div>
            <button class="btn-fechar" onclick="fecharPainel()">Fechar Janela</button>
        </div>
        
        <div id="legenda-container">
            <div class="legenda-item"><img src="https://img.icons8.com/fluency/96/switch.png" width="18"> Switch</div>
            <div class="legenda-item"><img src="https://img.icons8.com/fluency/96/monitor.png" width="18"> Host</div>
            <div class="legenda-item"><div class="linha-trunk"></div> Trunk / Link Direto</div>
            <div class="legenda-item"><div class="linha-host"></div> Porta de Acesso</div>
        </div>
    </div>

    <script>
        const nodesData = {nodes_json};
        const edgesData = {edges_json};

        const container = document.getElementById('mapa');
        const painel = document.getElementById('painel');
        const painelConteudo = document.getElementById('conteudo-painel');

        // Configuração Global e Limpa dos Nós
        const nodes = new vis.DataSet(nodesData.map(node => ({{
            ...node,
            shape: 'image',
            shapeProperties: {{ useBorderWithImage: true }},
            borderWidth: 2,
            borderWidthSelected: 5,
            color: {{
                border: 'transparent',
                highlight: {{ border: '#38bdf8', background: 'transparent' }},
                hover: {{ border: '#10b981', background: 'transparent' }}
            }},
            font: {{ color: '#e2e8f0', face: 'Inter', size: 12, background: 'rgba(15,23,42,0.7)', strokeWidth: 0, multi: 'html' }}
        }})));

        const edges = new vis.DataSet(edgesData);

        const options = {{
            layout: {{ hierarchical: false }},
            physics: {{
                solver: 'barnesHut', // Melhor engine para topologias de rede
                barnesHut: {{
                    gravitationalConstant: -4000,
                    centralGravity: 0.1,
                    springLength: 120,
                    springConstant: 0.04,
                    damping: 0.09,
                    avoidOverlap: 0.1
                }},
                stabilization: {{ iterations: 200, fit: true }}
            }},
            interaction: {{
                hover: true, tooltipDelay: 150, zoomView: true, dragView: true,
                navigationButtons: false, keyboard: false
            }}
        }};

        const network = new vis.Network(container, {{ nodes, edges }}, options);

        // Desliga a física pesada após carregar para poupar CPU
        network.once("stabilizationIterationsDone", function() {{
            network.setOptions({{ physics: {{ enabled: false }} }});
            network.fit();
        }});

        // ===== Lógica do Painel e Cliques =====
        function mostrarDetalhes(nodeId) {{
            const node = nodes.get(nodeId);
            if (!node) return;
            
            let html = '';
            if (node.tipo === 'switch') {{
                html += `<div class="info-row"><div class="info-label">Tipo de Equipamento</div><div class="info-value">🔌 Switch de Rede</div></div>`;
                html += `<div class="info-row"><div class="info-label">Identificação</div><div class="info-value">${{node.id.toUpperCase()}}</div></div>`;
                const hostsConectados = nodesData.filter(n => n.switch_pai === node.id).length;
                html += `<div class="info-row"><div class="info-label">Hosts Mapeados</div><div class="info-value">${{hostsConectados}} dispositivos</div></div>`;
            }} else if (node.tipo === 'host') {{
                html += `<div class="info-row"><div class="info-label">Tipo de Equipamento</div><div class="info-value">💻 Host / Endpoint</div></div>`;
                html += `<div class="info-row"><div class="info-label">MAC Resumido</div><div class="info-value">${{node.mac_maquina}}</div></div>`;
                html += `<div class="info-row"><div class="info-label">Endereço MAC Completo</div><div class="info-value">${{node.mac_completo}}</div></div>`;
                html += `<div class="info-row"><div class="info-label">Conectado ao Switch</div><div class="info-value">${{node.switch_pai.toUpperCase()}}</div></div>`;
                html += `<div class="info-row"><div class="info-label">Na Porta</div><div class="info-value">${{node.porta}}</div></div>`;
            }}
            
            painelConteudo.innerHTML = html;
            painel.classList.add('ativo');
        }}

        window.fecharPainel = function() {{
            painel.classList.remove('ativo');
        }};

        // Abre o painel se clicar no nó, FECHA se clicar no fundo vazio
        network.on("click", function(params) {{
            if (params.nodes.length > 0) {{
                mostrarDetalhes(params.nodes[0]);
            }} else {{
                fecharPainel();
                network.unselectAll(); // Tira a seleção ao clicar fora
            }}
        }});

        // ===== Busca Integrada Nativa (Corrigida) =====
        window.buscar = function() {{
            const termo = document.getElementById('pesquisaInput').value.trim().toUpperCase();
            if (!termo) return;
            
            let encontradoId = null;
            for (let node of nodes.get()) {{
                const macComp = (node.mac_completo || '').toUpperCase();
                const macCurto = (node.mac_maquina || '').toUpperCase();
                const porta = (node.porta || '').toUpperCase();
                const id = (node.id || '').toUpperCase();
                
                if (macComp.includes(termo) || macCurto.includes(termo) || porta.includes(termo) || id.includes(termo)) {{
                    encontradoId = node.id;
                    break;
                }}
            }}
            
            if (encontradoId) {{
                // Usa a função nativa para focar e selecionar, que é muito mais bonita e não quebra os nós
                network.selectNodes([encontradoId]);
                network.focus(encontradoId, {{ 
                    scale: 1.4, 
                    animation: {{ duration: 1000, easingFunction: 'easeInOutQuad' }} 
                }});
                mostrarDetalhes(encontradoId);
            }} else {{
                alert('Nenhum nó encontrado para: ' + termo);
            }}
        }};

        window.limparBusca = function() {{
            document.getElementById('pesquisaInput').value = '';
            network.unselectAll();
            network.fit({{ animation: {{ duration: 800, easingFunction: 'easeInOutQuad' }} }});
            fecharPainel();
        }};

        document.getElementById('pesquisaInput').addEventListener('keypress', function(e) {{
            if (e.key === 'Enter') buscar();
        }});

        // ===== Exportar Imagem (Fundo Escuro Nativo) =====
        window.exportarImagem = function() {{
            const canvas = container.querySelector('canvas');
            if (canvas) {{
                const tempCanvas = document.createElement('canvas');
                tempCanvas.width = canvas.width;
                tempCanvas.height = canvas.height;
                const ctx = tempCanvas.getContext('2d');
                
                // Preenche com a mesma cor de fundo da página
                ctx.fillStyle = '#020617'; 
                ctx.fillRect(0, 0, tempCanvas.width, tempCanvas.height);
                ctx.drawImage(canvas, 0, 0);

                const link = document.createElement('a');
                link.download = 'Mapeamento_Rede_SEAP.png';
                link.href = tempCanvas.toDataURL('image/png');
                link.click();
            }}
        }};
    </script>
</body>
</html>"""

    caminho = os.path.abspath('topologia.html')
    with open(caminho, 'w', encoding='utf-8') as f:
        f.write(html)
        
    print(f"✅ Mapa gerado em {caminho}")
    webbrowser.open(f'file://{caminho}')

if __name__ == "__main__":
    gerar_html()