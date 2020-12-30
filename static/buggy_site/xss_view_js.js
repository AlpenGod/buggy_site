function myFunction(item) {
  //var x = document.getElementById("myText").value;
  //document.getElementById("demo").innerHTML = x;
  alert('Hello' + item);
  console.log("form submitted!") 
}

// Submit post on submit
$('#post-form').on('submit', function(event){
    event.preventDefault();
    console.log("form submitted!")  // sanity check
    xss();
});

function xss(){
	alert(1);
}

$('.my-form').on('submit', function () {
    alert('Form submitted!');
    return false;
});

function grats(){
	var x=document.getElementById("title").value;
	//alert("You have successfully added " + x + "to your cart!")
	alert(x)
}
