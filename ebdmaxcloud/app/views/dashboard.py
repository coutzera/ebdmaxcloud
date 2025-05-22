from flask import Blueprint, render_template, request, jsonify
from datetime import date
from app.controllers.pedido_controller import PedidoController

dashboard_bp = Blueprint('dashboard', __name__)
pedido_controller = PedidoController()

@dashboard_bp.route('/data')
def get_data():
    data, last_update = pedido_controller.get_orders()
    return jsonify(data=data, last_update=last_update)

@dashboard_bp.route('/', methods=['GET', 'POST'])
def dashboard():
    hoje = date.today().strftime('%Y-%m-%d')
    data_inicial = request.form.get('data_inicial') or hoje
    data_final = request.form.get('data_final') or hoje
    pedido_controller.update_data(data_inicial, data_final)

    faixas_horarias = pedido_controller.agrupar_por_faixa_horaria()
    todos_os_status = pedido_controller.extrair_todos_os_status(faixas_horarias)

    return render_template('dashboard.html',
                           data_inicial=data_inicial,
                           data_final=data_final,
                           faixas_horarias=faixas_horarias,
                           todos_os_status=todos_os_status)