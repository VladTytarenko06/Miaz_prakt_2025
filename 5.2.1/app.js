// Дані НАТО та ЗСУ
const data = {
    NATO: {
        totalModels: 14,
        integration: 87,
        automation: 72,
        training: 74,
        models: [
            { name: "JCATS", type: "Оперативна", level: "Корпус", status: "Використовується" },
            { name: "JTLS-GO", type: "Стратегічна", level: "Оперативний", status: "Використовується" },
            { name: "OneSAF", type: "Тактична", level: "Батальйон", status: "Розгорнута" },
            { name: "JEMM", type: "Оперативна", level: "Бригада", status: "Актуальна" }
        ],
        bars: { strategic: 82, operational: 75, tactical: 71 }
    },

    UA: {
        totalModels: 5,
        integration: 63,
        automation: 48,
        training: 59,
        models: [
            { name: "Dnipro Simulation", type: "Оперативна", level: "Бригада", status: "Модернізується" },
            { name: "ОК Комплекси", type: "Тактична", level: "Батальйон", status: "Використовується" },
            { name: "Оперативні моделі", type: "Оперативна", level: "Командування", status: "У розробці" }
        ],
        bars: { strategic: 40, operational: 55, tactical: 50 }
    }
};


// === ВКЛАДКИ ===
function openTab(tabName, element) {
    document.querySelectorAll(".tab").forEach(el => el.classList.remove("active-tab"));
    document.querySelectorAll(".tab-btn").forEach(el => el.classList.remove("active"));

    document.getElementById(tabName).classList.add("active-tab");
    element.classList.add("active");
}


// === ПЕРЕМИКАЧ НАТО/ЗСУ ===
function renderDashboard() {
    const src = document.getElementById("sourceSelect").value;
    const d = data[src];

    document.getElementById("totalModels").innerText = d.totalModels;
    document.getElementById("integration").innerText = d.integration + "%";
    document.getElementById("automation").innerText = d.automation + "%";
    document.getElementById("training").innerText = d.training + "%";

    renderTable(d.models);
    renderBars(d.bars);
    renderCharts();
}


// === ТАБЛИЦЯ ===
function renderTable(models) {
    const table = document.getElementById("modelTable");
    table.innerHTML = "";

    models.forEach(m => {
        table.innerHTML += `
            <tr>
                <td>${m.name}</td>
                <td>${m.type}</td>
                <td>${m.level}</td>
                <td>${m.status}</td>
            </tr>
        `;
    });
}


// === ПРОГРЕС БАРИ ===
function renderBars(b) {
    document.getElementById("chartBars").innerHTML = `
        <div>
            <div>Стратегічні</div>
            <div class="dynamic-bar">
                <div class="dynamic-fill fill-green" style="width:${b.strategic}%"></div>
            </div>

            <div>Оперативні</div>
            <div class="dynamic-bar">
                <div class="dynamic-fill fill-yellow" style="width:${b.operational}%"></div>
            </div>

            <div>Тактичні</div>
            <div class="dynamic-bar">
                <div class="dynamic-fill fill-red" style="width:${b.tactical}%"></div>
            </div>
        </div>
    `;
}


// === ГРАФІКИ (Chart.js) ===
let lineChart, barChart, radarChart;

function destroyCharts() {
    if (lineChart) lineChart.destroy();
    if (barChart) barChart.destroy();
    if (radarChart) radarChart.destroy();
}

function renderCharts() {
    destroyCharts();

    const ctx1 = document.getElementById("lineChart");
    const ctx2 = document.getElementById("barChart");
    const ctx3 = document.getElementById("radarChart");

    lineChart = new Chart(ctx1, {
        type: "line",
        data: {
            labels: ["2018", "2019", "2020", "2021", "2022", "2023"],
            datasets: [{
                label: "НАТО",
                data: [60, 62, 65, 70, 75, 87],
                borderColor: "#8acb61",
                fill: false
            },
            {
                label: "ЗСУ",
                data: [30, 35, 38, 41, 47, 63],
                borderColor: "#cbb757",
                fill: false
            }]
        }
    });

    barChart = new Chart(ctx2, {
        type: "bar",
        data: {
            labels: ["Стратегічні", "Оперативні", "Тактичні"],
            datasets: [{
                label: "НАТО",
                data: [82, 75, 71],
                backgroundColor: "#8acb61"
            },
            {
                label: "ЗСУ",
                data: [40, 55, 50],
                backgroundColor: "#cbb757"
            }]
        }
    });

    radarChart = new Chart(ctx3, {
        type: "radar",
        data: {
            labels: ["Інтеграція", "Автоматизація", "Підготовленість"],
            datasets: [{
                label: "НАТО",
                data: [87, 72, 74],
                borderColor: "#8acb61",
                backgroundColor: "rgba(138,203,97,0.3)"
            },
            {
                label: "ЗСУ",
                data: [63, 48, 59],
                borderColor: "#cbb757",
                backgroundColor: "rgba(203,183,87,0.3)"
            }]
        }
    });
}


// === ПЕРШЕ ЗАВАНТАЖЕННЯ ===
renderDashboard();
