document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("load-more-btn");
    const container =
        document.getElementById("articles-container") ||
        document.getElementById("services-container");

    if (!button || !container) return;

    const isArticles = container.id === "articles-container";
    let loading = false;
    let nextPage = Number(button.dataset.page);

    // تعداد آیتم‌هایی که در بارگذاری اولیه، متناسب با عرض صفحه نمایش داده می‌شوند.
    const getInitialVisibleCount = () => {
        const width = window.innerWidth;

        if (width >= 1200) return 8;
        if (width >= 992) return 8;
        if (width >= 768) return 6;
        if (width >= 576) return 4;
        return 2;
    };

    const getCards = () =>
        Array.from(container.querySelectorAll(".service-card, .news-card, .article-card, .card"));

    const showCard = (card) => {
        card.hidden = false;
        card.style.removeProperty("display");
    };

    const hideCard = (card) => {
        card.hidden = true;
        card.style.setProperty("display", "none", "important");
    };

    const getHiddenCards = () =>
        getCards().filter((card) => card.hidden);

    // روی هر کارت موجود، وضعیت اولیه را اعمال می‌کنیم.
    const applyInitialVisibility = () => {
        const cards = getCards();
        const visibleCount = Math.min(getInitialVisibleCount(), cards.length);

        cards.forEach((card, index) => {
            if (index < visibleCount) {
                showCard(card);
            } else {
                hideCard(card);
            }
        });

        if (hiddenCount > 0) {
            button.disabled = false;
        }
    };

    let hiddenCount = 0;

    const refreshHiddenCount = () => {
        hiddenCount = getHiddenCards().length;
    };

    const updateButtonText = () => {
        button.innerHTML = `<span>${isArticles ? "نمایش مقالات بیشتر" : "نمایش خدمات بیشتر"}</span><i class="bi bi-chevron-down" aria-hidden="true"></i>`;
    };

    const updateAfterResize = () => {
        const cards = getCards();
        const targetVisible = getInitialVisibleCount();
        const currentlyVisible = cards.filter((card) => !card.hidden).length;

        // بزرگ‌تر شدن viewport، کارت‌های پنهان همان صفحه را خودکار آشکار می‌کند.
        if (targetVisible > currentlyVisible) {
            cards
                .filter((card) => card.hidden)
                .slice(0, targetVisible - currentlyVisible)
                .forEach(showCard);
        }

        refreshHiddenCount();
    };

    // فقط کارت‌های همان صفحه را کنترل می‌کنیم؛ داده‌ی سرور دست‌نخورده می‌ماند.
    applyInitialVisibility();
    refreshHiddenCount();
    updateButtonText();

    window.addEventListener("resize", updateAfterResize);

    button.addEventListener("click", async () => {
        if (loading) return;

        loading = true;
        button.disabled = true;
        button.innerHTML = '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span><span>در حال بارگذاری...</span>';

        try {
            refreshHiddenCount();

            // ابتدا کارت‌های باقی‌مانده‌ی همین صفحه را نمایش بده.
            if (hiddenCount > 0) {
                const visibleTarget = getInitialVisibleCount();
                const hiddenCards = getHiddenCards();

                hiddenCards
                    .slice(0, visibleTarget)
                    .forEach((card, index) => {
                        showCard(card);
                        card.classList.add("fade-card");
                        card.style.animationDelay = `${index * 100}ms`;
                    });

                refreshHiddenCount();

                // هنوز کارت‌های مخفی یا صفحه‌ی بعد وجود دارد.
                if (hiddenCount > 0 || button.dataset.page) {
                    button.disabled = false;
                    updateButtonText();
                    loading = false;
                    return;
                }
            }

            // وقتی کارت‌های فعلی تمام شدند، صفحه‌ی بعد از سرور دریافت می‌شود.
            const width = window.innerWidth;
            const response = await fetch(`?page=${nextPage}&width=${width}`, {
                headers: { "X-Requested-With": "XMLHttpRequest" }
            });

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

            refreshHiddenCount();

            if (data.has_next) {
                nextPage += 1;
                button.dataset.page = String(nextPage);
                button.disabled = false;
                updateButtonText();
            } else {
                button.remove();
            }
        } catch (error) {
            console.error("Load More Error:", error);
            button.disabled = false;
            button.innerHTML = '<span>تلاش مجدد</span><i class="bi bi-arrow-repeat" aria-hidden="true"></i>';
        } finally {
            loading = false;
        }
    });
});
