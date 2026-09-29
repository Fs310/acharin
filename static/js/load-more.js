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

    // تعداد آیتمی که در هر کلیک اضافه می‌شود، متناسب با breakpoint.
    const getBatchSize = () => {
        const width = window.innerWidth;

        if (width >= 992) return 8;
        if (width >= 768) return 6;
        if (width >= 576) return 4;
        return 4;
    };

    const getCards = () =>
        Array.from(
            container.querySelectorAll(".service-card, .blog-card, .news-card, .article-card, .card")
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

    // صفحه اول: تعداد اولیه بر اساس breakpoint.
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

    const revealHiddenCards = (count) => {
        const hiddenCards = getHiddenCards();
        const cardsToShow = hiddenCards.slice(0, count);

        cardsToShow.forEach((card, index) => {
            showCard(card, index, true);
        });

        return cardsToShow.length;
    };

    const updateAfterResize = () => {
        const cards = getCards();
        const target = getBatchSize();
        const visibleCount = cards.filter((card) => !card.hidden).length;

        // در بزرگ‌تر شدن viewport، کارت‌های موجود را تا batch فعلی آشکار کن.
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

    const fetchNextPage = async (page) => {
        const response = await fetch(`?page=${page}`, {
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

        return {
            cards: newCards,
            hasNext: Boolean(data.has_next)
        };
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
            const batchSize = getBatchSize();
            let remaining = batchSize;

            // هر کلیک همیشه به اندازه batch فعلی کارت اضافه می‌کند.
            // ابتدا از کارت‌های مخفی همین صفحه استفاده می‌شود.
            remaining -= revealHiddenCards(remaining);

            // اگر کارت مخفی کافی نبود، برای تکمیل batch همان کلیک صفحه بعد را می‌گیریم.
            while (remaining > 0 && hasNext) {
                const result = await fetchNextPage(nextPage);

                const visibleCount = Math.min(remaining, result.cards.length);

                result.cards.slice(0, visibleCount).forEach((card, index) => {
                    showCard(card, index, true);
                });

                result.cards.slice(visibleCount).forEach((card) => {
                    hideCard(card);
                });

                remaining -= visibleCount;
                hasNext = result.hasNext;

                if (hasNext) {
                    nextPage += 1;
                    button.dataset.page = String(nextPage);
                } else {
                    delete button.dataset.page;
                }

                // اگر صفحه بعد چیزی برای نمایش نداشت، حلقه تمام می‌شود.
                if (!result.cards.length) break;
            }

            syncButton();
        } catch (error) {
            console.error("Load More Error:", error);
            button.disabled = false;
            updateButtonText();
        } finally {
            loading = false;
        }
    });
});
