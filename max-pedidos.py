from flask import Flask, render_template_string, request, jsonify
from threading import Timer
from datetime import datetime, timedelta, date
from collections import defaultdict
import os
import requests
from dotenv import load_dotenv
import pytz

load_dotenv()

app = Flask(__name__)
data = []
last_update = None

# Define the timezone for São Paulo
saopaulo_tz = pytz.timezone('America/Sao_Paulo')

def agrupar_por_faixa_horaria(pedidos):
    contagem = defaultdict(lambda: defaultdict(int))
    for pedido in pedidos:
        if 'dataInclusao' in pedido and 'status' in pedido:
            try:
                timestamp = datetime.fromisoformat(pedido['dataInclusao']).astimezone(saopaulo_tz)
                hora = timestamp.replace(minute=0, second=0, microsecond=0)
                status = pedido['status'] or 'Sem status'
                contagem[hora][status] += 1
            except Exception as e:
                print("Erro ao processar dataInclusao:", e)
    return dict(sorted(contagem.items()))

def fetch_data(data_inicial, data_final):
    global data, last_update
    url = f"https://appsv.solucoesmaxima.com.br/RelatorioPedidos/Emita?dataInicial={data_inicial}&dataFinal={data_final}"
    headers = {
        "User-Agent": os.getenv("USER_AGENT"),
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://appsv.solucoesmaxima.com.br/RelatorioPedidos/Emissao",
    }
    cookies = {
        ".AspNetCore.Antiforgery.dfcmfiBUHUQ": os.getenv("ANTIFORGERY"),
        ".AspNetCore.Mvc.CookieTempDataProvider": os.getenv("COOKIE_TEMP"),
        ".AspNetCore.Identity.Application": os.getenv("COOKIE_IDENTITY"),
        "MaximaClienteData": os.getenv("COOKIE_MAXIMADADOS"),
        "tec-menucliente-cookie": os.getenv("MENU_CLIENT"),
        "sidebar_toggle_state": "on"
    }
    try:
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code == 200:
            data = response.json()
            last_update = datetime.now(saopaulo_tz).strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print("Erro ao buscar dados:", e)

def update_data(data_inicial, data_final):
    fetch_data(data_inicial, data_final)
    Timer(300, update_data, args=(data_inicial, data_final)).start()

def extrair_todos_os_status(faixas_horarias):
    status_set = set()
    for status_por_faixa in faixas_horarias.values():
        status_set.update(status_por_faixa.keys())
    return sorted(status_set)

