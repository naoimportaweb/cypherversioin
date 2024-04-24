#!/usr/bin/python3
import requests, json, os, base64, glob, hashlib, traceback, getpass;

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad

#   autor nao importa cara!!!
#   cyberframework.com.br
#   nao.importa.web@xmpp.jp
#   Toda GAMBIARRA eu posso pois o código é meu
#   COMEÇA LENDO O MÉTODO MAIN QUE ESTÁ NO FINAL DO ARQUIVO.

key = None;
MAX_OP = 10; # Número máximo de download (arquivos) por requisição

class Util:
    @staticmethod
    def encrypt(raw, key):
        raw = pad(raw.encode(),16)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw))
    @staticmethod
    def encryptbinary(raw, key):
        raw = pad(raw,16)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw))
    @staticmethod
    def decrypt(enc, key):
        enc = base64.b64decode(enc)
        cipher = AES.new(key.encode('utf-8'), AES.MODE_ECB)
        return unpad(cipher.decrypt(enc),16)
    @staticmethod
    def md5(fname):
        if not os.path.exists(fname):
            return "";
        hash_md5 = hashlib.md5()
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

class Server:
    def __init__(self, url, key):
        self.url_service = url;
        self.key = key;

    def post(self, url, data_raw):
        global key;
        data = Util.encrypt(data_raw, self.key);
        retorno = requests.post(self.url_service + url, data = data, headers= {'Content-Type': 'text/plain'});
        return Util.decrypt(  retorno.text, self.key ).decode('utf-8');

