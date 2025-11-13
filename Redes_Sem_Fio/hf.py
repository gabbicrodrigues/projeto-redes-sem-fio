import numpy as np
import matplotlib.pyplot as plt

# --- Configurações da Simulação HF (Alta Frequência - 2000 km) ---
np.random.seed(42) # Usando uma semente fixa para resultados consistentes
num_pacotes = 10
distancia_km = 2000

# --- Eixo X (Pacotes) ---
# NOVO: Criar um array explícito para o eixo X, necessário para o polyfit
x_pacotes = np.arange(1, num_pacotes + 1)

# 1. Retardo (Delay) em segundos - ALTO e INSTÁVEL
retardo_hf = np.random.normal(loc=0.25, scale=0.05, size=num_pacotes)

# 2. Jitter (variação do retardo) em segundos - ALTO e INSTÁVEL
jitter_hf = np.abs(np.random.normal(loc=0.04, scale=0.02, size=num_pacotes))

# 3. Taxa de Transmissão (Throughput) em Mbps - BAIXA e FLUTUANTE
taxa_transmissao_hf = np.random.normal(loc=0.3, scale=0.1, size=num_pacotes)
taxa_transmissao_hf = np.clip(taxa_transmissao_hf, 0.05, 0.5)

# 4. Taxa de Erro (BER) - ALTA
taxa_erro_hf = np.random.normal(loc=0.05, scale=0.015, size=num_pacotes)
taxa_erro_hf = np.clip(taxa_erro_hf, 0.01, 0.1)

# --- Criação dos subplots (2x2) ---
fig, axs = plt.subplots(2, 2, figsize=(12, 8))
fig.suptitle(f"Métricas de Comunicação via HF (Simulação Estocástica - {distancia_km} km)", fontsize=14)

# --- Retardo ---
axs[0, 0].plot(x_pacotes, retardo_hf, marker='o', linestyle='-', markersize=4, color='tab:blue', alpha=0.6)
axs[0, 0].set_title("Retardo (Delay)")
axs[0, 0].set_ylabel("Segundos (s)")
axs[0, 0].axhline(y=0.300, color='r', linestyle='--', label='Limite (300 ms)')
# NOVO: Calcular e plotar a reta de tendência
coef_retardo = np.polyfit(x_pacotes, retardo_hf, 1)
tendencia_retardo = np.poly1d(coef_retardo)(x_pacotes)
axs[0, 0].plot(x_pacotes, tendencia_retardo, color='black', linestyle='--', label='Tendência')
axs[0, 0].legend()
axs[0, 0].grid(True, linestyle=':')

# --- Jitter ---
axs[0, 1].plot(x_pacotes, jitter_hf, marker='s', linestyle='-', markersize=4, color='tab:orange', alpha=0.6)
axs[0, 1].set_title("Jitter")
axs[0, 1].set_ylabel("Segundos (s)")
axs[0, 1].axhline(y=0.030, color='r', linestyle='--', label='Limite (30 ms)')
# NOVO: Calcular e plotar a reta de tendência
coef_jitter = np.polyfit(x_pacotes, jitter_hf, 1)
tendencia_jitter = np.poly1d(coef_jitter)(x_pacotes)
axs[0, 1].plot(x_pacotes, tendencia_jitter, color='black', linestyle='--', label='Tendência')
axs[0, 1].legend()
axs[0, 1].grid(True, linestyle=':')

# --- Taxa de Transmissão ---
axs[1, 0].plot(x_pacotes, taxa_transmissao_hf, marker='^', linestyle='-', markersize=4, color='tab:green', alpha=0.6)
axs[1, 0].set_title("Taxa de Transmissão (Throughput)")
axs[1, 0].set_ylabel("Mbps")
# NOVO: Calcular e plotar a reta de tendência
coef_taxa = np.polyfit(x_pacotes, taxa_transmissao_hf, 1)
tendencia_taxa = np.poly1d(coef_taxa)(x_pacotes)
axs[1, 0].plot(x_pacotes, tendencia_taxa, color='black', linestyle='--', label='Tendência')
axs[1, 0].legend()
axs[1, 0].grid(True, linestyle=':')

# --- Taxa de Erro ---
dados_taxa_erro = taxa_erro_hf * 100
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

print("\n--- Métricas Médias da Simulação HF ---")
print(f"Retardo médio: {np.mean(retardo_hf) * 1000:.2f} ms")
print(f"Jitter médio: {np.mean(jitter_hf) * 1000:.2f} ms")
print(f"Taxa de erro média: {np.mean(taxa_erro_hf) * 100:.2f} %")
print(f"Taxa de transmissão média: {np.mean(taxa_transmissao_hf) * 1000:.2f} kbps")