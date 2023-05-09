from flask_restful import Resource, reqparse
from models.usuario import UserModel
from flask_jwt_extended import create_access_token, jwt_required, get_jwt 
# from werkzeug.security import safe_str_cmp - Importação desatualizada 
import hmac # Módulo que substitui o safe_str_cmp
from blacklist import BLACKLIST
import traceback

atributos = reqparse.RequestParser()
# Criará o usuário com os argumentos
atributos.add_argument('login', type=str, required=True, help="The field 'login' cannot be left blank.")
atributos.add_argument('senha', type=str, required=True, help="The field 'senha' cannot be left blank.")
atributos.add_argument('email', type=str)
atributos.add_argument('ativado', type=bool)

class User(Resource):
    # /usuarios/{user_id} --> Endpoint
    def get(self, user_id):
        # Estabelecendo a variável hotel recebendo a classe Hotel e função de busca
        user = UserModel.find_user(user_id)
        if user:
            return user.json()
        return {'message':'User not found.'}, 404

    @jwt_required() # Necessário o usuário estar logado
    def delete(self, user_id):
        user = UserModel.find_user(user_id)
        if user:
            try:
                user.delete_user()
            except:
                return {'message': 'An error ocurred trying to delete user.'}, 500
            return {'message': 'User deleted.'}
        return {'message': 'User not found.'}, 404

class UserRegister(Resource):
    # /cadastro --> Endpoint
    def post(self):
        # Variável recebendo e reconhecendo os atributos
        dados = atributos.parse_args()
        # Condicionais para verificar a existência do email no db
        if not dados.get('email') or dados.get('email') is None:
            return {'message': "The field 'email'cannot be left blank."}, 400

        if UserModel.find_by_email(dados['email']):
            return {"message": "The email '{}' already exists.".format(dados['email'])}, 400

        if UserModel.find_by_login(dados['login']):
            return {"message": "The login '{}' already exists.".format(dados['login'])}, 400 # bad request 
        
        user = UserModel(**dados) # == UserModel(dados['login'], dados['senha'])
        user.ativado = False
        try:
            user.save_user()
            user.send_confirmation_email()
        except:
            user.delete_user()
            traceback.print_exc()
            return {'message': 'An internal server error has ocurred.'}, 500

        return {'message': 'User created successfully!'}, 201 # Created

class UserLogin(Resource):

    @classmethod
    def post(cls):
        # Variável recebendo e reconhecendo os atributos
        dados = atributos.parse_args()

        user = UserModel.find_by_login(dados['login'])

        if user and hmac.compare_digest(user.senha, dados['senha']):
            if user.ativado:    
                # if user and safe_str_cmp(user.senha, dados['senha']): # Comando desatualizado
                token_de_acesso = create_access_token(identity=user.user_id)
                return {'access_token': token_de_acesso}, 200
            return {'message': 'User not confirmed.'}, 400
        return {'message' : 'The username or password is incorrect.'}, 401 # Unauthorized
    
class UserLogout(Resource):

    # Classe para verificar o lougt do usuário
    @jwt_required()
    def post(self):
        jwt_id = get_jwt()['jti'] # JWT Token Idenfifier
        BLACKLIST.add(jwt_id)
        return {'message': 'logged out successfully!'}, 200

class UserConfirm(Resource):
 
    # Classe para verificar se o usuário está ativo
    ## /confirmacao/{user_id}
    @classmethod
    def get(cls, user_id):
        user = UserModel.find_user(user_id)

        if not user:
            return {"message": "User id '{}' not found.". format(user_id)}, 404
        
        user.ativado = True
        user.save_user()
        return {"message": "User id '{}' confirmed successfully".format(user_id)}, 200