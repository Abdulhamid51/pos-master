
<script>
    function searchReturnProducts() {
        const searchInput = document.getElementById('return-search-input');
        if (!searchInput) return;
        
        const searchTerm = searchInput.value.toLowerCase();
        const productCards = document.querySelectorAll('#return-products-list .card');
        
        productCards.forEach(card => {
            const productName = card.querySelector('.card-title').textContent.toLowerCase();
            if (productName.includes(searchTerm)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    }
</script>
<script>    

    $('.payment_type').on('click', function () {
        let naqd = $(this).data('naqd');
        
        $('.payment_type_inputs').each(function () {
            let disable = $(this).data('naqd') != naqd;

            $(this).find('input, button').prop('disabled', disable);
            if(disable === true){
                $(this).find('input').val(0)
            }else{
                console.log($(this).data('valyuta-som'));
                
                if($(this).data('valyuta-som') === 'True'){
                    $(this).find('button').trigger('click')
                }
            }
        });
    });
    
    $('.payment_type_inputs').each(function () {
        let naqd = $('.payment_type_tab:checked').data('naqd');
        
        let disable = $(this).data('naqd') != naqd;
        
        $(this).find('input, button').prop('disabled', disable);
        if(disable === true){
            $(this).find('input').val(0)
        }else{
            console.log($(this).data('valyuta-som'));
            if($(this).data('valyuta-som') === 'True'){
                // $(this).find('button').trigger('click')
            }
        }
    });
    

    function getActiveTabId() {
        const btn = $('#myTab').find('.nav-link.active').attr('id');
        if(btn === 'naqd-tab'){
            return 'naqd'
        }else if(btn === 'qarz-tab'){
            return 'debtor'
        }else if(btn === 'taminotchi-tab'){
            return 'deliver'
        }
    }

    function changeVisualTab() {
        const btn = $('#myTab').find('.nav-link.active').attr('id');
        var $select = $('#valyuta_input').selectize();
        var selectize = $select[0].selectize;
        var firstValue = Object.keys(selectize.options)[0];
        
        if (btn === 'naqd-tab') {
            $('#qarztasir, #date_and_comment').addClass('d-none');
            selectize.setValue(firstValue);
            selectize.$control.hide();
            document.querySelector('#payment_types_block').style.display = 'none';
        } else if (btn === 'qarz-tab' || btn === 'taminotchi-tab') {
            document.querySelector('#payment_types_block').style.display = 'block';
            selectize.$control.show();
            $('#qarztasir, #date_and_comment').removeClass('d-none');
        }
    }


    function changeTab(tab) {
        // const $tabs = $('#myTab .nav-link');
        
        const $target = $('#' + tab);
        if ($target.length) {
            $target.trigger('click');
        }
    }

    function changeToNaqt(){
        const debtorSelectize = $('#mainSelectDebtor')[0]?.selectize;
        const deliverSelectize = $('#mainSelectDeliver')[0]?.selectize;
        debtorSelectize.setValue('')
        deliverSelectize.setValue('')
    }

    function setqarzdate() {
        const d = new Date();
        d.setDate(d.getDate() + 10);
        $('#qarzdate').val(d.toISOString().split('T')[0]);

    }

    //  Global o'zgaruvchi - joriy filial

    function loadProducts(filialId) {
        if (!filialId) {
            showEmptyTable("Filialni tanlang");
            return;
        }

        // Loaderni ko'rsatish
        showLoader();

        // AJAX so'rovi
        $.ajax({
            url: "{% url 'get_products_forsale' %}",
            method: 'GET',
            data: {
                'filial': filialId
            },
            dataType: 'json',
            success: function (response) {
                if (response.success) {
                    // Jadvalni to'ldirish
                    populateTable(response.products);
                    setTimeout(() => {
                        updateAllPrices();
                    }, 100); // 200 ms kutadi
                } else {
                    showEmptyTable("Xatolik: " + response.error);
                }
            },
            error: function (xhr, status, error) {
                showEmptyTable("Server bilan bog'lanishda xatolik");
                console.error("AJAX xatosi:", error);
            },
            complete: function () {
                // Loaderni yashirish
                hideLoader();
            }
        });

    }

    $('#skidka_percent_add').click(function () {
        let skidka = parseFloat($('#skidka_percent').val() || 0)
        $('#skidka_percent').val(skidka + 1)
    })


    // Loader ko'rsatish
    function showLoader() {
        $('#productsLoader').show();
        $('#productsTableWrapper').hide();
        $('#productSearchInput').prop('disabled', true);
    }

    // Loader yashirish
    function hideLoader() {
        setTimeout(function () {
            $('#productsLoader').hide();
            $('#productsTableWrapper').show();
            $('#productSearchInput').prop('disabled', false);
            $('#productSearchInput').focus();
        }, 300);
    }

    // Jadvalni to'ldirish
    function populateTable(products) {
        const tbody = $('#productTable');

        if (!products || products.length === 0) {
            showEmptyTable("Mahsulotlar topilmadi");
            return;
        }

        // Jadvalni tozalash
        tbody.empty();

        // Har bir mahsulot uchun qator yaratish
        products.forEach(function (product) {
            const row = `
                <tr class="product-row" id="productrow${product.id}"
                    data-value="${product.id}&${product.name}&${product.quantity}&${product.barcodes}&${product.pack}&${product.price}$${product.measurement_type}"
                    data-search="${product.name.toLowerCase()} ${product.barcodes}"
                    ondblclick="addCart('${product.id}')"
                    style="cursor:pointer">
                    <td>${product.barcodes || ''}</td>
                    <td><strong>${product.name}</strong></td>
                    <td id="quantity${product.id}">${parseFloat(product.quantity).toFixed(2)}</td>
                    <td>
                        <span data-prices='${product.pricetypevaluta_prices_json}' 
                            data-quantity="${product.quantity}" 
                            id="productprice${product.id}">
                            ${parseFloat(product.price).toFixed(2)}
                        </span>
                    </td>
                </tr>
            `;

            tbody.append(row);
        });

    }

    // Bo'sh jadvalni ko'rsatish
    function showEmptyTable(message) {
        const tbody = $('#productTable');
        tbody.html(`
            <tr>
                <td colspan="4" class="text-center text-muted py-4">
                    ${message}
                </td>
            </tr>
        `);
    }

    // Filial o'zgarganida ishga tushadi
    $(document).ready(function () {
        loadProducts($('#select-filial').val())
        
        // updateAllPrices()
    });
</script>

<script>
    if (document.querySelector('#smenaopenbtn')) {
        document.querySelector('#smenaopenbtn').addEventListener('click', function () {
            const filialName = $('#select-filial option:selected').data('name');
            $('#smenaModalLabel').text(filialName);
            $('#filial_hidden').val($('#select-filial').val())

            let filialId = document.getElementById('select-filial').value;

            document.querySelectorAll('.kassa_merges1').forEach(element => {
                if (element.dataset.filial != filialId) {
                    element.style.display = 'none';
                    return;
                } else {
                    element.style.display = '';
                }
            });
        });
    }

</script>


<script>
    $(document).ready(function () {
        let searchTimeout;

        $('#mainsearch').on('input', function () {
            clearTimeout(searchTimeout);

            searchTimeout = setTimeout(function () {
                $('#filter_submit').trigger('click');
            }, 1500);
        });
    });
</script>

<script>
    $(document).on('show.bs.modal', '.modal', function () {
        const zIndex = 1040 + (10 * $('.modal:visible').length);
        $(this).css('z-index', zIndex);
        setTimeout(() => {
            $('.modal-backdrop').not('.modal-stack')
                .css('z-index', zIndex - 1)
                .addClass('modal-stack');
        }, 0);
    });
</script>


<script>
    function updateProductQuantity(id, quantity) {
        const quantitySpan = document.getElementById(`quantity${id}`);

        if (quantitySpan) {
            // Matnni yangilash
            quantitySpan.textContent = parseFloat(quantity).toFixed(2);
            quantitySpan.setAttribute('data-quantity', quantity);

            // 🔹 Tegishli itemni topamiz
            const item = quantitySpan.closest('.select-product-item');
            if (item) {
                // 🔹 Hozirgi yangilangan HTML holatini olish
                const updatedHTML = item.innerHTML;
                // 🔹 data-original-html ni ham yangilab qo'yamiz
                item.setAttribute('data-original-html', updatedHTML);
            }
        } else {
            console.warn(`Element #quantity${id} topilmadi`);
        }
    }
</script>


<script>




    $(document).ready(function () {
        $('select.searchable').selectize({ normalize: true });

        var valyutaSelect = $('#valyuta_input')[0]?.selectize;
        if (valyutaSelect) {
            valyutaSelect.on('change', function () {
                updateShopDetails();
                updateAllPrices();
            });
        }

        const debtorSelect = $('.mainSelectDebtor').selectize({
            normalize: true,
            create: false,
            sortField: 'text',
            placeholder: 'Mijozni tanlang...',

            // Qidiruv sozlamalari - barcha qismlardan qidirish
            searchField: ['text'],
            score: function (search) {
                const searchTerm = search.toLowerCase().trim();

                return function (item) {
                    const fullText = item.text.toLowerCase();
                    const parts = item.text.split('—');
                    const name = parts[0]?.trim().toLowerCase() || '';
                    const phone = parts[1]?.trim().toLowerCase() || '';
                    const cleanPhone = phone.replace(/\D/g, '');

                    let score = 0;

                    // 1. TO'LIQ MOS KELISH
                    if (fullText === searchTerm) score += 10000;

                    // 2. ISM BO'YICHA QIDIRISH
                    if (name.includes(searchTerm)) {
                        score += 1000;
                        if (name.startsWith(searchTerm)) score += 500;
                    }

                    // 3. TELEFON BO'YICHA QIDIRISH
                    if (phone.includes(searchTerm)) score += 800;

                    // 4. FAQAT RAQAMLARDAN QIDIRISH
                    if (/^\d+$/.test(searchTerm)) {
                        if (cleanPhone === searchTerm) score += 2000;
                        if (cleanPhone.includes(searchTerm)) {
                            score += 600;
                            if (cleanPhone.endsWith(searchTerm)) score += 400;
                        }
                    }

                    // 5. HAR QANDAY QISMDAN QIDIRISH
                    const allWords = fullText.split(/[—\s]+/);
                    allWords.forEach(word => {
                        if (word.includes(searchTerm)) score += 200;
                    });

                    return score;
                };
            },

            // MARK QILISH UCHUN YANGI RENDER FUNKSIYA
            render: {
                option: function (item, escape) {
                    // Joriy qidiruv so'zini olish
                    const searchTerm = this.$control_input.val().toLowerCase().trim();
                    const parts = escape(item.text).split('—');
                    let name = parts[0]?.trim() || '';
                    let phone = parts[1]?.trim() || '';

                    // Regex special belgilarni escape qilish
                    const escapeRegex = (string) => {
                        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                    };

                    // Har qanday qismda topilgan so'zlarni mark qilish
                    const highlightAnywhere = (text, search) => {
                        if (!search || !text || search.length < 2) return text;

                        try {
                            const escapedSearch = escapeRegex(search);
                            const regex = new RegExp(`(${escapedSearch})`, 'gi');
                            return text.replace(regex, '<mark class="search-highlight">$1</mark>');
                        } catch (e) {
                            return text;
                        }
                    };

                    // Agar qidiruv so'zi bo'lsa, mark qilish
                    if (searchTerm && searchTerm.length >= 2) {
                        name = highlightAnywhere(name, searchTerm);
                        phone = highlightAnywhere(phone, searchTerm);

                        // Raqamli qidiruv uchun alohida
                        if (/^\d+$/.test(searchTerm)) {
                            const phoneRegex = new RegExp(`(${searchTerm})`, 'gi');
                            phone = phone.replace(phoneRegex, '<mark class="search-highlight">$1</mark>');
                        }
                    }

                    return `
                    <div class="selectize-option-item">
                        <div class="option-name">
                            <i class="bi bi-person-circle"></i>
                            <span>${name}</span>
                        </div>
                        <div class="option-phone">
                            <span>${phone}</span>
                        </div>
                    </div>`;
                },

                item: function (item, escape) {
                    const searchTerm = this.$control_input.val().toLowerCase().trim();
                    const parts = escape(item.text).split('—');
                    let name = parts[0]?.trim() || '';
                    let phone = parts[1]?.trim() || '';

                    // Tanlangan elementda ham mark qilish
                    const highlightAnywhere = (text, search) => {
                        if (!search || !text || search.length < 2) return text;

                        try {
                            const escapedSearch = escapeRegex(search);
                            const regex = new RegExp(`(${escapedSearch})`, 'gi');
                            return text.replace(regex, '<mark class="search-highlight">$1</mark>');
                        } catch (e) {
                            return text;
                        }
                    };

                    if (searchTerm && searchTerm.length >= 2) {
                        name = highlightAnywhere(name, searchTerm);
                        phone = highlightAnywhere(phone, searchTerm);
                    }

                    return `
                    <div class="selectize-selected-item">
                        <div class="selected-name">
                            <i class="bi bi-person-circle"></i>
                            <span>${name}</span>
                        </div>
                        <div class="selected-phone">
                            <span>${phone}</span>
                        </div>
                    </div>`;
                }
            },

            // Qidiruv o'zgarganida yangilash
            onType: function (value) {
                // Qisqa vaqt o'tgach refresh qilish (performance uchun)
                clearTimeout(this._searchTimeout);
                this._searchTimeout = setTimeout(() => {
                    this.refreshOptions();
                }, 50);
            },

            onInitialize: function () {
                const input = this.$control;
                input.css({
                    'border-radius': '2px',
                    'border': '1px solid #ced4da',
                    'padding': '10px 12px',
                    'background': '#fff',
                    'box-shadow': '0 1px 3px rgba(0,0,0,0.1)',
                    'transition': 'all 0.2s ease',
                });

                this.$dropdown.css({
                    'border-radius': '2px',
                    'overflow': 'hidden',
                    'box-shadow': '0 4px 8px rgba(0,0,0,0.12)',
                });

                // CSS qo'shish
                const style = document.createElement('style');
                style.textContent = `
                .search-highlight {
                    background: #ffeb3b !important;
                    color: #000 !important;
                    padding: 1px 2px;
                    border-radius: 2px;
                    font-weight: bold;
                }
                .selectize-option-item {
                    display: flex;
                    flex-direction: column;
                    padding: 8px 10px;
                    line-height: 1.3;
                }
                .option-name {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .option-name i {
                    color: #007bff;
                    font-size: 17px;
                }
                .option-name span {
                    font-weight: 500;
                    color: #333;
                }
                .option-phone {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    margin-top: 4px;
                    line-height: 1;
                }
                .option-phone span {
                    font-size: 13px;
                    color: #666;
                }
                .selectize-dropdown .option:hover .search-highlight {
                    background: #fff !important;
                    color: #007bff !important;
                }
            `;
                document.head.appendChild(style);

                this.$dropdown.on('mouseenter', '.option', function () {
                    $(this).css({
                        'background': '#007bff',
                        'color': '#fff',
                    });
                    $(this).find('i').css('color', '#fff');
                    $(this).find('.search-highlight').css({
                        'background': '#fff !important',
                        'color': '#007bff !important'
                    });
                }).on('mouseleave', '.option', function () {
                    $(this).css({
                        'background': '',
                        'color': ''
                    });
                    $(this).find('i').css('color', '#007bff');
                    $(this).find('.search-highlight').css({
                        'background': '#ffeb3b !important',
                        'color': '#000 !important'
                    });
                });

                input.on('focus', function () {
                    $(this).css({
                        'border-color': '#007bff',
                        'box-shadow': '0 0 0 3px rgba(0,123,255,0.15)'
                    });
                }).on('blur', function () {
                    $(this).css({
                        'border-color': '#ced4da',
                        'box-shadow': 'none'
                    });
                });
            }
        });
        
        const deliverSelect = $('.mainSelectDeliver').selectize({
            normalize: true,
            create: false,
            sortField: 'text',
            placeholder: 'Taminotchini tanlang...',

            // Qidiruv sozlamalari - barcha qismlardan qidirish
            searchField: ['text'],
            score: function (search) {
                const searchTerm = search.toLowerCase().trim();

                return function (item) {
                    const fullText = item.text.toLowerCase();
                    const parts = item.text.split('—');
                    const name = parts[0]?.trim().toLowerCase() || '';
                    const phone = parts[1]?.trim().toLowerCase() || '';
                    const cleanPhone = phone.replace(/\D/g, '');

                    let score = 0;

                    // 1. TO'LIQ MOS KELISH
                    if (fullText === searchTerm) score += 10000;

                    // 2. ISM BO'YICHA QIDIRISH
                    if (name.includes(searchTerm)) {
                        score += 1000;
                        if (name.startsWith(searchTerm)) score += 500;
                    }

                    // 3. TELEFON BO'YICHA QIDIRISH
                    if (phone.includes(searchTerm)) score += 800;

                    // 4. FAQAT RAQAMLARDAN QIDIRISH
                    if (/^\d+$/.test(searchTerm)) {
                        if (cleanPhone === searchTerm) score += 2000;
                        if (cleanPhone.includes(searchTerm)) {
                            score += 600;
                            if (cleanPhone.endsWith(searchTerm)) score += 400;
                        }
                    }

                    // 5. HAR QANDAY QISMDAN QIDIRISH
                    const allWords = fullText.split(/[—\s]+/);
                    allWords.forEach(word => {
                        if (word.includes(searchTerm)) score += 200;
                    });

                    return score;
                };
            },

            // MARK QILISH UCHUN YANGI RENDER FUNKSIYA
            render: {
                option: function (item, escape) {
                    // Joriy qidiruv so'zini olish
                    const searchTerm = this.$control_input.val().toLowerCase().trim();
                    const parts = escape(item.text).split('—');
                    let name = parts[0]?.trim() || '';
                    let phone = parts[1]?.trim() || '';

                    // Regex special belgilarni escape qilish
                    const escapeRegex = (string) => {
                        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
                    };

                    // Har qanday qismda topilgan so'zlarni mark qilish
                    const highlightAnywhere = (text, search) => {
                        if (!search || !text || search.length < 2) return text;

                        try {
                            const escapedSearch = escapeRegex(search);
                            const regex = new RegExp(`(${escapedSearch})`, 'gi');
                            return text.replace(regex, '<mark class="search-highlight">$1</mark>');
                        } catch (e) {
                            return text;
                        }
                    };

                    // Agar qidiruv so'zi bo'lsa, mark qilish
                    if (searchTerm && searchTerm.length >= 2) {
                        name = highlightAnywhere(name, searchTerm);
                        phone = highlightAnywhere(phone, searchTerm);

                        // Raqamli qidiruv uchun alohida
                        if (/^\d+$/.test(searchTerm)) {
                            const phoneRegex = new RegExp(`(${searchTerm})`, 'gi');
                            phone = phone.replace(phoneRegex, '<mark class="search-highlight">$1</mark>');
                        }
                    }

                    return `
                    <div class="selectize-option-item">
                        <div class="option-name">
                            <i class="bi bi-person-circle"></i>
                            <span>${name}</span>
                        </div>
                        <div class="option-phone">
                            <span>${phone}</span>
                        </div>
                    </div>`;
                },

                item: function (item, escape) {
                    const searchTerm = this.$control_input.val().toLowerCase().trim();
                    const parts = escape(item.text).split('—');
                    let name = parts[0]?.trim() || '';
                    let phone = parts[1]?.trim() || '';

                    // Tanlangan elementda ham mark qilish
                    const highlightAnywhere = (text, search) => {
                        if (!search || !text || search.length < 2) return text;

                        try {
                            const escapedSearch = escapeRegex(search);
                            const regex = new RegExp(`(${escapedSearch})`, 'gi');
                            return text.replace(regex, '<mark class="search-highlight">$1</mark>');
                        } catch (e) {
                            return text;
                        }
                    };

                    if (searchTerm && searchTerm.length >= 2) {
                        name = highlightAnywhere(name, searchTerm);
                        phone = highlightAnywhere(phone, searchTerm);
                    }

                    return `
                    <div class="selectize-selected-item">
                        <div class="selected-name">
                            <i class="bi bi-person-circle"></i>
                            <span>${name}</span>
                        </div>
                        <div class="selected-phone">
                            <span>${phone}</span>
                        </div>
                    </div>`;
                }
            },

            // Qidiruv o'zgarganida yangilash
            onType: function (value) {
                // Qisqa vaqt o'tgach refresh qilish (performance uchun)
                clearTimeout(this._searchTimeout);
                this._searchTimeout = setTimeout(() => {
                    this.refreshOptions();
                }, 50);
            },

            onInitialize: function () {
                const input = this.$control;
                input.css({
                    'border-radius': '2px',
                    'border': '1px solid #ced4da',
                    'padding': '10px 12px',
                    'background': '#fff',
                    'box-shadow': '0 1px 3px rgba(0,0,0,0.1)',
                    'transition': 'all 0.2s ease',
                });

                this.$dropdown.css({
                    'border-radius': '2px',
                    'overflow': 'hidden',
                    'box-shadow': '0 4px 8px rgba(0,0,0,0.12)',
                });

                // CSS qo'shish
                const style = document.createElement('style');
                style.textContent = `
                .search-highlight {
                    background: #ffeb3b !important;
                    color: #000 !important;
                    padding: 1px 2px;
                    border-radius: 2px;
                    font-weight: bold;
                }
                .selectize-option-item {
                    display: flex;
                    flex-direction: column;
                    padding: 8px 10px;
                    line-height: 1.3;
                }
                .option-name {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                }
                .option-name i {
                    color: #007bff;
                    font-size: 17px;
                }
                .option-name span {
                    font-weight: 500;
                    color: #333;
                }
                .option-phone {
                    display: flex;
                    align-items: center;
                    gap: 6px;
                    margin-top: 4px;
                    line-height: 1;
                }
                .option-phone span {
                    font-size: 13px;
                    color: #666;
                }
                .selectize-dropdown .option:hover .search-highlight {
                    background: #fff !important;
                    color: #007bff !important;
                }
            `;
                document.head.appendChild(style);

                this.$dropdown.on('mouseenter', '.option', function () {
                    $(this).css({
                        'background': '#007bff',
                        'color': '#fff',
                    });
                    $(this).find('i').css('color', '#fff');
                    $(this).find('.search-highlight').css({
                        'background': '#fff !important',
                        'color': '#007bff !important'
                    });
                }).on('mouseleave', '.option', function () {
                    $(this).css({
                        'background': '',
                        'color': ''
                    });
                    $(this).find('i').css('color', '#007bff');
                    $(this).find('.search-highlight').css({
                        'background': '#ffeb3b !important',
                        'color': '#000 !important'
                    });
                });

                input.on('focus', function () {
                    $(this).css({
                        'border-color': '#007bff',
                        'box-shadow': '0 0 0 3px rgba(0,123,255,0.15)'
                    });
                }).on('blur', function () {
                    $(this).css({
                        'border-color': '#ced4da',
                        'box-shadow': 'none'
                    });
                });
            }
        });
    });
</script>


<script>
    // Cart operatsiyalari uchun global o'zgaruvchilar
    let currentShopId = null;
    let cartItems = [];
    let currentKurs = document.querySelector('#dollar-kurs-base').value


    let currentDatas = null

    function refresh_total_price() {
        currentDatas.total_price = cartItems.reduce((sum, item) => sum + item.total, 0);
    }

    let existingPayments = [];



    function delete_all() {
        if (confirm("Rostdan ham barcha mahsulotlarni o‘chirmoqchimisiz?")) {
            fetch(`{% url 'b2c_shop_create' %}?id=${currentShopId}&request_type=delete_all`, {
                method: 'GET',
            })
                .then(response => response.json())
                .then(response => {
                    if (response.success) {
                        let products = response.products
                        products.forEach(function (item, index) {
                            updateProductQuantity(item.id, item.rest)
                        })
                        initializeShop(currentShopId)
                    } else {
                        console.error("So‘rov muvaffaqiyatli emas:", response.success);
                    }
                })
                .catch(error => {
                    console.error("Xatolik yuz berdi:", error);
                });
        }

    }


    function updateShopDetails() {
        if (!currentShopId) {
            console.log('Shop ID mavjud emas');
            return;
        }
        let for_who = getActiveTabId()
        // Selectize instansiyalaridan qiymatlarni olish
        const debtorSelectize = $('#mainSelectDebtor')[0]?.selectize;
        const deliverSelectize = $('#mainSelectDeliver')[0]?.selectize;
        // const filialSelectize = $('#selectFilial')[0]?.selectize;
        const valyutaSelectize = $('#valyuta_input')[0]?.selectize;
        let chegirma = cleanNumber($('#discountInput').val()) || 0;

        const debtorId = debtorSelectize ? debtorSelectize.getValue() : '';
        const deliverId = deliverSelectize ? deliverSelectize.getValue() : '';
        // const filialId = filialSelectize ? filialSelectize.getValue() : '';
        const valyutaId = $('#mainSelectValyuta').val();
        // const debtorId = $('#mainSelectDebtor').val();
        const filialId = $('#select-filial').val();

        if (filialId) {
            const formData = new FormData();
            if(for_who === 'debtor'){
                formData.append('debtor', debtorId);
            }else if(for_who === 'deliver'){
                formData.append('deliver', deliverId);
            }
            formData.append('filial', filialId);
            formData.append('chegirma', chegirma);
            formData.append('valyuta', valyutaSelectize.getValue());
            console.log(formData);
            
            fetch(`{% url 'b2c_shop_edit_ajax' %}?id=${currentShopId}`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            })
                .then(response => response.json()) // JSONni kutish
                .then(data => {
                    if (data.success) {
                        // showAlert("Shop ma'lumotlari yangilandi", 'success');
                        initializeShop(currentShopId);
                    } else {
                        showAlert(data.message || 'Yangilashda xatolik', 'danger');
                    }
                })
                .catch(error => {
                    console.error('Shop yangilashda xatolik:', error);
                    showAlert("Server bilan bog'lanishda xatolik", 'danger');
                });
        }
    }



    // Sahifa yuklanganda shop yaratish yoki olish
    document.addEventListener('DOMContentLoaded', function () {
        initializeShop();

        // POS modalini ochish
        const btn = document.getElementById('openPOSModalBtn');

        if (btn) {
            btn.addEventListener('click', function () {
                initializeShop();
                const modal = new bootstrap.Modal(document.getElementById('posModal'));
                modal.show();
            });
        }

    });


    function editShopModal(id) {
        const modal = new bootstrap.Modal(document.getElementById('posModal'));
        modal.show();
        initializeShop(id);

    }

    // Shopni yaratish yoki olish
    async function initializeShop(id) {
        // try {
        const response = await fetch(`{% url 'b2c_shop_create' %}?id=${id || ''}`);

        const data = await response.json();
        $('.payment-input').each(function() {
            $(this).val(0);
        });
        if (data.id) {
            console.log(data.tab, 'bekendan kegan tab idsi');
            
            changeTab(data.tab)
            changeVisualTab()
            currentShopId = data.id;
            currentDatas = data
            filialId = data.filial.id;
            valyutaId = data.valyuta_id;
            customerId = data.customer_info?.id
            deliverId = data.deliver_info?.id
            document.getElementById('shop_id').value = currentShopId;


            $('#discountInput').val(formatNumber(data.chegirma))
            $('#all_total').val(data.totals.total)
            $('#all_total_without_skidka').val(data.totals.total_without_skidka)


            // $('#mainSelectDebtor').val(customerId);
            // $('#selectFilial').val(filialId);
            // customerinput.setValue(customerId, true); // silent:true

            const debtorSelectize = $('#mainSelectDebtor')[0]?.selectize;
            const deliverSelectize = $('#mainSelectDeliver')[0]?.selectize;
            if (debtorSelectize) {
                debtorSelectize.setValue(customerId, true)
                deliverSelectize.setValue(deliverId, true)
            }




            // faqat user o‘zgartirganda ishlaydi
            // selectize.on('change', function () {
            //     if (ignoreChange) return;

            //     updateShopDetails();
            //     updateAllPrices();
            // });



            loadCartItems();
            // await loadExistingPayments();
            updateAllPrices()

            loadExistingPaymentsForModal();

            // updateCheckPayments()
            // updatecheckDatas()
            // updateCheckWithProducts()

            var valyutaSelect = $('#valyuta_input')[0]?.selectize;
            if (valyutaSelect) {
                valyutaSelect.setValue(valyutaId, true); // silent:true
            }
            if (data.active_shops) {
                renderActiveShops(data.active_shops);
            }

        }
        // } catch (error) {
        //     console.error('Shop yaratishda xatolik:', error);
        //     showAlert('Shop yaratishda xatolik yuz berdi', 'danger');
        // }
    }

    // Cart elementlarini yuklash
    async function loadCartItems() {
        if (!currentShopId) return;

        try {
            const response = await fetch(`{% url 'b2c_shop_create' %}?id=${currentShopId}`);
            const data = await response.json();

            if (data.cart_items) {
                cartItems = data.cart_items;
                renderCartItems();
                updateTotals();
            }
        } catch (error) {
            console.error('Cart elementlarini yuklashda xatolik:', error);
        }
    }

    function changeShopTab(tab, shop_id) {
        let new_shopid = $('#shop_id').val()
        let res = fetch(`{% url 'b2c_shop_create' %}?id=${shop_id}&request_type=change_tab&tab=${tab}`);
        console.log(shop_id, 'shop id\'si', new_shopid)
    }

    // Global o'zgaruvchilar
    let selectedCartIds = new Set();
    let isMouseDown = false;
    let selectionStartRow = null;
    let clickHandled = false; // Yangi flag qo'shamiz

    // Tanlash funksiyalari
    function initCartSelection() {
        const tbody = document.getElementById('cart-tbody');
        if (!tbody) return;

        // 1. Mouse bosilganda - tanlashni boshlash
        tbody.addEventListener('mousedown', function (e) {
            // Input, button yoki select elementlarida emasligiga ishonch hosil qilish
            if (e.target.tagName === 'INPUT' ||
                e.target.tagName === 'BUTTON' ||
                e.target.tagName === 'SELECT' ||
                e.target.closest('input, button, select')) {
                return;
            }

            isMouseDown = true;
            clickHandled = false;
            const row = e.target.closest('.cart-item-row');

            if (row) {
                selectionStartRow = row;

                // Shift bosilgan holda diapazon tanlash
                if (e.shiftKey) {
                    selectRange(row);
                    clickHandled = true;
                }
                // Ctrl bosilgan holda multiple tanlash
                else if (e.ctrlKey || e.metaKey) {
                    toggleSingleSelection(row);
                    clickHandled = true;
                }
                // Oddiy click - boshqalarni tozalab, bitta tanlash
                else {
                    // Agar bu qator allaqachon tanlangan bo'lsa
                    const cartId = getCartIdFromRow(row);
                    if (selectedCartIds.has(cartId)) {
                        // Faqat bu qatorni tanlashdan olib tashlash
                        toggleSingleSelection(row);
                        clickHandled = true;
                    } else {
                        // Boshqa barcha tanlovlarni tozalash, bu qatorni tanlash
                        clearAllSelections();
                        toggleSingleSelection(row);
                        clickHandled = true;
                    }
                }
            }
        });

        // 2. Mouse harakatlanganda - drag selection
        tbody.addEventListener('mousemove', function (e) {
            if (!isMouseDown) return;

            const currentRow = e.target.closest('.cart-item-row');
            if (currentRow && selectionStartRow) {
                selectRangeBetween(selectionStartRow, currentRow);
            }
        });

        // 3. Mouse qo'yilganda - tanlashni tugatish
        document.addEventListener('mouseup', function (e) {
            isMouseDown = false;
            selectionStartRow = null;
        });

        // 4. Click event - faqat tanlash ishlagan bo'lsa, preventDefault qilish
        tbody.addEventListener('click', function (e) {
            // Input yoki button bosilgan bo'lsa, tanlashni o'tkazib yuborish
            if (e.target.tagName === 'INPUT' ||
                e.target.tagName === 'BUTTON' ||
                e.target.closest('input, button')) {
                return;
            }

            // Agar mousedown da ishlangan bo'lsa, click ni to'xtatish
            if (clickHandled) {
                e.preventDefault();
                e.stopPropagation();
            }

            const row = e.target.closest('.cart-item-row');
            if (!row) return;

            // Ctrl + click
            if (e.ctrlKey || e.metaKey) {
                toggleSingleSelection(row);
                e.preventDefault();
            }
            // Shift + click
            else if (e.shiftKey) {
                selectRange(row);
                e.preventDefault();
            }
        });

        // 5. Escape tugmasi bilan tanlashni tozalash
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                clearAllSelections();
            }
        });
    }

    // Bitta qatorni tanlash/ochirish
    function toggleSingleSelection(row) {
        const cartId = getCartIdFromRow(row);

        if (selectedCartIds.has(cartId)) {
            // Tanlashni olib tashlash
            selectedCartIds.delete(cartId);
            row.classList.remove('selected');
        } else {
            // Tanlash
            selectedCartIds.add(cartId);
            row.classList.add('selected');
        }
    }

    // Barcha tanlovlarni tozalash
    function clearAllSelections() {
        // Barcha tanlangan qatorlarni tozalash
        document.querySelectorAll('#cart-tbody .cart-item-row.selected').forEach(row => {
            row.classList.remove('selected');
        });

        // ID'larni tozalash
        selectedCartIds.clear();
        console.log('Barcha tanlovlar tozalandi');
    }

    // Row dan cart ID olish
    function getCartIdFromRow(row) {
        if (!row) return null;

        // Avval data-cart-id ni tekshirish
        const cartIdAttr = row.getAttribute('data-cart-id');
        if (cartIdAttr) return parseInt(cartIdAttr);

        // Keyin data-id ni tekshirish
        const idAttr = row.getAttribute('data-id');
        if (idAttr) return parseInt(idAttr);

        // Datasets orqali
        if (row.dataset.cartId) return parseInt(row.dataset.cartId);
        if (row.dataset.id) return parseInt(row.dataset.id);

        return null;
    }

    // Shift bilan diapazon tanlash
    function selectRange(endRow) {
        if (!endRow) return;

        const rows = Array.from(document.querySelectorAll('#cart-tbody .cart-item-row'));
        if (rows.length === 0) return;

        // Avval tanlangan qatorni topish yoki birinchi qator
        let startRow = null;
        if (selectedCartIds.size > 0) {
            // Oxirgi tanlangan qatorni topish
            const selectedRows = Array.from(document.querySelectorAll('#cart-tbody .cart-item-row.selected'));
            if (selectedRows.length > 0) {
                startRow = selectedRows[selectedRows.length - 1];
            }
        }

        if (!startRow) {
            startRow = rows[0];
        }

        const startIndex = rows.indexOf(startRow);
        const endIndex = rows.indexOf(endRow);

        if (startIndex === -1 || endIndex === -1) return;

        // Barcha tanlovlarni tozalash
        clearAllSelections();

        // Yangi diaposonni tanlash
        const minIndex = Math.min(startIndex, endIndex);
        const maxIndex = Math.max(startIndex, endIndex);

        for (let i = minIndex; i <= maxIndex; i++) {
            const row = rows[i];
            const cartId = getCartIdFromRow(row);

            if (cartId) {
                selectedCartIds.add(cartId);
                row.classList.add('selected');
            }
        }
    }

    // Drag bilan diapazon tanlash
    function selectRangeBetween(startRow, endRow) {
        if (!startRow || !endRow) return;

        const rows = Array.from(document.querySelectorAll('#cart-tbody .cart-item-row'));
        const startIndex = rows.indexOf(startRow);
        const endIndex = rows.indexOf(endRow);

        if (startIndex === -1 || endIndex === -1) return;

        // Barcha tanlovlarni tozalash
        clearAllSelections();

        // Yangi diaposonni tanlash
        const minIndex = Math.min(startIndex, endIndex);
        const maxIndex = Math.max(startIndex, endIndex);

        for (let i = minIndex; i <= maxIndex; i++) {
            const row = rows[i];
            const cartId = getCartIdFromRow(row);

            if (cartId) {
                selectedCartIds.add(cartId);
                row.classList.add('selected');
            }
        }
    }

    // renderCartItems funksiyasini yangilang:
    function renderCartItems() {
        const tbody = document.getElementById('cart-tbody');
        if (!tbody) return;

        tbody.innerHTML = '';

        cartItems.slice().reverse().forEach((item, index) => {
            const row = document.createElement('tr');
            row.setAttribute('data-cart-id', item.id);
            row.setAttribute('data-id', item.id);
            row.className = 'cart-item-row';

            // Agar oldin tanlangan bo'lsa, selected class qo'shish
            if (selectedCartIds.has(item.id)) {
                row.classList.add('selected');
            }

            row.innerHTML = `
            <td>${index + 1}</td>
            <td class="product_name">${item.product_name}</td>
            <td class="d-none">${item.product_measure || ''}</td>
            <td class='d-none'>
                <div class="input-group">
                    <input type="text" onkeyup="formatInput(this)" class="make_intcomma cart-input pack-input" 
                           value="${formatNumber(item.total_pack)}" min="0" step="any"
                           data-pack="${item.pack_size || 1}"
                           onchange="updateCartItem(${item.id}, 'total_pack', this.value)">
                </div>
            </td>
            <td class="d-none">
                <div class="input-group">
                    <input type="text" onkeyup="formatInput(this)" class="make_intcomma cart-input price-input" 
                           value="${formatNumber(item.price)}" min="0" step="any"
                           onchange="updateCartItem(${item.id}, 'price', this.value)">
                </div>
            </td>
            <td class="price_text">${formatNumber(item.price_without_skidka)}</td>
            <td>
                <div class="input-group">
                    <input type="text" onkeyup="formatInput(this)" class="make_intcomma cart-input quantity-input" 
                           value="${formatNumber(item.quantity)}" min="0" step="any"
                           onchange="updateCartItem(${item.id}, 'quantity', this.value)">
                </div>
            </td>

            <td class="d-none">
                <div class="input-group">
                    <input type="text" onkeyup="formatInput(this)" class="make_intcomma cart-input discount-input" 
                           value="${formatNumber(item.discount)}" min="0" step="any"
                           onchange="updateCartItem(${item.id}, 'discount', this.value)">
                </div>
            </td>

            <td class="total" data-value="${item.total}">${formatNumber(item.total)}</td>
            <td>
                <span style="height:1.5rem;" onclick="deleteCartItem(${item.id})" type="button" class="delete-cart-btn">
                    ❌
                </span>
            </td>
        `;

            tbody.appendChild(row);
        });

        updateTotals();

        // Yangi qatorlar qo'shilganda event listener'larni qayta o'rnatish
        setTimeout(() => initCartSelection(), 0);

        if ($('#cart-tbody tr').length > 0) {
            $('#cartsdiv').show()
            $('#cartnonediv').hide()
            $('#valyuta_input')[0]?.selectize?.disable()
        } else {
            $('#cartsdiv').hide()
            $('#cartnonediv').show()
            $('#valyuta_input')[0]?.selectize?.enable()
        }
    }

    // DOM yuklanganda tanlashni ishga tushirish
    document.addEventListener('DOMContentLoaded', function () {
        // POS modal ochilganda
        $('#posModal').on('shown.bs.modal', function () {
            setTimeout(() => {
                initCartSelection();
            }, 500);
        });

        // Har safar cart yangilanganda event listener'larni qayta o'rnatish
        const originalLoadCartItems = loadCartItems;
        window.loadCartItems = async function () {
            await originalLoadCartItems();
            setTimeout(() => {
                initCartSelection();
            }, 200);
        };
    });

    // Input yoki button bosilganda tanlashni oldini olish
    document.addEventListener('click', function (e) {
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON') {
            e.stopPropagation();
        }
    });

    // Qatorning input elementlarida ishlaganda tanlashni o'chirish
    document.addEventListener('DOMContentLoaded', function () {
        // Input bosilganda
        document.addEventListener('focusin', function (e) {
            if (e.target.tagName === 'INPUT' && e.target.closest('.cart-item-row')) {
                const row = e.target.closest('.cart-item-row');
                row.style.backgroundColor = '#ffffff'; // Input focus bo'lganda rangni o'zgartirish
            }
        });

        // Input'dan chiqqanda
        document.addEventListener('focusout', function (e) {
            if (e.target.tagName === 'INPUT' && e.target.closest('.cart-item-row')) {
                const row = e.target.closest('.cart-item-row');
                const cartId = getCartIdFromRow(row);
                if (selectedCartIds.has(cartId)) {
                    row.style.backgroundColor = ''; // Tanlangan rangga qaytarish
                }
            }
        });
    });

    // DEBUG uchun: konsolga tanlanganlar ro'yxatini chiqarish
    function debugSelection() {
        // console.log('Tanlangan IDlar:', Array.from(selectedCartIds));
        // console.log('Tanlangan qatorlar soni:', selectedCartIds.size);
    }


    // Cartga yangi mahsulot qo'shish
    async function addCart(productId, quantity = 1) {
        if (!currentShopId) {
            showAlert('Iltimos, avval shop yaratiling', 'warning');
            return;
        }

        try {
            // const productElement = document.querySelector(`[data-value*="${productId}&"]`);productrow
            const productElement = document.querySelector(`#productrow${productId}`);
            if (!productElement) {
                showAlert('Mahsulot topilmadi', 'danger');
                return;
            }
            const productData = productElement.getAttribute('data-value').split('&');
            const productName = productData[1];
            // const quantity = 1;
            const packSize = parseFloat(productData[4]) || 1;
            const productMeasure = parseFloat(productData[-1]) || '';
            const totalPack = quantity / packSize;

            const price = parseFloat(cleanNumber(document.getElementById(`productprice${productId}`).textContent));

            const formData = new FormData();
            formData.append('product_id', productId);
            formData.append('quantity', quantity);
            formData.append('total_pack', totalPack);
            formData.append('agreed_price', price);
            formData.append('product_price', price);

            const response = await fetch(`{% url 'b2c_shop_create' %}?id=${currentShopId}&request_type=cart_add`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            });

            const data = await response.json();

            if (data.success) {
                //showAlert("Mahsulot savatga qo'shildi", "success");

                // Yangi cart elementini qo'shamiz
                const newItem = {
                    id: data.cart_id,
                    product_id: productId,
                    product_name: productName,
                    quantity: quantity,
                    total_pack: totalPack,
                    price: price,
                    price_without_skidka: price,
                    discount: 0,
                    total: quantity * price,
                    pack_size: packSize,
                    product_measure: productMeasure,
                };
                cartItems.push(newItem);
                renderCartItems();
                updateTotals();
                // Inputni tozalash
                // document.getElementById('productSearchInput').value = '';
                
                updateProductQuantity(data.product_id, data.rest)
                
                if (data.active_shops) {
                    renderActiveShops(data.active_shops)
                }
            } else {
                showAlert(data.message || "Xatolik yuz berdi", "danger");
            }
        } catch (error) {
            console.error('Cart qo\'shishda xatolik:', error);
            showAlert('Server bilan bog\'lanishda xatolik', 'danger');
        }
    }

    // Cart elementini yangilash
    async function updateCartItem(cartId, field, value) {
        try {
            const row = document.querySelector(`.cart-item-row[data-cart-id="${cartId}"]`);
            if (field === 'quantity' || field === 'price' || field === 'total_pack' || field === 'discount') {
                value = cleanNumber(value)
            }
            // Avvalgi qiymatni saqlab olamiz
            const itemIndex = cartItems.findIndex(item => item.id === cartId);
            if (itemIndex === -1) return;

            const oldItem = { ...cartItems[itemIndex] }; // Avvalgi qiymatlarni nusxalaymiz
            const oldValue = cartItems[itemIndex][field];

            // Local cart items ni yangilaymiz (vaqtincha)
            cartItems[itemIndex][field] = parseFloat(value);


            // Agar quantity yoki price o'zgarsa, totalni qayta hisoblaymiz
            if (field === 'quantity' || field === 'price') {
                const quantity = cartItems[itemIndex].quantity;
                const price = cartItems[itemIndex].price;
                cartItems[itemIndex].total = quantity * price;

                // Agar quantity o'zgarsa, total_pack ni ham yangilaymiz
                if (field === 'quantity') {
                    const packSize = cartItems[itemIndex].pack_size || 1;
                    cartItems[itemIndex].total_pack = quantity / packSize;
                }

                if (field === 'price') {
                    cartItems[itemIndex].price_without_skidka = cleanNumber(row.querySelector('.price_text').textContent)
                }
            }

            // Agar total_pack o'zgarsa, quantity ni yangilaymiz
            if (field === 'total_pack') {
                const packSize = cartItems[itemIndex].pack_size || 1;
                cartItems[itemIndex].quantity = value * packSize;
            }

            if (field === 'price') {
                cartItems[itemIndex].discount = 100 - (100 / cartItems[itemIndex].price_without_skidka * cartItems[itemIndex].price)
            }

            if (field === 'discount') {
                cartItems[itemIndex].price = cartItems[itemIndex].price_without_skidka * (1 - cartItems[itemIndex].discount / 100);
            }
            cartItems[itemIndex].total = cartItems[itemIndex].quantity * cartItems[itemIndex].price;
            // UI ni yangilaymiz (vaqtincha)
            renderCartItems();
            updateTotals();

            const formData = new FormData();
            // formData.append(field, value);

            formData.append('quantity', cartItems[itemIndex].quantity);
            formData.append('discount', cartItems[itemIndex].discount);
            formData.append('total_pack', cartItems[itemIndex].total_pack);
            formData.append('price', cartItems[itemIndex].price);
            formData.append('price_without_skidka', cartItems[itemIndex].price_without_skidka);

            const response = await fetch(`{% url 'b2c_shop_create' %}?id=${currentShopId}&cart_id=${cartId}&request_type=cart_edit`, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            });

            const data = await response.json();

            if (data.success) {
                // showAlert('Mahsulot yangilandi', 'success');
                updateProductQuantity(data.product_id, data.rest)

                if (data.active_shops) {
                    renderActiveShops(data.active_shops)
                }
            } else {
                // Xatolik bo'lsa, avvalgi qiymatlarga qaytaramiz
                cartItems[itemIndex] = { ...oldItem }; // Avvalgi holatiga qaytaramiz

                // UI ni qayta yangilaymiz
                renderCartItems();
                updateTotals();

                showAlert(data.message || 'Yangilashda xatolik', 'danger');

                // Xatolik bo'lsa, cartni qayta yuklaymiz
                loadCartItems();
            }
        } catch (error) {
            console.error('Cart yangilashda xatolik:', error);

            // Xatolik bo'lsa, avvalgi qiymatlarga qaytaramiz
            const itemIndex = cartItems.findIndex(item => item.id === cartId);
            if (itemIndex !== -1) {
                // Avvalgi qiymatni qayta o'rnatish
                const inputElement = document.querySelector(`[data-id="${cartId}"] .${field}-input`);
                if (inputElement) {
                    inputElement.value = oldValue;
                }
            }

            // Cartni qayta yuklaymiz
            loadCartItems();
            showAlert('Server bilan bog\'lanishda xatolik', 'danger');
        }
    }

    // Cart elementini o'chirish
    async function deleteCartItem(cartId) {
        if (!confirm('Haqiqatan ham ushbu mahsulotni o\'chirmoqchimisiz?')) {
            return;
        }
        const response = await fetch(`{% url 'b2c_shop_create' %}?id=${currentShopId}&cart_id=${cartId}&request_type=cart_delete`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        });

        const data = await response.json();

        if (data.success) {
            // showAlert("Mahsulot o'chirildi", "success");
            updateProductQuantity(data.product_id, data.rest)
            // Local cart items dan o'chiramiz
            cartItems = cartItems.filter(item => item.id !== cartId);
            renderCartItems();
            updateTotals();

            if (data.active_shops) {
                renderActiveShops(data.active_shops)
            }
        } else {
            showAlert(data.message || "O'chirishda xatolik", "danger");
        }

        try {
        } catch (error) {
            console.error('Cart o\'chirishda xatolik:', error);
            showAlert('Server bilan bog\'lanishda xatolik', 'danger');
        }
    }

    // Jami summalarni yangilash
    function updateTotals() {
        let totalPack = 0;
        let totalQuantity = 0;
        let totalSum = 0;
        let totalSumwithoutSkidka = 0

        let totalSkidkaPrice = 0;


        cartItems.forEach(item => {
            totalPack += item.total_pack;
            totalQuantity += item.quantity;
            totalSum += item.total;
            totalSumwithoutSkidka += item.price_without_skidka * item.quantity
        });

        chegirma = 0;
        if (chegirma > 0) {
            totalSum = totalSum - chegirma;
        }

        totalSkidkaPrice = totalSumwithoutSkidka - totalSum
        totalSkidkaPercent = 100 - (100 / totalSumwithoutSkidka * totalSum)

        // document.getElementById('pack_total').textContent = formatNumber(totalPack);
        document.getElementById('quantity_total').textContent = formatNumber(totalQuantity);
        document.getElementById('total_sum').textContent = formatNumber(totalSum);
        document.getElementById('all_total').textContent = formatNumber(totalSum);
        document.getElementById('all_total_without_skidka').textContent = formatNumber(totalSumwithoutSkidka);
        document.getElementById('total_skidka_price').textContent = formatNumber(totalSkidkaPrice);
        document.getElementById('total_skidka_percent').textContent = formatNumber(isNaN(Number(totalSkidkaPercent)) ? 0 : Number(totalSkidkaPercent));

        document.getElementById('all_total_2').value = formatNumber(totalSum);


        let total = calculatePaymentTotal().replace(/\s+/g, '')

        // if ($('#qarzvalyuta').data())
        // $('#qarzsumma').val(formatNumber(totalSum))

        // const isDollar = $('#qarzvalyuta option:selected').data('id_dollar');
        // $('#qarzsumma').val(formatNumber(isDollar ? totalSum / currentKurs : totalSum));

        updateqarzsumma(totalSum)
        currentDatas.total_price = totalSum

    }


    // Xabarlarni ko'rsatish
    function showAlert(message, type) {
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show`;
        alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
        alertElement.style.zIndex = '10000000';
        alertElement.style.position = 'relative';


        document.getElementById('alert-container').appendChild(alertElement);

        setTimeout(() => {
            alertElement.remove();
        }, 5000);
    }
    // Inputni tozalash
    function clearInputProduct() {
        document.getElementById('productSearchInput').value = '';
    }



    // Narx turini o'zgartirganda narxlarni yangilash
    const priceTypeRadios = document.querySelectorAll('.price_type_input');
    const valyutaSelect = document.getElementById('valyuta_input');



    function updateAllPrices() {
        const valyutaEl = document.getElementById('valyuta_input');
        // const selectedValyutaId = $('#valyuta_input')[0].selectize.getValue()
        const selectedValyutaId = document.getElementById('valyuta_input')?.selectize?.getValue()
            ?? document.getElementById('valyuta_input')?.value;


        const selectedPriceTypeId =
            document.querySelector('.price_type_input:checked')?.value || null;

        document.querySelectorAll('#productTable span[data-prices]').forEach(span => {
            let pricesData = [];

            try {
                pricesData = JSON.parse(span.dataset.prices || '[]');
            } catch (e) {
                console.error('JSON parse error:', e);
            }

            // default qiymat
            let price = 0;

            const foundValyuta = pricesData.find(
                v => String(v.valyuta_id) === String(selectedValyutaId)
            );

            if (foundValyuta && Array.isArray(foundValyuta.summas)) {
                const foundPrice = foundValyuta.summas.find(
                    s => String(s.price_type) === String(selectedPriceTypeId)
                );

                if (foundPrice?.summa) {
                    price = foundPrice.summa;
                }
            }

            span.textContent = formatNumber(price);
        });
    }

    updateAllPrices();
    priceTypeRadios.forEach(radio => radio.addEventListener('change', updateAllPrices));


</script>



<script>


    function calculaterest(item) {
        // const mainBox = $(item).closest('.plus_button');
        const isDollar = $(item).data('dollar') === true;
        let input = $(item).siblings('.payment-input');


        if (input) {
            $(input).val('')
            let inputValue = 0
            if (isDollar) {
                inputValue = (parseFloat(input.val()) || 0) * currentKurs;
            } else {
                inputValue = parseFloat(input.val()) || 0;
            }

            $(input).trigger('focus');

            let tolashSummasi = parseFloat(calculatePaymentTotal().replace(/\s+/g, ''));

            console.log(tolashSummasi, 'jjjjjjjjj')
            const selectize = $('#valyuta_input')[0]?.selectize;
            if (!selectize) return;
            const selectedValue = selectize.getValue();
            const selectedOption = selectize.options[selectedValue];

            const isSom_main = selectedOption?.is_som === true || selectedOption?.is_som === "True";
            const isDollar_main = selectedOption?.is_dollar === true || selectedOption?.is_dollar === "True";

            if (isSom_main) {
                if (isDollar) {
                    $(input).val(formatNumber((tolashSummasi / currentKurs).toFixed(2)));
                } else {
                    $(input).val(formatNumber(tolashSummasi));
                }
            }
            else {
                if (isDollar) {
                    $(input).val(formatNumber(tolashSummasi));
                } else {
                    $(input).val(formatNumber((tolashSummasi * currentKurs).toFixed(2)));
                }
            }

            updateCheckPayments();


            // Umumiy hisobni yangilash
            updatePaymentTotal();
        }
    }





    $(document).on('click', '.remove-field', function () {
        const parentBox = $(this).closest('.input-box');
        const input = parentBox.find('.payment-input');

        // Inputni tozalaymiz
        input.val('');

        updatePaymentTotal()
    });


    // function updatePaymentTotal() {
    //     let total = calculatePaymentTotal()
    //     // $('#tolash_summasi').text(total)
    //     console.log(total, 'yyyyyyyyyyy')
    //     $('#qarzsumma').val(total)
    // }

    // Masalan, har input o‘zgarganda hisoblash uchun:
    $(document).on('input', '.payment-input', function () {
        updatePaymentTotal();
        updateCheckPayments();

    });

</script>



<script>




    function fetchDebtInfo() {
        const debtorSelectize = $('#mainSelectDebtor')[0]?.selectize;
        const debtorId = debtorSelectize ? debtorSelectize.getValue() : '';

        fetch(`/get-debts/${debtorId}/`)
            .then(response => response.json())
            .then(data => {
                updatePaysDiv(data);
            })
            .catch(error => {
                console.error('Xatolik:', error);
            });
    }

    function updatePaysDiv(data) {
        const paysDiv = document.getElementById('pays-div');
        if (!paysDiv) return;

        let qarzHTML = `
        <div class="col-md-6">
            <strong>Qarz:</strong>
            <div class="mt-2">
    `;

        let haqHTML = `
        <div class="col-md-6">
            <strong>Haq:</strong>
            <div class="mt-2">
    `;

        // Valyuta + Wallet larni bog‘lash
        data.valyutas_for_debt.forEach(valyuta => {
            const wallet = data.wallets.find(w => w.valyuta_id === valyuta.id);
            const summa = wallet ? wallet.summa : 0;

            if (summa <= 0) {
                qarzHTML += `
                <p class="text-danger mb-0">
                    ${valyuta.name}: ${formatNumber(summa)}
                </p>
            `;
            } else {
                haqHTML += `
                <p class="text-success mb-0">
                    ${valyuta.name}: ${formatNumber(summa)}
                </p>
            `;
            }
        });

        qarzHTML += `</div></div>`;
        haqHTML += `</div></div>`;

        // Yakuniy HTML — ikki ustunli
        paysDiv.innerHTML = `
            ${qarzHTML}
            ${haqHTML}
    `;
    }

    $(document).ready(function () {
        // DOM elementni olish (jQuery elementning [0]-chi elementi)
        var fullscreenPaymentEl = $('#fullscreenPayment')[0];

        // Bootstrap modal obyekti yaratish
        var fullscreenPaymentModal = new bootstrap.Modal(fullscreenPaymentEl);

        // Modalni ochish
        $('#fullscreenPaymentBtn').on('click', function () {

            let filialId = document.getElementById('select-filial').value;

            document.querySelectorAll('.kassa_merges').forEach(element => {
                if (element.dataset.filial != filialId) {
                    element.style.display = 'none';
                    return;
                } else {
                    element.style.display = '';
                }
            });

            initializeShop(currentDatas.id);
            document.querySelectorAll('.input-box').forEach(element => {
                element.style.display = 'none';
            });
            fetchDebtInfo()
            fullscreenPaymentModal.show();
            calculatePaymentTotal();
            loadExistingPaymentsForModal();
            updatecheckDatas()
        });

        // Modalni yopish va inputlarni tozalash
        function closeFullscreen() {
            fullscreenPaymentModal.hide();
            $('#fullscreenPayment').find('.payment-input').val('0');
        }

        // Tugmalarni bog‘lash
        $('#closeFullscreenBtn, #cancelPaymentBtn').on('click', closeFullscreen);

        // ESC yoki backdrop bosilganda inputlarni tozalash
        $('#fullscreenPayment').on('hidden.bs.modal', function () {
            $(this).find('.payment-input').val('0');
        });
    });


    // </script>

<script>
    function renderActiveShops(activeShops) {
        const container = document.querySelector('.all_shops');
        container.innerHTML = ''; // avvalini tozalaymiz
        if (activeShops) {
            activeShops.forEach(shop => {
                const div = document.createElement('div');
                
                if(shop.id === currentShopId){
                    var color = 'background: #0d6efd; color: #fff;'
                }else{
                    var color = 'background: #default; color: default;'
                }
                div.className = 'btn btn-sm btn-light';
                div.style.margin = '0.5rem';
                div.style.padding = '0.5rem';

                div.innerHTML = `
                    <strong onclick="$('#posModal').modal('hide');;setTimeout(()=>editShopModal(${shop.id}),200);" style="${color}margin-right: 0.3rem;">${shop.date}</strong>
                    <i class="fa fa-x text-danger" style="cursor:pointer;"></i>
                `;

                // X bosilganda shu elementni o'chirish
                div.querySelector('.fa-x').addEventListener('click', () => {
                    div.remove();
                });

                container.appendChild(div);
            });
        }
    }
</script>
<script>
    // Sotuvlar ro'yxatini boshqarish
    document.addEventListener('DOMContentLoaded', function () {
        const shopsContainer = document.getElementById('shops-container');
        const paginationContainer = document.getElementById('pagination-container');
        const loadingSpinner = document.getElementById('loading-spinner');
        const filterForm = document.getElementById('filter-form');
        const returnModal = document.getElementById('return-modal');
        const returnOverlay = document.getElementById('return-modal-overlay');
        const closeReturnModal = document.getElementById('close-return-modal');
        const returnShopInfo = document.getElementById('return-shop-info');
        const subtractFromDebtCheckbox = document.getElementById('subtract-from-debt');
        const paymentSection = document.getElementById('payment-section');
        const addPaymentBtn = document.getElementById('add-payment');
        const paymentsContainer = document.getElementById('payments-container');
        const totalReturnDisplay = document.getElementById('total-return-display');
        const confirmReturnBtn = document.getElementById('confirm-return');
        // const filialId = document.getElementById('select-filial').value;


        let currentPage = 1;
        let currentShops = [];
        let currentShop = null;
        let totalReturnAmount = 0;
        let payments = [];



        // Sahifani yuklash
        function loadShops(page = 1) {
            currentPage = page;
            loadingSpinner.style.display = 'block';
            shopsContainer.style.opacity = '0.5';

            const formData = new FormData(filterForm);
            const params = new URLSearchParams();

            // Form ma'lumotlarini qo'shamiz
            for (let [key, value] of formData.entries()) {
                if (key === 'deliver' || key === 'client') {
                    const values = formData.getAll(key);
                    values.forEach(val => params.append(key, val));
                } else if (value) {
                    params.append(key, value);
                }
            }

            params.append('page', page);
            params.append('filial', document.getElementById('select-filial').value);

            fetch(`?${params.toString()}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => response.json())
                .then(data => {
                    currentShops = data.shops;
                    renderShops(data.shops);
                    renderPagination(data);
                    updateTotals(data);
                    loadingSpinner.style.display = 'none';
                    shopsContainer.style.opacity = '1';
                    // if (data.active_shops) {
                    //     renderActiveShops(data.active_shops);
                    // }

                })
                .catch(error => {
                    console.error('Xatolik:', error);
                    loadingSpinner.style.display = 'none';
                    shopsContainer.style.opacity = '1';
                    shopsContainer.innerHTML = `
                <div class="alert alert-danger">
                    Xatolik yuz berdi: ${error.message}
                </div>
            `;
                });
        }

        // Sotuvlarni render qilish
        function renderShops(shops) {
            if (shops.length === 0) {
                shopsContainer.innerHTML = `
                <div class="card">
                    <div class="card-body text-center py-5">
                        <h5>Hech qanday sotuv topilmadi</h5>
                        <p class="text-muted">Filterlarni o'zgartirib ko'ring</p>
                    </div>
                </div>
            `;
                return;
            }

            let html = '';
            shops.forEach((shop, index) => {

                // To'lov jami larini formatlash
                let paymentTotalsHtml = '';
                for (const [valyuta, summa] of Object.entries(shop.payment_totals)) {
                    paymentTotalsHtml += `
                        <div class="payment-total-item">
                            <div class="payment-total-label">${valyuta}</div>
                            <div class="payment-total-value">${parseFloat(summa).toLocaleString()}</div>
                        </div>
                    `;
                }

                // if (!paymentTotalsHtml) {
                //     paymentTotalsHtml = '<div class="text-muted">To\'lovlar mavjud emas</div>';
                // }




                const paymentByCurrency = {};
                let totalPaid = 0;

                if (shop.payment_details && shop.payment_details.length > 0) {
                    shop.payment_details.forEach(payment => {
                        if (!paymentByCurrency[payment.valyuta]) {
                            paymentByCurrency[payment.valyuta] = 0;
                        }
                        if (!payment.is_debt) {
                            paymentByCurrency[payment.valyuta] += payment.summa;
                        }
                        totalPaid += payment.summa;
                    });
                }




                let paymentDisplayHTML = '';
                if (Object.keys(paymentByCurrency).length > 0) {
                    paymentDisplayHTML = Object.entries(paymentByCurrency).map(([currency, amount]) => `
                        <div><strong>${formatNumber(amount)} ${currency}</strong></div>
                    `).join('');
                } else {
                    paymentDisplayHTML = '<div><strong>0</strong></div>';
                }


                let chiqimTotalsHtml = '';
                for (const [valyuta, summa] of Object.entries(shop.chiqim_totals)) {
                    chiqimTotalsHtml += `
                        <div class="payment-total-item">
                            <div class="payment-total-label">${valyuta}</div>
                            <div class="payment-total-value">${parseFloat(summa).toLocaleString()}</div>
                        </div>
                    `;
                }

                // if (!chiqimTotalsHtml) {
                //     chiqimTotalsHtml = '<div class="text-muted">Chiqimlar mavjud emas</div>';
                // }

                // Chegirma ko'rsatish
                let chegirmaHtml = '';
                if (shop.chegirma > 0) {
                    chegirmaHtml = `<span class="chegirma-badge">Chegirma: ${parseFloat(shop.chegirma).toLocaleString()}</span>`;
                }

                html += `
                    <div class="shop-table">
                        <div class="shop-header" onclick="toggleShopDetails(${shop.id})">
                            <div class="shop-main-info">
                                <div>
                                    <strong>${shop.debtor_name}</strong>
                                    <br>
                                    <small class="text-muted">${shop.date}</small>
                                    ${chegirmaHtml}
                                </div>
                                <div>
                                    <div class="text-success"><strong>${parseFloat(shop.total_price).toLocaleString()} ${shop.valyuta_name}</strong></div>
                                    <small class="text-muted">Jami summa</small>
                                </div>
    
                                <div>
                                    <div class="text-success"><strong>${parseFloat(shop.total_returned_sum).toLocaleString()} ${shop.valyuta_name}</strong></div>
                                    <small class="text-muted">Qaytarilgan summa</small>
                                </div>
    
                                <div>
                                    <div><strong>${shop.total_quantity}</strong></div>
                                    <small class="text-muted">Mahsulotlar</small>
                                </div>
                                <div>
                                    ${paymentDisplayHTML}
                                    <small class="text-muted">To'langan</small>
                                </div>
    
                                <div class="action-buttons">
                                    <button class="btn btn-primary btn-sm" onclick="event.stopPropagation(); setqarzdate(); editShopModal(${shop.id});$('#paymenttabopen').trigger('click')">
                                        <i class="fas fa-edit"></i>
                                    </button>
    
                                    <button class="btn btn-warning btn-sm" onclick="event.stopPropagation(); openReturnModal(${shop.id})">
                                        <i class="fas fa-undo"></i> Qaytarish
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="shop-details" id="details-${shop.id}">
                            <!-- Mahsulotlar qismi -->
                            <div class="carts-section">
                                <div class="section-title">
                                    <span>Sotilgan Mahsulotlar</span>
                                </div>
                                <div class="table-responsive">
                                    <table class="table table-sm table-bordered">
                                        <thead>
                                            <tr>
                                                <th>Mahsulot</th>
                                                <th>Narx</th>
                                                <th>Soni</th>
                                                <th>Summa</th>
                                                <th>Qaytarilgan</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            ${shop.carts.map(cart => `
                                                <tr>
                                                    <td>${cart.product_name}</td>
                                                    <td>${parseFloat(cart.price).toLocaleString()}</td>
                                                    <td>${parseFloat(cart.quantity).toLocaleString()}</td>
                                                    <td>${parseFloat(cart.total).toLocaleString()}</td>
                                                    <td>${parseFloat(cart.total_returned).toLocaleString()}</td>
                                                </tr>
                                            `).join('')}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                            
                            <!-- To'lovlar qismi -->
                            <div class="payments-section">
                                <div class="section-title">
                                    <span>To'lovlar</span>
                                </div>
                                <div class="payment-totals">
                                    ${paymentTotalsHtml}
                                </div>
                                ${shop.payment_details.length > 0 ? `
                                    <div class="table-responsive">
                                        <table class="table table-sm table-bordered">
                                            <thead>
                                                <tr>
                                                    <th>Summa</th>
                                                    <th>Valyuta</th>
                                                    <th>Kassa</th>
                                                    <th>Sana</th>
                                                    <th>Turi</th>
                                                    <th>Holat</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${shop.payment_details.map(payment => `
                                                <tr class="${payment.is_debt ? 'debt-payment' : ''}">
                                                    <td>${parseFloat(payment.summa).toLocaleString()}</td>
                                                    <td>${payment.valyuta}</td>
                                                    <td>${payment.kassa}</td>
                                                    <td>${payment.date}</td>
                                                    <td class="${payment.type_pay == 1 ? 'text-primary' : 'text-danger'}">
                                                        ${payment.type_pay == 1 ? 'Kirim' : 'Chiqim'}
                                                    </td>
                                                    <td>
                                                        ${payment.is_debt
                        ? '<span class="badge bg-warning">Qarz</span>'
                        : '<span class="badge bg-success">To\'lov</span>'
                    }
                                                    </td>
                                                </tr>
                                            `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                ` : '<p class="text-muted">To\'lovlar mavjud emas</p>'}
                            </div>
    
                            <!-- Qaytarilgan summalar qismi -->
                            <div class="payments-section">
                                <div class="section-title">
                                    <span>Qaytarilgan summalar</span>
                                </div>
                                <div class="payment-totals">
                                    ${chiqimTotalsHtml}
                                </div>
                                ${shop.chiqim_details.length > 0 ? `
                                    <div class="table-responsive">
                                        <table class="table table-sm table-bordered">
                                            <thead>
                                                <tr>
                                                    <th>Summa</th>
                                                    <th>Valyuta</th>
                                                    <th>Kassa</th>
                                                    <th>Sana</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${shop.chiqim_details.map(chiqim => `
                                                <tr class="">
                                                    <td>${parseFloat(chiqim.summa).toLocaleString()}</td>
                                                    <td>${chiqim.valyuta}</td>
                                                    <td>${chiqim.kassa}</td>
                                                    <td>${chiqim.date}</td>
                                                </tr>
                                            `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                ` : '<p class="text-muted">Chiqimlar mavjud emas</p>'}
                            </div>
                            
                            <!-- Qaytarilgan mahsulotlar qismi -->
                            ${shop.return_details.length > 0 ? `
                                <div class="returns-section">
                                    <div class="section-title">
                                        <span>Qaytarilgan Mahsulotlar</span>
                                    </div>
                                    <div class="table-responsive">
                                        <table class="table table-sm table-bordered">
                                            <thead>
                                                <tr>
                                                    <th>Mahsulot</th>
                                                    <th>Qaytarilgan miqdor</th>
                                                    <th>Sana</th>
                                                    <th>Kim tomonidan</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${shop.return_details.map(return_item => `
                                                    <tr>
                                                        <td>${return_item.product_name}</td>
                                                        <td>${parseFloat(return_item.return_quantity).toLocaleString()}</td>
                                                        <td>${return_item.date}</td>
                                                        <td>${return_item.returned_by}</td>
                                                    </tr>
                                                `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                </div>
                            ` : ''}
                        </div>
                    </div>
                `;
            });

            shopsContainer.innerHTML = html;
        }

        // Pagination render qilish
        function renderPagination(data) {
            let html = '';

            if (data.total_pages > 1) {
                html = '<nav><ul class="pagination justify-content-center">';

                if (data.has_previous) {
                    html += `<li class="page-item">
                    <a class="page-link" href="#" onclick="loadShops(${data.current_page - 1})">← Oldingi</a>
                </li>`;
                }

                // Birinchi sahifalar
                for (let i = 1; i <= Math.min(3, data.total_pages); i++) {
                    html += `<li class="page-item ${i === data.current_page ? 'active' : ''}">
                    <a class="page-link" href="#" onclick="loadShops(${i})">${i}</a>
                </li>`;
                }

                // O'rtada nuqtalar
                if (data.current_page > 4) {
                    html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
                }

                // Joriy sahifa atrofi
                for (let i = Math.max(4, data.current_page - 1); i <= Math.min(data.total_pages - 1, data.current_page + 1); i++) {
                    if (i > 3 && i < data.total_pages) {
                        html += `<li class="page-item ${i === data.current_page ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="loadShops(${i})">${i}</a>
                    </li>`;
                    }
                }

                // Oxirgi nuqtalar
                if (data.current_page < data.total_pages - 2) {
                    html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
                }

                // Oxirgi sahifalar
                if (data.total_pages > 3) {
                    for (let i = Math.max(data.total_pages - 2, data.current_page + 2); i <= data.total_pages; i++) {
                        html += `<li class="page-item ${i === data.current_page ? 'active' : ''}">
                        <a class="page-link" href="#" onclick="loadShops(${i})">${i}</a>
                    </li>`;
                    }
                }

                if (data.has_next) {
                    html += `<li class="page-item">
                    <a class="page-link" href="#" onclick="loadShops(${data.current_page + 1})">Keyingi →</a>
                </li>`;
                }

                html += '</ul></nav>';
            }

            paginationContainer.innerHTML = html;
        }

        // Jami qiymatlarni yangilash


        function updateTotals(data) {


            let paymentsHTML = '';
            let debtpaymentsHTML = '';

            if (data.payments_by_currency) {
                paymentsHTML = Object.entries(data.payments_by_currency)
                    .map(([currency, amount]) => {
                        if (!amount || amount === 0) return '';
                        return `<h6 class="text-primary"><small>${formatNumber(amount)} ${currency}</small></h6>`;
                    })
                    .join('');
            } else {
                paymentsHTML = '<h6 class="text-primary"><small>0</small></h6>';
            }


            if (data.debtpayments_by_currency) {
                debtpaymentsHTML = Object.entries(data.debtpayments_by_currency)
                    .map(([currency, amount]) => {
                        if (!amount || amount === 0) return '';
                        return `<h6 class="text-primary"><small>${formatNumber(amount)} ${currency}</small></h6>`;
                    })
                    .join('');
            } else {
                debtpaymentsHTML = '<h6 class="text-primary"><small>0</small></h6>';
            }






            let debtsHTML = '';
            if (data.debts_by_currency && Object.keys(data.debts_by_currency).length > 0) {
                debtsHTML = Object.entries(data.debts_by_currency)
                    .map(([currency, amount]) => `
                    <h6 class="text-primary"><small>${formatNumber(amount)} ${currency}</small></h6>
                `).join('');
            } else {
                debtsHTML = '<h6 class="text-primary"><small>0</small></h6>';
            }
            // document.getElementById('current-page').textContent = data.current_page;
            $('#total-price').html(paymentsHTML)
            $('#totalpay-fromdebt').html(debtpaymentsHTML)
            $('#total-debt').html(debtsHTML)
            document.getElementById('total-quantity').textContent = parseFloat(data.total_quantity).toLocaleString();
            document.getElementById('total-shops').textContent = parseInt(data.total_shops).toLocaleString();
        }

        // Shop tafsilotlarini ochish/yopish
        window.toggleShopDetails = function (shopId) {
            const details = document.getElementById(`details-${shopId}`);
            details.classList.toggle('show');
        }

        // Qaytarish modalini ochish
        window.openReturnModal = function (shopId) {
            currentShop = currentShops.find(s => s.id === shopId);
            if (!currentShop) return;

            // Shop ma'lumotlarini ko'rsatish
            returnShopInfo.innerHTML = `
            <strong>${currentShop.debtor_name}</strong><br>
            <small>Sana: ${currentShop.date}</small><br>
            <small>Jami summa: ${parseFloat(currentShop.total_price).toLocaleString()} ${currentShop.valyuta_name}</small>
            ${currentShop.chegirma > 0 ? `<br><small>Chegirma: ${parseFloat(currentShop.chegirma).toLocaleString()}</small>` : ''}
        `;

            // Qaytariladigan mahsulotlar ro'yxati
            let productsHtml = '';
            totalReturnAmount = 0;

            currentShop.carts.forEach(cart => {
                const maxReturnable = cart.quantity - cart.total_returned;
                if (maxReturnable > 0) {
                    productsHtml += `
                    <div class="card mb-2">
                        <div class="card-body">
                            <h6 class="card-title">${cart.product_name}</h6>
                            <div class="row align-items-center">
                                <div class="col-4">
                                    <small class="text-muted">Qaytarish mumkin: ${maxReturnable}</small>
                                </div>
                                <div class="col-4">
                                    <small class="text-muted">Narx: ${parseFloat(cart.price).toLocaleString()}</small>
                                </div>
                                <div class="col-4">
                                    <input type="number" 
                                           class="form-control form-control-sm return-quantity" 
                                           data-cart-id="${cart.id}"
                                           data-price="${cart.price}"
                                           min="0" 
                                           max="${maxReturnable}" 
                                           step="0.01"
                                           placeholder="Miqdor"
                                           value="0"
                                           onchange="updateReturnTotal()">
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                }
            });

            if (!productsHtml) {
                productsHtml = '<div class="alert alert-info">Qaytarish mumkin bo\'lgan mahsulotlar yo\'q</div>';
            }

            document.getElementById('return-products-list').innerHTML = productsHtml;

            // To'lovlarni tozalash
            payments = [];
            paymentsContainer.innerHTML = '';
            updatePaymentSection();

            returnModal.classList.add('show');
            returnOverlay.classList.add('show');
        }

        // Qaytarish jami summasini yangilash
        window.updateReturnTotal = function () {
            totalReturnAmount = 0;
            const inputs = document.querySelectorAll('.return-quantity');

            inputs.forEach(input => {
                const quantity = parseFloat(input.value) || 0;
                const price = parseFloat(input.dataset.price);
                totalReturnAmount += quantity * price;
            });

            totalReturnDisplay.innerHTML = `
            Jami qaytarish summasi: <strong>${totalReturnAmount.toLocaleString()} ${currentShop.valyuta_name}</strong>
        `;

            updatePaymentSection();
        }

        // To'lov bo'limini yangilash
        function updatePaymentSection() {
            const isNaqdMijoz = currentShop.debtor_name.toLowerCase().includes('naqd');
            const shouldShowPayment = !subtractFromDebtCheckbox.checked || isNaqdMijoz;

            paymentSection.style.display = shouldShowPayment ? 'block' : 'none';

            if (shouldShowPayment) {
                totalReturnDisplay.style.display = totalReturnAmount > 0 ? 'block' : 'none';
            }
        }

        // To'lov qo'shish
        addPaymentBtn.addEventListener('click', function () {
            const paymentId = Date.now();
            const paymentHtml = `
            <div class="payment-row" id="payment-${paymentId}">
                <div class="payment-amount">
                    <label>Summa</label>
                    <input type="number" class="form-control payment-amount-input" 
                           step="0.01" min="0" placeholder="Summa"
                           onchange="updatePayments()">
                </div>
                <div class="payment-amount">
                    <label>Valyuta</label>
                    <select class="form-control valyuta-select" onchange="onValyutaChange(${paymentId})">
                        <option value="">Valyuta tanlang</option>
                        {% for valyuta in valyutalar %}
                            <option value="{{ valyuta.id }}" 
                                    data-is-dollar="{{ valyuta.is_dollar|yesno:'true,false' }}"
                                    data-is-som="{{ valyuta.is_som|yesno:'true,false' }}">
                                {{ valyuta.name }}
                            </option>
                        {% endfor %}
                    </select>
                </div>
                <div class="payment-amount">
                    <label>Kassa</label>
                    <select class="form-control kassa-select" id="kassa-${paymentId}" onchange="updatePayments()">
                        <option value="">Kassa tanlang</option>
                    </select>
                </div>
                <div class="remove-payment" onclick="removePayment(${paymentId})">
                    <i class="fas fa-times"></i>
                </div>
            </div>
        `;

            paymentsContainer.insertAdjacentHTML('beforeend', paymentHtml);
            payments.push({
                id: paymentId,
                amount: 0,
                valyuta_id: null,
                kassa_id: null
            });
        });


        // Valyuta o'zgarganda kassalarni yuklash
        window.onValyutaChange = function (paymentId) {
            const valyutaSelect = document.querySelector(`#payment-${paymentId} .valyuta-select`);
            const kassaSelect = document.querySelector(`#kassa-${paymentId}`);
            const valyutaId = valyutaSelect.value;

            if (valyutaId) {
                fetch(`/get-kassalar-by-valyuta/?valyuta_id=${valyutaId}`)
                    .then(response => response.json())
                    .then(data => {
                        kassaSelect.innerHTML = '<option value="">Kassa tanlang</option>';
                        data.kassalar.forEach(kassa => {
                            kassaSelect.innerHTML += `<option value="${kassa.id}" data-balance="${kassa.balance}">${kassa.name}</option>`;
                        });
                        updatePayments();
                    });
            } else {
                kassaSelect.innerHTML = '<option value="">Kassa tanlang</option>';
                updatePayments();
            }
        }

        // To'lovni o'chirish
        window.removePayment = function (paymentId) {
            const paymentElement = document.getElementById(`payment-${paymentId}`);
            if (paymentElement) {
                paymentElement.remove();
            }
            payments = payments.filter(p => p.id !== paymentId);
            updatePayments();
        }

        // To'lovlarni yangilash
        window.updatePayments = function () {
            let totalPaid = 0;

            payments.forEach(payment => {
                const paymentElement = document.getElementById(`payment-${payment.id}`);
                if (paymentElement) {
                    const amountInput = paymentElement.querySelector('.payment-amount-input');
                    const valyutaSelect = paymentElement.querySelector('.valyuta-select');
                    const kassaSelect = paymentElement.querySelector('.kassa-select');

                    payment.amount = parseFloat(amountInput.value) || 0;
                    payment.valyuta_id = valyutaSelect.value;
                    payment.kassa_id = kassaSelect.value;

                    // Valyuta konvertatsiyasi
                    if (payment.amount > 0 && payment.valyuta_id) {
                        const valyutaOption = valyutaSelect.options[valyutaSelect.selectedIndex];
                        const isDollar = valyutaOption.dataset.isDollar === 'true';
                        const isSom = valyutaOption.dataset.isSom === 'true';

                        if (currentShop.valyuta_is_dollar && isSom) {
                            // Dollar -> So'm
                            totalPaid += payment.amount / currentShop.kurs;
                        } else if (!currentShop.valyuta_is_dollar && isDollar) {
                            // So'm -> Dollar
                            totalPaid += payment.amount * currentShop.kurs;
                        } else {
                            totalPaid += payment.amount;
                        }
                    }
                }
            });

            // Jami to'langan summani ko'rsatish
            if (totalReturnAmount > 0) {
                totalReturnDisplay.innerHTML = `
                Jami qaytarish summasi: <strong>${totalReturnAmount.toLocaleString()} ${currentShop.valyuta_name}</strong><br>
                Jami to'langan: <strong>${totalPaid.toLocaleString()} ${currentShop.valyuta_name}</strong><br>
                Farq: <strong>${(totalReturnAmount - totalPaid).toLocaleString()} ${currentShop.valyuta_name}</strong>
            `;
            }
        }

        // Qarzdan ayirish checkbox'ini tinglash
        subtractFromDebtCheckbox.addEventListener('change', function () {
            updatePaymentSection();
        });

        // Qaytarishni tasdiqlash
        confirmReturnBtn.addEventListener('click', function () {
            const returnItems = [];
            const returnInputs = document.querySelectorAll('.return-quantity');

            returnInputs.forEach(input => {
                const quantity = parseFloat(input.value);
                if (quantity > 0) {
                    returnItems.push({
                        cart_id: input.dataset.cartId,
                        return_quantity: quantity
                    });
                }
            });

            if (returnItems.length === 0) {
                alert('Hech qanday miqdor kiritilmagan');
                return;
            }

            // To'lovlarni tekshirish
            const subtractFromDebt = subtractFromDebtCheckbox.checked;
            const isNaqdMijoz = currentShop.debtor_name.toLowerCase().includes('naqd');

            if ((!subtractFromDebt || isNaqdMijoz) && payments.length === 0) {
                alert('To\'lov usulini tanlang yoki to\'lov qo\'shing');
                return;
            }

            // To'lovlarni tekshirish
            let totalPaid = 0;
            const validPayments = [];

            payments.forEach(payment => {
                if (payment.amount > 0 && payment.valyuta_id && payment.kassa_id) {
                    totalPaid += payment.amount;
                    validPayments.push(payment);
                }
            });

            if ((!subtractFromDebt || isNaqdMijoz) && validPayments.length === 0) {
                alert('To\'g\'ri to\'lov ma\'lumotlarini kiriting');
                return;
            }

            confirmReturnBtn.disabled = true;
            confirmReturnBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Amalga oshirilmoqda...';

            fetch("{% url 'return_products' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    shop_id: currentShop.id,
                    return_items: returnItems,
                    payments: validPayments,
                    subtract_from_debt: subtractFromDebt,
                    filial: $('#select-filial').val()
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        alert(data.message);
                        returnModal.classList.remove('show');
                        returnOverlay.classList.remove('show');
                        loadShops(currentPage); // Sahifani yangilash
                    } else {
                        alert('Xatolik: ' + data.error);
                    }
                })
                .catch(error => {
                    console.error('Xatolik:', error);
                    alert('Server xatosi yuz berdi');
                })
                .finally(() => {
                    confirmReturnBtn.disabled = false;
                    confirmReturnBtn.innerHTML = '<i class="fas fa-check"></i> Qaytarishni Tasdiqlash';
                });
        });

        // Qaytarish modalini yopish
        closeReturnModal.addEventListener('click', function () {
            returnModal.classList.remove('show');
            returnOverlay.classList.remove('show');
        });

        returnOverlay.addEventListener('click', function () {
            returnModal.classList.remove('show');
            returnOverlay.classList.remove('show');
        });

        // Filter formasi
        filterForm.addEventListener('submit', function (e) {
            e.preventDefault();
            loadShops(1);
        });

        // Sahifani boshlang'ich yuklash
        loadShops(1);
    });
</script>



<script>
    // QarzModal-ni boshqarish
    $(document).on('click', '#qarzModalButton .method-box', function (e) {
        e.stopPropagation();

        const customerSelect = $('#mainSelectDebtor')[0]?.selectize;

        showQarzInputBox(this);
    });

    // Qarz input boxini ko'rsatish
    function showQarzInputBox(element) {
        let qarzInputBox = document.getElementById('qarzInputBox');
        const mainBox = $(element).closest('.plus_button');
        const isDollar = mainBox.find('.toggle-input').data('dollar') === true;


        const selectize = $('#valyuta_input')[0]?.selectize;
        if (!selectize) return;
        const selectedValue = selectize.getValue();
        const selectedOption = selectize.options[selectedValue];

        const isSom_main = selectedOption?.is_som === true || selectedOption?.is_som === "True";
        const isDollar_main = selectedOption?.is_dollar === true || selectedOption?.is_dollar === "True";



        // Qarz input boxini ko'rsatish
        qarzInputBox.style.display = 'block';

        if (isSom_main) {
            // Asosiy valyuta so‘m bo‘lsa
            $('#qarzBoxValyuta option').each(function () {
                if ($(this).data('is-dollar') === false) {
                    $('#qarzBoxValyuta').val($(this).val()).trigger('change');
                }
            });
        } else {
            // Asosiy valyuta dollar bo‘lsa
            $('#qarzBoxValyuta option').each(function () {
                if ($(this).data('is-dollar') === true) {
                    $('#qarzBoxValyuta').val($(this).val()).trigger('change');
                }
            });
        }



        qarzInputBox = $(qarzInputBox)
        const input = qarzInputBox.find('#qarzBoxSumma');
        input.val('')

        let inputValue = 0
        if (isDollar) {
            inputValue = (parseFloat(cleanNumber(input.val())) || 0) * currentKurs;
        } else {
            inputValue = parseFloat(cleanNumber(input.val())) || 0;
        }
        input.trigger('focus');
        let tolashSummasi = parseFloat(calculatePaymentTotal().replace(/\s+/g, ''));



        // Agar dollar bo‘lsa, kursga ko‘ra hisoblash
        if (isDollar) {
            input.val(formatNumber((tolashSummasi / currentKurs).toFixed(2)));
        } else {
            input.val(formatNumber(tolashSummasi));
        }



        const dueDateInput = document.getElementById('qarzBoxDueDate');
        const today = new Date();
        const lastDay = new Date(today.getFullYear(), today.getMonth() + 1, 0);

        // Mahalliy vaqt formati bilan YYYY-MM-DD yaratamiz
        const year = lastDay.getFullYear();
        const month = String(lastDay.getMonth() + 1).padStart(2, '0');
        const day = String(lastDay.getDate()).padStart(2, '0');

        dueDateInput.value = `${year}-${month}-${day}`;



        updatePaymentTotal();
    }

    function clearInputBox() {
        let qarzInputBox = document.getElementById('qarzInputBox');
        qarzInputBox.style.display = 'none';
        // const input = qarzInputBox.find('#qarzBoxSumma');
        // input.value = ''


        // document.getElementById('qarzBoxValyuta').value = '';
        document.getElementById('qarzBoxSumma').value = '';
        document.getElementById('qarzBoxDueDate').value = '';
        document.getElementById('qarzBoxComment').value = '';


    }

    // Qarz input boxini yopish
    function hideQarzInputBox() {
        const qarzInputBox = document.getElementById('qarzInputBox');
        qarzInputBox.style.display = 'none';
        updatePaymentTotal();
    }

    // Qarzni to'lovlar ro'yxatiga qo'shish
    function addQarzToPayment() {
        const valyutaId = document.getElementById('qarzBoxValyuta').value;
        const summa = parseFloat(cleanNumber(document.getElementById('qarzBoxSumma').value));
        const dueDate = document.getElementById('qarzBoxDueDate').value;
        const comment = document.getElementById('qarzBoxComment').value;

        if (!valyutaId || !summa || summa <= 0 || !dueDate) {
            showAlert('Iltimos, valyuta, summani va sanani to\'g\'ri kiriting', 'warning');
            return;
        }

        const valyutaSelect = document.getElementById('qarzBoxValyuta');
        const selectedOption = valyutaSelect.options[valyutaSelect.selectedIndex];
        const valyutaName = selectedOption.getAttribute('data-name');
        const isDollar = selectedOption.getAttribute('data-is-dollar') === 'true';

        // Qarz ma'lumotlarini global o'zgaruvchiga saqlash (sessionStorage o'rniga)
        window.currentQarzData = {
            type: 'qarz',
            valyuta_id: valyutaId,
            valyuta_name: valyutaName,
            summa: summa,
            due_date: dueDate,
            comment: comment,
            is_dollar: isDollar
        };

        // Input boxni yopish
        hideQarzInputBox();

        // Chekda ko'rsatish
        updateCheckPayments();

        // To'lov jamiini yangilash
        updatePaymentTotal();

        updateCheckPayments();


        showAlert('Qarz ma\'lumotlari qo\'shildi', 'success');
    }

    // Qarzni to'lovlar ro'yxatiga qo'shish
    function addQarzToPayment() {
        const valyutaId = document.getElementById('qarzBoxValyuta').value;
        const summa = parseFloat(cleanNumber(document.getElementById('qarzBoxSumma').value));
        const dueDate = document.getElementById('qarzBoxDueDate').value;
        const comment = document.getElementById('qarzBoxComment').value;

        if (!valyutaId || !summa || summa <= 0 || !dueDate) {
            showAlert('Iltimos, valyuta, summani va sanani to\'g\'ri kiriting', 'warning');
            return;
        }

        const valyutaSelect = document.getElementById('qarzBoxValyuta');
        const selectedOption = valyutaSelect.options[valyutaSelect.selectedIndex];
        const valyutaName = selectedOption.getAttribute('data-name');
        const isDollar = selectedOption.getAttribute('data-is-dollar') === 'true';

        // Input boxni yopish
        hideQarzInputBox();

        // Chekda ko'rsatish
        updateCheckPayments();

        // To'lov jamiini yangilash
        updatePaymentTotal();

        showAlert('Qarz ma\'lumotlari qo\'shildi', 'success');
    }

    $(document).on('input', '#qarzBoxSumma, #qarzBoxValyuta, #qarzBoxDueDate, #qarzBoxComment', function () {
        updateCheckPayments();
    });


    // To'lov ma'lumotlarini yig'ish
    function collectPaymentData() {
        console.log('aaaaaaa')
        const payments = [];
        let totalPaid = 0;

        const selectize = $('#valyuta_input')[0]?.selectize;
        
        if (!selectize) return;
        const selectedValue = selectize.getValue();
        const selectedOption = selectize.options[selectedValue];

        const isSom_main = selectedOption?.is_som === true || selectedOption?.is_som === "True";
        const isDollar_main = selectedOption?.is_dollar === true || selectedOption?.is_dollar === "True";

        

        $('.paymentinputs:not([data-kassa-id="qarz"])').each(function (index, item) {
            const input = $(item).find('.payment-input');
            const button = $(item).find('button');

            let value = parseFloat(input.val()?.replace(/\s/g, '')) || 0;
            let isDollar = button.data('dollar') === true;

            let converted = 0;

            if (isSom_main) {
                converted = isDollar ? value * currentKurs : value;
            } else {
                converted = isDollar ? value : value / currentKurs;
            }

            totalPaid += converted;

            const kassaId = $(item).find('.payment-method').data('kassa-id');
            const valyutaId = $(item).find('.payment-method').data('valyuta-id');
            const valyutaName = $(item).find('.payment-method').data('valyuta-name');

            payments.push({
                kassa_id: kassaId,
                valyuta_id: valyutaId,
                valyuta_name: valyutaName,
                summa: value,
                converted_summa: converted,
                type: 'payment',
                is_dollar: isDollar
            });
        });

        const qarzSumma = parseFloat(cleanNumber($('#qarzsumma').val())) || 0;

        if (qarzSumma > 0) {

            const qarzIsDollar = $('#qarzvalyuta option:selected').data('id_dollar');
            let convertedQarzAmount = qarzSumma;

            if (isSom_main) {
                convertedQarzAmount = qarzIsDollar ? qarzSumma * currentKurs : qarzSumma;
            } else if (isDollar_main) {
                convertedQarzAmount = qarzIsDollar ? qarzSumma : qarzSumma / currentKurs;
            }

            payments.push({
                type: 'qarz',
                valyuta_id: $('#qarzvalyuta').val(),
                summa: qarzSumma,
                converted_summa: convertedQarzAmount,
                due_date: $('#qarzdate').val(),
                comment: $('#qarzcomment').val(),
                is_dollar: qarzIsDollar
            });
        }
        
        return {
            payments: payments,
            total_paid: totalPaid
        };
    }

    // To'lovni tekshirish va yakunlash
    async function Yakunlash() {
        try {
            let qarz = $('#qarzsumma').val()
            let tabSelect = getActiveTabId()
            if ($('#cart-tbody').is(':empty')) {
                showAlert('Mahsulot qo\'shing!', 'danger')
                return
            }
            if(tabSelect === 'naqd' && parseFloat(cleanNumber(qarz)) > 0){
                showAlert('To\'lov summasini kiriting!', 'danger')
                return
            }
            const totalRequired = parseFloat();
            const paymentResult = collectPaymentData();
            const totalPaid = paymentResult.total_paid;


            const selectize = $('#valyuta_input')[0]?.selectize;
            if (!selectize) return;
            const selectedValue = selectize.getValue();
            const selectedOption = selectize.options[selectedValue];

            const isSom_main = selectedOption?.is_som === true || selectedOption?.is_som === "True";
            const isDollar_main = selectedOption?.is_dollar === true || selectedOption?.is_dollar === "True";

            let allowed_amount = 0
            if (isSom_main) {
                allowed_amount = 500
            }
            else if (isDollar_main) {
                allowed_amount = 0.05
            }

            // To'lov miqdorini tekshirish
            const difference = totalRequired - totalPaid;
            // if (totalPaid < totalRequired) {
            //     if (allowed_amount < difference) {
            //         showAlert(`To'lov yetarli emas! Yetishmayotgan summa: ${formatNumber(difference)} ${currentDatas.valyuta_name}`, 'danger');
            //         return;
            //     }
            // }

            // Agar ortiqcha to'langan bo'lsa, ogohlantirish
            if (totalPaid > totalRequired) {

                if (allowed_amount < difference) {
                    const confirmContinue = confirm(`To'lov keragidan ${formatNumber(difference)} ${currentDatas.valyuta_name} ko'p. Davom ettirilsinmi?`);
                    if (!confirmContinue) {
                        return;
                    }
                }
            }

            // To'lov ma'lumotlarini tayyorlash
            let paymentType = $('input[name="payment_type"]').val()
            const paymentData = {
                shop_id: currentShopId,
                payments: paymentResult.payments,
                total_required: totalRequired,
                total_paid: totalPaid,
                payment_type: paymentType,
                chegirma: parseFloat(cleanNumber($('#discountInput').val())) || 0
            };
            console.log(paymentData);
            


            // Yuklash indikatorini ko'rsatish
            const submitBtn = document.getElementById('submit-payment');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Amalga oshirilmoqda...';

            // Serverga yuborish
            const response = await fetch("{% url 'complete_payment' %}", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}'
                },
                body: JSON.stringify(paymentData)
            });

            const result = await response.json();

            if (result.success) {
                const isConfirmed = confirm("Print qilasizmi?");

                if (isConfirmed) {
                    // printCheckDiv()
                    // $('#paymentsTab').removeClass('active')
                    $('#checktabopen').trigger('click');

                    setTimeout(function () {
                        $('#printcheck').trigger('click');
                    }, 300);
                }

                showAlert('To\'lov muvaffaqiyatli yakunlandi!', 'success');

                // Modalni yopish
                // const paymentModal = bootstrap.Modal.getInstance(document.getElementById('fullscreenPayment'));
                // paymentModal.hide();

                // POS modalini ham yopish
                const posModal = bootstrap.Modal.getInstance(document.getElementById('posModal'));
                if (posModal) {
                    posModal.hide();
                }

                // Ma'lumotlarni tozalash
                $('.payment-input').val('');
                $('.input-box').hide();
                // document.getElementById('qarzBoxValyuta').value = '';
                document.getElementById('qarzBoxSumma').value = '';
                document.getElementById('qarzBoxDueDate').value = '';
                document.getElementById('qarzBoxComment').value = '';
                document.getElementById('check_tolovlar').innerHTML = '';

                $('#filter_submit').trigger('click')
                // Sahifani yangilash
                setTimeout(() => {
                    // window.location.reload();
                }, 1500);

            } else {
                showAlert(result.message || 'To\'lovda xatolik yuz berdi', 'danger');
            }
        } catch (error) {
            console.error('Yakunlashda xatolik:', error);
            showAlert('Server bilan bog\'lanishda xatolik', 'danger');
        } finally {
            // Tugmani qayta faollashtirish
            const submitBtn = document.getElementById('submit-payment');
            if (submitBtn) {
                submitBtn.disabled = false;
                submitBtn.innerHTML = 'Rasmiylashtirish';
            }
        }
    }

    // Real vaqtda to'lov miqdorini tekshirish va ko'rsatish
    function updatePaymentTotal() {
        const totalRequired = parseFloat(currentDatas.total_price);
        const paymentResult = collectPaymentData();
        let totalPaid = paymentResult.total_paid;


        // const remaining = totalRequired - totalPaid;
        const remaining = calculatePaymentTotal().replace(/\s+/g, '')
        $('#tolash_summasi').text(formatNumber(remaining > 0 ? remaining : 0));

        // To'lov holatini rang bilan ko'rsatish
        const tolashElement = $('#tolash_summasi');
        tolashElement.removeClass('text-success text-warning text-danger');

        if (remaining <= 0) {
            tolashElement.addClass('text-success');
        } else if (remaining <= totalRequired * 0.1) { // 10% dan kam qolgan
            tolashElement.addClass('text-warning');
        } else {
            tolashElement.addClass('text-danger');
        }

        // Submit tugmasini holatini yangilash
        const submitBtn = document.getElementById('submit-payment');
        if (submitBtn) {
            if (totalPaid >= totalRequired) {
                submitBtn.classList.remove('btn-primary');
                submitBtn.classList.add('btn-success');
            } else {
                submitBtn.classList.remove('btn-success');
                submitBtn.classList.add('btn-primary');
            }
        }

        // if (remaining > 0) {
        //     const isDollar = $('#qarzvalyuta option:selected').data('id_dollar');
        //     $('#qarzsumma').val(formatNumber(isDollar ? remaining / currentKurs : remaining));
        // } else {
        //     $('#qarzsumma').val(0)
        // }
        updateqarzsumma(remaining)
        return formatNumber(remaining > 0 ? remaining : 0);
    }

    function updateqarzsumma(summa) {
        const valyutaInput = $('#valyuta_input');
        const selectize = valyutaInput.length && valyutaInput[0].selectize ? valyutaInput[0].selectize : null;

        if (!selectize) {
            console.warn('Valyuta selectize not ready in updateqarzsumma');
            return;
        }

        const selectedValue = selectize.getValue();
        const selectedOption = selectize.options[selectedValue];
        const isSom_main = selectedOption?.is_som === true || selectedOption?.is_som === "True";
        const isDollar_main = selectedOption?.is_dollar === true || selectedOption?.is_dollar === "True";

        if (isSom_main) {
            if (summa > 0) {
                const isDollar = $('#qarzvalyuta option[value="' + $('#qarzvalyuta').val() + '"]').data('id_dollar');
                $('#qarzsumma').val(formatNumber(isDollar == 'True' ? summa / currentKurs : summa));
            } else {
                $('#qarzsumma').val(0)
            }
        } else {
            if (summa > 0) {
                const isDollar = $('#qarzvalyuta option[value="' + $('#qarzvalyuta').val() + '"]').data('id_dollar');
                $('#qarzsumma').val(formatNumber(isDollar == 'True' ? summa : summa * currentKurs));
            } else {
                $('#qarzsumma').val(0)
            }
        }
    }

    // DOM yuklanganda submit tugmasini sozlash
    document.addEventListener('DOMContentLoaded', function () {
        // Har bir input o'zgarganda to'lovni yangilash
        $(document).on('input', '.payment-input, #qarzsumma, #qarzvalyuta, #qarzdate, #qarzcomment', function () {
            updatePaymentTotal();
        });

        // Fullscreen payment modal ochilganda to'lovni yangilash
        $('#checktabopen').on('click', function () {
            updatePaymentTotal();
            loadExistingPaymentsForModal();
            updateCheckWithProducts();
        });

        // Modal yopilganda inputlarni tozalash
        $('#fullscreenPayment').on('hidden.bs.modal', function () {
            // Faqat qarz inputlarini tozalash, kassa inputlarini emas
            // document.getElementById('qarzBoxValyuta').value = '';
            document.getElementById('qarzBoxSumma').value = '';
            document.getElementById('qarzBoxDueDate').value = '';
            document.getElementById('qarzBoxComment').value = '';

            // Chekni tozalash
            document.getElementById('chek_products').innerHTML = '';
            document.getElementById('check_tolovlar').innerHTML = '';
            document.getElementById('chek_oraliq_jami').textContent = `0 ${currentDatas?.valyuta_name || ''}`;
            document.getElementById('chek_chegirma').textContent = `0 ${currentDatas?.valyuta_name || ''}`;
            document.getElementById('chek_total_jami').textContent = `0 ${currentDatas?.valyuta_name || ''}`;
        });
    });



    async function loadExistingPaymentsForModal() {
        console.log(currentShopId, 'yyyyyyyyyy')
        if (!currentShopId) return;
        try {
            const response = await fetch(`{% url 'get_shop_payments' %}?shop_id=${currentShopId}`);
            const data = await response.json();
            if (data.success && data.payments.length > 0) {

                const qarzSummaEl = document.getElementById('qarzsumma');
                if (qarzSummaEl) qarzSummaEl.value = 0;
                
                const qarzCommentEl = document.getElementById('qarzcomment');
                if (qarzCommentEl) qarzCommentEl.value = '';
                
                // document.getElementById('qarzdate').value = '';
                setqarzdate()
                // document.getElementById('qarzvalyuta').value = '';

                // Keyin paymentlarni ishlaymiz
                data.payments.forEach(payment => {
                    if (payment.type === 'payment') {
                        const paymentMethod = $(`.payment-method[data-kassa-id="${payment.kassa_id}"][data-valyuta-id="${payment.valyuta_id}"]`);
                        if (paymentMethod.length) {
                            const paymentInput = paymentMethod.siblings('.payment-input');
                            paymentInput.val(formatNumber(payment.summa));
                        }
                    } else if (payment.type === 'qarz') {
                        const qarzValyutaEl = document.getElementById('qarzvalyuta');
                        if (qarzValyutaEl) qarzValyutaEl.value = payment.valyuta_id;
                        
                        const qarzSummaEl = document.getElementById('qarzsumma');
                        if (qarzSummaEl) qarzSummaEl.value = formatNumber(payment.summa);
                        
                        const qarzDateEl = document.getElementById('qarzdate');
                        if (qarzDateEl) qarzDateEl.value = payment.due_date ? new Date(payment.due_date).toISOString().split('T')[0] : '';
                        
                        const qarzCommentEl = document.getElementById('qarzcomment');
                        if (qarzCommentEl) qarzCommentEl.value = payment.comment || '';
                    }
                });

                // So‘ngra check paymentni yangilaymiz
                updateCheckPayments();

            }
            else {
                
            }
        } catch (error) {
            console.error('To\'lovlarni yuklashda xatolik:', error);
        }
    }

    function updatecheckDatas() {
        $('#order_customer').text(currentDatas.customer_name)
        $('#order_date').text(currentDatas.date)
    }

    function updateCheckWithProducts() {
        if (!currentDatas || !cartItems.length) return;

        const chekProducts = document.getElementById('chek_products');
        const chekOraliqJami = document.getElementById('chek_oraliq_jami');
        const chekChegirma = document.getElementById('chek_chegirma');
        const chekTotalJami = document.getElementById('chek_total_jami');

        let totalWithoutDiscount = 0;
        let productsHtml = '';

        // Mahsulotlarni chekga joylash
        cartItems.forEach(item => {
            const itemTotal = item.quantity * item.price;
            totalWithoutDiscount += itemTotal;

            productsHtml += `
            <div class="item-title">${item.product_name}</div>
            <div class="subline">
                <span>${formatNumber(item.quantity)} x ${formatNumber(item.price)}</span>
                <span>${formatNumber(itemTotal)}</span>
            </div>
            <hr style="border: 1.5px solid #000;">
        `;
        });

        chegirma = parseFloat(cleanNumber($('#discountInput').val())) || 0;
        const totalWithDiscount = totalWithoutDiscount - chegirma;

        // Chek qiymatlarini yangilash
        chekProducts.innerHTML = productsHtml;
        chekOraliqJami.textContent = `${formatNumber(totalWithoutDiscount)} ${currentDatas.valyuta_name}`;
        chekChegirma.textContent = `${formatNumber(chegirma)} ${currentDatas.valyuta_name}`;
        chekTotalJami.textContent = `${formatNumber(totalWithDiscount)} ${currentDatas.valyuta_name}`;

        // Jami summani yangilash
        $('#total_jami').text(`${formatNumber(currentDatas.total_price)}`);
    }



    // function updateCheckPayments() {
    //     const checkTolovlar = document.getElementById('check_tolovlar');
    //     const paymentResult = collectPaymentData();

    //     // console.log(paymentResult,'uuuuuu')
    //     let paymentsHtml = '';
    //     let qarzValyutaName = $('#qarzvalyuta option[value="' + $('#qarzvalyuta').val() + '"]').data('name') || '';

    //     // Kassalar bo'yicha to'lovlar
    //     paymentResult.payments.forEach(payment => {
    //         if (payment.type === 'payment') {
    //             const paymentMethod = $(`.payment-method[data-kassa-id="${payment.kassa_id}"][data-valyuta-id="${payment.valyuta_id}"]`);
    //             if (paymentMethod.length) {
    //                 const kassaName = paymentMethod.find('p').text().split(' (')[0];
    //                 const valyutaName = (paymentMethod.find('p').text().match(/\(([^)]+)\)/) || [])[1] || '';                
    //                 paymentsHtml += `
    //                     <div class="lines">
    //                         <span>${valyutaName}</span>
    //                         <span>${formatNumber(payment.summa)}</span>
    //                     </div>
    //                 `;
    //             }
    //         } else if (payment.type === 'qarz') {
    //             paymentsHtml += `
    //                 <div class="lines">
    //                     <span class="bold">Qarz</span>
    //                     <span>${formatNumber(payment.summa)} ${qarzValyutaName}</span>
    //                 </div>
    //             `;
    //         }
    //     });

    //     checkTolovlar.innerHTML = paymentsHtml;
    // }


    function updateCheckPayments() {
        const checkTolovlar = document.getElementById('check_tolovlar');
        const paymentResult = collectPaymentData();

        let paymentsHtml = '';

        // Kassalar bo'yicha to'lovlar
        paymentResult.payments.forEach(payment => {
            if (payment.type === 'payment') {
                // To'g'ridan-to'g'ri payment obyektidan valyuta nomini olish
                const valyutaName = payment.valyuta_name || '';
                paymentsHtml += `
                <div class="lines">
                    <span>${valyutaName}</span>
                    <span>${formatNumber(payment.summa)}</span>
                </div>
            `;
            } else if (payment.type === 'qarz') {
                // jQuery bilan qarz valyutasini olish
                const qarzValyutaName = $('#qarzvalyuta option:selected').text();

                paymentsHtml += `
                <div class="lines">
                    <span class="bold">Qarz</span>
                    <span>${formatNumber(payment.summa)} ${qarzValyutaName}</span>
                </div>
            `;
            }
        });

        checkTolovlar.innerHTML = paymentsHtml;
    }






    // To'lov jamiini yangilash (qarzni hisobga olgan holda)
    function calculatePaymentTotal() {
        $('#total_jami').text(formatNumber(currentDatas.total_price));
        let total = 0;


        const valyutaInput = $('#valyuta_input');
        const selectize = valyutaInput.length && valyutaInput[0].selectize ? valyutaInput[0].selectize : null;

        // Agar selectize hali yuklanmagan bo'lsa, default qiymatlarni ishlatish
        const selectedValue = selectize ? selectize.getValue() : valyutaInput.val();
        const selectedOption = selectize ? selectize.options[selectedValue] : null;

        const isSom_main = selectedOption ? (selectedOption.is_som === true || selectedOption.is_som === "True") : true;
        const isDollar_main = selectedOption ? (selectedOption.is_dollar === true || selectedOption.is_dollar === "True") : false;


        $('.paymentinputs:not([data-kassa-id="qarz"])').each(function () {
            const input = $(this).find('.payment-input');
            const button = $(this).find('button');

            let value = parseFloat(
                input.val()?.replace(/\s/g, '')
            ) || 0;

            let isDollar = button.data('dollar') === true;

            if (isSom_main) {
                total += isDollar ? value * currentKurs : value;
            } else {
                total += isDollar ? value : value / currentKurs;
            }
        });
        console.log(currentDatas)
        console.log(currentDatas.total_price, total, 'uuu')
        const remaining = parseFloat(currentDatas.total_price) - parseFloat(total);
        // $('#tolash_summasi').text(formatNumber(remaining > 0 ? remaining : 0));
        // $('#qarzsumma').val(formatNumber(remaining > 0 ? remaining : 0));
        return formatNumber(parseFloat(currentDatas.total_price) - parseFloat(total));
    }

    // Qarz input boxini yopish
    function hideQarzInputBox() {
        const qarzInputBox = document.getElementById('qarzInputBox');
        qarzInputBox.style.display = 'none';

        // Agar qarz ma'lumotlari to'liq kiritilmagan bo'lsa, chekni tozalash
        const qarzValyutaId = document.getElementById('qarzBoxValyuta').value;
        const qarzSumma = parseFloat(cleanNumber(document.getElementById('qarzBoxSumma').value)) || 0;

        if (!qarzValyutaId || qarzSumma <= 0) {
            document.getElementById('check_tolovlar').innerHTML = '';
        }

        updatePaymentTotal();
    }

    // Modal yopilganda inputlarni tozalash
    $('#fullscreenPayment').on('hidden.bs.modal', function () {
        // Qarz inputlarini tozalash
        // document.getElementById('qarzBoxValyuta').value = '';
        document.getElementById('qarzBoxSumma').value = '';
        document.getElementById('qarzBoxDueDate').value = '';
        document.getElementById('qarzBoxComment').value = '';
        document.getElementById('check_tolovlar').innerHTML = '';
    });
</script>



<script>


    $(document).ready(function () {
        let lastSubmitTime = 0;
        const SUBMIT_DELAY = 1000; // 1 soniya

        // Event listener'larni kuzatish
        let eventCount = {
            priceTypeForm: 0,
            debtorForm: 0
        };

        function handleFormSubmit(formId, url, selectId, modalId) {
            // Avvalgi event listener'larni olib tashlash
            $(formId).off('submit');

            $(formId).submit(function (e) {
                e.preventDefault();

                const currentTime = Date.now();
                const formKey = formId.replace('#', '');
                eventCount[formKey]++;


                // Agar oxirgi so'rovdan 1 soniya o'tmagan bo'lsa
                if (currentTime - lastSubmitTime < SUBMIT_DELAY) {
                    return false;
                }

                lastSubmitTime = currentTime;

                // Tugmani disable qilish
                const submitBtn = $(this).find('button[type="submit"]');
                const originalText = submitBtn.text();
                submitBtn.prop('disabled', true).text('Yuklanmoqda...');

                const formDatas = $(this).serialize();


                $.ajax({
                    url: url,
                    type: 'POST',
                    data: formDatas + '&csrfmiddlewaretoken={{ csrf_token }}',
                    success: function (data) {

                        if ($(selectId)[0]?.selectize) {
                            let selectize = $(selectId)[0]?.selectize;
                            selectize.addOption({ value: data.id, text: data.name });
                            selectize.addItem(data.id, true);
                            $(selectId).append(`<option value="${data.id}" selected>${data.name}</option>`);
                        } else {
                            $(selectId).append(`<option value="${data.id}" selected>${data.name}</option>`);
                        }

                        $(selectId).trigger("change");

                        if (modalId === "#debtorModal" && document.querySelector("#debtor_add_close")) {
                            document.querySelector("#debtor_add_close").click();
                        }else if(modalId === "#deliverModal" && document.querySelector("#deliver_add_close")){
                            document.querySelector("#deliver_add_close").click();
                            $(modalId).modal('hide');
                        }else{
                            $(modalId).modal('hide');
                        }

                        $(formId)[0].reset();
                        if (url === '{% url "create_debtor" %}') {
                            $('#mainSelectDebtor').append(`<option value="${data.id}" selected>${data.name}</option>`);
                        }else if(url === '{% url "create_deliver_new" %}'){
                            $('#mainSelectDeliver').append(`<option value="${data.id}" selected>${data.name}</option>`);
                        }
                    },
                    error: function (xhr, status, error) {
                        console.log('AJAX xatosi:', error);
                        alert("Xatolik yuz berdi!");
                    },
                    complete: function () {
                        // Tugmani qayta faollashtirish
                        submitBtn.prop('disabled', false).text(originalText);
                    }
                });
            });
        }

        handleFormSubmit('#priceTypeForm', '{% url "create_price_type" %}', '#recipient-price_type', '#priceTypeModal');
        handleFormSubmit('#debtorForm', '{% url "create_debtor" %}', '#mainSelectDebtor', '#debtorModal');
        handleFormSubmit('#deliverForm', '{% url "create_deliver_new" %}', '#mainSelectDeliver', '#deliverModal');
    });
</script>


<script>
    // Debtor modal muammosini hal qilish
    document.addEventListener('DOMContentLoaded', function () {
        const debtorModal = document.getElementById('debtorModal');

        if (debtorModal) {
            // 1. Modal ochilganda - barcha focus event'larini to'xtatish
            debtorModal.addEventListener('show.bs.modal', function () {
                // Focus event'ini butun modal uchun to'xtatish
                debtorModal.addEventListener('focusin', function (e) {
                    e.stopPropagation();
                    e.stopImmediatePropagation();
                }, true); // capture phase - eng avval ishlashi uchun
            });

            // 2. Modal yopilganda - event listener'larni tozalash
            debtorModal.addEventListener('hidden.bs.modal', function () {
                // Simple debounce - modal yopilganda biroz kutish
                setTimeout(() => {
                    const activeElement = document.activeElement;
                    if (activeElement && activeElement.tagName === 'INPUT') {
                        activeElement.blur();
                    }
                }, 50);
            });

            // 3. Modal ichidagi input'larda focus bo'lganda
            const debtorInputs = debtorModal.querySelectorAll('input, select, textarea');
            debtorInputs.forEach(input => {
                input.addEventListener('focus', function (e) {
                    e.stopPropagation();
                });
            });

            // 4. Form submit handler - event bubbling to'xtatish
            const debtorForm = document.getElementById('debtorForm');
            if (debtorForm) {
                debtorForm.addEventListener('submit', function (e) {
                    e.preventDefault();
                    e.stopPropagation();

                    const formData = new FormData(this);
                    fetch('{% url "create_debtor" %}', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': '{{ csrf_token }}'
                        }
                    })
                        .then(response => response.json())
                        .then(data => {
                            if (data.id) {
                                // Selectize yoki oddiy select uchun
                                const mainSelect = document.getElementById('mainSelectDebtor');
                                if (mainSelect?.selectize) {
                                    mainSelect.selectize?.addOption({ value: data.id, text: data.name });
                                    mainSelect.selectize?.setValue(data.id);
                                } else {
                                    mainSelect.innerHTML += `<option value="${data.id}" selected>${data.name}</option>`;
                                }

                                // Modalni yopish
                                bootstrap.Modal.getInstance(debtorModal).hide();
                                this.reset();
                            }
                        })
                        .catch(error => {
                            console.error('Xatolik:', error);
                            alert('Xatolik yuz berdi!');
                        });
                });
            }
        }
    });

    // Debtor modalini ochish funksiyasi
    function openDebtorModal() {
        const modal = new bootstrap.Modal(document.getElementById('debtorModal'));
        modal.show();

        // Focus muammosini oldini olish uchun biroz kutish
        setTimeout(() => {
            const firstInput = document.querySelector('#debtorModal input');
            if (firstInput) {
                firstInput.focus({ preventScroll: true });
            }
        }, 200);
    }

    function openDeliverModal() {
        const modal = new bootstrap.Modal(document.getElementById('deliverModal'));
        modal.show();

        // Focus muammosini oldini olish uchun biroz kutish
        setTimeout(() => {
            const firstInput = document.querySelector('#deliverModal input');
            if (firstInput) {
                firstInput.focus({ preventScroll: true });
            }
        }, 200);
    }
