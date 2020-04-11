from eyes import Eyes
import pprint

e = Eyes()
e.auth()

e.searchProcesso("5002074-02.2015.404.7005")
# e.acessarIntegra()
# e.exibirTodosEventos()
# print(e.getAdicionais())
# teste = e.getCapa()
# print(teste)
# e.getAssuntos()
# print(e.getPartes())
# eventos = e.getEventos()
# pprint.pprint(eventos)
# for ev in eventos:
# 	# pprint.pprint(ev['documentos'])
# 	if ev['documentos']:
# 		for doc in ev['documentos']:
# 			if doc['tipo'] == 'html':
# 				e.download_html(doc['url'], doc['nome'])
# 			elif doc['tipo'] == 'pdf':
# 				e.download_pdf(doc['url'], doc['nome'])
# 				input("Press Enter to continue...")
# 			# doc[]
e.close()
