import numpy as np
import matplotlib.pyplot as plt

# --- Configurações da Simulação SATÉLITE (Geoestacionário - VSAT) ---
np.random.seed(42) # Usando a mesma semente para consistência
num_pacotes = 10

# --- Eixo X (Pacotes) ---
x_pacotes = np.arange(1, num_pacotes + 1)

# 1. Retardo (Delay) em segundos - MUITO ALTO e MUITO ESTÁVEL
# Média: ~550 ms (tempo de ida e volta ao satélite GEO + processamento)
# Instabilidade (scale): Muito baixa (ex: 5 ms)
retardo_sat = np.random.normal(loc=0.55, scale=0.005, size=num_pacotes)

# 2. Jitter (variação do retardo) em segundos - MUITO BAIXO
# O caminho é fixo, então a variação é mínima.
# Média: 2 ms, Instabilidade: 1 ms
jitter_sat = np.abs(np.random.normal(loc=0.002, scale=0.001, size=num_pacotes))

# 3. Taxa de Transmissão (Throughput) em Mbps - ALTA
# Links VSAT (banda Ku/Ka) são de banda larga.
# Média: 25 Mbps, Instabilidade: 2 Mbps
taxa_transmissao_sat = np.random.normal(loc=25.0, scale=2.0, size=num_pacotes)
taxa_transmissao_sat = np.clip(taxa_transmissao_sat, 15.0, 35.0) # Garante valores de banda larga

# 4. Taxa de Erro (BER) - MUITO BAIXA (Quase Zero)
# Links de satélite são muito confiáveis (exceto por chuva forte)
# Média: 0.0001% (loc=0.000001), Instabilidade muito baixa
taxa_erro_sat = np.abs(np.random.normal(loc=0.000001, scale=0.0000005, size=num_pacotes))

# --- Criação dos subplots (2x2) ---
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle("Métricas de Comunicação via SATÉLITE (Simulação Estocástica)", fontsize=14)

# --- Retardo ---
axs[0, 0].plot(x_pacotes, retardo_sat, marker='o', linestyle='-', markersize=4, color='tab:blue', alpha=0.6)
axs[0, 0].set_title("Retardo (Delay)")
axs[0, 0].set_ylabel("Segundos (s)")
axs[0, 0].axhline(y=0.55, color='r', linestyle='--', label='Média (550 ms)')
# NOVO: Calcular e plotar a reta de tendência
coef_retardo = np.polyfit(x_pacotes, retardo_sat, 1)
tendencia_retardo = np.poly1d(coef_retardo)(x_pacotes)
axs[0, 0].plot(x_pacotes, tendencia_retardo, color='black', linestyle='--', label='Tendência')
axs[0, 0].legend()
axs[0, 0].grid(True, linestyle=':')

# --- Jitter ---
axs[0, 1].plot(x_pacotes, jitter_sat, marker='s', linestyle='-', markersize=4, color='tab:orange', alpha=0.6)
axs[0, 1].set_title("Jitter")
axs[0, 1].set_ylabel("Segundos (s)")
# NOVO: Calcular e plotar a reta de tendência
coef_jitter = np.polyfit(x_pacotes, jitter_sat, 1)
tendencia_jitter = np.poly1d(coef_jitter)(x_pacotes)
axs[0, 1].plot(x_pacotes, tendencia_jitter, color='black', linestyle='--', label='Tendência')
axs[0, 1].legend()
axs[0, 1].grid(True, linestyle=':')

# --- Taxa de Transmissão ---
axs[1, 0].plot(x_pacotes, taxa_transmissao_sat, marker='^', linestyle='-', markersize=4, color='tab:green', alpha=0.6)
axs[1, 0].set_title("Taxa de Transmissão (Throughput)")
axs[1, 0].set_ylabel("Mbps")
# NOVO: Calcular e plotar a reta de tendência
coef_taxa = np.polyfit(x_pacotes, taxa_transmissao_sat, 1)
tendencia_taxa = np.poly1d(coef_taxa)(x_pacotes)
axs[1, 0].plot(x_pacotes, tendencia_taxa, color='black', linestyle='--', label='Tendência')
axs[1, 0].legend()
axs[1, 0].grid(True, linestyle=':')

# --- Taxa de Erro ---
dados_taxa_erro = taxa_erro_sat * 100
axs[1, 1].plot(x_pacotes, dados_taxa_erro, marker='d', linestyle='-', markersize=4, color='tab:red', alpha=0.6)
axs[1, 1].set_title("Taxa de Erro (BER)")
axs[1, 1].set_ylabel("Proporção de Erros (%)")
# NOVO: Calcular e plotar a reta de tendência
coef_erro = np.polyfit(x_pacotes, dados_taxa_erro, 1)
tendencia_erro = np.poly1d(coef_erro)(x_pacotes)
axs[1, 1].plot(x_pacotes, tendencia_erro, color='black', linestyle='--', label='Tendência')
axs[1, 1].legend()
axs[1, 1].grid(True, linestyle=':')

# --- Ajustes finais ---
for ax in axs.flat:
    ax.set_xlabel("Pacote")

plt.tight_layout(rect=[0, 0, 1, 0.96])
plt.show()

print("\n--- Métricas Médias da Simulação SATÉLITE ---")
print(f"Retardo médio: {np.mean(retardo_sat) * 1000:.2f} ms")
print(f"Jitter médio: {np.mean(jitter_sat) * 1000:.2f} ms")
print(f"Taxa de erro média: {np.mean(taxa_erro_sat) * 100:.6f} %") # Precisa de mais casas decimais
print(f"Taxa de transmissão média: {np.mean(taxa_transmissao_sat):.2f} Mbps")