class Project:
    def __init__(self, name, path_project, server):
        global key;
        self.name = Util.encrypt(name, key).decode('utf-8');
        self.path_project = path_project;
        self.server = server;
        self.files = [];

    # Limpa a lista de arquivos, usado quando queremos limpar tudo e iniciar subindo novamente os arquivos 
    #       como estão, é uma forma de forçar uma nova versão toda como está em seu computador
    def flush(self): 
        self.files = [];
    
    # Atualiza a lista de arquivos que tem lá no servidor em um arquivo JSON com todos os arquivos, isso fica na
    #       memória, então não é presistido em lugar nenhum.
    def listdir(self):
        self.files = []; self.commits = [];
        return_list = self.server.post("list.php",  json.dumps({"cypher_version" : "1", "action_version" : "1", "project" : self.name}));
        
        # Se não existe nada lá no servidor, ou seja, nem o projeto (quando é novo projeto)
        #    ele retorna True e não coloca nada como commits nem files.
        if return_list == None or json.loads(   return_list   ) ['files'] == None:
            return True;

        # Exibe como output o numero de arquivos e quantos comits foram realizados
        print("Files:\t\t" , len(json.loads(   return_list   ) ['files']));
        print("Commits\t\t", len(json.loads(   return_list   ) ['commits']));
        
        # Atualzia as variaveis em memória com o que vem do servidor
        self.files = json.loads(   return_list   ) ['files'];
        self.commits = json.loads(   return_list   ) ['commits'];

        return True;
    
    #  Busca a versão atual do arquivo no servidor, e extrai dele as informações de versão e MD5
    #       é utilizado para depois comprar se o arquivo local é diferente do arquivo remoto por MD5
    def info_file(self, file_name):
        global key;
        envelop = json.dumps({"cypher_version" : "1", "action_version" : "1", "project" : self.name, "name" : file_name });
        request_result = json.loads( self.server.post("info_file.php", envelop )  );
        return request_result;

    # Download em sí de um arquivo único e específico
    def download_file(self, file_name, version=""):
        global key;
        
        envelop = json.dumps({"cypher_version" : "1", "action_version" : "1", "project" : self.name, "name" : file_name, "version" : version });
        request_result = json.loads( self.server.post("download_file.php", envelop )  );
        
        name_file = Util.decrypt( json.loads(request_result['info'])['name'] , key   ).decode('utf-8');
        buffer_name = self.path_project + "/" + name_file; # No servidor não se pode guardar info de diretório da máquina do programador
                                                           #         e nem no cliente guardar path completo de servidor, então tem que dar um join
        buffer_path = buffer_name[:buffer_name.rfind("/")];# Tendo o diretório completo (fullpath) do arquivo na maquina do cliente
                                                           #         então temos que pegar o diretório 
        
        # se no local não existe os diretórios, então vamos criar os diretórios para depois salvar o arquivo.
        if not os.path.exists(buffer_path):
            os.makedirs(buffer_path, exist_ok=True)
        
        # a escrita/leitura dos arquivos é no formato binário.
        with open(buffer_name, "wb") as f:
            f.write( Util.decrypt(    request_result['content'], key   ) );
            f.close()
        
        return  request_result["status"] == "1"; 
    
    # Download de uma lista de arquivos.
    def download_files(self, elements):
        global key;

        #se não tem arquivos, pula fora
        if elements == None or len(elements) == 0:
            return True;

        envelop = json.dumps({"cypher_version" : "1", "action_version" : "1", "project" : self.name, "files" : elements });
        request_result = json.loads( self.server.post("download_files.php", envelop )  );
        
        # Laço de repetição nos arquivos
        for i in range( len(request_result['files']) ):
            
            # Decripta o nome do arquivo, todos os nomese de arquivos no servidor estão criptografados
            #    nem o nome dos diretórios, lã n o server os arquivos ficam em lista, nem em árvore ficam para
            #    nao expor a estrutura do projeto.
            name_file = Util.decrypt( json.loads(request_result['files'][i]['info'])['name'] , key   ).decode('utf-8');
            buffer_name = self.path_project + "/" + name_file;   # junta como path do projeto
            buffer_path = buffer_name[:buffer_name.rfind("/")];  # pega o diretório.

            if not os.path.exists(buffer_path):
                os.makedirs(buffer_path, exist_ok=True)
            
            # tanto leitura quanto escrita estão no formato binário
            with open(buffer_name, "wb") as f:
                f.write( Util.decrypt(    request_result['files'][i]['content'], key   ) );
                f.close()
        return  request_result["status"] == "1"; 

    # A idẽia do revert é voltar um envio (upload) d o projeto que foi feito no passado, geralmente usado quando fazemos cagada
    #    e não percebemos imediatamente, então podemos voltar um commit anterior, ou muito anterior.
    def revert(self):

        # busca a lista de arquivos que estão diferentes. Não podemos deixar passar, o usuáŕio deve remover os aruqivos
        #     pois se o cver fizer isso e a pessoa não gostar depois, nao tem como encher nosso saco por um erro dele.
        files_diff = self.changed_files();
        if len(files_diff) > 0:
            print('ATENÇÃO: Existe arquivos alterados no seu computador e por isso não será feito o revert, faça o UPLOAD de tudo para depois realizar o REVERT');
            return;

        # se passou podemos então baixar a lista de commits e exibir na tela
        #      NUMERO - DESCRIÇÃO DO COMMIT
        # temos que perguntar qual o numero do commit
        self.commit_list();
        postion_commit = input('Qual o número do commit: ');
        
        # limpa tudo, tudo mesmo, pode ter coisas que não estao na lista, DEIXAR O DIRETÓRIO ZERO BALA
        os.system("rm -r " + self.path_project + "/*");
        
        # Baixa a lista de arquiso baseado no commit esecolhido, e traz uma lista de arquivos.
        self.files = self.commits[int(postion_commit) - 1]['files'];
        for i in range(len(self.files)):
            # Decripta o nome do arquivo
            filename = Util.decrypt( self.files[i]['name'] , key   ).decode('utf-8');
            if filename[0:1] == '.': # as vezes o PHP retorna . e .. como diretórios, tem também os diretorios/arquivos .ALGUMACOISA
                continue;

            # testa se o MD5 do servidor bate com o MD5 do local (caso tenha)
            if Util.encrypt(  Util.md5(self.path_project + "/" + filename), key).decode('utf-8') == self.files[i]['md5']:
                continue;

            # ou o MD5 é diferente, ou não existe o arquivo no local. Baixar então com download.
            print("Donwload", "("+ str(i) +"/"+ str(len(self.files)) +")", filename);

            # Arquivo por arquivo download
            self.download_file(self.files[i]['name'], self.files[i]['version'] );

    # Inicia o download, este é o método que é invocado
    def download(self):
        global MAX_OP;

        # Busca uma lista de arquivos que está diferente do local (existe tanto no servidor quanto no local)
        files_diff = self.changed_files();
        if len(files_diff) > 0:
            # exibie uma lista, vai que o cara fez algum código, esqueceu e para nao jogar seu trabalho fora, então vamos mostrar para ele.
            for i in range(len(files_diff)):
                print("Arquivo: ", Util.decrypt( files_diff[i]['name'] , key   ).decode('utf-8'));
            # se ele mesmo vendo que tem arquivos alterados no cliente, e deseja continaur, conta e risco dele.
            if input('Arquivos diferentes entre local e servidor, deseja continuar digite \033[96m\033[1ms\033[0m? \033[96m\033[1m(default n)\033[0m: ') != 's':
                return;            
        
        # Legal, ele vai continuar o download
        files_for_download = [];

        # antes de pedir o arquivo, vamos fazer uma lista do que precisa, vamos testar tudo no cliente pois está tudo criptografado
        #   e o servidor nunca, nunca pode saber a chave de descriptografia.
        for i in range(len(self.files)):

            # O nome está criptografado
            filename = Util.decrypt( self.files[i]['name'] , key   ).decode('utf-8');
            if filename[0:1] == '.': # arquivos ocultos nao quero saber
                continue;

            # pega o MD5 tanto do arquivo no servidor quanto no arquivo local, se o MD5 for igual então nao foi alterado
            if Util.encrypt(  Util.md5(self.path_project + "/" + filename), key).decode('utf-8') == self.files[i]['md5']: # file modif
                continue;

            # adiciona o arquivo na lista de arquviso que tem que ser feito o download, manda a versão do arquivo.
            files_for_download.append({"name" : self.files[i]['name'], "version" : self.files[i]['version']});
            print("Donwload", "("+ str(i) +"/"+ str(len(self.files)) +")", filename);

            # se baixar de 1 em 1 fica lento, se baixar 1000 fica travando, então deixei 10
            #    aqui se atingiu 10 elementos, ele baixa 10 elementos e zera o vetor de arquivos para
            #    download, poderia ter feito um outro método para isso, mas coloquei aqui para agilizar.
            #    MASSSS se não tem 10 arquivos ainda no vetor, e por exemplo tem 5
            #    e não existe mais nada para adicionar, então baixar os 5 arquivos, por isso o && na lógica abaixo.
            if len(files_for_download) == MAX_OP or ( (i == len(self.files) -1) and (len(files_for_download) > 0)  ) :
                self.download_files( files_for_download );
                files_for_download = []; 
        return True;
    
    # Pega a definição dos arquivos do servidor e compara com os arquivos local, retorna um array de tudo que está diferente server<>local
    #    repare que o arquivo existe tanto no servidor quanto no cliente.
    def changed_files(self):
        files_diff = [];
        for i in range(len(self.files)):
            filename = Util.decrypt( self.files[i]['name'] , key   ).decode('utf-8');
            if filename[0:1] == '.': # ignora aruivos ocultos
                continue;
            if not os.path.exists(self.path_project + "/" + filename): # arquivo tem que existir tanto no server quanto no local
                continue;
            if Util.encrypt(  Util.md5(self.path_project + "/" + filename), key).decode('utf-8') == self.files[i]['md5']: # tem que ser diferente
                continue;
            files_diff.append(self.files[i]);
        return files_diff;

    def upload_file(self, file_name, path_file_local):
        global key;

        # abre o arquivo para leitura no formato bytes
        with open(path_file_local, 'rb') as f:

            # encripta o nome, temos que esconder o nome. No servidor até o nome dos arquivos são criptografados
            file_name = Util.encrypt(file_name, key).decode('utf-8');
            data_binary = f.read(); # leia os bytes do arquivo local

            # criptografa o conteũdo do arquivo
            content = Util.encryptbinary(data_binary, key).decode('utf-8');

            # tem que tirar um MD5 do arquivo, e adivinha, criptografa até o MD5, afinal isso pode ser uma prova contra você
            md5_file = Util.encrypt(hashlib.md5(data_binary).hexdigest(), key).decode('utf-8');
            
            # vamos pegar as info do arquivo, um arquivo possui muitas versões
            info_server_file = self.info_file(file_name) ;
            for version in info_server_file['info']['versions']:
                if version['md5'] == md5_file: # se teemos uma versão compatível entre o cliente e o servidor, por que fazer upload?
                    return {"status" : 1, "version" : version['name'], "name" : file_name }; # vamos retornar dizendo que estã tudo OK. FORÇA UM RETORNO COMPATIVEL COM O RETORNO DO FINAL DESTE MÉTODO.
            
            # Não foi possível localizar nenhuma versão, então faz o UPLOAD REALMENTE.
            envelop = json.dumps({"cypher_version" : "1", "action_version" : "1", "project" : self.name, "name" : file_name, "content" : content, "md5" : md5_file });
            request_result = self.server.post("upload_file.php",envelop );

            # cria um retorno JSON.
            return {"status" : json.loads( request_result  )["status"], "version" : json.loads( request_result  )["version"], "name" : file_name} ; 
    
    # Faz o envio de 1 arquivo, um único arquivo para commit
    def commit(self, commit):
        global key;

        envelop = json.dumps({"cypher_version" : "1", "action_version" : "1", "project" : self.name,  "commit" : commit });
        request_result = json.loads( self.server.post("commit.php", envelop )  );
        return request_result;
    
    # Lista de commits, printa na tela do cara para ele ver.
    def commit_list(self):
        for i in range(len(self.commits)):
            print('- \033[96m\033[1m'+ str(i + 1) +'\033[0m', "\t"   , self.commits[i]['name'][4:6] + "/" + self.commits[i]['name'][2:4] + "/" + self.commits[i]['name'][0:2] + " " +  self.commits[i]['name'][6:8] + ":" + self.commits[i]['name'][8:10] , "\t", Util.decrypt( self.commits[i]['comment'], key   ).decode('utf-8'));
    
    # faz uma lista recursiva de diretórios e arquivos, tem que ser em LISTA, ou seja N níveis para 1 nível apenas.
    #    no servidor não podemos guardar a estrutura da ãrvore de arquivos, por isso lá no servidor guardamos em lista
    #    e o nome dos arquivos sao criptografados.
    def list_directory_recursiv(self, path_root, path_list):
        resultado = [];
        files = os.listdir(path_list);
        for file_name in files:
            path_file_name = path_list + "/" + file_name;
            if os.path.isdir(path_file_name):
                resultado = resultado + self.list_directory_recursiv(path_root, path_file_name);
            else:
                resultado.append(path_file_name);
        return resultado;

    # Método chamado pelo Menu do usuário
    def upload(self, comment=""):

        # Pode ter comentário, pode, mas também pode ir sem comentário.
        #    se tiver comentário tem que criptografar o comentário, lembre-se, criptografamos até a ALMA DO PROGRAMADOR
        if comment != "":
            comment = Util.encrypt(comment, key).decode('utf-8');

        # um envelope para o commit, que vamos preencher com arquivos.
        commit_file = {"message" :  comment, "files" : []};

        # Uma lista de arquivos, uma busca recursiva em todo o sistema de arquivos do projeto.
        buffer_files_local = self.list_directory_recursiv(self.path_project, self.path_project);

        for i in range(len(buffer_files_local)):
            # Pega o nome do arquivo, e fazer o MD5 do conteúdo do arquivo.
            filename = buffer_files_local[i];
            local_file_md5 = Util.encrypt( Util.md5(filename), key).decode('utf-8');

            # tirar o path do projeto do nome do arquivo, pois o filename é o caminho completo da raiz até a extensão
            filename_clear = filename[ len(self.path_project) + 1 :  ];

            # vamos criptografar o nome do arquivo, para nao deixar o nome visível
            filename_crypto = Util.encrypt(filename_clear, key).decode('utf-8');

            # self.files é um array que possui todos os arquivos, se é None, então nao iniciamos o repositório está vazio no server.
            #    agora se é diferente de None, vamos localizar no servidor qual arquivo é o arquivo local, por isso o lambda
            if self.files != None:
                find_elements = [x for x in self.files if x['name'] == filename_crypto];
                # Se tem lá e cá, confirma o MD5, se for igual, nem vamos aidiconar na lista de Upload.
                if len(find_elements) > 0:
                    if find_elements[0]['md5'] == local_file_md5:
                        commit_file['files'].append({"name" : find_elements[0]['name'], "version" : find_elements[0]['version'], "md5" : local_file_md5 });
                        continue;
            
            # exibe na tela o arrquivo que será enviado....
            print("Upload: ", "("+ str(i + 1) +"/"+ str(len(buffer_files_local)) +")", filename_clear);

            # faz o upload do arquivo propriamente dito, recupera o detalhe para saber se status = 1, se sim, sucesso, se nao, falha.
            details = self.upload_file(filename_clear, filename);
            if details['status'] != 1:
                print("Falha ao enviar versao");
                return;
            # os scuessos vamos aidcionando emuma outra lista, a lista do commit. Esta lista também será enviada no final
            #   com todos os sucuessos, em caso de falha de 1 envio, não vai chegar neste ponto.
            commit_file['files'].append({"name" : details['name'], "version" : details['version'], "md5" : local_file_md5 });

        # o envio do commit, que vai registrar os arquivos enviados, lembre-se que tudo é criptografado.
        self.commit(commit_file);

        # Lista o diretório do servidor, para chancelar o que fofi enviado.
        self.listdir();