</script>



<script>
    document.getElementById('productSearchInput').addEventListener('keyup', function () {
        const searchValue = this.value.toLowerCase().trim();
        const productRows = document.querySelectorAll('#productTable .product-row');

        productRows.forEach(row => {
            // data-search atributidan nom va shtrix kodlarni olamiz
            const searchData = row.getAttribute('data-search').toLowerCase();

            // Agar qidiruv bo'sh bo'lsa yoki ma'lumot mavjud bo'lsa ko'rsatamiz
            if (searchValue === '' || searchData.includes(searchValue)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });

</script>


<script>
    document.getElementById('main_input').addEventListener('keypress', function (e) {
        if (e.key !== 'Enter') return;
        e.preventDefault();

        const barcode = this.value.trim();
        if (!barcode) {
            alert("Iltimos, shtrix kodni kiriting!");
            return;
        }

        const rows = document.querySelectorAll('.product-row');
        let found = false;

        rows.forEach(row => {
            const barcodes = row.getAttribute('data-value').split('&')[3];
            if (barcodes.split(',').includes(barcode)) {
                found = true;
                $(row).trigger('dblclick');
                // row.dispatchEvent(new MouseEvent('dblclick', { bubbles: true }));
            }
        });

        if (!found) showAlert(`Shtrix kod: "${barcode}" bo'yicha mahsulot topilmadi!`, 'danger');
        this.value = '';
        this.focus();
    });

</script>


<script>


    function handleKeyboardShortcuts(e) {
        const mainInput = document.getElementById('main_input');
        const activeElement = document.activeElement;

        // Agar boshqa input yoki textarea'da fokus bo'lsa, shortcut'lar ishlamasin
        if ((activeElement.tagName === 'INPUT' && activeElement !== mainInput) ||
            activeElement.tagName === 'TEXTAREA') {
            return;
        }

        const key = e.key.toUpperCase();
        const isShiftPressed = e.shiftKey;

        // + tugmasi - miqdorni oshirish
        if (key === '+' || key === '=') {
            e.preventDefault();
            e.stopPropagation();
            modifySelectedOrLastItem('quantity', 'increase');
            return;
        }

        // - tugmasi - miqdorni kamaytirish
        else if (key === '-' || key === '_') {
            e.preventDefault();
            e.stopPropagation();
            modifySelectedOrLastItem('quantity', 'decrease');
            return;
        }

        // * tugmasi - narxni o'zgartirish
        else if (key === '*') {
            e.preventDefault();
            e.stopPropagation();
            modifySelectedOrLastItem('price_without_skidka', 'modify');
            return;
        }

        // / tugmasi - paket sonini o'zgartirish
        else if (key === '/') {
            e.preventDefault();
            e.stopPropagation();
            modifySelectedOrLastItem('pack', 'modify');
            return;
        }

        // F5 - foiz chegirma
        else if (key === 'F5') {
            e.preventDefault();
            e.stopPropagation();
            applyPercentageDiscount();
            return;
        }

        // F6 - jami summa chegirma
        else if (key === 'F6') {
            e.preventDefault();
            e.stopPropagation();
            applyFixedDiscount();
            return;
        }

        // Enter - shtrix kod bo'yicha qidirish (faqat boshqa elementda fokus bo'lsa)
        else if (key === 'ENTER') {
            // Agar main_input'da fokus yo'q bo'lsa, fokusni o'tkazamiz
            if (activeElement !== mainInput) {
                e.preventDefault();
                e.stopPropagation();
                mainInput.focus();
                mainInput.select();
                return;
            }
            // Agar main_input'da bo'lsa, odatdagi Enter ishlashi uchun chiqamiz
        }
    }

    // Tanlangan yoki oxirgi elementni o'zgartirish
    function modifySelectedOrLastItem(field, action) {
        // 1. Avval tanlangan elementlarni tekshiramiz
        const selectedRows = document.querySelectorAll('#cart-tbody .cart-item-row.selected');

        let itemsToModify = [];

        if (selectedRows.length > 0) {
            // Tanlangan elementlar bor
            selectedRows.forEach(row => {
                const cartId = getCartIdFromRow(row);
                const item = cartItems.find(item => item.id === cartId);
                if (item) itemsToModify.push(item);
            });
        } else if (cartItems.length > 0) {
            // Tanlangan element yo'q, oxirgi elementni olamiz
            const lastItem = cartItems[cartItems.length - 1];
            itemsToModify.push(lastItem);
        } else {
            showAlert('Oʻzgartirish uchun mahsulot yoʻq', 'warning');
            return;
        }

        // 2. main_input qiymatini olish
        const mainInput = document.getElementById('main_input');
        const inputValue = parseFloat(cleanNumber(mainInput.value)) || 0;

        // 3. Har bir elementni o'zgartirish
        itemsToModify.forEach(item => {
            const row = document.querySelector(`.cart-item-row[data-cart-id="${item.id}"]`);
            if (!row) return;

            let newValue;

            switch (field) {
                case 'quantity':
                    if (action === 'increase') {
                        newValue = item.quantity + (inputValue > 0 ? inputValue : 1);
                    } else if (action === 'decrease') {
                        newValue = item.quantity - (inputValue > 0 ? inputValue : 1);
                        if (newValue < 0) newValue = 0;
                    }
                    break;

                case 'price_without_skidka':
                    if (inputValue > 0) {
                        newValue = inputValue;
                    } else {
                        // Agar input bo'sh bo'lsa, hozirgi narxni ko'rsatish
                        const currentPrice = parseFloat(cleanNumber(row.querySelector('.price_text').textContent)) || 0;
                        showAlert(`Joriy narx: ${formatNumber(currentPrice)}`, 'info');
                        return;
                    }
                    break;

                case 'pack':
                    if (inputValue > 0) {
                        // Paket o'lchamiga asoslanib miqdorni hisoblash
                        const packSize = item.pack_size || 1;
                        newValue = inputValue;
                        const newQuantity = newValue * packSize;

                        // Miqdorni ham yangilash
                        updateCartItem(item.id, 'quantity', newQuantity.toString());
                    }
                    break;
            }

            if (newValue !== undefined) {
                // UI ni yangilash
                const inputSelector = field === 'quantity' ? '.quantity-input' :
                    field === 'price_without_skidka' ? '.price_text' :
                        '.pack-input';
                const inputElement = row.querySelector(inputSelector);
                if (inputElement) {
                    inputElement.value = formatNumber(newValue);
                    $(inputElement).trigger('change');
                    // inputElement.dispatchEvent(new Event('change'));
                    if (inputSelector == '.price_text') {
                        $('.price-input').val(formatNumber(newValue));
                        $('.price-input').trigger('change');
                    }
                }

                // Backend ga yangilash
                updateCartItem(item.id, field, newValue.toString());
            }
        });

        // 4. Inputni tozalash
        mainInput.value = '';
    }

    // Foiz chegirma qo'llash (F5)
    function applyPercentageDiscount() {
        const mainInput = document.getElementById('main_input');
        const discountPercent = parseFloat(cleanNumber(mainInput.value)) || 0;

        if (discountPercent < 0 || discountPercent > 100) {
            showAlert('Iltimos, 0-100 orasida foiz kiriting', 'warning');
            return;
        }

        // 1. Avval tanlangan elementlarni tekshiramiz
        const selectedRows = document.querySelectorAll('#cart-tbody .cart-item-row.selected');
        let itemsToModify = [];

        if (selectedRows.length > 0) {
            // Tanlangan elementlarga chegirma
            selectedRows.forEach(row => {
                const cartId = getCartIdFromRow(row);
                const item = cartItems.find(item => item.id === cartId);
                if (item) itemsToModify.push(item);
            });
        } else {
            // Barcha elementlarga chegirma
            itemsToModify = [...cartItems];
        }

        if (itemsToModify.length === 0) {
            showAlert('Chegirma qoʻllash uchun mahsulot yoʻq', 'warning');
            return;
        }

        // Har bir elementga chegirma qo'llash
        itemsToModify.forEach(item => {
            const row = document.querySelector(`.cart-item-row[data-cart-id="${item.id}"]`);
            if (!row) return;

            // Eski narxni saqlash
            const oldPrice = item.price_without_skidka;
            const newPrice = oldPrice * (1 - discountPercent / 100);

            // Chegirma foizini hisoblash
            const newDiscount = discountPercent;

            // UI ni yangilash
            const priceInput = row.querySelector('.price-input');
            const discountInput = row.querySelector('.discount-input');

            // if (priceInput) {
            //     priceInput.value = formatNumber(newPrice);
            // }

            if (discountInput) {
                discountInput.value = formatNumber(newDiscount);
                $(discountInput).trigger('change')
            }

        });

        // Inputni tozalash va xabar
        mainInput.value = '';
        showAlert(`${itemsToModify.length} ta mahsulotga ${discountPercent}% chegirma qoʻllandi`, 'success');
    }

    // Jami summa chegirma (F6)
    function applyFixedDiscount() {
        const mainInput = document.getElementById('main_input');
        const discountAmount = parseFloat(cleanNumber(mainInput.value)) || 0;

        if (discountAmount <= 0) {
            showAlert('Iltimos, chegirma miqdorini kiriting', 'warning');
            return;
        }

        // Jami summani hisoblash
        let totalSum = 0;
        let itemsToModify = [];

        // 1. Avval tanlangan elementlarni tekshiramiz
        const selectedRows = document.querySelectorAll('#cart-tbody .cart-item-row.selected');

        if (selectedRows.length > 0) {
            // Tanlangan elementlar uchun jami summa
            selectedRows.forEach(row => {
                const cartId = getCartIdFromRow(row);
                const item = cartItems.find(item => item.id === cartId);
                if (item) {
                    itemsToModify.push(item);
                    totalSum += (item.quantity * item.price_without_skidka);
                }
            });
        } else {
            // Barcha elementlar uchun jami summa
            itemsToModify = [...cartItems];
            totalSum = itemsToModify.reduce((sum, item) => sum + (item.quantity * item.price_without_skidka), 0);
        }


        if (itemsToModify.length === 0) {
            showAlert('Chegirma qoʻllash uchun mahsulot yoʻq', 'warning');
            return;
        }

        if (discountAmount > totalSum) {
            showAlert(`Chegirma jami summadan (${formatNumber(totalSum)}) katta boʻlishi mumkin emas`, 'warning');
            return;
        }

        // Har bir elementga chegirma qo'llash (proportional ravishda)
        itemsToModify.forEach(item => {
            const row = document.querySelector(`.cart-item-row[data-cart-id="${item.id}"]`);
            if (!row) return;

            // Elementning jami summadagi ulushini hisoblash
            const itemShare = (item.quantity * item.price_without_skidka) / totalSum;
            const itemDiscountAmount = discountAmount * itemShare;

            // Yangi narxni hisoblash (bir dona uchun)
            const discountPerUnit = itemDiscountAmount / item.quantity;
            const newPrice = Math.max(0, item.price_without_skidka - discountPerUnit);

            // Chegirma foizini hisoblash
            const newDiscount = 100 - (100 / item.price_without_skidka * newPrice);

            // UI ni yangilash
            const priceInput = row.querySelector('.price-input');
            const discountInput = row.querySelector('.discount-input');

            if (priceInput) {
                priceInput.value = formatNumber(newPrice);
                $(priceInput).trigger('change')
            }

        });

        // Inputni tozalash va xabar
        mainInput.value = '';
        showAlert(`${itemsToModify.length} ta mahsulotga jami ${formatNumber(discountAmount)} chegirma qoʻllandi`, 'success');
    }

    // Shtrix kod bo'yicha qidirish
    // function searchByBarcode() {
    //     const mainInput = document.getElementById('main_input');
    //     const barcode = mainInput.value.trim();

    //     if (!barcode) return;

    //     // Mahsulotlar jadvalidan qidirish
    //     const productRows = document.querySelectorAll('#productTable .product-row');
    //     let foundProduct = null;

    //     for (const row of productRows) {
    //         const barcodes = row.getAttribute('data-value').split('&')[3];
    //         if (barcodes.split(',').includes(barcode)) {
    //             foundProduct = row;
    //             break;
    //         }
    //     }

    //     if (foundProduct) {
    //         // Mahsulotni tanlash (highlight qilish)
    //         productRows.forEach(row => row.style.backgroundColor = '');
    //         foundProduct.style.backgroundColor = '#e3f2fd';

    //         // Avtomatik ravishda cartga qo'shish
    //         const productId = foundProduct.getAttribute('data-value').split('&')[0];
    //         addCart(productId);

    //         // Inputni tozalash
    //         mainInput.value = '';
    //         showAlert('Mahsulot savatga qoʻshildi', 'success');
    //     } else {
    //         showAlert(`"${barcode}" shtrix kodli mahsulot topilmadi`, 'warning');
    //     }
    // }


    function searchByBarcode() {
        const mainInput = document.getElementById('main_input');
        const barcode = mainInput.value.trim();

        if (!barcode) return;

        // Mahsulotlar jadvalidan qidirish
        const productRows = document.querySelectorAll('#productTable .product-row');
        let foundProduct = null;
        let foundQuantity = 1.0; // default quantity

        for (const row of productRows) {
            const barcodes = row.getAttribute('data-value').split('&')[3];
            const barcodePairs = barcodes.split(',');

            for (const pair of barcodePairs) {
                if (pair) { // Bo'sh string bo'lmasligi uchun tekshirish
                    const [bc, qty] = pair.split('x');
                    if (bc === barcode) {
                        foundProduct = row;
                        foundQuantity = parseFloat(qty) || 1.0;
                        break;
                    }
                }
            }

            if (foundProduct) break;
        }

        if (foundProduct) {
            // Mahsulotni tanlash (highlight qilish)
            productRows.forEach(row => row.style.backgroundColor = '');
            foundProduct.style.backgroundColor = '#e3f2fd';

            // Avtomatik ravishda cartga qo'shish
            const productId = foundProduct.getAttribute('data-value').split('&')[0];

            // Quantity bilan addCart ga yuborish
            addCart(productId, foundQuantity);

            // Inputni tozalash
            mainInput.value = '';
            // showAlert(`"${barcode}" mahsulot savatga qoʻshildi (Miqdor: ${foundQuantity})`, 'success');
        } else {
            showAlert(`"${barcode}" shtrix kodli mahsulot topilmadi`, 'warning');
        }
    }

    // Enter bosilganda shtrix kod qidiruvi
    function handleMainInputEnter(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            searchByBarcode();
        }
    }

    // DOM yuklanganda event listener'larni qo'shish
    document.addEventListener('DOMContentLoaded', function () {
        // Klaviatura shortcut'lari
        document.addEventListener('keydown', handleKeyboardShortcuts);

        // main_input uchun Enter handler
        const mainInput = document.getElementById('main_input');
        if (mainInput) {
            mainInput.addEventListener('keydown', handleMainInputEnter);

            // Fokus olganda matnni tanlash
            mainInput.addEventListener('focus', function () {
                this.select();
            });
        }

        // POS modal ochilganda ham event listener'larni qo'shish
        $('#posModal').on('shown.bs.modal', function () {
            document.addEventListener('keydown', handleKeyboardShortcuts);
        });

        // POS modal yopilganda event listener'larni olib tashlash
        $('#posModal').on('hidden.bs.modal', function () {
            document.removeEventListener('keydown', handleKeyboardShortcuts);
        });
    });



    // Row dan cart ID olish
    function getCartIdFromRow(row) {
        if (!row) return null;
        return parseInt(row.getAttribute('data-cart-id')) ||
            parseInt(row.getAttribute('data-id')) ||
            row.dataset.cartId ||
            row.dataset.id;
    }

    // Xabarlarni ko'rsatish
    function showAlert(message, type) {
        const alertElement = document.createElement('div');
        alertElement.className = `alert alert-${type} alert-dismissible fade show`;
        alertElement.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

        document.getElementById('alert-container').appendChild(alertElement);

        setTimeout(() => {
            alertElement.remove();
        }, 3000);
    }
</script>


<script>
    const helpBtn = document.querySelector('.pos-help-btn');
    const helpBox = document.getElementById('helpBox');

    helpBtn.addEventListener('click', function (e) {
        e.stopPropagation(); // tashqariga click ketmasin
        helpBox.style.display = helpBox.style.display === 'block'
            ? 'none'
            : 'block';
    });

    // Help oynasi ichiga bosilganda yopilmasin
    helpBox.addEventListener('click', function (e) {
        e.stopPropagation();
    });

    // Sahifaning boshqa joyiga bosilganda yopilsin
    document.addEventListener('click', function () {
        helpBox.style.display = 'none';
    });
</script>

<script src="https://cdnjs.cloudflare.com/ajax/libs/jQuery.print/1.6.2/jQuery.print.min.js"></script>


<script>
    function printCheckDiv() {
        //   const checkDiv = document.getElementById('check_div');

        //   if (!checkDiv) {
        //     alert("'check_div' topilmadi");
        //     return;
        //   }

        //   // Print jarayoni tugagach ishlaydigan hook (ixtiyoriy)
        //   window.onafterprint = () => {
        //     // Masalan: console.log('Print tugadi');
        //   };

        //   window.print();

        $('#check_div').print();


    }
</script>

<script>
    $('#all_cash').on('click', function () {
        // qarz bo‘lmagan inputlarni tozalash
        $('.payment-input[data-qarz="false"]').each(function () {
            $(this).val('');
        });

        // asosiy valyuta tugmasini bosish
        $(`.paymentinputs[data-valyuta-id="{{ brand.main_valyuta.id }}"] .btn`).trigger('click');
    });
</script>

<!-- <script>
    function openSaleTypeComponent(url) {
        $.ajax({
            url: url,
            method: 'get',
            success: function (res) {
                $('#myTabContent').html(res)
            }
        })
    }

    openSaleTypeComponent(url = '/today_sales_naqt/')
</script> -->