@app.route('/data')
def get_data():
    return jsonify(data=data, last_update=last_update)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    hoje = date.today().strftime('%Y-%m-%d')
    data_inicial = request.form.get('data_inicial') or hoje
    data_final = request.form.get('data_final') or hoje
    update_data(data_inicial, data_final)

    faixas_horarias = agrupar_por_faixa_horaria(data)
    todos_os_status = extrair_todos_os_status(faixas_horarias)

    return render_template_string('''
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Dashboard interativo de pedidos com filtros, gráficos e status em tempo real.">
<meta name="theme-color" content="#4F46E5">
<title>Dashboard de Pedidos</title>
<script src="https://cdn.tailwindcss.com"></script>
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

body {
    font-family: 'Inter', sans-serif;
    background-color: #f8fafc;
}

.chart-container {
    position: relative;
    height: 100%;
    min-height: 300px;
    max-height: 300px;
    max-width: 100%;
    overflow-x: auto;
}
canvas {
    max-width: 100% !important;
    height: auto !important;
}
</style>
</head>
<body class="text-gray-800">
<div class="container mx-auto p-6">
<h1 class="text-3xl font-bold mb-8">Dashboard de Pedidos</h1>

<!-- Filtros -->
<form method="POST" class="bg-white rounded-xl shadow-sm p-6 mb-6">
<div class="flex flex-col md:flex-row md:items-end md:space-x-6 space-y-4 md:space-y-0">
<div class="flex-1">
<label class="block text-sm font-medium text-gray-700 mb-1">Data Inicial</label>
<div class="relative">
<input type="date" id="data_inicial" name="data_inicial" class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" value="{{ data_inicial }}">
<i class="fas fa-calendar-alt absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
</div>
</div>
<div class="flex-1">
<label class="block text-sm font-medium text-gray-700 mb-1">Data Final</label>
<div class="relative">
<input type="date" id="data_final" name="data_final" class="w-full p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500" value="{{ data_final }}">
<i class="fas fa-calendar-alt absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400"></i>
</div>
</div>
<div>
<button type="submit" class="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-lg transition-colors flex items-center space-x-2">
<i class="fas fa-filter"></i>
<span>Filtrar</span>
</button>
</div>
</div>

<div class="mt-4 flex items-center text-sm text-gray-500">
<i class="fas fa-info-circle mr-2"></i>
<span>Última atualização: <span id="last-update" class="font-medium text-gray-700">Carregando...</span></span>
<button id="refresh-button" class="ml-4 text-indigo-600 hover:text-indigo-800 flex items-center">
<i class="fas fa-sync-alt mr-1"></i>
<span>Atualizar</span>
</button>
</div>
</form>

<!-- Cards de Status -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-6" id="status-container">
<!-- Loading state -->
<div class="bg-white rounded-xl shadow-sm p-6 animate-pulse">
<div class="h-6 w-3/4 bg-gray-200 rounded mb-4"></div>
<div class="h-8 w-1/2 bg-gray-200 rounded"></div>
</div>
<div class="bg-white rounded-xl shadow-sm p-6 animate-pulse">
<div class="h-6 w-3/4 bg-gray-200 rounded mb-4"></div>
<div class="h-8 w-1/2 bg-gray-200 rounded"></div>
</div>
<div class="bg-white rounded-xl shadow-sm p-6 animate-pulse">
<div class="h-6 w-3/4 bg-gray-200 rounded mb-4"></div>
<div class="h-8 w-1/2 bg-gray-200 rounded"></div>
</div>
<div class="bg-white rounded-xl shadow-sm p-6 animate-pulse">
<div class="h-6 w-3/4 bg-gray-200 rounded mb-4"></div>
<div class="h-8 w-1/2 bg-gray-200 rounded"></div>
</div>
<div class="bg-white rounded-xl shadow-sm p-6 animate-pulse">
<div class="h-6 w-3/4 bg-gray-200 rounded mb-4"></div>
<div class="h-8 w-1/2 bg-gray-200 rounded"></div>
</div>
</div>

<!-- Tabela de Pedidos por Faixa Horária -->
<div class="bg-white rounded-xl shadow-sm overflow-hidden mb-6">
<div class="p-6 border-b border-gray-200">
<h2 class="text-lg font-semibold text-gray-800">Pedidos por Faixa de Horário e Status</h2>
</div>
<div class="overflow-x-auto">
<table class="min-w-full divide-y divide-gray-200">
<thead class="bg-gray-50">
<tr>
<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Faixa de Horário</th>
{% for status in todos_os_status %}
<th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">{{ status }}</th>
{% endfor %}
</tr>
</thead>
<tbody class="bg-white divide-y divide-gray-200">
{% for hora, status_dict in faixas_horarias.items() %}
<tr>
<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
{{ hora.strftime('%H:%M') }} - {{ (hora + timedelta(hours=1)).strftime('%H:%M') }}
</td>
{% for status in todos_os_status %}
<td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
{{ status_dict.get(status, 0) }}
</td>
{% endfor %}
</tr>
{% endfor %}
</tbody>
</table>
</div>
</div>

<!-- Gráficos -->
<div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
<div class="bg-white rounded-xl shadow-sm p-6">
<div class="flex justify-between items-center mb-4">
<h2 class="text-lg font-semibold text-gray-800">Distribuição de Status</h2>
</div>
<div class="chart-container">
<canvas id="pieChart"></canvas>
</div>
</div>

<div class="bg-white rounded-xl shadow-sm p-6">
<div class="flex justify-between items-center mb-4">
<h2 class="text-lg font-semibold text-gray-800">Evolução por Hora</h2>
</div>
<div class="chart-container">
<canvas id="lineChart"></canvas>
</div>
</div>
</div>
</div>

<script>
// Função para atualizar o dashboard com os dados reais
function updateDashboard() {
fetch('/data')
.then(res => res.json())
.then(info => {
// Atualiza a data/hora da última atualização
document.getElementById('last-update').innerText = info.last_update;

// Calcula as contagens por status
const counts = {};
info.data.forEach(p => {
const s = p.status || 'Sem status';
counts[s] = (counts[s] || 0) + 1;
});

// Atualiza os cards de status
const container = document.getElementById('status-container');
container.innerHTML = '';

const statusColors = {
"Recebido pelo servidor": "bg-gradient-to-r from-gray-300 to-gray-400",      // Neutro, início do processo
"Pedido gravado na FV": "bg-gradient-to-r from-blue-400 to-blue-500",         // Azul mais vivo, indicando progresso
"Enviado para o ERP": "bg-gradient-to-r from-yellow-400 to-yellow-500",       // Amarelo chamativo, transição
"Processado pelo ERP": "bg-gradient-to-r from-green-400 to-green-600",        // Verde mais escuro, sucesso
"Bloqueado envio ERP": "bg-gradient-to-r from-orange-500 to-orange-600",      // Laranja, alerta de atenção
"Bloqueado / cancelado": "bg-gradient-to-r from-red-600 to-red-800"           // Vermelho intenso, erro ou bloqueio
};

const statusIcons = {
"Recebido pelo servidor": "fas fa-cloud",
"Pedido gravado na FV": "fas fa-layer-group",
"Enviado para o ERP": "fas fa-light fa-truck-fast",
"Processado pelo ERP": "fas fa-check-circle",
"Bloqueado envio ERP": "fas fa-eye-slash",
"Bloqueado / cancelado": "fas fa-times-circle"
};

let cardIndex = 1;
for (const [status, count] of Object.entries(counts)) {
const card = document.createElement('div');
card.className = `min-w-[180px] bg-white rounded-xl shadow-sm p-6 flex items-center justify-between ${statusColors[status] || ''}`;

card.innerHTML = `
<div>
<p class="text-sm ${statusColors[status] ? 'text-white' : 'text-gray-500'}">${status}</p>
<p class="text-2xl font-bold ${statusColors[status] ? 'text-white' : 'text-gray-800'}">${count}</p>
</div>
<div class="w-12 h-12 rounded-full ${statusColors[status] ? 'bg-white bg-opacity-20' : 'bg-gray-100'} flex items-center justify-center">
<i class="${statusIcons[status] || 'fas fa-box'} ${statusColors[status] ? 'text-white' : 'text-indigo-600'}"></i>
</div>
`;
container.appendChild(card);
cardIndex++;
}

// Atualiza o gráfico de pizza
const pieCtx = document.getElementById('pieChart').getContext('2d');
if (window.pieChart && typeof window.pieChart.destroy === 'function') {
window.pieChart.destroy();
}

window.pieChart = new Chart(pieCtx, {
type: 'pie',
data: {
labels: Object.keys(counts),
datasets: [{
data: Object.values(counts),
backgroundColor: [
'rgba(99, 102, 241, 0.8)',
'rgba(59, 130, 246, 0.8)',
'rgba(16, 185, 129, 0.8)',
'rgba(245, 158, 11, 0.8)',
'rgba(239, 68, 68, 0.8)'
],
borderColor: [
'rgba(99, 102, 241, 1)',
'rgba(59, 130, 246, 1)',
'rgba(16, 185, 129, 1)',
'rgba(245, 158, 11, 1)',
'rgba(239, 68, 68, 1)'
],
borderWidth: 1
}]
},
options: {
responsive: true,
maintainAspectRatio: false,
plugins: {
legend: {
position: 'right',
labels: {
usePointStyle: true,
padding: 20
}
},
tooltip: {
callbacks: {
label: function(context) {
const label = context.label || '';
const value = context.raw || 0;
const total = context.dataset.data.reduce((a, b) => a + b, 0);
const percentage = Math.round((value / total) * 100);
return `${label}: ${value} (${percentage}%)`;
}
}
}
}
}
});

// Atualiza o gráfico de linha
const lineCtx = document.getElementById('lineChart').getContext('2d');
if (window.lineChart && typeof window.lineChart.destroy === 'function') {
window.lineChart.destroy();
}

// Extrai os labels (horas) dos dados
const labels = Object.keys(info.data.reduce((acc, p) => {
    const hora = new Date(p.dataInclusao).getHours();
    acc[hora] = true;
    return acc;
}, {})).map(Number).sort((a, b) => a - b);


// Cria datasets para cada status
const datasets = Object.keys(counts).map(status => ({
label: status,
data: labels.map(hora =>
info.data.filter(p =>
new Date(p.dataInclusao).getHours() == hora &&
p.status == status
).length
),
borderColor: getStatusColor(status),
backgroundColor: getStatusColor(status, 0.2),
tension: 0.3,
fill: true
}));

window.lineChart = new Chart(lineCtx, {
type: 'line',
data: {
labels: labels.map(h => `${h.toString().padStart(2, '0')}:00`)
,
datasets: datasets
},
options: {
responsive: true,
maintainAspectRatio: false,
plugins: {
legend: {
position: 'top',
labels: {
usePointStyle: true
}
},
tooltip: {
mode: 'index',
intersect: false
}
},
scales: {
x: {
grid: {
display: false
},
title: {
display: true,
text: 'Hora do dia'
}
},
y: {
beginAtZero: true,
title: {
display: true,
text: 'Número de pedidos'
}
}
}
}
});
});
}

// Função auxiliar para obter cores baseadas no status
function getStatusColor(status, opacity = 1) {
    const colors = {
        "Recebido pelo servidor": `rgba(148, 163, 184, ${opacity})`, // Gray-400
        "Pedido gravado na FV": `rgba(59, 130, 246, ${opacity})`,    // Blue-500
        "Enviado para o ERP": `rgba(234, 179, 8, ${opacity})`,       // Yellow-500
        "Processado pelo ERP": `rgba(16, 185, 129, ${opacity})`,     // Green-500
        "Bloqueado envio ERP": `rgba(249, 115, 22, ${opacity})`,     // Orange-500
        "Bloqueado / cancelado": `rgba(239, 68, 68, ${opacity})`,    // Red-500
    };
    return colors[status] || `rgba(107, 114, 128, ${opacity})`; // Gray-500 default
}

// Inicializa o dashboard quando a página carrega
document.addEventListener('DOMContentLoaded', () => {
    updateDashboard();
});

// Atualiza automaticamente a cada 5 minutos
setInterval(updateDashboard, 300000);
});
document.getElementById('refresh-button').addEventListener('click', (e) => {
    e.preventDefault();
    updateDashboard();
});
</script>
</body>
</html>
''',
data_inicial=data_inicial,
data_final=data_final,
faixas_horarias=faixas_horarias,
todos_os_status=todos_os_status,
timedelta=timedelta
)

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