# é necessário um arquivo de cofiguração, eu sempre penso na existencia deste arquivo que me liga a um servidor
#    mas mesmom que a Polícia Federal tenha o servidor, como tem 2 níveis de criptografia, também nnão me incomodo, ou seja, incomoda mas não incomoda
#    é algo que tira minhas noites de sono, essa dúvida.
def setup():
    config = None;
    if not os.path.exists( os.path.expanduser("~/.cver.json") ):
        ser = input('\t\033[96m\033[1mDominio do servidor: \033[0m');  # informar o domínio, exemplo: exemplo.com..br
        key = input('\t\033[96m\033[1mChave de criptografia do servidor: \033[0m'); # informar uma chave comum de criptografia entre o servidor e o cliente.
        key = key[:16].rjust(16, '-'); # a chave tem 16 caracteres, se nao tiver, temos que criar caracteres extra.

        config = {"server" : "http://"+ ser +"/cryptoversion/version/", "key" : key};
        print("\t\033[96m\033[1mSalvar informcoes?\n\tServer: " +  ser +  "\nKey: \033[0m", key);
        if input('\t\033[96m\033[1mDigite s para sim? (padrao e n): \033[0m') == 's':
            with open(os.path.expanduser("~/.cver.json"), 'w') as f:
                f.write( json.dumps(config) );
    else:
        config = json.loads( open(os.path.expanduser("~/.cver.json"), 'r').read() );
    return config;

