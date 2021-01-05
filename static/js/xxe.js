var element = document.getElementById('check');
//var quantity = document.getElementById('cart_quantity');
//var id = document.getElementById('id');

element.onclick = function() {
        let url = "/media/read.xml";
        fetch(url)
        .then(response=>response.text())
        .then(data=>{
            let parser = new DOMParser();
            let xml = parser.parseFromString(data, "application/xml");
            //document.getElementById('output').textContent = data;
            send(data);
            //buildHouseList(xml);
            //buildSwordList(xml);
            //var quantity = document.getElementById('cart_quantity').value;
			//var id = document.getElementById('slug').value;
        });
    }


        
function buildHouseList(x){
    let list = document.getElementById('houses');
    let houses = x.getElementsByTagName('house');
    for(let i=0; i<houses.length; i++){
        let li = document.createElement('li');
        let house = houses[i].firstChild.nodeValue;
        li.textContent = house;
        list.appendChild(li);
    }
}

function buildSwordList(x){
    let list = document.getElementById('swords');
    let swords = x.getElementsByTagName('sword');
    for(let i=0; i<swords.length; i++){
        let li = document.createElement('li');
        let swordName = swords[i].firstChild.nodeValue;
        let person = swords[i].getAttribute('owner');
        li.textContent = `${swordName} - ${person}`;
        list.appendChild(li);
    }
}

function send(body) {
var xhr = new XMLHttpRequest();
console.log("xd")
xhr.open("POST", '/test/', true);
xhr.setRequestHeader("Content-Type", "application/xml");
xhr.send(body);
//window.location.href="/test";
//setTimeout(function(){ window.location.href="/test" }, 3000);

}

