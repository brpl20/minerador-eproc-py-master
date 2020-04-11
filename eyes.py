from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from multiprocessing import Process
import pprint
import os
class Eyes(object):
	def __init__(self, hide=False):
		self.temp_dir = 'temp_files'
		self.positionPartes = -1
		self.url_principal = ''
		opts = webdriver.ChromeOptions()
		opts.set_headless(hide)
		
		prefs = {
			"download.default_directory" : os.path.abspath(self.temp_dir),
			"plugins.plugins_disabled" : "Chrome PDF Viewer",
			"download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True,
		}
		opts.add_experimental_option("prefs",prefs)

		self.driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", chrome_options=opts)
		# self.driver = webdriver.Chrome(executable_path="./chromedriver", chrome_options=opts)
		self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
		params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': os.path.abspath(self.temp_dir)}}
		command_result = self.driver.execute("send_command", params)
		# self.driver.set_window_size(900, 750)

	def auth(self):
		self.driver.get("https://eproc.jfpr.jus.br/eprocV2/externo_controlador.php?acao=principal")
		elem = self.driver.find_element_by_name("txtUsuario")
		elem.send_keys("xxxPASS")
		elem = self.driver.find_element_by_name("pwdSenha")
		elem.send_keys("xxxPASS")
		elem.send_keys(Keys.RETURN)
		time.sleep(4)
		self.url_principal = self.driver.current_url

	def takeSs(self):
		name = str(int(time.time()))
		self.driver.save_screenshot("screenshots/{}.png".format(name))

	def close(self):
		self.driver.close()

	def getDriver(self):
		return self.driver

	def check_url_principal(self):
		if self.url_principal != self.driver.current_url:
			self.driver.get(self.url_principal)

	def searchProcesso(self, num):
		self.check_url_principal()
		elem = self.driver.find_element_by_id("txtNumProcessoPesquisaRapida")
		elem.send_keys(num)
		elem.send_keys(Keys.RETURN)
		time.sleep(5)

	def acessarIntegra(self):
		try:
			elem = self.driver.find_element_by_link_text("Acesso íntegra do processo")
		except Exception as e:
			return
		self.driver.get(elem.get_attribute("href"))
		alert = WebDriverWait(self.driver, 10).until(EC.alert_is_present())
		alert.accept()

	def exibirTodosEventos(self):
		try:
			self.driver.execute_script("carregarTodasPaginas();")
			time.sleep(5)
		except Exception as e:
			pass

	def getCapa(self):
		return {
			"data_autuacao" 	: self.driver.find_element_by_id("txtAutuacao").text.strip(),
			"situacao" 			: self.driver.find_element_by_id("txtSituacao").text.strip(),
			"orgao_julgador" 	: self.driver.find_element_by_id("txtOrgaoJulgador").text.strip(),
			"magistrado" 		: self.driver.find_element_by_id("txtMagistrado").text.strip(),
			"competencia" 		: self.driver.find_element_by_id("txtCompetencia").text.strip(),
			"classe" 			: self.driver.find_element_by_id("txtClasse").text.strip(),
		}

	def getAssuntos(self):
		self.driver.execute_script("infraAbrirFecharElementoHTML('conteudoAssuntos2', 'imgStatusAssunto');")
		trs = self.driver.find_elements_by_css_selector("#conteudoAssuntos2 table tbody tr")
		assuntos = []
		for tr in trs:
			try:
				tds = tr.find_elements_by_tag_name("td")
				assunto = {
					'codigo' 	: tds[0].text.strip(),
					'descricao' : tds[1].text.strip(),
					'tipo' 		: tds[2].text.strip(),
					'principal' : tds[3].text.strip(),
				}
				assuntos.append(assunto)
			except Exception as e:
				continue
		return assuntos

	def getAdicionais(self):
		self.driver.execute_script("infraAbrirFecharElementoHTML('conteudoInfAdicional', 'imgStatusInfAdicional');")
		self.driver.execute_script("adicionaRemoveLabelInfAdicional();")
		trs = self.driver.find_elements_by_css_selector('#conteudoInfAdicional table tbody tr')
		infos = {}
		for tr in trs:
			isTitle = True
			title = ''
			tds = tr.find_elements_by_tag_name("td")
			for td in tds:
				if isTitle:
					try:
						title = td.find_element_by_tag_name('label').text
					except Exception as e:
						try:
							title = td.find_element_by_tag_name('a').text
						except Exception as e:
							pass
						pass
					try:
						title = title.replace("&nbsp;", "").strip(':').strip()
					except Exception as e:
						pass
					isTitle = False
				else:
					try:
						infos[title] = td.find_element_by_tag_name('label').text
					except Exception as e:
						try:
							infos[title] = td.find_element_by_tag_name('a').text
						except Exception as e:
							pass
						pass
					try:
						infos[title] = infos[title].replace("&nbsp;", "").strip()
					except Exception as e:
						pass
					isTitle = True
		return infos

	def getPartes(self):
		trs = self.driver.find_elements_by_css_selector('#fldPartes table tbody tr')

		partes = [
			{
				'tipo' 		: 'AUTOR',
				'pessoas' 	: self.getAutores(trs)
			},
			{
				'tipo' 		: 'RÉU',
				'pessoas' 	: self.getReu(trs[1])
			}
		]
		outras = self.getOutrasPartes(trs)
		partes = partes + outras
		return partes

	def getAutores(self, trs):
		autores = []
		for tr in trs:
			self.positionPartes += 1
			if self.positionPartes == 0:
				continue
			cols = tr.find_elements_by_css_selector("*")
			if cols[0].tag_name == 'th':
				break
			autores.append(self.getPessoasParte(cols[0].text))
		return autores

	def getPessoasParte(self, content):
		pessoa = {
			'nome' 			: '',
			'tipo' 			: '',
			'documento' 	: '',
			'representantes' : []
		}
		pessoas = content.split("\n")
		aux = pessoas[0].replace("&nbsp;", "").split('(')
		pessoa['nome'] = aux[0].strip()
		aux = aux[1].split(' - ')
		pessoa['tipo'] = aux[1].strip()
		pessoa['documento'] = aux[0].replace(')', '').strip()
		for i in range(1, len(pessoas)):
			if pessoas[i].strip():
				aux = pessoas[i].replace("&nbsp;", " ")
				aux2 = aux.strip().split(' ')
				usuario = aux2[len(aux2)-1]
				pessoa['representantes'].append({
					'nome' 		: aux.replace(usuario, '').strip(),
					'usuario' 	: usuario.strip()
				})
		return pessoa

	def getOutrasPartes(self, trs):
		partes = []
		title = ''
		for i in range(self.positionPartes, len(trs)):
			col = trs[i].find_elements_by_css_selector("*")[0]
			if col.tag_name == 'th':
				title = col.text.strip()
			if col.tag_name == 'td':
				partes.append({'tipo' : title, 'pessoas' : [self.getPessoasParte(col.text)]})
		return partes

	def getReu(self, content):
		pessoas = []
		tds = content.find_elements_by_tag_name('td')
		pessoas.append(self.getPessoasParte(tds[1].text))
		return pessoas

	def getEventos(self):
		eventos = []
		tbs = self.driver.find_elements_by_css_selector('#tblEventos tbody')
		for tb in tbs:
			trs = tb.find_elements_by_tag_name('tr')
			for tr in trs:
				tds = tr.find_elements_by_tag_name('td')
				evento = {
					'ordem' 		: tds[0].text.replace('&nbsp', '').strip(),
					'data_hora' 	: tds[1].text.strip(),
					'descricao' 	: tds[2].text.strip(),
					'usuario'		: {
						'usuario' 		: tds[3].text,
						'nome' 			: tds[3].text
					},
					'documentos' 	: []
				}
				try:
					aux = tds[3].find_element_by_tag_name('label').get_attribute('onmouseover')
					aux = aux.replace("return carregarInfoUsuario('", "").replace("');", "")
					usuario = aux.split('<br>')
					evento['usuario']['nome']	= usuario[0]
					evento['usuario']['cargo'] 	= usuario[1] if len(usuario) > 1 else ''
					evento['usuario']['orgao'] 	= usuario[2] if len(usuario) > 2 else ''
				except Exception as e:
					pass
					
				try:
					btn = tds[4].find_element_by_tag_name('input')
					btn.click()
				except Exception as e:
					pass
				try:
					aux = tds[4].find_elements_by_tag_name('a')
					docs = []
					for doc in aux:
						docs.append({
							'tipo'		: doc.get_attribute('data-mimetype'),
							'url' 		: doc.get_attribute('href'),
							'descricao' : doc.get_attribute('title').strip(),
							'nome' 		: doc.text.strip(),
						})
					evento['documentos'] = docs
				except Exception as e:
					pass
				eventos.append(evento)
		return eventos

	def download_html(self, url, name):
		self.driver.get(url)
		file_object = open(os.path.abspath('temp_files/'+name+'.html'), "w")
		html = ''

		try:
			iframe = self.driver.find_element_by_tag_name('iframe')
			url_original = iframe.get_attribute('src').replace('&amp;', '&')
			self.driver.get(url_original)
			html = self.driver.page_source
		except Exception as e:
			pass

		try:
			divhtml = self.driver.find_element_by_id('divdochtml')
			html = divhtml.get_attribute('innerHTML')
		except Exception as e:
			pass

		file_object.write(html)
		file_object.close()

	def download_pdf(self, url, name):
		self.driver.get(url)

	def reset(self):
		self.positionPartes = -1

	def logout(self):
		self.check_url_principal()
		self.driver.find_element_by_id('lnkSairSistema').click()
		time.sleep(5)
