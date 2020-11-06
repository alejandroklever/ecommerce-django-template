let asc = true
let key = 'nombre'
let elements = []


function load() {
    asc = true;
    elements = [];
    let listItems = document.getElementById('item_list');
    for (let i = 0; i < listItems.childElementCount; i++)
        elements[i] = listItems.children[i].cloneNode(true);
}

function search() {
    let value = document.getElementById('search').value;
    let itemListNode = document.getElementById('item_list');

    for (let i = itemListNode.childElementCount - 1; i >= 0; i--)
        itemListNode.children[i].remove();

    if (value === '' || value === undefined)
        for (let i = 0; i < elements.length; i++)
            itemListNode.appendChild(elements[i].cloneNode(true));
    else
        for (let i = 0; i < elements.length; i++)
            if (value && elements[i].getAttribute('id').includes(value))
                itemListNode.appendChild(elements[i].cloneNode(true));

}

function orderBy() {
    let items = []
    let listItems = document.getElementById('item_list');
    for (let i = 0; i < listItems.childElementCount; i++)
        items.push(listItems.children[i].cloneNode(true))

    items.sort()
}
