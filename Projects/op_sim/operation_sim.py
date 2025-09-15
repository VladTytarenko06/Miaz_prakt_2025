# operation_sim.py
# Модель імітації наступальної операції (3 фази) з Монте‑Карло
# Працює як окремий файл: достатньо "python operation_sim.py"
# Друкує середні метрики та ймовірність успіху; графік — опційно.

import random
from dataclasses import dataclass
from typing import List, Tuple, Dict

import numpy as np

# Спроба підключити matplotlib для графіка (не обов'язково)
try:
    import matplotlib.pyplot as plt
    HAS_MPL = True
except Exception:
    HAS_MPL = False


@dataclass
class Unit:
    name: str
    strength: float   # чисельність
    morale: float     # [0..1]
    firepower: float  # відносна вогнева міць


def initialize_units() -> Tuple[List[Unit], List[Unit]]:
    """Початкові сили сторін (можна змінювати під свій сценарій)."""
    ukr_units = [
        Unit("Ukr_Mech_1", 1500, 0.9, 0.8),
        Unit("Ukr_Tank_2", 1200, 0.9, 1.2),
        Unit("Ukr_Inf_3", 1000, 0.8, 0.6),
    ]
    rus_units = [
        Unit("Rus_Defense_1", 2000, 0.8, 0.9),
        Unit("Rus_Reserve_2", 1500, 0.7, 1.1),
    ]
    return ukr_units, rus_units


def simulate_battle(ukr_units: List[Unit], rus_units: List[Unit]) -> Tuple[int, int]:
    """Одна сутичка з випадковістю, оновленням чисельності та моралі."""
    # Базові втрати залежать від (1 - morale) та випадковості
    ukr_losses_base = sum(
        u.strength * (1 - u.morale) * random.uniform(0.01, 0.05) for u in ukr_units
    )
    rus_losses_base = sum(
        u.strength * (1 - u.morale) * random.uniform(0.01, 0.05) for u in rus_units
    )

    # Корекція на середню вогневу міць сторін
    avg_ukr_fp = sum(u.firepower for u in ukr_units) / max(1, len(ukr_units))
    avg_rus_fp = sum(u.firepower for u in rus_units) / max(1, len(rus_units))

    final_ukr_losses = max(0, int(rus_losses_base * (1.1 - avg_ukr_fp)))
    final_rus_losses = max(0, int(ukr_losses_base * (1.1 - avg_rus_fp)))

    # Розподіл втрат пропорційно поточній чисельності
    for units, total in ((ukr_units, final_ukr_losses), (rus_units, final_rus_losses)):
        if total <= 0:
            continue
        total_strength = sum(u.strength for u in units) or 1.0
        for u in units:
            share = total * (u.strength / total_strength)
            u.strength = max(0.0, u.strength - share)

    # Оновлення моралі (чим більші втрати, тим сильніше падіння; є нижній поріг)
    def update_morale(units: List[Unit], total_losses: float) -> None:
        total_strength = sum(u.strength for u in units) or 1.0
        loss_ratio = (total_losses / total_strength) / 10.0  # помірний вплив
        for u in units:
            u.morale = max(0.2, u.morale * (1 - loss_ratio))

    update_morale(ukr_units, final_ukr_losses)
    update_morale(rus_units, final_rus_losses)

    return final_ukr_losses, final_rus_losses


def run_sim(
    num_simulations: int = 1000,
    logistics_success_rate: float = 0.8,
    seed: int | None = None,
    make_plot: bool = False,
) -> Dict[str, float]:
    """Повний цикл Монте‑Карло з 3 фазами на ітерацію."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    ukr_final: list[float] = []
    rus_final: list[float] = []

    for _ in range(num_simulations):
        ukr_units, rus_units = initialize_units()

        # Фаза 1: прорив
        simulate_battle(ukr_units, rus_units)

        # Фаза 2: розвиток наступу + логістика (може підвищити firepower ЗСУ)
        if random.random() < logistics_success_rate:
            for u in ukr_units:
                u.firepower *= 1.1
        simulate_battle(ukr_units, rus_units)

        # Фаза 3: бій за ключовий об'єкт
        simulate_battle(ukr_units, rus_units)

        ukr_final.append(sum(u.strength for u in ukr_units))
        rus_final.append(sum(u.strength for u in rus_units))

    ukr_final = np.array(ukr_final, dtype=float)
    rus_final = np.array(rus_final, dtype=float)

    win_probability = float(np.mean(ukr_final > rus_final))
    avg_ukr_strength = float(ukr_final.mean())
    avg_rus_strength = float(rus_final.mean())

    if make_plot and HAS_MPL:
        # Розподіл різниці (ЗСУ - противник)
        diff = ukr_final - rus_final
        plt.figure()
        plt.hist(diff, bins=50)
        plt.title("Розподіл переваги (ЗСУ - противник) по ітераціях")
        plt.xlabel("Різниця кінцевої чисельності")
        plt.ylabel("Кількість симуляцій")
        plt.show()

    return {
        "avg_ukr_strength": avg_ukr_strength,
        "avg_rus_strength": avg_rus_strength,
        "win_probability": win_probability,
    }


if __name__ == "__main__":
    # Запуск зі стандартними параметрами; графік вимкнено за замовчуванням
    res = run_sim(num_simulations=1000, logistics_success_rate=0.8, seed=None, make_plot=False)
    print(f"Середня кінцева чисельність ЗСУ: {res['avg_ukr_strength']:.2f}")
    print(f"Середня кінцева чисельність противника: {res['avg_rus_strength']:.2f}")
    print(f"Ймовірність успішного завершення операції: {res['win_probability']:.2%}")
