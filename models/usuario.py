from sql_alchemy import banco
from flask import request, url_for
from requests import post
from key import MAILGUN_API_KEY, MAILGUN_DOMAIN, FROM_EMAIL, FROM_TITLE

class UserModel(banco.Model):
    # Classe modelo para representar os usuários
    ## Ter todas as cofigurações que determina que será uma tabela em um db
    ## Cada atributo do modelo seja uma coluna no db - Mapeamento
    __tablename__ = 'usuarios'

    user_id = banco.Column(banco.Integer, primary_key=True)
    login = banco.Column(banco.String(40), nullable=False, unique=True)
    senha = banco.Column(banco.String(40), nullable=False)
    email = banco.Column(banco.String(80), nullable=False, unique=True)
    ativado = banco.Column(banco.Boolean, default=False)

    def __init__(self, login, senha, email, ativado):
        # Receberá apenas como parâmetros o 'login' e 'senha' para o ID ficar nulo
        # Automaticamente o sqlalchemy vai autoincrementar o ID, por este ser int e PK
        self.login = login
        self.senha = senha
        self.email = email
        self.ativado = ativado
    
    def send_confirmation_email(self):
        # http://127.0.0.1:5000/confirmacao/{user_id}
        link = request.url_root[:-1] + url_for('userconfirm', user_id=self.user_id)
        return post(
            'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN),
            auth=('api', MAILGUN_API_KEY),
            data={'from': '{} <{}>'.format(FROM_TITLE, FROM_EMAIL),
                'to': self.email,
                'subject': 'Confirmação de Cadastro',
                'text': 'Confirme seu cadastro clicando no link a seguir: {}'.format(link),
                'html': '<html><p>\
                Confirme seu cadastro clicando no link a seguir: <a href="{}">CONFIRMAR EMAIL</a>\
                </p></html>'.format(link)
                }
            )
    
    def json(self):
        # Transforma o objeto em dicionário formato json
        # Não será emitida a senha
        return {
            'user_id': self.user_id,
            'login': self.login,
            'email': self.email,
            'ativado': self.ativado
            }

    @classmethod # decorador
    def find_user(cls, user_id):
        user = cls.query.filter_by(user_id=user_id).first() # Select * FROM hoteis WHERE hotel_id=$hotel_id
        if user:
            return user # retornar um objeto 'user'
        return None 

    @classmethod
    def find_by_email(cls, email):
        user = cls.query.filter_by(email=email).first() # Select * FROM hoteis WHERE hotel_id=$hotel_id
        if user:
            return user # retornar um objeto 'user'
        return None 
    
    @classmethod
    def find_by_login(cls, login):
        user = cls.query.filter_by(login=login).first() # Select * FROM hoteis WHERE hotel_id=$hotel_id
        if user:
            return user # retornar um objeto 'user'
        return None 
    
    def save_user(self):
        # Função para adiconar o próprio objeto ao db
        banco.session.add(self)
        banco.session.commit()
    
    def delete_user(self):
        banco.session.delete(self)
        banco.session.commit()