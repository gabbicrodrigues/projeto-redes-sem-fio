# salva como sat_sim_corrigido.py e execute: python sat_sim_corrigido.py

import math
import random
import collections
import statistics
import sys

# ==============================
# PARÂMETROS GERAIS
# ==============================
SIM_TIME_MAX = 300.0        # s
DT = 0.001                  # passo de tempo (s)
PACKET_SIZE_BITS = 1024 * 8 # bits (1 KB payload)
C = 3e8                     # m/s

# Satélite LEO (simplificado)
EARTH_RADIUS = 6371e3       # m
ALTITUDE = 550e3            # m
ORBIT_RADIUS = EARTH_RADIUS + ALTITUDE
ORBITAL_PERIOD = 300.0      # s (reduzido para ver variação)

# Distância entre organizações
DIST_ORG = 2000e3           # m (2000 km)

# Links (nominais)
UPLINK_RATE = 20e6          # bps
DOWNLINK_RATE = 100e6       # bps
UPLINK_BUFFER_BITS = int(50e3 * 8)
DOWNLINK_BUFFER_BITS = int(50e3 * 8)

# BER nominal (placeholder — idealmente derivar de SNR/link budget)
BER = 1e-7

# Aplicações UDP
FLOW_INTERVAL = 0.1       # s
FLOW_START_A = 1.1
FLOW_START_B = 1.0
MAX_PKTS_PER_FLOW = 10000

# Ruídos / variações
ATMOSPHERIC_STD = 0.0005    # s
ORBITAL_STD = 0.0005        # s
DATARATE_FLUCT_PCT = 0.05   # 5%
PROCESSING_DELAY_MIN = 0.0002
PROCESSING_DELAY_MAX = 0.001

# ==============================
# AUXILIARES
# ==============================

def sat_position(t):
    angle = 2 * math.pi * (t % ORBITAL_PERIOD) / ORBITAL_PERIOD
    return ORBIT_RADIUS * math.cos(angle), ORBIT_RADIUS * math.sin(angle)

def propagation_delay(org_x, sat_pos):
    dx = org_x - sat_pos[0]
    dy = - sat_pos[1]
    # distância correta
    d = math.sqrt(dx*dx + dy*dy)
    return d / C

def packet_error_occurred(bits, ber):
    p = 1 - math.exp(-ber * bits)
    return random.random() < p

# ==============================
# CLASSES
# ==============================

class Link:
    """Link com buffer em bits e taxa nominal (bps)."""
    def __init__(self, datarate_bps_nominal, buffer_bits, name=""):
        self.nominal = datarate_bps_nominal
        self.buffer = collections.deque()
        self.buffer_capacity = buffer_bits
        self.buffer_occupancy = 0  # bits
        self.transmitting = None   # (packet, tx_start, tx_finish, rate)
        self.name = name

    def enqueue(self, packet, current_time):
        if self.buffer_occupancy + PACKET_SIZE_BITS <= self.buffer_capacity:
            self.buffer.append((packet, current_time))
            self.buffer_occupancy += PACKET_SIZE_BITS
            return True
        else:
            return False

    def start_transmission_if_idle(self, current_time):
        if self.transmitting is None and self.buffer:
            packet, enqueue_time = self.buffer.popleft()
            self.buffer_occupancy -= PACKET_SIZE_BITS
            fluct = 1.0 + random.uniform(-DATARATE_FLUCT_PCT, DATARATE_FLUCT_PCT)
            effective_rate = max(1e3, self.nominal * fluct)
            tx_time = PACKET_SIZE_BITS / effective_rate
            tx_finish = current_time + tx_time
            self.transmitting = (packet, current_time, tx_finish, effective_rate)

    def process_completion(self, current_time):
        if self.transmitting is not None:
            packet, tx_start, tx_finish, rate = self.transmitting
            if current_time >= tx_finish:
                self.transmitting = None
                return packet, tx_start, tx_finish, rate
        return None

class UdpFlow:
    def __init__(self, name, start_time):
        self.name = name
        self.start_time = start_time
        self.last_send_time = start_time - FLOW_INTERVAL
        self.sent = 0
        self.received = 0
        self.lost = 0
        self.delays = []
        self.send_times = []

    def should_send(self, t):
        return (self.sent < MAX_PKTS_PER_FLOW) and (t >= self.last_send_time + FLOW_INTERVAL)

    def send_packet(self, t):
        self.last_send_time = t
        self.sent += 1
        pkt = {"flow": self.name, "tx_time": t, "id": f"{self.name}_{self.sent}"}
        self.send_times.append(t)
        return pkt

# ==============================
# SIMULAÇÃO
# ==============================

