from flask import Flask, jsonify
from flask_restful import Api
from resources.hotel import Hoteis, Hotel
from resources.usuario import User, UserRegister, UserLogin, UserLogout, UserConfirm
from resources.site import Site, Sites
from flask_jwt_extended import JWTManager
from blacklist import BLACKLIST
from key import key

app = Flask(__name__)
# Estabelecendo configurações (definindo o caminho e nome)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/Vinicius/Documents/Projetos AD/Rest_api_flask_python/banco.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = key 
app.config['JWT_BLACKLIST_ENABLED'] = True # Ativando a lista negra

api = Api(app)
# Variável para auxíliar o recebimento do token_de_acesso (resources.usuario)
jwt = JWTManager(app)

# Função com um  decorador
# Antes da primeira requisição vai verificar se já existe a tabela
@app.before_first_request
def cria_banco():
    # Criar automaticamente um banco e todas as tabelas
    banco.create_all()

# Determinando que a função verifique se o token está ou não na blacklist
@jwt.token_in_blocklist_loader 
def verifica_blacklist(self, token):
    return token['jti'] in BLACKLIST

@jwt.revoked_token_loader
def token_de_acesso_invalidado(jwt_header, jwt_payload):
    # Converte um dicionário para json
    return jsonify({'message': 'You have been logged out.'}), 401 # unauthorized

## Endpoints
# Adicionando os recursos dos hotéis
api.add_resource(Hoteis, '/hoteis')
api.add_resource(Hotel, '/hoteis/<string:hotel_id>')
# Adicionando os recursos dos usuários
api.add_resource(User, '/usuarios/<int:user_id>')
api.add_resource(UserRegister, '/cadastro')
# Adicionando os recursos de login
api.add_resource(UserLogin, '/login')
# Adicionando os recursos de logout
api.add_resource(UserLogout, '/logout')
# Adicionando os recursos de sites
api.add_resource(Sites, '/sites')
api.add_resource(Site, '/sites/<string:url>')
# Adicionando os recursos de confirmação de usuário
api.add_resource(UserConfirm, '/confirmacao/<int:user_id>')

# http://127.0.0.1:5000/hoteis

if __name__=='__main__':
    # Importação realizada neste local para apenas ocorrer com a execução desse arquivo
    from sql_alchemy import banco
    banco.init_app(app)
    app.run(debug=True)