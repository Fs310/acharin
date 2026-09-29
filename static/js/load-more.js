document.addEventListener("DOMContentLoaded", () => {
    const button = document.getElementById("load-more-btn");
    const container =
        document.getElementById("articles-container") ||
        document.getElementById("services-container");

    if (!button || !container) return;

    const isArticles = container.id === "articles-container";
    let loading = false;
    let nextPage = Number(button.dataset.page);
    let hasNext = Boolean(button.dataset.page);

    // تعداد کارت قابل‌نمایش در هر مرحله، بر اساس breakpoint.
    const getBatchSize = () => {
        const width = window.innerWidth;

        if (width >= 992) return 8;
        if (width >= 768) return 6;
        if (width >= 576) return 4;
        return 2;
    };

    const getCards = () =>
        Array.from(
            container.querySelectorAll(".service-card, .news-card, .article-card, .card")
        );

    const showCard = (card, index = 0, animate = false) => {
        card.hidden = false;
        card.style.removeProperty("display");

        if (animate) {
            card.classList.add("fade-card");
            card.style.animationDelay = `${index * 100}ms`;
        }
    };

    const hideCard = (card) => {
        card.hidden = true;
        card.style.setProperty("display", "none", "important");
    };

    const getHiddenCards = () =>
        getCards().filter((card) => card.hidden);

    const updateButtonText = () => {
        button.innerHTML =
            `<span>${isArticles ? "نمایش مقالات بیشتر" : "نمایش خدمات بیشتر"}</span>` +
            '<i class="bi bi-chevron-down" aria-hidden="true"></i>';
    };

    // صفحه اول: فقط اندازه‌ی مناسب همین breakpoint دیده شود.
    const prepareInitialCards = () => {
        const cards = getCards();
        const batchSize = getBatchSize();

        cards.forEach((card, index) => {
            if (index < batchSize) {
                showCard(card);
            } else {
                hideCard(card);
            }
        });
    };

    const revealHiddenCards = () => {
        const hiddenCards = getHiddenCards();
        if (!hiddenCards.length) return 0;

        const batchSize = getBatchSize();

        hiddenCards
            .slice(0, batchSize)
            .forEach((card, index) => showCard(card, index, true));

        return hiddenCards.slice(0, batchSize).length;
    };

    const updateAfterResize = () => {
        const cards = getCards();
        const target = getBatchSize();
        const visibleCount = cards.filter((card) => !card.hidden).length;

        // با بزرگ‌تر شدن viewport، کارت‌های پنهان همان داده‌ها را آشکار کن.
        if (target > visibleCount) {
            cards
                .filter((card) => card.hidden)
                .slice(0, target - visibleCount)
                .forEach((card, index) => showCard(card, index, true));
        }
    };

    const syncButton = () => {
        const hasHidden = getHiddenCards().length > 0;

        if (hasHidden || hasNext) {
            button.disabled = false;
            updateButtonText();
        } else {
            button.remove();
        }
    };

    prepareInitialCards();
    syncButton();
    window.addEventListener("resize", updateAfterResize);

    button.addEventListener("click", async () => {
        if (loading) return;

        loading = true;
        button.disabled = true;
        button.innerHTML =
            '<span class="spinner-border spinner-border-sm" aria-hidden="true"></span>' +
            '<span>در حال بارگذاری...</span>';

        try {
            // اول کارت‌های مخفیِ همین صفحه را نشان بده.
            const revealed = revealHiddenCards();

            if (revealed > 0) {
                syncButton();
                loading = false;
                return;
            }

            // وقتی کارت‌های فعلی تمام شدند، صفحه‌ی بعد را بگیر.
            if (!hasNext) {
                button.remove();
                loading = false;
                return;
            }

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

            const newCards = [...temp.children];

            newCards.forEach((card) => container.appendChild(card));

            // از صفحه‌ی جدید فقط batch مناسب breakpoint نمایش بده.
            const batchSize = getBatchSize();
            newCards.forEach((card, index) => {
                if (index < batchSize) {
                    showCard(card, index, true);
                } else {
                    hideCard(card);
                }
            });

            hasNext = Boolean(data.has_next);

            if (hasNext) {
                nextPage += 1;
                button.dataset.page = String(nextPage);
            } else {
                delete button.dataset.page;
            }

            syncButton();
        } catch (error) {
            console.error("Load More Error:", error);
            button.disabled = false;
            button.innerHTML =
                '<span>تلاش مجدد</span><i class="bi bi-arrow-repeat" aria-hidden="true"></i>';
        } finally {
            loading = false;
        }
    });
});
