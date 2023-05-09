from sql_alchemy import banco

class HotelModel(banco.Model):
    # Classe modelo para representar os hotéis
    ## Ter todas as cofigurações que determina que será uma tabela em um db
    ## Cada atributo do modelo seja uma coluna no db - Mapeamento
    __tablename__ = 'hoteis'

    hotel_id = banco.Column(banco.String, primary_key=True)
    nome = banco.Column(banco.String(80))
    estrelas = banco.Column(banco.Float(precision=1))
    diaria = banco.Column(banco.Float(precision=2))
    cidade = banco.Column(banco.String(40))
    site_id = banco.Column(banco.Integer, banco.ForeignKey('sites.site_id'))
    # site = banco.relationship('SiteModel')

    def __init__(self, hotel_id, nome, estrelas, diaria, cidade, site_id):
        # Função construtora
        self.hotel_id = hotel_id
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.site_id = site_id
    
    def json(self):
        # Transforma o objeto em dicionário formato json
        return {
            'hotel_id': self.hotel_id,
            'nome': self.nome,
            'estrelas': self.estrelas,
            'diaria': self.diaria,
            'cidade': self.cidade,
            'site_id': self.site_id
        }

    @classmethod # decorador
    def find_hotel(cls, hotel_id):
        hotel = cls.query.filter_by(hotel_id=hotel_id).first() # Select * FROM hoteis WHERE hotel_id=$hotel_id
        if hotel:
            return hotel
        return None 

    def save_hotel(self):
        # Função para adiconar o próprio objeto ao db
        banco.session.add(self)
        banco.session.commit()

    def update_hotel(self, nome, estrelas, diaria, cidade, site_id):
        # Função para atualizar 
        self.nome = nome
        self.estrelas = estrelas
        self.diaria = diaria
        self.cidade = cidade
        self.site_id = site_id
    
    def delete_hotel(self):
        # Função para excluir o próprio objeto do db
        banco.session.delete(self)
        banco.session.commit()