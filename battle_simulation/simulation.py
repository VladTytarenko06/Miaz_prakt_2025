import numpy as np
import random
import matplotlib.pyplot as plt

def run_simulation(ukr_start_forces, rus_start_forces, hours):
    ukr_losses = []
    rus_losses = []

    ukr_forces = ukr_start_forces
    rus_forces = rus_start_forces

    for h in range(hours):
        # Розрахунок втрат
        ukr_lost_this_hour = int(ukr_forces * 0.05 * random.uniform(0.5, 1.5))
        rus_lost_this_hour = int(rus_forces * 0.07 * random.uniform(0.5, 1.5))

        ukr_forces -= ukr_lost_this_hour
        rus_forces -= rus_lost_this_hour

        ukr_losses.append(ukr_lost_this_hour)
        rus_losses.append(rus_lost_this_hour)

        # Умова завершення бою
        if ukr_forces <= 0 or rus_forces <= 0:
            break

    return ukr_losses, rus_losses


# --- Запуск симуляції ---
ukr_start = 1000
rus_start = 1200
hours = 50

ukr_losses, rus_losses = run_simulation(ukr_start, rus_start, hours)

# Кумулятивні втрати
ukr_cum_losses = np.cumsum(ukr_losses)
rus_cum_losses = np.cumsum(rus_losses)

# --- Побудова графіка ---
plt.figure(figsize=(10, 6))
plt.plot(ukr_cum_losses, label="Втрати України", linewidth=2)
plt.plot(rus_cum_losses, label="Втрати РФ", linewidth=2)
plt.xlabel("Години бою")
plt.ylabel("Кумулятивні втрати")
plt.title("Імітація бойових втрат")
plt.legend()
plt.grid(True)
plt.show()
