#!/usr/bin/env python3
from datetime import datetime
from models import *
from eyes import Eyes
from minerador import Minerador
import os
import time


eyes = Eyes(True)
eyes.auth()
miner = Minerador(eyes)
reauth_in = 10
aux_reauth = 1

processos = Processo.select().where(Processo.data_autuacao == None)
for processo in processos.iterator(database):
	sigilo = True
	print('{} Obtendo {}'.format(datetime.now(), processo.numero))
	try:
		miner.get_processo(processo.numero)
		data = miner.get_data()
		miner.get_files(data['eventos'])
	except Exception as e:
		print('Falha ao obter dados do processo: {} \n e: {}'.format(processo.numero, str(e)))
		eyes.takeSs()
		print('Screenshot salva')
		continue

	try:
		for k, v in data['adicionais'].items():
			if k.find('Sigilo') >= 0 and v.find('Sem Sigilo') >= 0:
				sigilo = False
	except Exception as e:
		continue

	try:
		situacao, created = ChaveValor.get_or_create(valor=data['capa']['situacao'], grupo='SITUACAO_PROCESSO')
		magistrado, created = Pessoa.get_or_create(nome_principal=data['capa']['magistrado'])

		processo.data_autuacao = datetime.strptime(data['capa']['data_autuacao'], '%d/%m/%Y %H:%M:%S')
		processo.classe = data['capa']['classe']
		processo.situacao_id = situacao.id
		processo.magistrado_id = magistrado.id
		processo.sigilo = sigilo
		processo.save()
	except Exception as e:
		print('Falha ao salvar dados do processo: {} \n e: {}'.format(processo.numero, str(e)))
		eyes.takeSs()
		print('Screenshot salva')
		pass

	if sigilo:
		print('Processo em sigilo. Pulado.')
		continue

	try:
		for _parte in data['partes']:
			tipo_parte, created = ChaveValor.get_or_create(valor=_parte['tipo'], grupo='TIPO_PARTE')
			parte = Parte.create(tipo=tipo_parte.id, processo_id=processo.id)
			for _pessoa in _parte['pessoas']:
				pessoa = None
				doc, created = Documento.get_or_create(registro=_pessoa['documento'], principal=True)
				if created:
					tipo_pessoa, created = ChaveValor.get_or_create(valor=_pessoa['tipo'], grupo='TIPO_PESSOA')
					pessoa = Pessoa.create(
						nome_principal=_pessoa['nome'],
						tipo=tipo_pessoa.id
					)
					doc.pessoa_id = pessoa.id
					doc.save()

				parte_pessoa = PartePessoa.create(
					pessoa_id = doc.pessoa_id,
					parte_id = parte.id
				)

				try:
					for _representante in _pessoa['representantes']:
						usuario_eproc, created = UsuarioEproc.get_or_create(nome=_representante['usuario'])
						if created:
							pessoa = Pessoa.create(
								nome_principal=_pessoa['nome']
							)
							usuario_eproc.pessoa_id = pessoa.id
							usuario_eproc.save()
						representante = Representante.create(
							parte_pessoa_id = parte_pessoa.id,
							pessoa_id = usuario_eproc.pessoa_id
						)
				except Exception as e:
					print('Falha ao salvar dados do representante: {} \n e: {}'.format(processo.numero, str(e)))
					pass
	except Exception as e:
		pass

	try:
		for _evento in data['eventos']:
			usuario_eproc, created = UsuarioEproc.get_or_create(
				nome=_evento['usuario']['usuario']
			)
			if 'orgao' in _evento['usuario']:
				orgao, ignored = Orgao.get_or_create(nome=_evento['usuario']['orgao'])
				usuario_eproc.orgao_id = orgao.id
			if 'cargo' in _evento['usuario']:
				cargo, ignored = Cargo.get_or_create(nome=_evento['usuario']['cargo'])
				usuario_eproc.cargo_id = cargo.id
			usuario_eproc.save()
			
			if created:
				pessoa = Pessoa.create(
					nome_principal=_evento['usuario']['nome']
				)
				usuario_eproc.pessoa_id = pessoa.id
				usuario_eproc.save()
			evento = Evento.create(
				ordem 		= _evento['ordem'],
				data_hora 	= _evento['data_hora'],
				descricao 	= _evento['descricao'],
				tem_arquivo 	= True if _evento['documentos'] else False,
				processo_id 	= processo.id,
				usuario_eproc_id = usuario_eproc.id
			)
	except Exception as e:
		print('Falha ao salvar eventos: {} \n e: {}'.format(processo.numero, str(e)))
		pass

	try:
		miner.move_files()
	except Exception as e:
		print('Há downloads incompletos, certifique-se da conexão com a internet. Tentando novamente mover arquivos.')
		miner.move_files()
		pass

	eyes.reset()

	# if reauth_in == aux_reauth:
	# 	eyes.logout()
	# 	eyes.auth()
	# 	aux_reauth = 1
	# else:
	# 	aux_reauth += 1

	# time.sleep(60)
eyes.close()