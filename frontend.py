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
<body style="background:#0a111f;color:#fff;font-family:sans-serif;display:flex;align-items:center;justify-content:center;height:100vh;">
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
            "shape": "image",
            "image": "https://img.icons8.com/fluency/96/switch.png",
            "size": 60,
            "font": {"color": "#ffffff", "size": 18, "face": "Segoe UI", "background": "rgba(0,0,0,0.8)", "bold": True},
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
            "shape": "image",
            "image": "https://img.icons8.com/fluency/96/monitor.png",
            "size": 30,
            "font": {"color": "#cbd5e1", "size": 12, "face": "monospace"},
            "tipo": "host",
            "porta": porta,
            "mac_completo": mac,
            "mac_maquina": mac_curto,
            "switch_pai": sw
        })

        edges.append({
            "from": sw,
            "to": mac,
            "label": f"P: {porta}",
            "font": {"align": "horizontal", "color": "#94a3b8", "size": 11},
            "color": {"color": "#334155", "highlight": "#38bdf8"},
            "width": 2
        })

    # 3. Processar Trunks (Uplinks)
    for ul in dados['uplinks']:
        edges.append({
            "from": ul['origem'],
            "to": ul['destino'],
            "label": f"[{ul['porta_origem']}] ⟷ [{ul['porta_destino']}]",
            "font": {"align": "horizontal", "color": "#00e676", "size": 15, "background": "#000000", "bold": True},
            "color": {"color": "#00e676", "highlight": "#00e5ff"},
            "width": 6,
            "length": 350
        })

    # Transformar listas em JSON para o JavaScript ler
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    edges_json = json.dumps(edges, ensure_ascii=False)

    total_sw = len(dados['switches'])
    total_hosts = len(dados['hosts'])
    total_trunks = len(dados['uplinks'])

    # Geração do HTML com formatação corrigida e f-string
    html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Topologia de Rede – SEAP</title>
    <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            background: #050b14;
            font-family: 'Segoe UI', sans-serif;
            display: flex;
            flex-direction: column;
            height: 100vh;
            overflow: hidden;
            color: #fff;
        }}
        #toolbar {{
            background: linear-gradient(90deg, #0a1a2b, #142433);
            padding: 8px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid #00e676;
            flex-shrink: 0;
            z-index: 10;
            flex-wrap: wrap;
            gap: 8px;
        }}
        #toolbar .logo {{
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 20px;
            font-weight: 300;
            letter-spacing: 1px;
        }}
        #toolbar .logo span {{ color: #00e676; font-weight: bold; }}
        #toolbar .stats {{
            display: flex;
            gap: 12px;
            font-size: 13px;
            flex-wrap: wrap;
        }}
        #toolbar .stats .stat-item {{
            background: rgba(255,255,255,0.06);
            padding: 4px 14px;
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,0.08);
        }}
        #toolbar .stats .stat-item b {{ color: #00e676; }}
        #toolbar .search {{
            display: flex;
            gap: 6px;
            align-items: center;
            background: rgba(255,255,255,0.06);
            border-radius: 25px;
            padding: 4px 12px 4px 16px;
            border: 1px solid rgba(255,255,255,0.1);
        }}
        #toolbar .search input {{
            background: transparent;
            border: none;
            color: #fff;
            padding: 6px 0;
            font-size: 13px;
            outline: none;
            width: 180px;
        }}
        #toolbar .search input::placeholder {{ color: #4a6a8a; }}
        #toolbar .search button {{
            background: #00e676;
            color: #000;
            border: none;
            padding: 4px 14px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 12px;
            cursor: pointer;
            transition: 0.2s;
        }}
        #toolbar .search button:hover {{ background: #00c853; }}
        #toolbar .search .limpar {{
            background: transparent;
            color: #4a6a8a;
            padding: 4px 8px;
            font-size: 16px;
            border: none;
            cursor: pointer;
        }}
        #toolbar .search .limpar:hover {{ color: #fff; }}
        #toolbar .actions {{
            display: flex;
            gap: 8px;
        }}
        #toolbar .actions button {{
            background: #00e676;
            color: #000;
            border: none;
            padding: 6px 16px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 12px;
            cursor: pointer;
            transition: 0.3s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        #toolbar .actions button:hover {{
            background: #00c853;
            transform: scale(1.05);
            box-shadow: 0 0 20px rgba(0,230,118,0.4);
        }}
        #main {{
            display: flex;
            flex: 1;
            min-height: 0;
        }}
        #mapa {{
            flex: 1;
            background: radial-gradient(circle at center, #0a1a2b, #020811);
            min-height: 0;
        }}
        #painel {{
            width: 320px;
            background: rgba(10, 20, 30, 0.95);
            border-left: 1px solid #00e67633;
            padding: 20px;
            overflow-y: auto;
            flex-shrink: 0;
            display: flex;
            flex-direction: column;
            transition: 0.3s;
        }}
        #painel h3 {{
            color: #00e676;
            border-bottom: 1px solid #00e67633;
            padding-bottom: 10px;
            margin-bottom: 15px;
            font-weight: 300;
            letter-spacing: 1px;
        }}
        #painel .info {{
            margin-bottom: 12px;
            font-size: 14px;
            line-height: 1.6;
        }}
        #painel .info .label {{
            color: #8a9bb2;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        #painel .info .value {{
            color: #fff;
            font-weight: bold;
            word-break: break-all;
        }}
        #painel .fechar {{
            background: none;
            border: 1px solid #4a6a8a;
            color: #8a9bb2;
            padding: 5px 12px;
            border-radius: 4px;
            cursor: pointer;
            margin-top: 15px;
            align-self: flex-end;
            font-size: 12px;
            transition: 0.2s;
        }}
        #painel .fechar:hover {{
            background: #4a6a8a33;
            color: #fff;
        }}
        #painel .vazio {{
            color: #4a6a8a;
            text-align: center;
            margin-top: 40px;
            font-size: 14px;
        }}
        .footer {{
            background: #0a1a2b;
            padding: 6px 25px;
            text-align: right;
            font-size: 11px;
            color: #4a6a8a;
            border-top: 1px solid #1a2a3b;
            flex-shrink: 0;
        }}
        .vis-tooltip {{
            background: rgba(10, 20, 30, 0.95) !important;
            color: #fff !important;
            border: 1px solid #00e676 !important;
            border-radius: 8px !important;
            padding: 12px 18px !important;
            font-size: 13px !important;
            font-family: 'Segoe UI', sans-serif !important;
            max-width: 300px !important;
        }}
        #legenda {{
            display: flex;
            gap: 20px;
            padding: 6px 25px;
            background: rgba(10, 20, 30, 0.8);
            border-top: 1px solid #1a2a3b;
            flex-shrink: 0;
            flex-wrap: wrap;
            font-size: 12px;
            color: #8a9bb2;
            align-items: center;
        }}
        #legenda .item {{ display: flex; align-items: center; gap: 6px; }}
        #legenda .cor {{ width: 16px; height: 4px; border-radius: 2px; }}
        #legenda .cor.trunk {{ background: #00e676; height: 6px; }}
        #legenda .cor.host {{ background: #334155; height: 2px; }}
        #legenda img {{ width: 20px; height: 20px; filter: brightness(0.8); }}
        .no-data {{ display: flex; align-items: center; justify-content: center; height: 100%; color: #4a6a8a; font-size: 18px; }}
    </style>
</head>
<body>
    <div id="toolbar">
        <div class="logo"><span>🌐</span> SEAP <span>·</span> Topologia</div>
        <div class="stats">
            <div class="stat-item">🔌 <b>{total_sw}</b> Switches</div>
            <div class="stat-item">💻 <b>{total_hosts}</b> Hosts</div>
            <div class="stat-item">🔗 <b>{total_trunks}</b> Trunks</div>
        </div>
        <div class="search">
            <input type="text" id="pesquisaInput" placeholder="Buscar MAC ou porta..." />
            <button onclick="buscar()">🔍</button>
            <button class="limpar" onclick="limparBusca()">✕</button>
        </div>
        <div class="actions">
            <button onclick="network.fit()">🎯 Centralizar</button>
            <button onclick="exportarImagem()">📷 Exportar PNG</button>
        </div>
    </div>
    <div id="main">
        <div id="mapa"></div>
        <div id="painel">
            <h3>📋 Detalhes</h3>
            <div id="conteudo-painel" class="vazio">Clique num nó para ver informações.</div>
            <button class="fechar" onclick="document.getElementById('conteudo-painel').innerHTML = '<div class=\\"vazio\\">Clique num nó para ver informações.</div>';">✕ Fechar</button>
        </div>
    </div>
    <div id="legenda">
        <div class="item"><img src="https://img.icons8.com/fluency/96/switch.png" style="width:20px;height:20px;"> Switch</div>
        <div class="item"><img src="https://img.icons8.com/fluency/96/monitor.png" style="width:20px;height:20px;"> Host (MAC)</div>
        <div class="item"><span class="cor trunk"></span> Trunk</div>
        <div class="item"><span class="cor host"></span> Conexão host-switch</div>
    </div>
    <div class="footer">Clique num nó para detalhes · Passe o mouse para tooltip · Arraste para navegar</div>

    <script>
        const nodesData = {nodes_json};
        const edgesData = {edges_json};

        console.log('Nós:', nodesData);
        console.log('Arestas:', edgesData);

        const container = document.getElementById('mapa');
        const painelConteudo = document.getElementById('conteudo-painel');

        if (nodesData.length === 0) {{
            container.innerHTML = '<div class="no-data">Nenhum nó encontrado.</div>';
        }} else {{
            const nodes = new vis.DataSet(nodesData);
            const edges = new vis.DataSet(edgesData);

            const options = {{
                layout: {{ hierarchical: false }},
                physics: {{
                    solver: 'forceAtlas2Based',
                    forceAtlas2Based: {{
                        gravitationalConstant: -120,
                        centralGravity: 0.005,
                        springLength: 200,
                        springConstant: 0.06
                    }},
                    stabilization: {{ iterations: 300 }}
                }},
                interaction: {{
                    dragNodes: false,
                    zoomView: true,
                    dragView: true,
                    hover: true,
                    tooltipDelay: 200
                }},
                nodes: {{ shape: 'image', size: 40 }},
                edges: {{ smooth: {{ type: 'curvedCCW', roundness: 0.2 }} }}
            }};

            const network = new vis.Network(container, {{ nodes, edges }}, options);

            network.once("stabilizationIterationsDone", function() {{
                network.setOptions({{ physics: false }});
                network.fit();
            }});
            setTimeout(() => network.fit(), 1000);

            // ===== Painel =====
            function mostrarDetalhes(nodeId) {{
                const node = nodes.get(nodeId);
                if (!node) {{
                    painelConteudo.innerHTML = '<div class="vazio">Nó não encontrado.</div>';
                    return;
                }}
                let html = '';
                if (node.tipo === 'switch') {{
                    html += `<div class="info"><div class="label">Equipamento</div><div class="value">🔌 Switch</div></div>`;
                    html += `<div class="info"><div class="label">Nome</div><div class="value">${{node.id.toUpperCase()}}</div></div>`;
                    const hostsConectados = nodesData.filter(n => n.switch_pai === node.id);
                    html += `<div class="info"><div class="label">Hosts conectados</div><div class="value">${{hostsConectados.length}}</div></div>`;
                }} else if (node.tipo === 'host') {{
                    html += `<div class="info"><div class="label">Tipo</div><div class="value">💻 Host</div></div>`;
                    html += `<div class="info"><div class="label">Identificador</div><div class="value">${{node.mac_maquina}}</div></div>`;
                    html += `<div class="info"><div class="label">MAC completo</div><div class="value">${{node.mac_completo}}</div></div>`;
                    html += `<div class="info"><div class="label">Switch</div><div class="value">${{node.switch_pai.toUpperCase()}}</div></div>`;
                    html += `<div class="info"><div class="label">Porta</div><div class="value">${{node.porta}}</div></div>`;
                }}
                painelConteudo.innerHTML = html;
            }}

            network.on("click", function(params) {{
                if (params.nodes.length > 0) {{
                    mostrarDetalhes(params.nodes[0]);
                }}
            }});

            // ===== Exportar PNG =====
            window.exportarImagem = function() {{
                const canvas = container.querySelector('canvas');
                if (canvas) {{
                    const link = document.createElement('a');
                    link.download = 'topologia.png';
                    link.href = canvas.toDataURL('image/png');
                    link.click();
                }} else {{
                    alert('Aguarde a renderização completa.');
                }}
            }};

            // ===== Busca =====
            window.buscar = function() {{
                const termo = document.getElementById('pesquisaInput').value.trim().toUpperCase();
                if (!termo) return;
                let encontrado = null;
                for (let node of nodes.get()) {{
                    const macComp = (node.mac_completo || '').toUpperCase();
                    const macCurto = (node.mac_maquina || '').toUpperCase();
                    const porta = (node.porta || '').toUpperCase();
                    const id = (node.id || '').toUpperCase();
                    if (macComp.includes(termo) || macCurto.includes(termo) || porta.includes(termo) || id.includes(termo)) {{
                        encontrado = node.id;
                        break;
                    }}
                }}
                if (encontrado) {{
                    // CORREÇÃO: No vis.js, a cor da borda fica dentro da propriedade 'color'
                    nodes.update([{{ id: encontrado, size: 55, borderWidth: 4, color: {{ border: '#ffeb3b' }} }}]);
                    network.fit({{ nodes: [encontrado], animation: {{ duration: 800 }} }});
                    mostrarDetalhes(encontrado);
                    
                    setTimeout(() => {{
                        const node = nodes.get(encontrado);
                        const sizeOriginal = node.tipo === 'switch' ? 60 : 30;
                        // CORREÇÃO: Remover o destaque devolvendo a cor da borda ao normal
                        nodes.update([{{ id: encontrado, size: sizeOriginal, borderWidth: 0, color: {{ border: 'transparent' }} }}]);
                    }}, 4000);
                }} else {{
                    alert('Nenhum nó encontrado para: ' + termo);
                }}
            }};

            window.limparBusca = function() {{
                document.getElementById('pesquisaInput').value = '';
                for (let node of nodes.get()) {{
                    const sizeOrig = node.tipo === 'switch' ? 60 : 30;
                    nodes.update([{{ id: node.id, size: sizeOrig, borderWidth: 0, color: {{ border: 'transparent' }} }}]);
                }}
                network.fit();
            }};

            document.getElementById('pesquisaInput').addEventListener('keypress', function(e) {{
                if (e.key === 'Enter') buscar();
            }});
        }}
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