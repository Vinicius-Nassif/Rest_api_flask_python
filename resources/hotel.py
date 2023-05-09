from flask_restful import Resource, reqparse
from models.hotel import HotelModel
from models.site import SiteModel
from resources.filtros import normalize_path_params, consulta_com_cidade, consulta_sem_cidade
from flask_jwt_extended import jwt_required
import sqlite3

# Possíveis parâmetros de consulta
# ex de path /hoteis?cidade=Rio de Janeiro&estrelas_min=4&diaria_max=400
path_params = reqparse.RequestParser()
path_params.add_argument('cidade', type=str, location='args')
path_params.add_argument('estrelas_min', type=float, location='args')
path_params.add_argument('estrelas_max', type=float, location='args')
path_params.add_argument('diaria_min', type=float, location='args')
path_params.add_argument('diaria_max', type=float, location='args')
path_params.add_argument('limit', type=float, location='args')
path_params.add_argument('offset', type=float, location='args')

# Criação da primeira versão do REST
class Hoteis(Resource):
    # Esses hoteis serão o primeiro recurso da API
    def get(self):
        connection = sqlite3.connect('banco.db')
        cursor = connection.cursor()

        # Aplicando compreensão de dicionários para receber dados não nulos
        dados = path_params.parse_args()
        dados_validos = {chave:dados[chave] for chave in dados if dados[chave] is not None}
        # Retornará um dicionário com os parâmetros normalizados ou com o valor default, com ou sem cidade
        parametros = normalize_path_params(**dados_validos)

        if not parametros.get('cidade'):
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_sem_cidade, tupla)
        else: 
            tupla = tuple([parametros[chave] for chave in parametros])
            resultado = cursor.execute(consulta_com_cidade, tupla)
        
        # Interando  sobre o resultado de consulta do banco 
        hoteis = []
        for linha in resultado:
            hoteis.append({
            'hotel_id': linha[0],
            'nome': linha[1],
            'estrelas': linha[2],
            'diaria': linha[3],
            'cidade': linha[4],
            'site_id': linha[5]
            })
        
        return {'hoteis': hoteis}

        # Transformando o objeto em json cada hotel dentro do query.all
        # return {'hoteis': [hotel.json() for hotel in HotelModel.query.all()]} # select * from hoteis

class Hotel(Resource):
    # Estabelecendo argumentos da classe
    argumentos = reqparse.RequestParser()
    # Tornando o campo 'nome' e 'estrelas' obrigatórios
    argumentos.add_argument('nome', type=str, required=True, help="The field 'nome' cannot be left blank.") 
    argumentos.add_argument('estrelas', type=float, required=True, help="The field 'estrelas'cannot be left blank.")
    argumentos.add_argument('diaria')
    argumentos.add_argument('cidade')
    argumentos.add_argument('site_id', type=int, required=True, help="Every hotel needs to be linked with a site.")

    def get(self, hotel_id):
        # Estabelecendo a variável hotel recebendo a classe Hotel e função de busca
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            return hotel.json()
        return {'message':'Hotel not found.'}, 404

    @jwt_required() # Essas operações vão requerer que o usuário esteja logado
    def post(self, hotel_id):
        if HotelModel.find_hotel(hotel_id):
            return {"message": "Hotel id '{}' already exists.".format(hotel_id)}, 400 
        # Variável que recebem chave e valor de todos os argumentos passados
        dados = Hotel.argumentos.parse_args()

        # Variável instancianda com a classe modelo e desembrulhando os dados via kwargs
        hotel = HotelModel(hotel_id, **dados)

        # Condição para caso não seja encontrado pelo id
        if not SiteModel.find_by_id(dados['site_id']):
            return {'message': 'The hotel must be associated to a valid site id.'}, 404
        
        try:
            # Salvar o hotel no db
            hotel.save_hotel()
        except:
            return {'message': 'An internal error ocurred trying to save hotel.'}, 500 # Internal Server Error
        
        return hotel.json(), 201

    @jwt_required()
    def put(self, hotel_id):
        # Pegando os dados através dos argumentos passados
        dados = Hotel.argumentos.parse_args()

        # Encontrar o hotel utilizando a função da classe HotelModel
        hotel_encontrado = HotelModel.find_hotel(hotel_id)

        # Condição para retornar os dados do hotel, atualizar e salvar no db
        if hotel_encontrado:
            hotel_encontrado.update_hotel(**dados)
            hotel_encontrado.save_hotel()
            return hotel_encontrado.json(), 200 # OK
        
        # Variável instancianda com a classe modelo e desembrulhando os dados via kwargs
        hotel = HotelModel(hotel_id, **dados)

        try:
            # Salvar o hotel no db
            hotel.save_hotel()
        except:
            return {'message': 'An internal error ocurred trying to save hotel.'}, 500 # Internal Server Error
        
        return hotel.json(), 201 # criado

    @jwt_required()
    def delete(self, hotel_id):
        hotel = HotelModel.find_hotel(hotel_id)
        if hotel:
            try:
                hotel.delete_hotel()
            except:
                return {'message': 'An error ocurred trying to delete hotel.'}, 500
            return {'message': 'Hotel deleted.'}
        
        return {'message': 'Hotel not found.'}, 404