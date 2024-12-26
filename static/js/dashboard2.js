function sdbarshw(){
    var shcl=document.getElementById('iconshcl')
    if (shcl.classList.contains("bi-list"))
{
    shcl.classList.replace("bi-list","bi-x")
    document.getElementById("sdbar").style.marginLeft="0px"
    document.getElementById("log").style.marginLeft="0px"
}
else{
    shcl.classList.replace("bi-x","bi-list")
    document.getElementById("sdbar").style.marginLeft="-260px"

    document.getElementById("log").style.marginLeft="-220px"
}
    
}
function tblenter1(){
        document.getElementById("tbl1").style.display="block"
}
function tblout1(){
    document.getElementById("tbl1").style.display="none"
}

function tblenter2(){
    document.getElementById("tbl2").style.display="block"
}
function tblout2(){
document.getElementById("tbl2").style.display="none"
}

function tblenter3(){
    document.getElementById("tbl3").style.display="block"
}
function tblout3(){
document.getElementById("tbl3").style.display="none"
}



window.addEventListener('load', function() {
    // Select all img tags on the page
    const images = document.querySelectorAll('img');
    
    // Loop over each image and attach an onerror handler
    images.forEach(img => {
      img.onerror = function() {
        this.onerror = null;  // Prevent infinite loop if fallback also fails
        this.src = 'images/noimage.jpeg';  // Fallback image if the original fails to load
      };
    });
  });