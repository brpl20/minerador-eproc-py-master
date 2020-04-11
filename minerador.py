from eyes import Eyes
import os
import time
import shutil

class Minerador(object):
	"""docstring for Minerador."""
	def __init__(self, eyes):
		self.eyes = eyes
		self.temp_dir = 'temp_files/'
		self.files_path = 'arquivos/'
		self.processo_dir = ''

	def get_data(self):
		return {
			'capa' : self.eyes.getCapa(),
			'assuntos' : self.eyes.getAssuntos(),
			'adicionais' : self.eyes.getAdicionais(),
			'partes' : self.eyes.getPartes(),
			'eventos' : self.eyes.getEventos()
		}

	def get_processo(self, processo):
		self.processo_dir = os.path.abspath(self.files_path + processo)
		try:
			os.mkdir(self.processo_dir)
		except Exception as e:
			pass
		self.eyes.searchProcesso(processo)
		self.eyes.acessarIntegra()
		self.eyes.exibirTodosEventos()

	def get_files(self, eventos):
		for ev in eventos:
			if ev['documentos']:
				for doc in ev['documentos']:
					if doc['tipo'] == 'html':
						self.eyes.download_html(doc['url'], doc['nome'])
					elif doc['tipo'] == 'pdf':
						self.eyes.download_pdf(doc['url'], doc['nome'])

	""" Move arquivos temporarios para a pasta do processo. Observe que não pode ter arquivos na pasta temporário """
	def move_files(self):
		files_list = os.listdir(os.path.abspath(self.temp_dir))
		incompleto = False
		for f in files_list:
			if f.find('crdownload') > 0:
				incompleto = True
				continue
			try:
				shutil.move(os.path.abspath(self.temp_dir + '/' + f), os.path.abspath(self.processo_dir))
			except Exception as e:
				print("Falha ao mover arquivo")
				print(e)
				pass
		if incompleto:
			time.sleep(10)
			self.move_files()
