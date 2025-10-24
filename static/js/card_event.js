document.addEventListener("DOMContentLoaded", () => {
  console.log("card_event.js loaded");
  attachBookmarkHandlers();
});

function attachBookmarkHandlers() {
  const buttons = document.querySelectorAll(".bookmark-btn");
  console.log("Bookmark buttons found:", buttons.length);

  buttons.forEach((btn) => {
    btn.addEventListener("click", async () => {
      const eventId = btn.dataset.eventId;
      console.log("Clicked bookmark for event:", eventId);

      try {
        const response = await fetch(`/bookmark/${eventId}/`, {
          method: "POST",
          headers: { "X-CSRFToken": getCookie("csrftoken") },
        });

        console.log("Response:", response.status);

        if (response.redirected) {
          window.location.href = response.url;
          return;
        }

        const data = await response.json();
        console.log("Data:", data);

        // Ubah ikon sesuai status
        if (data.status === "added") {
          btn.classList.add("active");
          btn.querySelector(".bookmark-icon").src = "/static/icons/bookmark-toggle.png";
        } else {
          btn.classList.remove("active");
          btn.querySelector(".bookmark-icon").src = "/static/icons/bookmark-default.png";

          // Kalau user di halaman bookmark list → hapus card
          if (window.location.pathname.startsWith("/bookmark")) {
            const card = btn.closest("article.event-card");
            if (card) {
              card.classList.add("opacity-0", "transition", "duration-300");
              setTimeout(() => {
                card.remove();

                // kalau udah gak ada event, tampilkan empty state
                const remaining = document.querySelectorAll("article.event-card").length;
                if (remaining === 0) {
                  const container = document.querySelector("#event-grid");
                  const emptyState = `
                    <div id="no-events" class="rounded-lg border border-gray-200 p-12 text-center max-w-5xl mx-auto my-10">
                      <h3 class="text-lg font-medium text-gray-900 mb-2">You haven't bookmarked any event yet.</h3>
                    </div>`;
                  container.insertAdjacentHTML("afterend", emptyState);
                }
              }, 300);
            }
          }
        }
      } catch (err) {
        console.error("Error toggling bookmark:", err);
      }
    });
  });
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(";").shift();
}