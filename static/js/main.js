/* =====================================================================
   Третий возраст — интерактив без внешних библиотек
   ===================================================================== */
(function () {
    'use strict';

    /* ---------- 1. Мобильное меню ---------- */
    var toggle = document.getElementById('navToggle');
    var nav = document.getElementById('mainNav');

    if (toggle && nav) {
        toggle.addEventListener('click', function () {
            var open = nav.classList.toggle('is-open');
            toggle.classList.toggle('is-open', open);
            toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
        });

        /* Закрываем меню после клика по ссылке */
        nav.addEventListener('click', function (e) {
            if (e.target.tagName === 'A') {
                nav.classList.remove('is-open');
                toggle.classList.remove('is-open');
                toggle.setAttribute('aria-expanded', 'false');
            }
        });

        /* Клик вне меню — закрыть */
        document.addEventListener('click', function (e) {
            if (nav.classList.contains('is-open') &&
                !nav.contains(e.target) && !toggle.contains(e.target)) {
                nav.classList.remove('is-open');
                toggle.classList.remove('is-open');
                toggle.setAttribute('aria-expanded', 'false');
            }
        });
    }

    /* ---------- 2. Тень шапки при прокрутке ---------- */
    var header = document.querySelector('.site-header');
    function onScroll() {
        if (header) {
            header.classList.toggle('is-scrolled', window.scrollY > 12);
        }
    }
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();

    /* ---------- 3. Плавное появление блоков ---------- */
    var revealItems = document.querySelectorAll('.reveal');

    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });

        revealItems.forEach(function (el, i) {
            /* Небольшая задержка создаёт эффект «волны» */
            el.style.transitionDelay = (i % 3) * 90 + 'ms';
            observer.observe(el);
        });
    } else {
        revealItems.forEach(function (el) { el.classList.add('is-visible'); });
    }

    /* ---------- 4. Фильтр по категориям и поиск ---------- */
    var cards = Array.prototype.slice.call(document.querySelectorAll('[data-category]'));
    var chips = Array.prototype.slice.call(document.querySelectorAll('.chip[data-filter]'));
    var tiles = Array.prototype.slice.call(document.querySelectorAll('.cat-tile[data-filter]'));
    var search = document.getElementById('search');
    var emptyHint = document.getElementById('emptyHint');

    var state = { category: 'all', query: '' };

    function applyFilter() {
        if (!cards.length) { return; }
        var shown = 0;

        cards.forEach(function (card) {
            var byCat = state.category === 'all' || card.dataset.category === state.category;
            var haystack = (card.dataset.search || card.textContent || '').toLowerCase();
            var byText = !state.query || haystack.indexOf(state.query) !== -1;
            var ok = byCat && byText;

            card.classList.toggle('is-hidden', !ok);
            if (ok) {
                card.classList.add('is-visible');
                shown++;
            }
        });

        if (emptyHint) { emptyHint.hidden = shown !== 0; }
    }

    function setActiveChip(filter) {
        chips.forEach(function (chip) {
            chip.classList.toggle('is-active', chip.dataset.filter === filter);
        });
        tiles.forEach(function (tile) {
            tile.classList.toggle('is-active', tile.dataset.filter === filter);
        });
    }

    chips.forEach(function (chip) {
        chip.addEventListener('click', function () {
            state.category = chip.dataset.filter;
            setActiveChip(state.category);
            applyFilter();
        });
    });

    /* Клик по большой плитке категории: включаем фильтр и ведём к материалам */
    tiles.forEach(function (tile) {
        tile.addEventListener('click', function () {
            state.category = tile.dataset.filter;
            setActiveChip(state.category);
            applyFilter();
            var target = document.getElementById('materials');
            if (target) { target.scrollIntoView({ behavior: 'smooth', block: 'start' }); }
        });
    });

    /* Деактивация плитки категории при выборе чипа «Все материалы» */
    chips.forEach(function (chip) {
        if (chip.dataset.filter === 'all') {
            chip.addEventListener('click', function () {
                tiles.forEach(function (t) { t.classList.remove('is-active'); });
            });
        }
    });

    if (search) {
        search.addEventListener('input', function () {
            state.query = search.value.trim().toLowerCase();
            applyFilter();
        });
    }

    /* Клики по категориям в подвале ведут к материалам и включают фильтр */
    document.querySelectorAll('[data-cat]').forEach(function (link) {
        link.addEventListener('click', function () {
            state.category = link.dataset.cat;
            setActiveChip(state.category);
            applyFilter();
        });
    });

    /* ---------- 5. Кнопка «наверх» по клику на логотип-якоря ---------- */
    document.querySelectorAll('a[href^="#"]').forEach(function (link) {
        link.addEventListener('click', function (e) {
            var id = link.getAttribute('href');
            if (id && id.length > 1) {
                var el = document.querySelector(id);
                if (el) {
                    e.preventDefault();
                    el.scrollIntoView({ behavior: 'smooth', block: 'start' });
                }
            }
        });
    });
})();
