const form = document.getElementById("car-form");
const message = document.getElementById("message");
const tableBody = document.getElementById("car-list");

function showMessage(text, isError = false) {
  message.textContent = text;
  message.className = isError ? "warning" : "info";
}

async function loadData() {
  try {
    const [carsResponse, statsResponse] = await Promise.all([
      fetch("/api/cars"),
      fetch("/api/stats"),
    ]);
    if (!carsResponse.ok || !statsResponse.ok) {
      throw new Error("Server unavailable");
    }
    const cars = await carsResponse.json();
    const stats = await statsResponse.json();

    document.getElementById("count").textContent = stats.inside;
    document.getElementById("capacity").textContent = stats.capacity;

    const alert = document.getElementById("capacity-alert");
    alert.textContent = stats.full ? "PARKING FULL!" : "Spaces available";
    alert.className = stats.full ? "warning" : "info";

    tableBody.replaceChildren();
    for (const car of cars) {
      const row = document.createElement("tr");
      for (const value of [car.plate, car.category, car.entry_time]) {
        const cell = document.createElement("td");
        cell.textContent = value;
        row.appendChild(cell);
      }
      const actionCell = document.createElement("td");
      const button = document.createElement("button");
      button.textContent = "Release";
      button.addEventListener("click", () => releaseCar(car.plate));
      actionCell.appendChild(button);
      row.appendChild(actionCell);
      tableBody.appendChild(row);
    }
  } catch (error) {
    showMessage("Cannot reach the server. Check Docker containers.", true);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const plate = document.getElementById("plate").value.trim();
  const category = document.getElementById("category").value;
  try {
    const response = await fetch("/api/cars", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ plate, category }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not add car");
    showMessage(`Car ${result.plate} entered successfully.`);
    form.reset();
    await loadData();
  } catch (error) {
    showMessage(error.message, true);
  }
});

async function releaseCar(plate) {
  try {
    const response = await fetch(`/api/cars/${encodeURIComponent(plate)}/exit`, {
      method: "POST",
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not release car");
    showMessage(result.message);
    await loadData();
  } catch (error) {
    showMessage(error.message, true);
  }
}

loadData();
setInterval(loadData, 3000);
