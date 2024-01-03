class ListComponent {
    
    constructor(component, renderType, url, navBar=true) {

        var component = component;
        var self = this;

        let page = null;
        let page_size = null;
        let otherParams = null;
        const searchInput = document.getElementById('search-input-' + component);
        const orderFilterInput = document.getElementById('order-filter-' + component);
        const items = document.getElementById('items-' + component);
        const loader = document.getElementById('loader-' + component);
        const noResults = document.getElementById('no-results-' + component);
        const errorMessage = document.getElementById('error-message-' + component);
        const loadMoreButton = document.getElementById('load-more-button-' + component);
        const resultsCountHolder = document.getElementById('results-count-holder-' + component);
        const resultsCount = document.getElementById('results-count-' + component);
        let typingTimeout;
        let pendingRequest = false;
        let initialRequest = true;

        if (navBar) {
            searchInput.addEventListener('input', function () {
                clearTimeout(typingTimeout);
    
                typingTimeout = setTimeout(function () {
                    // call function for search after 1 second of inactivity
                    if (searchInput.value == '' && !pendingRequest) {
                        // call function for search when input is cleared
                        reloadResults();
                    }
                }, 500);
            });
    
            searchInput.addEventListener('keypress', function (event) {
                if (event.key === 'Enter') {
                    // call function for search when enter key is pressed
                    reloadResults();
                }
            });
    
            orderFilterInput.addEventListener("change", (event) => {
                const selectedValue = event.target.value;
                reloadResults();
            });
        }

        loadMoreButton.addEventListener("click", (event) => {
            loadMore();
        });

        function getItems() {

            if (initialRequest) {
                items.innerHTML = '';
            }
            let searchTerm;
            let orderFilter;
            if (navBar) {
                searchTerm = searchInput.value;
                orderFilter = orderFilterInput.value;
            }
            fetchData(searchTerm, orderFilter);

        }

        this.initialLoad = function () {
            items.innerHTML = '';
            let searchTerm;
            let orderFilter;
            if (navBar) {
                searchTerm = searchInput.value;
                orderFilter = orderFilterInput.value;
            }
            fetchData(searchTerm, orderFilter);
        };

        this.setPage = function (page_value) {
            page = page_value;
        };

        this.setPageSize = function (page_size_value) {
            page_size = page_size_value;
        };

        this.setOtherParams = function (otherParams_obj) {
            console.log('SET OTHER PARAMS')
            console.log(otherParams_obj)
            otherParams = otherParams_obj;
        };

        function fetchData(searchTerm, orderFilter) {
            
            pendingRequest = true;
            loader.classList.remove('d-none');
            errorMessage.classList.add('d-none');
            noResults.classList.add('d-none');
            loadMoreButton.classList.add('d-none');
            if (initialRequest) {
                items.classList.add('d-none');
            }

            if (page == null) {
                page = 1;
            }
            if (page_size == null) {
                page_size = 25;
            }

            let queryParams = '';

            if (searchTerm) {
                searchTerm = searchTerm.trim()
                queryParams += `search_term=${searchTerm}&`;
            }
            if (orderFilter && orderFilter != '') {
                queryParams += `order=${orderFilter}&`;
            }

            queryParams += `page=${page}&`;
            queryParams += `page_size=${page_size}&`;
            queryParams += `render_type=${renderType}&`;

            if (otherParams) {
                console.log('Other Params')
                for (let key in otherParams) {
                    console.log(key)
                    queryParams += `${key}=${otherParams[key]}&`;
                 }
            }

            // remove the trailing "&" from the queryParams
            queryParams = queryParams.slice(0, -1);

            console.log('Query Params')
            console.log(queryParams)

            let request_url = url

            if (url.includes('?')) {
                request_url += '&' + queryParams;
            } else {
                request_url += '?' + queryParams;
            }
            
            fetch(request_url, {
                method: "GET",
                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": getCookie('csrftoken'),
                },
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                const results = data['results'];
                const loadMore = data['load_more'];
                initialRequest = false;
                if (results) {
                    const html = data['items'];
                    renderHtml(html, loadMore);
                } else {
                    displayNoResults();
                }
                resultsCountHolder.classList.remove('invisible')
                resultsCount.innerHTML = data['total_count']
            })
            .catch(error => {
                console.error('There was a problem with the fetch operation:', error);
                displayErrorMessage();
            });
        
        }

        function renderHtml(html, loadMore) {
            for (const item of html) {
                items.insertAdjacentHTML('beforeend', item);
            }
            displayList(loadMore);
        }

        function displayList(loadMore) {
            pendingRequest = false;
            loader.classList.add('d-none');
            items.classList.remove('d-none');
            if (loadMore) {
                loadMoreButton.classList.remove('d-none');
            }
        }

        function displayNoResults() {
            pendingRequest = false;
            loader.classList.add('d-none');
            noResults.classList.remove('d-none');
        }

        function displayErrorMessage() {
            pendingRequest = false;
            loader.classList.add('d-none');
            errorMessage.classList.remove('d-none');
        }

        function reloadResults() {
            if (!pendingRequest) {
                initialRequest = true;
                page = 1;
                getItems();
            }
        }

        function loadMore() {
            page = page + 1;
            getItems();
        }

    }

}