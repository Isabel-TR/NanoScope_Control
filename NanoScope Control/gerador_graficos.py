import os
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

def salvar_grafico_interativo(dados, ip_maquina, alias_maquina, canais, momento_coleta):
    hora = momento_coleta.strftime('%Hh%Mm%Ss')
    data = momento_coleta.strftime('%d%m%Y')
    ip_limpo = ip_maquina.replace(".", "_")
    
    nome_base = f"{alias_maquina} {hora} {data} ip{ip_limpo}"
    
    pasta_graficos = os.path.join(os.getcwd(), "graficos", ip_limpo)
    os.makedirs(pasta_graficos, exist_ok=True)
    caminho_grafico = os.path.join(pasta_graficos, f"{nome_base}.png")
    
    fig = Figure(figsize=(9, 5), dpi=100, facecolor="#0a0a0a")
    ax = fig.add_subplot(111)
    
    ax.set_facecolor("#111111")
    ax.spines['bottom'].set_color('#555555')
    ax.spines['top'].set_color('#555555')
    ax.spines['left'].set_color('#555555')
    ax.spines['right'].set_color('#555555')
    ax.tick_params(axis='x', colors='white')
    ax.tick_params(axis='y', colors='white')
    
    total_pontos = len(dados[canais[0]])
    tempo_eixo = [round(x * 0.1, 1) for x in range(total_pontos)]
    
    if "CH1" in canais: 
        ax.plot(tempo_eixo, dados["CH1"], label='Canal 1 (CH1)', color='#1f538d', linewidth=2, marker='o', markersize=3)
    if "CH2" in canais: 
        ax.plot(tempo_eixo, dados["CH2"], label='Canal 2 (CH2)', color='#a32626', linewidth=2, linestyle='--', marker='s', markersize=3)

    ax.set_title(f"Monitoramento Magnético: {alias_maquina}", color='white', fontsize=12, pad=10)
    ax.set_xlabel("Tempo (s)", color='white')
    ax.set_ylabel("Voltagem (V)", color='white')
    
    leg = ax.legend(facecolor='#1a1a1a', edgecolor='#333333')
    for texto in leg.get_texts():
        texto.set_color("white")
        
    ax.grid(True, color='#222222', linestyle='-', linewidth=0.5)
    fig.tight_layout()
    
    # --- SISTEMA DE RASTREAMENTO PROFISSIONAL (HOVER) ---
    annot = ax.annotate("", xy=(0,0), xytext=(15, 15), textcoords="offset points",
                        bbox=dict(boxstyle="round,pad=0.4", fc="#222222", ec="#555555", lw=1),
                        color="white", fontsize=10, arrowprops=dict(arrowstyle="->", color="white"))
    annot.set_visible(False)

    def ao_mover_mouse(event):
        if event.inaxes == ax:
            x_mouse = event.xdata
            if x_mouse is None: return
            
            # Encontra o ponto de tempo mais próximo (Magnetismo/Nanotecnologia exige precisão)
            idx_proximo = min(range(len(tempo_eixo)), key=lambda i: abs(tempo_eixo[i] - x_mouse))
            x_real = tempo_eixo[idx_proximo]
            
            textos = [f"Tempo: {x_real:.1f}s"]
            if "CH1" in canais: textos.append(f"CH1: {dados['CH1'][idx_proximo]:.3f} V")
            if "CH2" in canais: textos.append(f"CH2: {dados['CH2'][idx_proximo]:.3f} V")
            
            # Ancorar a caixa no primeiro canal selecionado
            y_real = dados[canais[0]][idx_proximo]
            
            annot.xy = (x_real, y_real)
            annot.set_text("\n".join(textos))
            annot.set_visible(True)
            fig.canvas.draw_idle()
        else:
            if annot.get_visible():
                annot.set_visible(False)
                fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", ao_mover_mouse)
    # ---------------------------------------------------

    fig.savefig(caminho_grafico, facecolor=fig.get_facecolor(), edgecolor='none')
    
    janela_grafico = ctk.CTkToplevel()
    janela_grafico.title(f"Plataforma de Análise Gráfica - {alias_maquina}")
    janela_grafico.geometry("950x650")
    janela_grafico.attributes("-topmost", True)
    
    canvas = FigureCanvasTkAgg(fig, master=janela_grafico)
    canvas.draw()
    
    frame_ferramentas = ctk.CTkFrame(janela_grafico, fg_color="transparent")
    frame_ferramentas.pack(side="bottom", fill="x", pady=5)
    
    toolbar = NavigationToolbar2Tk(canvas, frame_ferramentas)
    toolbar.update()
    toolbar.pack(side="bottom")
    
    canvas.get_tk_widget().pack(side="top", fill="both", expand=True)