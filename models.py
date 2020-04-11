from peewee import *

database = PostgresqlDatabase('sentencas', **{'host': 'localhost', 'user': 'postgres', 'password': 'postgres'})

class UnknownField(object):
    def __init__(self, *_, **__): pass

class BaseModel(Model):
    class Meta:
        database = database

class Pais(BaseModel):
    codigo_ddi = CharField(null=True)
    nome = CharField(null=True)

    class Meta:
        table_name = 'pais'

class Regiao(BaseModel):
    nome = CharField(null=True)

    class Meta:
        table_name = 'regiao'

class Estado(BaseModel):
    codigo_ibge = CharField(null=True)
    nome = CharField(null=True)
    pais = ForeignKeyField(column_name='pais_id', field='id', model=Pais, null=True)
    regiao = ForeignKeyField(column_name='regiao_id', field='id', model=Regiao, null=True)
    uf = CharField(null=True)

    class Meta:
        table_name = 'estado'

class Cidade(BaseModel):
    codigo_ibge = CharField(null=True)
    estado = ForeignKeyField(column_name='estado_id', field='id', model=Estado, null=True)
    nome = CharField(null=True)

    class Meta:
        table_name = 'cidade'

class Pessoa(BaseModel):
    cidade = ForeignKeyField(column_name='cidade_id', field='id', model=Cidade, null=True)
    data_nascimento = DateField(null=True)
    nome_principal = CharField(null=True)
    nome_secundario = CharField(null=True)
    pais = ForeignKeyField(column_name='pais_id', field='id', model=Pais, null=True)
    tipo = IntegerField(null=True)

    class Meta:
        table_name = 'pessoa'

class ChaveValor(BaseModel):
    grupo = CharField(null=True)
    valor = CharField(null=True)

    class Meta:
        table_name = 'chave_valor'

class Processo(BaseModel):
    classe = CharField(null=True)
    data_autuacao = DateTimeField(null=True)
    magistrado = ForeignKeyField(column_name='magistrado_id', field='id', model=Pessoa, null=True)
    numero = CharField(null=True)
    sigilo = BooleanField(null=True)
    situacao = ForeignKeyField(column_name='situacao_id', field='id', model=ChaveValor, null=True)

    class Meta:
        table_name = 'processo'

class Cargo(BaseModel):
    nome = CharField(null=True)

    class Meta:
        table_name = 'cargo'

class Orgao(BaseModel):
    nome = CharField(null=True)
    pessoa = ForeignKeyField(column_name='pessoa_id', field='id', model=Pessoa, null=True)

    class Meta:
        table_name = 'orgao'

class UsuarioEproc(BaseModel):
    cargo = ForeignKeyField(column_name='cargo_id', field='id', model=Cargo, null=True)
    nome = CharField(null=True)
    orgao = ForeignKeyField(column_name='orgao_id', field='id', model=Orgao, null=True)
    pessoa = ForeignKeyField(column_name='pessoa_id', field='id', model=Pessoa, null=True)

    class Meta:
        table_name = 'usuario_eproc'

class Evento(BaseModel):
    data_hora = CharField(null=True)
    descricao = CharField(null=True)
    ordem = IntegerField(null=True)
    processo = ForeignKeyField(column_name='processo_id', field='id', model=Processo, null=True)
    tem_arquivo = BooleanField(null=True)
    usuario_eproc = ForeignKeyField(column_name='usuario_eproc_id', field='id', model=UsuarioEproc, null=True)

    class Meta:
        table_name = 'evento'

class Arquivo(BaseModel):
    caminho = CharField(null=True)
    descricao = CharField(null=True)
    evento = ForeignKeyField(column_name='evento_id', field='id', model=Evento, null=True)
    nome = CharField(null=True)
    tipo = IntegerField(null=True)

    class Meta:
        table_name = 'arquivo'

class Documento(BaseModel):
    cidade = ForeignKeyField(column_name='cidade_id', field='id', model=Cidade, null=True)
    estado = ForeignKeyField(column_name='estado_id', field='id', model=Estado, null=True)
    pais = ForeignKeyField(column_name='pais_id', field='id', model=Pais, null=True)
    pessoa = ForeignKeyField(column_name='pessoa_id', field='id', model=Pessoa, null=True)
    principal = BooleanField(null=True)
    registro = CharField(null=True)
    tipo = IntegerField(null=True)

    class Meta:
        table_name = 'documento'

class Endereco(BaseModel):
    bairro = CharField(null=True)
    cep = CharField(null=True)
    cidade = ForeignKeyField(column_name='cidade_id', field='id', model=Cidade, null=True)
    complemento = CharField(null=True)
    logradouro = CharField(null=True)
    numero = CharField(null=True)
    numero_interno = CharField(null=True)
    pessoa = ForeignKeyField(column_name='pessoa_id', field='id', model=Pessoa, null=True)
    tipo_logradouro = IntegerField(null=True)

    class Meta:
        table_name = 'endereco'

class Parte(BaseModel):
    processo = ForeignKeyField(column_name='processo_id', field='id', model=Processo, null=True)
    tipo = IntegerField(null=True)

    class Meta:
        table_name = 'parte'

class PartePessoa(BaseModel):
    parte = ForeignKeyField(column_name='parte_id', field='id', model=Parte, null=True)
    pessoa = ForeignKeyField(column_name='pessoa_id', field='id', model=Pessoa, null=True)

    class Meta:
        table_name = 'parte_pessoa'

class Representante(BaseModel):
    parte_pessoa = IntegerField(column_name='parte_pessoa_id', null=True)
    pessoa = ForeignKeyField(column_name='pessoa_id', field='id', model=Pessoa, null=True)
    tipo = IntegerField(null=True)

    class Meta:
        table_name = 'representante'

class Telefone(BaseModel):
    codigo_ddd = CharField(null=True)
    numero = CharField(null=True)
    pais = ForeignKeyField(column_name='pais_id', field='id', model=Pais, null=True)
    pessoa = ForeignKeyField(column_name='pessoa_id', field='id', model=Pessoa, null=True)
    tipo = IntegerField(null=True)

    class Meta:
        table_name = 'telefone'
