document.addEventListener("DOMContentLoaded", () => {

    const button = document.getElementById("load-more-btn");
    const container = document.getElementById("services-container");

    if (!button || !container) return;

    let loading = false;

    button.addEventListener("click", async () => {

        if (loading) return;

        loading = true;

        const page = Number(button.dataset.page);
        const width = window.innerWidth;

        button.disabled = true;

        button.innerHTML = `
            <span class="spinner-border spinner-border-sm" aria-hidden="true"></span>
            <span>در حال بارگذاری...</span>
        `;

        try {

            const response = await fetch(
                `?page=${page}&width=${width}`,
                {
                    headers: {
                        "X-Requested-With": "XMLHttpRequest"
                    }
                }
            );

            if (!response.ok) {
                throw new Error(`Server Error: ${response.status}`);
            }

            const data = await response.json();

            const temp = document.createElement("div");
            temp.innerHTML = data.html;

            [...temp.children].forEach((card, index) => {

                card.classList.add("fade-card");
                card.style.animationDelay = `${index * 100}ms`;

                container.appendChild(card);

            });

            if (data.has_next) {

                button.dataset.page = page + 1;

                button.disabled = false;
                button.innerHTML = "نمایش خدمات بیشتر";

            } else {

                button.classList.add("hide-btn");

                setTimeout(() => {
                    button.remove();
                }, 350);

            }

        } catch (error) {

            console.error("Load More Error:", error);

            button.disabled = false;
            button.innerHTML = "تلاش مجدد";

            alert("خطا در دریافت اطلاعات.");

        } finally {

            loading = false;

        }

    });

});