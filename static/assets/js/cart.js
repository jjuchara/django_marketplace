document.addEventListener("DOMContentLoaded", function () {

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

    const addToCartBtn = document.querySelectorAll('.add-to-cart')
    const updateAmountBtn = document.querySelectorAll('.amount-update')
    const deleteItemBtn = document.querySelectorAll('.item-delete')
    const cart = document.querySelector('.Cart')
    const seller_el = document.querySelectorAll('.Cart-block_seller>select')
    const promoCodBtn = document.getElementById('promo-code-apply')
    const cartCheckoutBtn = document.getElementById('cart-checkout')
    const cart_qty = document.getElementById('cart-qty')

    if (cart_qty.innerText === '0') {
        if (cartCheckoutBtn) {
            cartCheckoutBtn.style.pointerEvents = 'none'
        }

    }

    async function makeRequest(url, method, body) {
        let headers = {
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/json',
        }

        if (method == 'post') {
            headers['X-CSRFToken'] = csrftoken
        }

        let response = await fetch(url, {
            method: method, headers: headers, body: body,
        })
        return await response.json()
    }

    function createDataToRequest(cartItem, seller = null) {
        const url = '/cart/update-cart/'
        const itemId = cartItem.getAttribute('data-item-id')
        const action = cartItem.getAttribute('data-action')
        let selected_seller = seller
        let itemQty = document.querySelector(`.Amount-input[data-item-id="${itemId}"]`)
        itemQty ? itemQty.value : null
        switch (action) {
            case 'increase':
                itemQty = Number(itemQty) + 1;
                break
            case 'decrease':
                itemQty = Number(itemQty) - 1;
                break
            case 'add':
                itemQty ? itemQty = itemQty.value : itemQty = 1
                break
            default:
                itemQty = null
                break
        }
        const body = JSON.stringify({
            'item_id': itemId,
            'action': action,
            'item_qty': itemQty,
            'selected_seller': selected_seller,
        })
        return [body, url]
    }

    addToCartBtn.forEach(item => {
        item.addEventListener('click', async (e) => {
            e.preventDefault()
            const seller = item.getAttribute('data-seller')
            let [body, url] = createDataToRequest(item, seller)

            let data = await makeRequest(url, 'post', body)

            changeCartQty(data)
            changeCartTotalPrice(data)
            addMessage(data)
        })
    })

    deleteItemBtn.forEach(item => {
        item.addEventListener('click', async (e) => {
            e.preventDefault()
            let [body, url] = createDataToRequest(item)
            let data = await makeRequest(url, 'post', body)

            deleteItemFromCart(data)
            changeCartQty(data)
            changeCartTotalPrice(data)
            location.reload()
        })
    })

    updateAmountBtn.forEach(item => {
        item.addEventListener('click', async (e) => {
            e.preventDefault()
            let [body, url] = createDataToRequest(item)
            let data = await makeRequest(url, 'post', body)
            const itemQty = data['item_qty']

            if (data['action'] === 'decrease' && itemQty < 1) {
                deleteItemFromCart(data, itemQty)
            }

            updateItemQuantity(data)
            if (data['action'] === 'increase' && data['message'][1] === 'danger') {
                addMessage(data)
            }
            changeCartQty(data)
            changeItemsTotalPrice(data, data['action'])
            changeCartTotalPrice(data, data['action'])
            location.reload()
        })
    })

    seller_el.forEach(item => {
        item.addEventListener('change', async (e) => {
            e.preventDefault()

            let selected_seller = e.target.options[e.target.selectedIndex].value
            let [body, url] = createDataToRequest(item, selected_seller)
            let data = await makeRequest(url, 'post', body)

            addMessage(data)
            updateItemQuantity(data)
            changeItemsTotalPrice(data, data['action'])
            changeCartTotalPrice(data, data['action'])
        })
    })


    function updateItemQuantity(data) {
        const domAmount = document.querySelector(`.Amount-input[data-item-id="${data['item_id']}"]`)
        domAmount ? domAmount.value = data['item_qty'] : null
    }

    function changeCartQty(data) {
        let cart = document.getElementById('cart-qty')
        cart.innerText = data['cart_qty']
    }

    function changeCartTotalPrice(data) {
        document.querySelector('.header-cart-total-price').innerHTML = data['new_cart_total_price'] + '&#8381;'
        if (data['action'] !== 'add') {
            document.querySelector('.cart-total-price').innerHTML = data['new_cart_total_price'] + '&#8381;'
            const promoCodeInput = document.getElementById('promo-code')
            promoCodeInput.value = ''
        }
    }

    function changeItemsTotalPrice(data, action) {
        const itemPrice = document.querySelector(`.item-price[data-item-id="${data['item_id']}"]`)
        const itemPriceOld = document.querySelector(`.Cart-price_old[data-item-id="${data['item_id']}"]`)
        if (action === 'increase' || action === 'update') {
            itemPrice.innerHTML = data['new_item_total_price'] + '&#8381;'
            if (itemPriceOld) {
                itemPriceOld.innerHTML = (data['old_item_total_price'] * data['item_qty']) + '&#8381;'
            }
        } else if (action === 'decrease' && data['item_qty'] > 0) {
            itemPrice.innerHTML = data['new_item_total_price'] + '&#8381;'
            if (itemPriceOld) {
                itemPriceOld.innerHTML = (data['old_item_total_price'] * data['item_qty']) + '&#8381;'
            }

        }
    }

    function deleteItemFromCart(data) {
        const itemToDelId = data['item_id']
        document.querySelector(`.Cart-product[data-item-id="${itemToDelId}"]`).remove()
    }

    function addCartEmptySign() {
        console.log(cart.length)
        if (cart.length === 0) {
            cart.insertAdjacentHTML("afterbegin", `<h2 style="text-align: center">Корзина пуста!</h2>`)
        }
    }

    function addMessage(data) {
        const item_message_node = document.querySelector(`.message[data-item-id="${data['item_id']}"]`)
        let cart_message_node = null
        if (data['message'].length > 0) {
            cart_message_node = document.getElementById('cart-message')
            if (item_message_node) {
                set_display_message(data['message'], item_message_node)
            } else if (cart_message_node) {
                set_display_message(data['message'], cart_message_node)
            }
        }
    }

    function set_display_message(message, message_node) {
        message_node.innerText = message[0]
        message_node.classList.add(`alert-${message[1]}`)
        message_node.style.display = 'block'

        setTimeout(() => {
            message_node.style.display = 'none'
        }, 2000)
    }

    if (promoCodBtn) {
        promoCodBtn.addEventListener('click', async e => {
            const promoCodeText = document.getElementById('promo-code').value
            const url = '/cart/use-promo-code/'
            const action = promoCodBtn.getAttribute('data-action')
            const body = JSON.stringify({
                'promo_code': promoCodeText,
                'action': action
            })
            const data = await makeRequest(url, 'post', body)
            addMessage(data)
            changeCartTotalPrice(data)
        })
    }
})