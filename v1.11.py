import heapq
import requests
from collections import defaultdict

class GrafoMusica:
    def __init__(self):
        self.musicas = {}

    def adicionar_musica(self, nome, artista, genero):
        if nome not in self.musicas:
            self.musicas[nome] = {'artista': artista, 'genero': genero, 'vizinhos': {}}
            self.calcular_similaridades(nome)

    def adicionar_musica_com_api(self, nome, artista):
        genero_api, artista_api = self.buscar_informacoes_lastfm(nome, artista)
        if genero_api and artista_api:
            if nome not in self.musicas:
                self.adicionar_musica(nome, artista_api, genero_api)
            else:
                print(f"A música '{nome}' já existe no grafo.")
        else:
            print(f"Informações não encontradas para a música '{nome}' de '{artista}'.")
            genero_manual = input(f"Informe o gênero da música '{nome}': ").strip()
            self.adicionar_musica(nome, artista, genero_manual)

    def calcular_similaridades(self, nova_musica):
        for musica in self.musicas:
            if musica != nova_musica:
                similaridade = self.calcular_similaridade(nova_musica, musica)
                self.musicas[nova_musica]['vizinhos'][musica] = similaridade
                self.musicas[musica]['vizinhos'][nova_musica] = similaridade

    def calcular_similaridade(self, musica1, musica2):
        genero1 = self.musicas[musica1]['genero']
        genero2 = self.musicas[musica2]['genero']
        artista1 = self.musicas[musica1]['artista']
        artista2 = self.musicas[musica2]['artista']
        similaridade = 0
        if genero1 == genero2:
            similaridade += 0.5
        if artista1 == artista2:
            similaridade += 0.4
        if (genero1 == "MPB" and genero2 == "MPB") or (genero1 != "MPB" and genero2 != "MPB"):
            similaridade += 0.1
        return similaridade

    def obter_musicas(self):
        return list(self.musicas.keys())

    def obter_similaridades(self):
        similaridades = []
        for de, atributos in self.musicas.items():
            for para, similaridade in atributos['vizinhos'].items():
                if (para, de, similaridade) not in similaridades:
                    similaridades.append((de, para, similaridade))
        return similaridades

    def buscar_informacoes_lastfm(self, nome, artista):
        url = f"http://ws.audioscrobbler.com/2.0/?method=track.getInfo&api_key=6230742a9fa87e33d6889f55ff4ebfa7&artist={artista}&track={nome}&format=json"
        try:
            response = requests.get(url)
            data = response.json()
            if 'track' in data:
                track_info = data['track']
                genero = track_info['toptags']['tag'][0]['name']
                artista_api = track_info['artist']['name']
                return genero, artista_api
            else:
                print(f"Informações não encontradas para a música '{nome}' de '{artista}'.")
                return None, None
        except requests.exceptions.RequestException as e:
            print(f"Erro na requisição para Last.fm API: {e}")
            return None, None

def criar_grafo_predefinido():
    grafo = GrafoMusica()
    grafo.adicionar_musica("Águas de Março", "Tom Jobim e Elis Regina", "MPB")
    grafo.adicionar_musica("Chega de Saudade", "João Gilberto", "MPB")
    grafo.adicionar_musica("Garota de Ipanema", "Tom Jobim e Vinícius de Moraes", "MPB")
    grafo.adicionar_musica("Tarde em Itapuã", "Toquinho e Vinícius de Moraes", "MPB")
    grafo.adicionar_musica("Aquarela", "Toquinho", "MPB")
    grafo.adicionar_musica("O Que Será (À Flor da Pele)", "Chico Buarque", "MPB")
    grafo.adicionar_musica("Construção", "Chico Buarque", "MPB")
    grafo.adicionar_musica("Sampa", "Caetano Veloso", "MPB")
    grafo.adicionar_musica("Tropicália", "Caetano Veloso", "MPB")
    grafo.adicionar_musica("Lose Yourself", "Eminem", "Rap")
    grafo.adicionar_musica("Juicy", "The Notorious B.I.G.", "Rap")
    grafo.adicionar_musica("Billie Jean", "Michael Jackson", "Pop")
    grafo.adicionar_musica("Thriller", "Michael Jackson", "Pop")
    grafo.adicionar_musica("Smooth Criminal", "Michael Jackson", "Pop")
    grafo.adicionar_musica("Man in the Mirror", "Michael Jackson", "Pop")
    grafo.adicionar_musica("Houdini", "Eminem", "Rap")
    grafo.adicionar_musica("Candy Shop", "50 Cent", "Rap")
    grafo.adicionar_musica("All Eyez on Me", "2Pac", "Rap")
    return grafo

