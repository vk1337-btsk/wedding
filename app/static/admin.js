const statsGrid = document.getElementById("statsGrid");
const invitationsList = document.getElementById("invitationsList");
const responsesList = document.getElementById("responsesList");
const photosList = document.getElementById("photosList");
const programList = document.getElementById("programList");
const invitationForm = document.getElementById("invitationForm");
const programForm = document.getElementById("programForm");
const photoForm = document.getElementById("photoForm");

const invitationIdInput = document.getElementById("invitationId");
const guestNameInput = document.getElementById("guestNameInput");
const inviteTextInput = document.getElementById("inviteTextInput");
const inviteCodeInput = document.getElementById("inviteCodeInput");
const programItemIdInput = document.getElementById("programItemId");
const programTimeInput = document.getElementById("programTimeInput");
const programTitleInput = document.getElementById("programTitleInput");
const photoFileInput = document.getElementById("photoFileInput");

async function fetchJson(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    const err = await response.json().catch(() => ({}));
    throw new Error(err.detail || "Ошибка запроса");
  }
  return response.json();
}

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
          <td>${item.guest_name}</td>
          <td>${item.invite_code}</td>
          <td>${item.created_at}</td>
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
          <td>${item.guest_name}</td>
          <td>${item.attendance ? "Да" : "Нет"}</td>
          <td>${item.guest_count || 0}</td>
          <td>${item.children ? "Да" : "Нет"}</td>
          <td>${item.vegetarian ? "Да" : "Нет"}</td>
          <td>${item.allergies || "-"}</td>
          <td>${item.phone || "-"}</td>
          <td>${item.telegram || "-"}</td>
          <td>${item.comment || "-"}</td>
          <td>${item.answered_at}</td>
        </tr>`
    )
    .join("");
  responsesList.innerHTML = `<table><thead><tr><th>Гость</th><th>Придут</th><th>Гостей</th><th>Дети</th><th>Вегет.</th><th>Аллергии</th><th>Телефон</th><th>Telegram</th><th>Комментарий</th><th>Дата</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function renderPhotos(items) {
  const rows = items
    .map(
      (item) => `
        <tr>
          <td><img style="width:120px; border-radius:14px;" src="${item.url}" alt="photo" /></td>
          <td>${item.original_filename}</td>
          <td>${item.sort_order}</td>
          <td>${item.uploaded_at}</td>
          <td><button data-delete-photo="${item.id}">Удалить</button></td>
        </tr>`
    )
    .join("");
  photosList.innerHTML = `<table><thead><tr><th>Превью</th><th>Имя файла</th><th>Порядок</th><th>Загружен</th><th>Действия</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function renderProgram(items) {
  const rows = items
    .map(
      (item) => `
        <tr>
          <td>${item.event_time}</td>
          <td>${item.title}</td>
          <td>${item.sort_order}</td>
          <td>
            <button data-edit-program="${item.id}">Изменить</button>
            <button data-delete-program="${item.id}">Удалить</button>
          </td>
        </tr>`
    )
    .join("");
  programList.innerHTML = `<table><thead><tr><th>Время</th><th>Описание</th><th>Порядок</th><th>Действия</th></tr></thead><tbody>${rows}</tbody></table>`;
}

async function refresh() {
  renderStats(await fetchJson("/api/admin/stats"));
  renderInvitations((await fetchJson("/api/admin/invitations")).invitations);
  renderResponses((await fetchJson("/api/admin/responses")).responses);
  renderPhotos((await fetchJson("/api/admin/photos")).photos);
  renderProgram((await fetchJson("/api/admin/program")).program);
}

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

programForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    event_time: programTimeInput.value.trim(),
    title: programTitleInput.value.trim(),
    sort_order: 100,
  };
  try {
    const id = programItemIdInput.value;
    if (id) {
      await fetchJson(`/api/admin/program/${id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    } else {
      await fetchJson("/api/admin/program", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
    }
    programForm.reset();
    programItemIdInput.value = "";
    await refresh();
  } catch (error) {
    alert(error.message);
  }
});

photoForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const file = photoFileInput.files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("file", file);
  try {
    await fetchJson("/api/admin/photos", {
      method: "POST",
      body: formData,
    });
    photoForm.reset();
    await refresh();
  } catch (error) {
    alert(error.message);
  }
});

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

photosList.addEventListener("click", async (event) => {
  const deleteId = event.target.dataset.deletePhoto;
  if (deleteId && confirm("Удалить фотографию?")) {
    await fetchJson(`/api/admin/photos/${deleteId}`, { method: "DELETE" });
    await refresh();
  }
});

programList.addEventListener("click", async (event) => {
  const editId = event.target.dataset.editProgram;
  const deleteId = event.target.dataset.deleteProgram;
  if (editId) {
    const program = (await fetchJson("/api/admin/program")).program;
    const item = program.find((entry) => entry.id === Number(editId));
    if (item) {
      programItemIdInput.value = item.id;
      programTimeInput.value = item.event_time;
      programTitleInput.value = item.title;
    }
  }
  if (deleteId && confirm("Удалить этап программы?")) {
    await fetchJson(`/api/admin/program/${deleteId}`, { method: "DELETE" });
    await refresh();
  }
});

refresh().catch((error) => {
  document.body.innerHTML = `<div style="padding:40px;"><h2>Ошибка доступа</h2><p>${error.message}</p><p>Проверьте учетные данные администратора.</p></div>`;
});
