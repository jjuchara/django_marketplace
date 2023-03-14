document.addEventListener("DOMContentLoaded", function () {
    const item_cards = document.querySelectorAll('.compare')
    const compare_amount = document.getElementById('compare-amount')
    let messages_ul = document.querySelector('.messages')
    const compare_rows = [...document.querySelectorAll('.Compare-row')].slice(2)

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    const csrftoken = getCookie('csrftoken');


    async function addToCompareList(e) {
        e.preventDefault()
        const slug = e.target.closest('.compare').getAttribute('data-slug')
        const url = '/add_to_compare/'
        const body = JSON.stringify({
            'item_slug': slug
        })

        let data = await makeRequest(url, 'post', body)
        changeCompareAmount(data['compare_item_quantity'])
        addMessage(data['messages'][0])

        setTimeout(() => {
            let message_ul = document.querySelector('.messages')
            hideMessage(message_ul)
        }, 1000)
    }

    async function makeRequest(url, method, body) {
        let headers = {
            'X-Requested-With': 'XMLHttpRequest', 'Content-Type': 'application/json',
        }

        if (method == 'post') {
            headers['X-CSRFToken'] = csrftoken
        }

        let response = await fetch(url, {
            method: method, headers: headers, body: body,
        })
        return await response.json()
    }

    const changeCompareAmount = (amount) => compare_amount.innerText = amount

    const addMessage = (message) => {
        let message_div = messages_ul.children[0].children[0]
        message_div.classList.add(`alert-${message['tags']}`)
        message_div.innerHTML = message['message_text']
        messages_ul.style.display = 'block'
    }

    const hideMessage = (message_ul) => {
        // TODO: сделать плавную анимацию скрытия сообщения
        message_ul.style.display = 'none'
    }

    function createCompareObjectBySpecValue(compare_rows) {
        compare_rows.forEach(row => {
            let compare_dict = {}
            const spec_name = row.children[0].innerText
            if (row.children.length > 1) {

                const items = [...row.children[1].children]
                items.forEach(item => {
                    const compare_feature_value = item.children[1].innerText
                    !compare_dict[spec_name]
                        ? compare_dict[spec_name] = [compare_feature_value]
                        : compare_dict[spec_name].push(compare_feature_value)
                })
                allEqual(compare_dict[spec_name]) ? row.classList.add('Compare-row_hide') : row.classList.remove('Compare-row_hide')
            }
        })
    }

    function allEqual(arr) {
        return new Set(arr).size == 1;
    }

    if (item_cards.length > 0) {
        item_cards.forEach(item => {
            item.addEventListener('click', addToCompareList)
        })
    }

    if (window.getComputedStyle(messages_ul).display === 'block') {
        setTimeout(() => {
            hideMessage(messages_ul)
        }, 1000)

    }

    if (compare_rows.length > 0) {
        createCompareObjectBySpecValue(compare_rows)
    }

});



