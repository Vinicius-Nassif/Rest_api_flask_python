from sql_alchemy import banco

class SiteModel(banco.Model):
    # Classe modelo para representar o site
    ## Ter todas as cofigurações que determina que será uma tabela em um db
    ## Cada atributo do modelo seja uma coluna no db - Mapeamento
    __tablename__ = 'sites'

    site_id = banco.Column(banco.Integer, primary_key=True)
    url = banco.Column(banco.String(80))
    # Criando relacionamento com a classe 
    hoteis = banco.relationship('HotelModel') # Lista de objetos hoteis

    def __init__(self, url):
        # Somente a url será passada como argumento na criação
        ## o ID será criado automaticamente, pois é uma chave primária e nulo 
        self.url = url
    
    def json(self):
        # Transforma o objeto em dicionário formato json
        return {
            'site_id': self.site_id,
            'url': self.url,
            'hoteis': [hotel.json() for hotel in self.hoteis]
        }

    @classmethod # decorador
    def find_site(cls, url):
        site = cls.query.filter_by(url=url).first() # Select * FROM hoteis WHERE hotel_id=$hotel_id
        if site:
            return site
        return None 
    
    @classmethod # decorador
    def find_by_id(cls, site_id):
        site = cls.query.filter_by(site_id=site_id).first() # Select * FROM hoteis WHERE hotel_id=$hotel_id
        if site:
            return site
        return None 

    def save_site(self):
        # Função para adiconar o próprio objeto ao db
        banco.session.add(self)
        banco.session.commit()
    
    def delete_site(self):
        # Função para excluir o próprio objeto do db
        # Deletando todos os hoteis associados ao site
        [hotel.delete_hotel() for hotel in self.hoteis]
        # Deletando site
        banco.session.delete(self)
        banco.session.commit()