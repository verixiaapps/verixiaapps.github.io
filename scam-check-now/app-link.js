function openApp(){
window.location.href="https://apps.apple.com/app/id6759490910";
}

document.addEventListener("DOMContentLoaded",function(){

const buttons=document.querySelectorAll("button");

buttons.forEach(function(btn){
if(btn.innerText.includes("iPhone App")){
btn.addEventListener("click",openApp);
}
});

});