import customtkinter as ctk
from tkinter import colorchooser, filedialog
from PIL import Image
import os
import shutil
import json
import copy

ARQUIVO_CONFIG = "perfis_config.json"

PERFIS_PADRAO = {
    "192.168.1.10": {"alias": "Osciloscópio Principal", "cor": "#FFFFFF", "imagem": None},
    "192.168.1.20": {"alias": "Osciloscópio Secundário", "cor": "#FFFFFF", "imagem": None},
    "192.168.1.30": {"alias": "Osciloscópio Auxiliar", "cor": "#FFFFFF", "imagem": None}
}

PERFIS = {}

def carregar_perfis():
    global PERFIS
    if os.path.exists(ARQUIVO_CONFIG):
        with open(ARQUIVO_CONFIG, "r", encoding="utf-8") as f:
            PERFIS = json.load(f)
    else:
        PERFIS = copy.deepcopy(PERFIS_PADRAO)
        salvar_perfis_json()

def salvar_perfis_json():
    with open(ARQUIVO_CONFIG, "w", encoding="utf-8") as f:
        json.dump(PERFIS, f, indent=4, ensure_ascii=False)

carregar_perfis()

class GerenciadorBiblioteca:
    def __init__(self, container, callback_atualizacao, callback_mudanca_global):
        self.container = container
        self.callback = callback_atualizacao
        self.callback_mudanca_global = callback_mudanca_global 
        self.ip_selecionado = None
        
        self.frame_lista = ctk.CTkScrollableFrame(self.container, fg_color="#0a0a0a", border_width=1, border_color="#333", label_text="Aparelhos Cadastrados (Duplo Clique para Personalizar)")
        self.frame_lista.pack(pady=20, padx=20, fill="both", expand=True)
        
        self.frame_botoes = ctk.CTkFrame(self.container, fg_color="transparent")
        self.frame_botoes.pack(fill="x", padx=20, pady=(0, 20))
        
        # Alteração: O botão agora restaura APENAS o osciloscópio selecionado
        ctk.CTkButton(self.frame_botoes, text="Restaurar Aparelho Selecionado", fg_color="#8b0000", hover_color="#5a0000", command=self.restaurar_padrao).pack(side="left")
        
        self.btn_personalizar = ctk.CTkButton(self.frame_botoes, text="Personalizar Aparelho", state="disabled", fg_color="#333333", text_color="#777777", command=self.abrir_janela_edicao)
        self.btn_personalizar.pack(side="right")
        
        self.botoes_lista = {} 
        self.atualizar_lista_visual()

    def acao_duplo_clique(self, event, ip_clicado):
        self.selecionar_aparelho(ip_clicado)
        self.abrir_janela_edicao()

    def selecionar_aparelho(self, ip_clicado):
        self.ip_selecionado = ip_clicado
        for ip, btn in self.botoes_lista.items():
            if ip == ip_clicado:
                btn.configure(fg_color="#333333") 
            else:
                btn.configure(fg_color="transparent")
                
        self.btn_personalizar.configure(state="normal", fg_color="#1f538d", text_color="#FFFFFF", hover_color="#14375e")
        self.callback_mudanca_global(ip_clicado)

    def restaurar_padrao(self):
        # Alteração: Age cirurgicamente sobre o IP selecionado
        global PERFIS
        if self.ip_selecionado:
            PERFIS[self.ip_selecionado] = copy.deepcopy(PERFIS_PADRAO[self.ip_selecionado])
            salvar_perfis_json()
            self.atualizar_lista_visual()
            self.selecionar_aparelho(self.ip_selecionado)
            self.callback()

    def atualizar_lista_visual(self):
        for widget in self.frame_lista.winfo_children():
            widget.destroy()
            
        self.botoes_lista.clear()
        ips_ordenados = sorted(PERFIS.keys())
        
        for ip in ips_ordenados:
            dados = PERFIS[ip]
            texto_exibicao = f"[{ip}] - {dados['alias']}"
            btn = ctk.CTkButton(self.frame_lista, text=texto_exibicao, font=("Consolas", 14), 
                                text_color=dados['cor'], fg_color="transparent", hover_color="#222222", 
                                anchor="w", command=lambda i=ip: self.selecionar_aparelho(i))
            
            btn.bind("<Double-1>", lambda event, i=ip: self.acao_duplo_clique(event, i))
            
            btn.pack(fill="x", pady=2, padx=5)
            self.botoes_lista[ip] = btn

    def abrir_janela_edicao(self):
        if not self.ip_selecionado: return 

        self.janela_edicao = ctk.CTkToplevel()
        self.janela_edicao.title(f"Personalizando: {self.ip_selecionado}")
        self.janela_edicao.geometry("650x380")
        self.janela_edicao.attributes("-topmost", True)
        
        perfil_atual = PERFIS[self.ip_selecionado]
        self.cor_temporaria = perfil_atual["cor"]
        self.caminho_img_temporario = perfil_atual["imagem"]

        frame_editor = ctk.CTkFrame(self.janela_edicao, fg_color="#0a0a0a")
        frame_editor.pack(pady=10, padx=10, fill="both", expand=True)

        frame_img = ctk.CTkFrame(frame_editor, fg_color="transparent")
        frame_img.grid(row=0, column=0, padx=20, pady=20, sticky="n")
        
        self.lbl_imagem = ctk.CTkLabel(frame_img, text="Sem\nImagem", width=120, height=120, fg_color="#111", border_width=1)
        self.lbl_imagem.pack()
        ctk.CTkButton(frame_img, text="Selecionar Imagem", width=120, command=self.escolher_imagem).pack(pady=10)

        frame_dados = ctk.CTkFrame(frame_editor, fg_color="transparent")
        frame_dados.grid(row=0, column=1, padx=20, pady=20, sticky="nw")

        self.lbl_titulo_alias = ctk.CTkLabel(frame_dados, text="Apelido do Aparelho (Alias):", font=("Segoe UI", 14, "bold"))
        self.lbl_titulo_alias.pack(anchor="w")
        
        self.entrada_alias = ctk.CTkEntry(frame_dados, width=250)
        self.entrada_alias.pack(pady=(0, 15), anchor="w")
        self.entrada_alias.insert(0, perfil_atual["alias"])

        ctk.CTkLabel(frame_dados, text="Paleta de Cores:").pack(anchor="w")
        frame_cores = ctk.CTkFrame(frame_dados, fg_color="transparent")
        frame_cores.pack(anchor="w")

        self.botoes_cor = []
        cores_padrao = ["#FFFFFF", "#1f538d", "#a32626", "#d4a017", "#277a27"]
        for cor in cores_padrao:
            btn = ctk.CTkButton(frame_cores, text="", width=30, height=30, fg_color=cor, hover_color=cor, border_width=2, command=lambda c=cor: self.mudar_cor_temporaria(c))
            btn.pack(side="left", padx=2)
            self.botoes_cor.append(btn)
            
        ctk.CTkButton(frame_cores, text="Cores (RGB)", fg_color="#333", command=self.escolher_cor_avancada).pack(side="left", padx=10)
        
        ctk.CTkButton(frame_dados, text="Salvar Alterações", fg_color="#277a27", hover_color="#1a521a", command=self.salvar_alteracoes).pack(pady=30, anchor="w")

        self.atualizar_visual_imagem()
        self.mudar_cor_temporaria(self.cor_temporaria)

    def atualizar_visual_imagem(self):
        if self.caminho_img_temporario and os.path.exists(self.caminho_img_temporario):
            img = ctk.CTkImage(light_image=Image.open(self.caminho_img_temporario), size=(120, 120))
            self.lbl_imagem.configure(image=img, text="")
        else:
            self.lbl_imagem.configure(image="", text=f"IP:\n{self.ip_selecionado}")

    def escolher_imagem(self):
        arquivo = filedialog.askopenfilename(parent=self.janela_edicao, filetypes=[("Imagens", "*.png;*.jpg;*.jpeg")])
        if arquivo:
            pasta_assets = os.path.join(os.getcwd(), "assets")
            os.makedirs(pasta_assets, exist_ok=True)
            novo_caminho = os.path.join(pasta_assets, f"icon_{self.ip_selecionado.replace('.', '_')}.png")
            shutil.copy(arquivo, novo_caminho)
            self.caminho_img_temporario = novo_caminho
            self.atualizar_visual_imagem()

    def mudar_cor_temporaria(self, nova_cor):
        self.cor_temporaria = nova_cor
        self.lbl_titulo_alias.configure(text_color=nova_cor)
        
        for btn in self.botoes_cor:
            if btn.cget("fg_color") == nova_cor:
                btn.configure(border_color="#FFFFFF" if nova_cor != "#FFFFFF" else "#00FF00")
            else:
                btn.configure(border_color="#222222")

    def escolher_cor_avancada(self):
        cor_rgb = colorchooser.askcolor(parent=self.janela_edicao, title="Escolha a cor")[1]
        if cor_rgb:
            btn = ctk.CTkButton(self.botoes_cor[0].master, text="", width=30, height=30, fg_color=cor_rgb, hover_color=cor_rgb, border_width=2, command=lambda c=cor_rgb: self.mudar_cor_temporaria(c))
            btn.pack(side="left", padx=2)
            self.botoes_cor.append(btn)
            self.mudar_cor_temporaria(cor_rgb)

    def salvar_alteracoes(self):
        PERFIS[self.ip_selecionado]["alias"] = self.entrada_alias.get()
        PERFIS[self.ip_selecionado]["cor"] = self.cor_temporaria
        PERFIS[self.ip_selecionado]["imagem"] = self.caminho_img_temporario
        
        salvar_perfis_json()
        
        self.atualizar_lista_visual()
        self.selecionar_aparelho(self.ip_selecionado)
        self.callback()
        self.janela_edicao.destroy()