def simulate(verbose=False):
    orgA_x = -DIST_ORG/2
    orgB_x =  DIST_ORG/2

    flowA = UdpFlow("AtoB", FLOW_START_A)
    flowB = UdpFlow("BtoA", FLOW_START_B)

    uplink_A_to_sat = Link(UPLINK_RATE, UPLINK_BUFFER_BITS, name="uplink_A")
    downlink_sat_to_B = Link(DOWNLINK_RATE, DOWNLINK_BUFFER_BITS, name="downlink_B")

    uplink_B_to_sat = Link(UPLINK_RATE, UPLINK_BUFFER_BITS, name="uplink_B")
    downlink_sat_to_A = Link(DOWNLINK_RATE, DOWNLINK_BUFFER_BITS, name="downlink_A")

    # pacotes em voo (propagação): list of (arrival_time, packet, dest_flow)
    in_flight = []

    t = 0.0
    steps = 0

    while True:
        # parada
        both_sent = (flowA.sent >= MAX_PKTS_PER_FLOW) and (flowB.sent >= MAX_PKTS_PER_FLOW)
        links_idle = (not uplink_A_to_sat.buffer and uplink_A_to_sat.transmitting is None and
                      not downlink_sat_to_B.buffer and downlink_sat_to_B.transmitting is None and
                      not uplink_B_to_sat.buffer and uplink_B_to_sat.transmitting is None and
                      not downlink_sat_to_A.buffer and downlink_sat_to_A.transmitting is None)
        if both_sent and links_idle and not in_flight:
            break
        if t > SIM_TIME_MAX:
            print("Tempo máximo atingido.")
            break

        sat_pos = sat_position(t)

        # gerar pacotes
        if flowA.should_send(t):
            pkt = flowA.send_packet(t)
            ok = uplink_A_to_sat.enqueue(pkt, t)
            if not ok:
                flowA.lost += 1
                if verbose: print(f"[{t:.3f}] UPLINK A buffer cheio: {pkt['id']} perdido")

        if flowB.should_send(t):
            pkt = flowB.send_packet(t)
            ok = uplink_B_to_sat.enqueue(pkt, t)
            if not ok:
                flowB.lost += 1
                if verbose: print(f"[{t:.3f}] UPLINK B buffer cheio: {pkt['id']} perdido")

        # iniciar transmissões
        uplink_A_to_sat.start_transmission_if_idle(t)
        uplink_B_to_sat.start_transmission_if_idle(t)
        downlink_sat_to_B.start_transmission_if_idle(t)
        downlink_sat_to_A.start_transmission_if_idle(t)

        # processar completions uplink A->sat
        comp = uplink_A_to_sat.process_completion(t)
        if comp is not None:
            packet, tx_start, tx_finish, rate = comp
            # sat recebe; agora enfileira no downlink_sat_to_B
            # processamento no satélite
            processing = random.uniform(PROCESSING_DELAY_MIN, PROCESSING_DELAY_MAX)
            # propagation delay sat->B
            delay_down = propagation_delay(orgB_x, sat_pos)
            # apply small noise
            atm_noise = random.gauss(0.0, ATMOSPHERIC_STD)
            orbital_noise = random.gauss(0.0, ORBITAL_STD)
            total_delay = max(0.0, processing + delay_down + atm_noise + orbital_noise)
            arrival_time_at_downlink = t  # time when downlink enqueue attempt occurs (sat ready)
            # simulate bit errors on the uplink first (could be applied on either hop)
            lost = packet_error_occurred(PACKET_SIZE_BITS, BER)
            if lost:
                flowA.lost += 1
                if verbose: print(f"[{t:.6f}] Pacote {packet['id']} corrompido no uplink.")
            else:
                # enqueue on downlink; but we keep the final arrival_time after tx of downlink
                ok = downlink_sat_to_B.enqueue((packet, arrival_time_at_downlink, total_delay), t)
                if not ok:
                    # buffer do downlink cheio -> perda
                    flowA.lost += 1
                    if verbose: print(f"[{t:.6f}] DOWNLINK B buffer cheio: {packet['id']} perdido no sat.")
        # process completion downlink sat->B
        comp = downlink_sat_to_B.process_completion(t)
        if comp is not None:
            packet_wrapped, tx_start, tx_finish, rate = comp
            # packet_wrapped is (packet, enqueue_time_at_sat, extra_delay)
            packet, enqueue_time_at_sat, extra_delay = packet_wrapped
            # now schedule flight/arrival after the extra_delay used earlier (propagation)
            arrival_time = t + extra_delay
            # apply BER on downlink hop
            lost = packet_error_occurred(PACKET_SIZE_BITS, BER)
            if lost:
                flowA.lost += 1
                if verbose: print(f"[{t:.6f}] Pacote {packet['id']} corrompido no downlink.")
            else:
                in_flight.append((arrival_time, packet, "B"))

        # symmetric for B->A
        comp = uplink_B_to_sat.process_completion(t)
        if comp is not None:
            packet, tx_start, tx_finish, rate = comp
            processing = random.uniform(PROCESSING_DELAY_MIN, PROCESSING_DELAY_MAX)
            delay_down = propagation_delay(orgA_x, sat_pos)
            atm_noise = random.gauss(0.0, ATMOSPHERIC_STD)
            orbital_noise = random.gauss(0.0, ORBITAL_STD)
            total_delay = max(0.0, processing + delay_down + atm_noise + orbital_noise)
            lost = packet_error_occurred(PACKET_SIZE_BITS, BER)
            if lost:
                flowB.lost += 1
                if verbose: print(f"[{t:.6f}] Pacote {packet['id']} corrompido no uplink B.")
            else:
                ok = downlink_sat_to_A.enqueue((packet, t, total_delay), t)
                if not ok:
                    flowB.lost += 1
                    if verbose: print(f"[{t:.6f}] DOWNLINK A buffer cheio: {packet['id']} perdido no sat.")
        comp = downlink_sat_to_A.process_completion(t)
        if comp is not None:
            packet_wrapped, tx_start, tx_finish, rate = comp
            packet, enqueue_time_at_sat, extra_delay = packet_wrapped
            arrival_time = t + extra_delay
            lost = packet_error_occurred(PACKET_SIZE_BITS, BER)
            if lost:
                flowB.lost += 1
                if verbose: print(f"[{t:.6f}] Pacote {packet['id']} corrompido no downlink A.")
            else:
                in_flight.append((arrival_time, packet, "A"))

        # processar chegadas
        if in_flight:
            in_flight.sort(key=lambda x: x[0])
            arrived_now = [it for it in in_flight if it[0] <= t + 1e-12]
            if arrived_now:
                in_flight = [it for it in in_flight if it[0] > t + 1e-12]
                for arr_time, packet, dest in arrived_now:
                    if dest == "B":
                        flowA.received += 1
                        delay = arr_time - packet["tx_time"]
                        flowA.delays.append(delay)
                        if verbose: print(f"[{t:.6f}] {packet['id']} chegou B delay={delay*1000:.3f} ms")
                    else:
                        flowB.received += 1
                        delay = arr_time - packet["tx_time"]
                        flowB.delays.append(delay)
                        if verbose: print(f"[{t:.6f}] {packet['id']} chegou A delay={delay*1000:.3f} ms")

        t += DT
        steps += 1

    # métricas por fluxo
    def compute_metrics(flow):
        delays = flow.delays
        avg_delay = statistics.mean(delays) if delays else 0.0
        std_delay = statistics.pstdev(delays) if len(delays) > 1 else 0.0
        if len(delays) > 1:
            jitter_vals = [abs(delays[i+1] - delays[i]) for i in range(len(delays)-1)]
            avg_jitter = statistics.mean(jitter_vals)
        else:
            avg_jitter = 0.0
        throughput_bps = (flow.received * PACKET_SIZE_BITS) / t
        return {
            "sent": flow.sent,
            "received": flow.received,
            "lost": flow.lost,
            "loss_pct": 100.0 * flow.lost / max(1, flow.sent),
            "avg_delay_ms": avg_delay * 1000.0,
            "std_delay_ms": std_delay * 1000.0,
            "avg_jitter_ms": avg_jitter * 1000.0,
            "throughput_mbps": throughput_bps / 1e6,
            "delays_ms": [d*1000 for d in delays]
        }

    resA = compute_metrics(flowA)
    resB = compute_metrics(flowB)
    results = {
        "time_simulated_s": t,
        "steps": steps,
        "A": resA,
        "B": resB,
    }
    return results

if __name__ == "__main__":
    random.seed(42)
    res = simulate(verbose=False)
    print("=== RESULTADOS ===")
    print(f"Tempo simulado: {res['time_simulated_s']:.3f} s em {res['steps']} passos")
    for dir_name in ("A", "B"):
        r = res[dir_name]
        print(f"\nFluxo {dir_name}:")
        print(f"  Enviados: {r['sent']}, Recebidos: {r['received']}, Perdidos: {r['lost']} ({r['loss_pct']:.3f}%)")
        print(f"  Atraso médio: {r['avg_delay_ms']:.3f} ms  | Jitter médio: {r['avg_jitter_ms']:.3f} ms")
        print(f"  Throughput observado: {r['throughput_mbps']:.6f} Mbps")
