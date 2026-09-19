import time
import math

def coletar_dados(modo_simulacao, canais):
    dados = {}
    pontos_de_leitura = 100 # Um osciloscópio real envia centenas de pontos
    
    if modo_simulacao:
        time.sleep(0.5) # Simula o handshake *IDN?
        
        onda_ch1 = []
        onda_ch2 = []
        
        for i in range(pontos_de_leitura):
            tempo = i * 0.1
            # Imita a resposta do campo magnético alternado (Senoide)
            onda_ch1.append(round(2.5 * math.sin(tempo), 3))
            onda_ch2.append(round(1.5 * math.cos(tempo) + 0.1, 3))
            
        if "CH1" in canais: dados["CH1"] = onda_ch1
        if "CH2" in canais: dados["CH2"] = onda_ch2
        
    else:
        # Ponto de injeção da biblioteca RsInstrument (CHAN1:DATA?)
        time.sleep(1) 
        if "CH1" in canais: dados["CH1"] = [0.0] * pontos_de_leitura
        if "CH2" in canais: dados["CH2"] = [0.0] * pontos_de_leitura
        
    return dados