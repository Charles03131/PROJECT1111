

const buttons=document.querySelectorAll("button");

for(let button of buttons){
    button.addEventListener("click",function(e){
        e.target.classList.toggle('.isLiked');
    });
    
}