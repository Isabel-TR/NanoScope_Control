import sys
import subprocess
import platform
import datetime

try:
    import matplotlib
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "--quiet"])

import customtkinter as ctk
import pywinstyles
from PIL import Image
import os
import gerador_dados
import teste_planilha
import gerador_graficos
import biblioteca

ctk.set_appearance_mode("dark")
FONTE_TERMINAL = ("Consolas", 13)

janela = ctk.CTk()
janela.title("NanoScope Control")
janela.geometry("1150x680")
janela.configure(fg_color="#010101")

try:
    pywinstyles.apply_style(janela, "mica")
except:
    pass

DADOS_EM_MEMORIA = None
CANAIS_EM_MEMORIA = []
TIMESTAMP_MEMORIA = None

abas = ctk.CTkTabview(janela, fg_color="transparent")
abas.pack(fill="both", expand=True, padx=10, pady=10)

aba_dash = abas.add("💻 Página Inicial")
aba_biblio = abas.add("📚 Biblioteca de Aparelhos")

aba_dash.grid_columnconfigure(0, weight=3)
aba_dash.grid_columnconfigure(1, weight=2)
aba_dash.grid_rowconfigure(1, weight=1)

ip_atual_selecionado = list(biblioteca.PERFIS.keys())[0]

def abrir_hibrido(caminho):
    sistema = platform.system()
    if sistema == "Windows":
        os.startfile(caminho)
    elif sistema == "Linux":
        subprocess.call(["xdg-open", caminho])

def atualizar_interface_global():
    lista_formatada = [f"[{ip}] - {dados['alias']}" for ip, dados in biblioteca.PERFIS.items()]
    seletor_perfil.configure(values=lista_formatada)
    seletor_perfil.set(f"[{ip_atual_selecionado}] - {biblioteca.PERFIS[ip_atual_selecionado]['alias']}")
    
    perfil = biblioteca.PERFIS[ip_atual_selecionado]
    cor_ativa = perfil['cor']
    cor_fonte_botao = "#000000" if cor_ativa.upper() == "#FFFFFF" else "#FFFFFF"
    
    status_osciloscopio.configure(text=f"{perfil['alias']} (IP: {ip_atual_selecionado})", text_color=cor_ativa)
    botao_coletar.configure(fg_color=cor_ativa, text_color=cor_fonte_botao)
    botao_gerar_planilha.configure(fg_color=cor_ativa, text_color=cor_fonte_botao)
    botao_gerar_grafico.configure(fg_color=cor_ativa, text_color=cor_fonte_botao)
    
    caixa_dados.configure(border_color=cor_ativa)
    topo.configure(border_color=cor_ativa)
    switch_simulacao.configure(progress_color=cor_ativa)
    check_ch1.configure(fg_color=cor_ativa, hover_color=cor_ativa)
    check_ch2.configure(fg_color=cor_ativa, hover_color=cor_ativa)
    
    if perfil["imagem"] and os.path.exists(perfil["imagem"]):
        img = ctk.CTkImage(light_image=Image.open(perfil["imagem"]), size=(40, 40))
        icone_dash.configure(image=img, text="")
    else:
        icone_dash.configure(image="", text="[X]")
        
    atualizar_pastas_visuais()

def mudar_ip_global(novo_ip):
    global ip_atual_selecionado
    ip_atual_selecionado = novo_ip
    atualizar_interface_global()

def ao_trocar_osciloscopio(selecao):
    global ip_atual_selecionado
    ip_atual_selecionado = selecao.split("[")[1].split("]")[0]
    atualizar_interface_global()

def abrir_arquivo_duplo_clique(event, caminho_completo):
    abrir_hibrido(caminho_completo)

# Lógica inteligente para abrir a pasta baseada na aba selecionada
def abrir_pasta_sistema_dinamica():
    tipo = var_visualizacao.get().lower() # "planilhas" ou "gráficos"
    if tipo == "gráficos": tipo = "graficos" # Remove o acento para a pasta
    
    ip_limpo = ip_atual_selecionado.replace(".", "_")
    pasta = os.path.join(os.getcwd(), tipo, ip_limpo)
    os.makedirs(pasta, exist_ok=True)
    abrir_hibrido(pasta)

