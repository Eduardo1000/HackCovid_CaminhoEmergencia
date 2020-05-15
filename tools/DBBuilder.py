import os
import pandas as pd


class DBBuilder:
    def __init__(self, data_folder):
        self.data_folder = data_folder

    def load(self):
        """
        Carrega as tabelas necessárias e Retorna um Dataset
        """
        join_key = 'CO_UNIDADE'

        # CARREGA AS INFORMAÇÕES DO NÚMERO DE LEITOS
        columns = ['CO_LEITO', 'CO_TIPO_LEITO', 'QT_EXIST', 'QT_SUS']
        leitos = pd.read_csv(os.path.join(self.data_folder, 'rlEstabComplementar202003.csv'), sep=';')
        leitos = leitos.set_index(join_key)[columns]
        # FILTRA OS TIPOS DE LEITO
        columns = ["CO_LEITO", "DS_LEITO"]
        tipos_leito_escolhidos = ["51", "52", "74", "75", "76", "46", "34", "49"]
        tipo_leito_key = 'CO_LEITO'
        tipo_leitos = pd.read_csv(os.path.join(self.data_folder, 'tbLeito202003.csv'), sep=';')
        tipo_leitos = tipo_leitos[columns].set_index(tipo_leito_key)
        leitos = leitos[leitos[tipo_leito_key].isin(tipos_leito_escolhidos)]
        leitos = leitos.join(tipo_leitos, on=tipo_leito_key, lsuffix='_').drop(
            columns=[tipo_leito_key])

        # CARREGA AS INFORMAÇÕES DO ESTABELECIMENTO
        columns = ['CO_CNES', 'NO_FANTASIA', 'NO_LOGRADOURO', 'NU_ENDERECO', 'NO_COMPLEMENTO', 'NO_BAIRRO', 'CO_CEP',
            'NU_LATITUDE', 'NU_LONGITUDE', 'NU_TELEFONE', 'TP_UNIDADE', 'CO_MUNICIPIO_GESTOR',
            'TP_ESTAB_SEMPRE_ABERTO', 'CO_TIPO_ESTABELECIMENTO', 'CO_ATIVIDADE_PRINCIPAL']
        estabelecimentos = pd.read_csv(os.path.join(self.data_folder, 'tbEstabelecimento202003.csv'), sep=';')
        estabelecimentos = estabelecimentos.set_index(join_key)[columns]
            # SELECIONA APENAS O MUNICIPIO DO RIO DE JANEIRO
        estabelecimentos = estabelecimentos.loc[estabelecimentos['CO_MUNICIPIO_GESTOR'] == 330455].drop(
            columns=['CO_MUNICIPIO_GESTOR'])
        # CARREGA OS TIPOS DE ESTABELECIMENTO
        columns = ["CO_TIPO_ESTABELECIMENTO", "DS_TIPO_ESTABELECIMENTO"]
        key_tipo = "CO_TIPO_ESTABELECIMENTO"
        tipo_estabelecimentos = pd.read_csv(os.path.join(self.data_folder, 'tbTipoEstabelecimento202003.csv'), sep=';')
        tipo_estabelecimentos = tipo_estabelecimentos[columns].set_index(key_tipo)
        estabelecimentos = estabelecimentos.join(tipo_estabelecimentos, on='CO_TIPO_ESTABELECIMENTO', lsuffix='_').drop(
            columns=[key_tipo]
        )
        # FILTRA OS ESTABELECIMENTOS DE INTERESSE
        EXCLUDE_COLUMNS = [
            "CENTRAL DE GESTAO EM SAUDE", "CENTRAL DE REGULACAO", "CENTRAL DE ABASTECIMENTO",
            "CENTRAL DE TRANSPLANTE", "CENTRO DE ASSISTENCIA OBSTETRICA E NEONATAL NORMAL", "FARMACIA",
            "UNIDADE DE ATENCAO HEMATOLOGICA E/OU HEMOTERAPICA", "UNIDADE DE ATENCAO PSICOSSOCIAL",
            "UNIDADE DE APOIO DIAGNOSTICO","UNIDADE DE TERAPIAS ESPECIAIS", "LABORATORIO DE PROTESE DENTARIA",
            "UNIDADE DE VIGILANCIA DE ZOONOSES","LABORATORIO DE SAUDE PUBLICA",
            "CENTRO DE REFERENCIA EM SAUDE DO TRABALHADOR","SERVICO DE VERIFICACAO DE OBITO","CENTRO DE IMUNIZACAO"]
        estabelecimentos = estabelecimentos[~estabelecimentos['DS_TIPO_ESTABELECIMENTO'].isin(EXCLUDE_COLUMNS)]

        # Concatena os dados
        dataframe = estabelecimentos.join(leitos, on='CO_UNIDADE', lsuffix='_tb')
        save_path = os.path.join(self.data_folder, 'dataset')
        os.makedirs(save_path, exist_ok=True)
        dataframe.to_csv(os.path.join(save_path, 'datasus.csv'))
