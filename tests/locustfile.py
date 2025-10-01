from locust import HttpUser, task, between

class PolosUser(HttpUser):
    wait_time = between(1, 3)  # Espera entre 1 e 3 segundos entre as tarefas
    
    @task(3)
    def buscar_polos(self):
        # Simula busca de polos
        self.client.get("/")
        self.client.post("/busca/", {
            "municipio": "São Paulo",
            "curso": "Engenharia"
        })
    
    @task(2)
    def visualizar_polo(self):
        # Simula visualização de detalhes do polo
        self.client.get("/polo/1/")
    
    @task(1)
    def enviar_feedback(self):
        # Simula envio de feedback
        self.client.post("/feedback/", {
            "polo_id": "1",
            "avaliacao": "5",
            "comentario": "Ótima estrutura e atendimento"
        })
    
    def on_start(self):
        # Simula login (se necessário)
        pass
