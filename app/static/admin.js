// app/static/admin.js
const statsGrid = document.getElementById("statsGrid");
const invitationsList = document.getElementById("invitationsList");
const responsesList = document.getElementById("responsesList");

// Формы
const invitationForm = document.getElementById("invitationForm");
const responseForm = document.getElementById("responseForm");

// Поля приглашений
const invitationIdInput = document.getElementById("invitationId");
const guestNameInput = document.getElementById("guestNameInput");
const inviteTextInput = document.getElementById("inviteTextInput");
const inviteCodeInput = document.getElementById("inviteCodeInput");

// Поля ответов
const responseIdInput = document.getElementById("responseId");
const responseInvitationSelect = document.getElementById("responseInvitationSelect");
const responseWillCome = document.getElementById("responseWillCome");
const responseComment = document.getElementById("responseComment");
const responseAllergies = document.getElementById("responseAllergies");
const responseAllergiesDetails = document.getElementById("responseAllergiesDetails");
const responseAlcohol = document.getElementById("responseAlcohol");
const responseAdditionalInfo = document.getElementById("responseAdditionalInfo");

// ---------- Утилиты ----------
async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Ошибка запроса");
  }
  return response.json();
}

function escapeHtml(value) {
  return String(value ?? "")
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// ---------- Рендеринг ----------
function renderStats(stats) {
  statsGrid.innerHTML = "";
  for (const [label, value] of Object.entries(stats)) {
    const card = document.createElement("div");
    card.className = "stats-card";
    card.innerHTML = `<h3>${label.replace(/_/g, " ")}</h3><p>${value}</p>`;
    statsGrid.appendChild(card);
  }
}

function renderInvitations(items) {
  const rows = items
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.guest_name)}</td>
          <td>${escapeHtml(item.invite_code)}</td>
          <td>${escapeHtml(item.created_at)}</td>
          <td>
            <button data-edit="${item.id}">Редактировать</button>
            <button data-delete="${item.id}">Удалить</button>
          </td>
        </tr>`
    )
    .join("");
  invitationsList.innerHTML = `<table><thead><tr><th>Гость</th><th>Код</th><th>Создано</th><th>Действия</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function renderResponses(items) {
  const rows = items
    .map(
      (item) => `
        <tr>
          <td>${escapeHtml(item.guest_name)}</td>
          <td>${item.will_come === "yes" ? "Да" : "Нет"}</td>
          <td>${escapeHtml(item.comment_will_come || "-")}</td>
          <td>${item.allergies ? "Да" : "Нет"}</td>
          <td>${escapeHtml(item.allergies_details || "-")}</td>
          <td>${item.alcohol ? "Да" : "Нет"}</td>
          <td>${escapeHtml(item.additional_info || "-")}</td>
          <td>${escapeHtml(item.answered_at)}</td>
          <td>
            <button data-edit-response="${item.id}">Редактировать</button>
            <button data-delete-response="${item.id}">Удалить</button>
          </td>
        </tr>`
    )
    .join("");
  responsesList.innerHTML = `<table><thead><tr><th>Гость</th><th>Придёт?</th><th>Пояснение</th><th>Аллергии</th><th>Описание</th><th>Алкоголь</th><th>Доп. инфо</th><th>Дата ответа</th><th>Действия</th></tr></thead><tbody>${rows}</tbody></table>`;
}

// ---------- Загрузка данных для селекта гостей ----------
async function populateGuestSelect() {
  try {
    const data = await fetchJson("/api/admin/invitations");
    const select = responseInvitationSelect;
    const currentValue = select.value;
    select.innerHTML = '<option value="">-- Выберите гостя --</option>';
    data.invitations.forEach((inv) => {
      const option = document.createElement("option");
      option.value = inv.id;
      option.textContent = `${inv.guest_name} (${inv.invite_code})`;
      select.appendChild(option);
    });
    if (currentValue) select.value = currentValue;
  } catch (e) {
    console.error("Не удалось загрузить список гостей", e);
  }
}