def dijkstra_musica(grafo, inicio):
    similaridades = {musica: float('-inf') for musica in grafo.obter_musicas()}
    similaridades[inicio] = 1.0
    pq = [(-1.0, inicio)]
    while pq:
        similaridade_atual, musica_atual = heapq.heappop(pq)
        similaridade_atual = -similaridade_atual
        if similaridade_atual < similaridades[musica_atual]:
            continue
        for vizinho, similaridade in grafo.musicas[musica_atual]['vizinhos'].items():
            similaridade_acumulada = similaridade_atual * similaridade
            if similaridade_acumulada > similaridades[vizinho]:
                similaridades[vizinho] = similaridade_acumulada
                heapq.heappush(pq, (-similaridade_acumulada, vizinho))
    return similaridades

class DisjointSetMusica:
    def __init__(self, musicas):
        self.parent = {musica: musica for musica in musicas}
        self.rank = {musica: 0 for musica in musicas}

    def find(self, musica):
        if self.parent[musica] != musica:
            self.parent[musica] = self.find(self.parent[musica])
        return self.parent[musica]

    def union(self, musica1, musica2):
        root1 = self.find(musica1)
        root2 = self.find(musica2)
        if root1 != root2:
            if self.rank[root1] > self.rank[root2]:
                self.parent[root2] = root1
            else:
                self.parent[root1] = root2
                if self.rank[root1] == self.rank[root2]:
                    self.rank[root2] += 1

def kruskal_musica(grafo, genero):
    similaridades = [sim for sim in grafo.obter_similaridades() if grafo.musicas[sim[0]]['genero'] == genero and grafo.musicas[sim[1]]['genero'] == genero]
    disjoint_set = DisjointSetMusica([musica for musica, atributos in grafo.musicas.items() if atributos['genero'] == genero])
    similaridades = sorted(similaridades, key=lambda x: -x[2])
    mst = []
    for similaridade in similaridades:
        de, para, grau_similaridade = similaridade
        if disjoint_set.find(de) != disjoint_set.find(para):
            disjoint_set.union(de, para)
            mst.append(similaridade)
    return mst

def imprimir_arvore_similaridade(mst, grafo):
    tree_map = defaultdict(list)
    for de, para, similaridade in mst:
        tree_map[de].append((para, similaridade))

    def imprimir_recursivo(musica, nivel):
        if nivel == 0:
            print(f"{musica} (Artista: {grafo.musicas[musica]['artista']}, Gênero: {grafo.musicas[musica]['genero']})")
        if musica in tree_map:
            for vizinho, similaridade in tree_map[musica]:
                print(' ' * (nivel * 2) + f"- {vizinho} (Artista: {grafo.musicas[vizinho]['artista']}, Gênero: {grafo.musicas[vizinho]['genero']}, Similaridade: {similaridade:.2f})")
                imprimir_recursivo(vizinho, nivel + 1)

    if mst:
        imprimir_recursivo(mst[0][0], 0)

def main():
    grafo = criar_grafo_predefinido()
    while True:
        print("\nMenu:")
        print("1. Adicionar música manualmente")
        print("2. Adicionar música via API")
        print("3. Calcular similaridade")
        print("4. Construir árvore de similaridade")
        print("5. Sair")
        escolha = input("Escolha uma opção: ").strip()
        if escolha == "1":
            nome = input("Nome da música: ").strip()
            artista = input("Artista: ").strip()
            genero = input("Gênero: ").strip()
            grafo.adicionar_musica(nome, artista, genero)
        elif escolha == "2":
            nome = input("Nome da música: ").strip()
            artista = input("Artista: ").strip()
            grafo.adicionar_musica_com_api(nome, artista)
        elif escolha == "3":
            inicio = input("Música inicial: ")
            if inicio in grafo.obter_musicas():
                similaridades = dijkstra_musica(grafo, inicio)
                print(f"\nMúsicas similares a partir de '{inicio}':")
                musicas_similares = sorted(similaridades.items(), key=lambda item: -item[1])
                for destino, similaridade in musicas_similares:
                    if destino != inicio:
                        percentual_similaridade = similaridade * 100
                        if percentual_similaridade > 0:
                            print(f"Música: {destino} - Similaridade: {percentual_similaridade:.2f}%")
            else:
                print(f"A música '{inicio}' não foi encontrada no grafo.")
        elif escolha == "4":
            generos = set(musica['genero'] for musica in grafo.musicas.values())
            print("\nGêneros disponíveis:")
            for genero in generos:
                print(f"- {genero}")
            genero_escolhido = input("Escolha um gênero: ")
            if genero_escolhido in generos:
                mst = kruskal_musica(grafo, genero_escolhido)
                print(f"\nÁrvore de Similaridade das Músicas do gênero '{genero_escolhido}':")
                imprimir_arvore_similaridade(mst, grafo)
            else:
                print(f"Gênero '{genero_escolhido}' não encontrado.")
        elif escolha == "5":
            break
        else:
            print("Opção inválida. Por favor, escolha novamente.")

if __name__ == "__main__":
    main()