def atualizar_pastas_visuais(*args):
    tipo = var_visualizacao.get().lower()
    if tipo == "gráficos": tipo = "graficos"
    
    ip_limpo = ip_atual_selecionado.replace(".", "_")
    pasta = os.path.join(os.getcwd(), tipo, ip_limpo)
    os.makedirs(pasta, exist_ok=True)
    
    for widget in painel_arquivos.winfo_children(): 
        widget.destroy()
        
    icone = "📈" if tipo == "graficos" else "📊"
    
    for arq in os.listdir(pasta):
        caminho = os.path.join(pasta, arq)
        lbl = ctk.CTkLabel(painel_arquivos, text=f"{icone} {arq}", font=FONTE_TERMINAL, text_color="white", cursor="hand2")
        lbl.pack(anchor="w", pady=2, padx=5)
        lbl.bind("<Double-1>", lambda e, p=caminho: abrir_arquivo_duplo_clique(e, p))

def acao_coletar_dados():
    global DADOS_EM_MEMORIA, CANAIS_EM_MEMORIA, TIMESTAMP_MEMORIA
    modo_simulacao = switch_simulacao.get()
    canais_selecionados = []
    if check_ch1.get(): canais_selecionados.append("CH1")
    if check_ch2.get(): canais_selecionados.append("CH2")
    
    if not canais_selecionados:
        caixa_dados.insert("end", "\n[ERRO] Selecione ao menos um canal ativo!\n")
        caixa_dados.see("end")
        return
        
    estado = "SIMULAÇÃO" if modo_simulacao else "HARDWARE REAL"
    caixa_dados.insert("end", f"\n[{estado}] Iniciando leitura em {ip_atual_selecionado}...\n")
    
    TIMESTAMP_MEMORIA = datetime.datetime.now()
    DADOS_EM_MEMORIA = gerador_dados.coletar_dados(modo_simulacao, canais_selecionados)
    CANAIS_EM_MEMORIA = canais_selecionados
    
    if not modo_simulacao:
         caixa_dados.insert("end", "[ALERTA] Hardware ausente. Buffer preenchido com zeros.\n")
    
    # Exibe a prévia dos dados coletados direto na tela!
    caixa_dados.insert("end", "-> Prévia dos dados coletados:\n")
    for canal in canais_selecionados:
        amostra = DADOS_EM_MEMORIA[canal][:4] # Mostra os 4 primeiros pontos
        total = len(DADOS_EM_MEMORIA[canal])
        caixa_dados.insert("end", f"   {canal}: {amostra}... (Total: {total} pontos)\n")
         
    caixa_dados.insert("end", "-> Buffer armazenado na Memória RAM!\n")
    caixa_dados.see("end")

def acao_gerar_planilha():
    if not DADOS_EM_MEMORIA:
        caixa_dados.insert("end", "\n[ERRO] Memória vazia. Colete os dados primeiro!\n")
        caixa_dados.see("end")
        return
        
    alias = biblioteca.PERFIS[ip_atual_selecionado]['alias']
    teste_planilha.salvar_csv(DADOS_EM_MEMORIA, ip_atual_selecionado, alias, CANAIS_EM_MEMORIA, TIMESTAMP_MEMORIA)
    caixa_dados.insert("end", "-> Planilha (CSV) estruturada com sucesso!\n")
    caixa_dados.see("end")
    if var_visualizacao.get() == "Planilhas": atualizar_pastas_visuais()

def acao_gerar_grafico():
    if not DADOS_EM_MEMORIA:
        caixa_dados.insert("end", "\n[ERRO] Memória vazia. Colete os dados primeiro!\n")
        caixa_dados.see("end")
        return
        
    alias = biblioteca.PERFIS[ip_atual_selecionado]['alias']
    gerador_graficos.salvar_grafico_interativo(DADOS_EM_MEMORIA, ip_atual_selecionado, alias, CANAIS_EM_MEMORIA, TIMESTAMP_MEMORIA)
    caixa_dados.insert("end", "-> Interface Gráfica Científica lançada!\n")
    caixa_dados.see("end")
    if var_visualizacao.get() == "Gráficos": atualizar_pastas_visuais()

