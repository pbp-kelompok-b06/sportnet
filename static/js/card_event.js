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
        console.log("Attempting to bookmark event ID:", eventId);
        const response = await fetch(`/bookmark/${eventId}/`, {
          method: "POST",
          headers: { 
            "X-CSRFToken": getCookie("csrftoken"),
            "Content-Type": "application/json"
          },
        });

        console.log("Response status:", response.status);
        console.log("Response URL:", response.url);

        if (response.redirected) {
          window.location.href = response.url;
          return;
        }

        const data = await response.json();
        console.log("Data:", data);

        // ambil icon di dalam tombol
        const icon = btn.querySelector(".bookmark-icon");

        if (data.status === "added") {
          btn.classList.add("active");
          if (icon) icon.src = "/static/icons/bookmark-toggle.png";
        } else if (data.status === "removed") {
          btn.classList.remove("active");
          if (icon) icon.src = "/static/icons/bookmark-default.png";

          console.log(
            "Status is 'removed', trying to remove DOM for event:",
            eventId
          );

          const path = window.location.pathname.toLowerCase();
          console.log("Current pathname:", path);

          if (path.includes("bookmark")) {
            let wrapper = btn.closest(".bookmark-item");
            console.log("closest('.bookmark-item') =>", wrapper);

            if (!wrapper) {
              wrapper = document.querySelector(
                `.bookmark-item[data-event-id="${eventId}"]`
              );
              console.log(
                "querySelector('.bookmark-item[data-event-id=...]') =>",
                wrapper
              );
            }

            if (!wrapper) {
              console.warn(
                "Wrapper .bookmark-item tidak ditemukan, fallback ke .bookmark-item pertama"
              );
              wrapper = document.querySelector(".bookmark-item");
            }

            if (wrapper) {
              wrapper.classList.add("opacity-0", "transition", "duration-300");

              setTimeout(() => {
                wrapper.remove();

                const remaining =
                  document.querySelectorAll(".bookmark-item").length;
                console.log("Remaining bookmark-item:", remaining);

                if (remaining === 0) {
                  const container = document.querySelector("#event-grid");
                  if (container) {
                    const emptyState = `
                      <div id="no-events"
                           class="text-center bg-white shadow-sm rounded-xl border border-gray-100 p-12 mt-10">
                        <h3 class="text-xl font-semibold text-gray-900 mb-2">No Bookmarks Yet</h3>
                        <p class="text-gray-500 mb-6 max-w-md mx-auto">
                          It looks like you haven't bookmarked any events. Start exploring to find events you'll love!
                        </p>
                      </div>`;
                    container.insertAdjacentHTML("afterend", emptyState);
                  }
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