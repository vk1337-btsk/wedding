const guestNameEl = document.getElementById("guestName");
const inviteTextEl = document.getElementById("inviteText");
const programListEl = document.getElementById("programList");
const carouselEl = document.getElementById("carousel");
const prevButton = document.getElementById("prevPhoto");
const nextButton = document.getElementById("nextPhoto");
const rsvpForm = document.getElementById("rsvpForm");
const thankYouMessage = document.getElementById("thankYouMessage");
const guestCountWrapper = document.getElementById("guestCountWrapper");
const attendanceRadios = Array.from(document.querySelectorAll("input[name='attendance']"));

let photos = [];
let activePhotoIndex = 0;
let inviteCode = null;

function getInviteCode() {
  const parts = window.location.pathname.split("/").filter(Boolean);
  if (parts.length === 2 && parts[0] === "invite") {
    return parts[1];
  }
  return null;
}

function updateTimer(targetDate) {
  const now = new Date();
  const distance = new Date(targetDate).getTime() - now.getTime();
  const days = Math.max(0, Math.floor(distance / (1000 * 60 * 60 * 24)));
  const hours = Math.max(0, Math.floor((distance / (1000 * 60 * 60)) % 24));
  const minutes = Math.max(0, Math.floor((distance / (1000 * 60)) % 60));
  const seconds = Math.max(0, Math.floor((distance / 1000) % 60));
  document.getElementById("days").textContent = String(days).padStart(2, "0");
  document.getElementById("hours").textContent = String(hours).padStart(2, "0");
  document.getElementById("minutes").textContent = String(minutes).padStart(2, "0");
  document.getElementById("seconds").textContent = String(seconds).padStart(2, "0");
}

function renderProgram(program) {
  programListEl.innerHTML = "";
  if (!program || program.length === 0) {
    programListEl.innerHTML = "<li>Программа будет доступна позже.</li>";
    return;
  }
  program.forEach((item) => {
    const li = document.createElement("li");
    li.innerHTML = `<strong>${item.event_time}</strong> — ${item.title}`;
    programListEl.appendChild(li);
  });
}

function renderPhotos(list) {
  photos = list;
  if (photos.length === 0) {
    carouselEl.innerHTML = "<p>Фотографии будут добавлены позже.</p>";
    return;
  }
  activePhotoIndex = 0;
  showPhoto(activePhotoIndex);
}

function showPhoto(index) {
  if (!photos.length) return;
  const photo = photos[index];
  carouselEl.innerHTML = `<img src="${photo.url}" alt="Свадебная фотография" />`;
}

function nextPhoto() {
  if (!photos.length) return;
  activePhotoIndex = (activePhotoIndex + 1) % photos.length;
  showPhoto(activePhotoIndex);
}

function prevPhoto() {
  if (!photos.length) return;
  activePhotoIndex = (activePhotoIndex - 1 + photos.length) % photos.length;
  showPhoto(activePhotoIndex);
}

function setResponseState(response) {
  rsvpForm.hidden = !!response;
  thankYouMessage.hidden = !response;
}

function updateGuestCountVisibility() {
  const selected = document.querySelector("input[name='attendance']:checked").value === "true";
  guestCountWrapper.style.display = selected ? "block" : "none";
}

attendanceRadios.forEach((radio) => {
  radio.addEventListener("change", updateGuestCountVisibility);
});

rsvpForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const formData = new FormData(rsvpForm);
  const data = {
    attendance: formData.get("attendance") === "true",
    guest_count: Number(formData.get("guest_count")) || null,
    children: formData.get("children") === "true",
    vegetarian: formData.get("vegetarian") === "true",
    allergies: formData.get("allergies")?.toString().trim() || "",
    phone: formData.get("phone")?.toString().trim() || "",
    telegram: formData.get("telegram")?.toString().trim() || "",
    comment: formData.get("comment")?.toString().trim() || "",
  };

  if (!inviteCode) {
    alert("Неверная ссылка.");
    return;
  }

  try {
    const response = await fetch(`/api/respond/${inviteCode}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const body = await response.json();
      alert(body.detail || "Не удалось отправить ответ.");
      return;
    }
    setResponseState(true);
  } catch (error) {
    alert("Ошибка отправки. Попробуйте позже.");
  }
});

async function loadInvitation() {
  inviteCode = getInviteCode();
  if (!inviteCode) {
    // Общая публичная страница — без формы RSVP
    try {
      const site = await fetch(`/api/site`).then((r) => r.json());
      guestNameEl.textContent = "Алёна & Валерий";
      inviteTextEl.textContent = `Мы будем рады видеть вас на нашем празднике в ${site.venue_name}, ${site.venue_address}. Для отправки RSVP используйте персональную ссылку из приглашения.`;
      // загрузить программу и фото в общем виде
      const program = await fetch(`/api/program`).then((r) => r.json()).then((j) => j.program);
      const photos = await fetch(`/api/photos`).then((r) => r.json()).then((j) => j.photos);
      renderProgram(program);
      renderPhotos(photos);
      // скрыть форму RSVP
      rsvpForm.hidden = true;
      document.getElementById("generalNote").hidden = false;
      const countdownTarget = new Date(site.wedding_date);
      updateTimer(countdownTarget);
      setInterval(() => updateTimer(countdownTarget), 1000);
    } catch (err) {
      guestNameEl.textContent = "Приглашение";
      inviteTextEl.textContent = "Информация о событии временно недоступна.";
    }
    return;
  }

  const response = await fetch(`/api/invite/${inviteCode}`);
  if (!response.ok) {
    guestNameEl.textContent = "Приглашение не найдено";
    inviteTextEl.textContent = "Пожалуйста, свяжитесь с организатором.";
    return;
  }
  const data = await response.json();
  guestNameEl.textContent = data.invitation.guest_name;
  inviteTextEl.textContent = data.invitation.invitation_text;
  renderProgram(data.program);
  renderPhotos(data.photos);
  setResponseState(data.response);
  updateTimer(data.invitation.created_at || new Date().toISOString());
  const targetDate = new Date(data.invitation.created_at || new Date().toISOString());
  if (data.invitation && data.invitation.created_at) {
    const countdownDate = new Date(document.querySelector(".hero-date").textContent || new Date());
  }
  const countdownTarget = new Date("2026-09-01T15:00:00");
  updateTimer(countdownTarget);
  setInterval(() => updateTimer(countdownTarget), 1000);
}

prevButton.addEventListener("click", prevPhoto);
nextButton.addEventListener("click", nextPhoto);
loadInvitation();