topo = ctk.CTkFrame(aba_dash, fg_color="#0a0a0a", border_width=1)
topo.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

icone_dash = ctk.CTkLabel(topo, text="[X]", width=40, height=40, fg_color="#222")
icone_dash.pack(side="left", padx=10, pady=10)

status_osciloscopio = ctk.CTkLabel(topo, text="", font=("Consolas", 18, "bold"))
status_osciloscopio.pack(side="left", padx=10)

seletor_perfil = ctk.CTkOptionMenu(topo, values=[], command=ao_trocar_osciloscopio)
seletor_perfil.pack(side="right", padx=15, pady=10)

caixa_dados = ctk.CTkTextbox(aba_dash, font=FONTE_TERMINAL, fg_color="#050505", border_width=1)
caixa_dados.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

frame_controles = ctk.CTkFrame(aba_dash, fg_color="#0a0a0a", border_width=1, border_color="#333")
frame_controles.grid(row=2, column=0, padx=5, pady=(0, 5), sticky="ew")

switch_simulacao = ctk.CTkSwitch(frame_controles, text="Modo Simulação", font=("Consolas", 12, "bold"))
switch_simulacao.select()
switch_simulacao.pack(side="left", padx=20, pady=10)

check_ch1 = ctk.CTkCheckBox(frame_controles, text="Canal 1 (CH1)", font=("Consolas", 12))
check_ch1.select()
check_ch1.pack(side="left", padx=10)

check_ch2 = ctk.CTkCheckBox(frame_controles, text="Canal 2 (CH2)", font=("Consolas", 12))
check_ch2.pack(side="left", padx=10)

botao_coletar = ctk.CTkButton(aba_dash, text="1. ACESSAR HARDWARE E COLETAR DADOS", font=("Consolas", 14, "bold"), height=40, command=acao_coletar_dados)
botao_coletar.grid(row=3, column=0, padx=5, pady=2, sticky="ew")

frame_botoes = ctk.CTkFrame(aba_dash, fg_color="transparent")
frame_botoes.grid(row=4, column=0, padx=5, pady=5, sticky="ew")
frame_botoes.grid_columnconfigure(0, weight=1)
frame_botoes.grid_columnconfigure(1, weight=1)

botao_gerar_planilha = ctk.CTkButton(frame_botoes, text="2A. EXPORTAR PLANILHA (CSV)", font=("Consolas", 13, "bold"), height=45, command=acao_gerar_planilha)
botao_gerar_planilha.grid(row=0, column=0, padx=(0, 5), sticky="ew")

botao_gerar_grafico = ctk.CTkButton(frame_botoes, text="2B. RENDERIZAR GRÁFICO", font=("Consolas", 13, "bold"), height=45, command=acao_gerar_grafico)
botao_gerar_grafico.grid(row=0, column=1, padx=(5, 0), sticky="ew")

# --- NOVO PAINEL DIREITO (UNIFICADO) ---
direita_frame = ctk.CTkFrame(aba_dash, fg_color="transparent")
direita_frame.grid(row=1, column=1, rowspan=4, padx=5, pady=5, sticky="nsew")

# Seletor Segmentado no Topo
var_visualizacao = ctk.StringVar(value="Planilhas")
seletor_vis = ctk.CTkSegmentedButton(direita_frame, values=["Planilhas", "Gráficos"], variable=var_visualizacao, command=atualizar_pastas_visuais)
seletor_vis.pack(fill="x", pady=(0, 5))

# Container Único de Arquivos
painel_arquivos = ctk.CTkScrollableFrame(direita_frame, fg_color="#0a0a0a", border_width=1, border_color="#333", label_text="Arquivos Salvos")
painel_arquivos.pack(expand=True, fill="both", pady=(0, 5))

# Botão Único Dinâmico
botao_abrir_pasta = ctk.CTkButton(direita_frame, text="Abrir Pasta Selecionada", fg_color="#333", hover_color="#555", command=abrir_pasta_sistema_dinamica)
botao_abrir_pasta.pack(fill="x")

gerenciador = biblioteca.GerenciadorBiblioteca(aba_biblio, atualizar_interface_global, mudar_ip_global)
atualizar_interface_global()

janela.mainloop()