def main():
    global key, MAX_OP;
    proj = None;

    # temos que criar/carregar um arquivo de configuração
    config = setup();
    if config == None:
        print("FALHA AO OBTER ARQUIVO DE CONFIGURAÇÃO");
        return;
    
    #OBTER O PASSWORD da SEGUNDA CRIPTOGRAFIA, ou seja:
    #   1 - criptografa os arquivos: somente voce sabe
    #   2 - criptografa a criptografia dos arquivos: tanto o cliente quanto o servidor possuem essa informação
    key = getpass.getpass('Password key (1-16): ')
    #key = input('Password key (1-16): ');
    key = key[:16].rjust(16, '-');
    
    while True:
        try:
            # Criando um MENU de opções para o usuário.
            print("--------//-------------");
            if proj != None:
                print("\t\t\033[94m\033[1m", Util.decrypt( proj.name, key).decode('utf-8'), '\t', proj.path_project, '\033[0m');
            print("\033[95mload:\033[0m\t\tCarregar projeto");
            print("\033[95mlist:\033[0m\t\tAtualizar lista de arquivos do servidor no local");
            print("\033[95mupload:\033[0m\t\tEnviar arquivos");
            print("\033[95mdownload:\033[0m\tCarregar arquivos");
            print("\033[95mcommits:\033[0m\tLista de Commits");
            print("\033[95mrevert:\033[0m\t\tReverter um commit especifico");
            print("-------------------------------");
            print("\033[96mclear:\033[0m\t\tLimpa a tela");
            print("\033[96m\033[1mexit:\033[0m\t\tSair do programa");
            print();
            op = input('Comando: ');

            if(op == 'load'):
                name_project = input('\t\033[96m\033[1mProject name: \033[0m');
                path_project = input('\t\033[96m\033[1mProject path ("" para usar ' + os.getcwd() +'): \033[0m');
                if path_project == "":
                    path_project = os.getcwd();
                if path_project[-1:] == "/":
                    path_project = path_project[0:-1];
                proj = Project(name_project, path_project, Server( config['server'], config['key']));
                proj.listdir();
                continue;
            if(op == 'clone'):
                proj.clone();
                continue;
            if(op == 'upload'):
                comment = input('\t\033[96m\033[1mComment (default is empty): \033[0m');
                if comment == None: 
                    comment = "";
                proj.upload(comment);
                continue;
            if(op == 'download'):
                MAX_OP = int( input('\t\033[96m\033[1mMaximum per operation: \033[0m') );
                proj.download();
                continue;
            if(op == 'list'):
                proj.listdir();
                continue;
            if(op == 'commits'):
                proj.commit_list();
                continue;
            if(op == 'flush'):
                proj.flush();
                continue;
            if(op == 'revert'):
                proj.revert();
                continue;
            if(op == 'exit'):
                break;
            if(op == 'clear'):
                os.system('clear')
                continue;
                
        except:
            traceback.print_exc();
            
main();


