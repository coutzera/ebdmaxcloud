class Pedido:
    def __init__(self, id, data_inclusao, status):
        self.id = id
        self.data_inclusao = data_inclusao
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'dataInclusao': self.data_inclusao,
            'status': self.status
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get('id'),
            data_inclusao=data.get('dataInclusao'),
            status=data.get('status', 'Sem status')
        )