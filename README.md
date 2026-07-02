🌐 Automação de Mapeamento de Switch (SEAP)

Este projeto é uma ferramenta de automação desenvolvida em Python para mapear conexões de switches de rede. Ele extrai informações de portas e MACs e gera um Dashboard interativo e visual automaticamente no navegador.

🚀 Funcionalidades

Extração automática de dados (MAC, Porta e VLAN).

Geração instantânea de uma topologia de rede gráfica (HTML/JS).

Dashboard no estilo Dark Mode corporativo.

Sistema de busca em tempo real por dispositivo (MAC) ou Porta física.

Painel de estatísticas da rede.

🛠️ Tecnologias Utilizadas

Python 3 (Lógica de processamento e extração)

Netmiko (Automação de conexões SSH em equipamentos de rede)

Vis-network.js (Biblioteca gráfica para o mapa interativo)

HTML / CSS (Interface visual)

📦 Como utilizar

Instale a biblioteca necessária no terminal:

pip install netmiko


Configure o IP e as credenciais do Switch no arquivo backend.py.

Execute o programa através do arquivo principal:

python frontend.py


O navegador abrirá automaticamente exibindo o painel da rede!