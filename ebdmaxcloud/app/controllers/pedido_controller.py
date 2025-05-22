from flask import request, jsonify
from app.models.pedido import Pedido
from app import db

class PedidoController:
    @staticmethod
    def fetch_data(data_inicial, data_final):
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
                return response.json()
        except Exception as e:
            print("Error fetching data:", e)
        return []

    @staticmethod
    def update_data(data_inicial, data_final):
        data = PedidoController.fetch_data(data_inicial, data_final)
        # Logic to update the database or application state with the fetched data
        for item in data:
            pedido = Pedido(**item)
            db.session.add(pedido)
        db.session.commit()

    @staticmethod
    def get_orders():
        return Pedido.query.all()