// ---------- Обновление всех данных ----------
async function refresh() {
  await Promise.all([
    fetchJson("/api/admin/stats").then(renderStats),
    fetchJson("/api/admin/invitations").then(data => renderInvitations(data.invitations)),
    fetchJson("/api/admin/responses").then(data => renderResponses(data.responses)),
  ]);
  await populateGuestSelect();
}

// ---------- Обработчики форм ----------

// Приглашения
invitationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    guest_name: guestNameInput.value.trim(),
    invitation_text: inviteTextInput.value.trim(),
    invite_code: inviteCodeInput.value.trim() || undefined,
  };
  try {
    const id = invitationIdInput.value;
    if (id) {
      await fetchJson(`/api/admin/invitations/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } else {
      await fetchJson("/api/admin/invitations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }
    invitationForm.reset();
    invitationIdInput.value = "";
    inviteCodeInput.value = "";
    await refresh();
  } catch (error) {
    alert(error.message);
  }
});

// Ответы
responseForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const invitationId = responseInvitationSelect.value;
  if (!invitationId) {
    alert("Выберите гостя");
    return;
  }
  const payload = {
    will_come: responseWillCome.value,
    comment_will_come: responseComment.value.trim(),
    allergies: responseAllergies.value === "yes",
    allergies_details: responseAllergiesDetails.value.trim(),
    alcohol: responseAlcohol.value === "yes",
    additional_info: responseAdditionalInfo.value.trim(),
  };
  try {
    const id = responseIdInput.value;
    if (id) {
      await fetchJson(`/api/admin/responses/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } else {
      await fetchJson(`/api/admin/responses?invitation_id=${invitationId}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }
    responseForm.reset();
    responseIdInput.value = "";
    await refresh();
  } catch (error) {
    alert(error.message);
  }
});

// ---------- Клики по таблицам ----------

// Приглашения
invitationsList.addEventListener("click", async (event) => {
  const editId = event.target.dataset.edit;
  const deleteId = event.target.dataset.delete;
  if (editId) {
    const invitations = (await fetchJson("/api/admin/invitations")).invitations;
    const item = invitations.find((invite) => invite.id === Number(editId));
    if (item) {
      invitationIdInput.value = item.id;
      guestNameInput.value = item.guest_name;
      inviteTextInput.value = item.invitation_text;
      inviteCodeInput.value = item.invite_code;
    }
  }
  if (deleteId) {
    if (confirm("Удалить приглашение?")) {
      await fetchJson(`/api/admin/invitations/${deleteId}`, { method: "DELETE" });
      await refresh();
    }
  }
});

// Ответы
responsesList.addEventListener("click", async (event) => {
  const editId = event.target.dataset.editResponse;
  const deleteId = event.target.dataset.deleteResponse;
  if (editId) {
    const responses = (await fetchJson("/api/admin/responses")).responses;
    const item = responses.find((r) => r.id === Number(editId));
    if (item) {
      responseIdInput.value = item.id;
      responseInvitationSelect.value = item.invitation_id;
      responseWillCome.value = item.will_come;
      responseComment.value = item.comment_will_come || "";
      responseAllergies.value = item.allergies ? "yes" : "no";
      responseAllergiesDetails.value = item.allergies_details || "";
      responseAlcohol.value = item.alcohol ? "yes" : "no";
      responseAdditionalInfo.value = item.additional_info || "";
    }
  }
  if (deleteId) {
    if (confirm("Удалить ответ?")) {
      await fetchJson(`/api/admin/responses/${deleteId}`, { method: "DELETE" });
      await refresh();
    }
  }
});

// ---------- Инициализация ----------
refresh().catch((error) => {
  document.body.innerHTML = `<div style="padding:40px;"><h2>Ошибка доступа</h2><p>${error.message}</p><p>Проверьте учетные данные администратора.</p></div>`;
});