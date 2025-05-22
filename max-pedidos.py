from flask import Flask, render_template_string, request, jsonify
from threading import Thread
from datetime import datetime, timedelta, date
from collections import defaultdict
import os
import requests
from dotenv import load_dotenv
import pytz
from dateutil.parser import parse
import time

load_dotenv()

app = Flask(__name__)
data = []
last_update = None
saopaulo_tz = pytz.timezone('America/Sao_Paulo')

def agrupar_por_faixa_horaria(pedidos):
    contagem = defaultdict(lambda: defaultdict(int))
    for pedido in pedidos:
        if 'dataInclusao' in pedido and 'status' in pedido:
            try:
                timestamp = parse(pedido['dataInclusao']).astimezone(saopaulo_tz)
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
        "User-Agent": "Mozilla/5.0",
        "Accept": "*/*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://appsv.solucoesmaxima.com.br/RelatorioPedidos/Emissao",
        "Cookie": os.getenv("COOKIE")
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            last_update = datetime.now(saopaulo_tz).strftime('%Y-%m-%d %H:%M:%S')
            print(f'Dados atualizados em {last_update}')
        else:
            print(f'Erro ao buscar dados, status code: {response.status_code}')
    except Exception as e:
        print("Erro ao buscar dados:", e)

def background_updater(data_inicial, data_final, interval=300):
    while True:
        fetch_data(data_inicial, data_final)
        time.sleep(interval)

@app.route('/data')
def get_data():
    return jsonify(data=data, last_update=last_update)

@app.route('/', methods=['GET', 'POST'])
def dashboard():
    hoje = date.today().strftime('%Y-%m-%d')
    data_inicial = request.form.get('data_inicial') or hoje
    data_final = request.form.get('data_final') or hoje
    # NÃO chama update_data aqui para evitar múltiplos timers
    faixas_horarias = agrupar_por_faixa_horaria(data)
    todos_os_status = extrair_todos_os_status(faixas_horarias)
    return render_template_string(
        # ... seu template HTML com variáveis data_inicial, data_final, faixas_horarias e todos_os_status ...
    )

@app.route('/refresh', methods=['POST'])
def refresh():
    hoje = date.today().strftime('%Y-%m-%d')
    data_inicial = request.json.get('data_inicial', hoje)
    data_final = request.json.get('data_final', hoje)
    fetch_data(data_inicial, data_final)
    return jsonify(success=True)

if __name__ == '__main__':
    data_inicial = date.today().strftime('%Y-%m-%d')
    data_final = data_inicial
    updater_thread = Thread(target=background_updater, args=(data_inicial, data_final), daemon=True)
    updater_thread.start()
    app.run(debug=True)
