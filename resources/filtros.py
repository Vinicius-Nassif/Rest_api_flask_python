## Função para normalizar os dados passados via parâmetros de consulta 
# Receber dados que tenham chave e valor
def normalize_path_params(cidade=None, 
                        estrelas_min = 0,
                        estrelas_max = 5,
                        diaria_min = 0,
                        diaria_max = 10000,
                        limit = 50,
                        offset = 0, **dados):
    if cidade: 
        return {
            'estrelas_min' : estrelas_min,
            'estrelas_max' : estrelas_max,
            'diaria_min' : diaria_min,
            'diaria_max' : diaria_max,
            'cidade' : cidade,
            'limit' : limit,
            'offset': offset
        }
    return {
            'estrelas_min' : estrelas_min,
            'estrelas_max' : estrelas_max,
            'diaria_min' : diaria_min,
            'diaria_max' : diaria_max,
            'limit' : limit,
            'offset': offset
        }

# Variáveis referentes as consultas do método get
# hotel.py(resources) - Class Hoteis 
consulta_sem_cidade = "SELECT * FROM hoteis \
                WHERE (estrelas >= ? and estrelas <= ?) \
                and (diaria >= ? and diaria <= ?) \
                LIMIT ? OFFSET ?"

consulta_com_cidade = "SELECT * FROM hoteis \
                WHERE (estrelas >= ? and estrelas <= ?) \
                and (diaria >= ? and diaria <= ?) \
                and cidade = ? LIMIT ? OFFSET ?"