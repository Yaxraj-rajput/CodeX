var main = document.querySelector(".hero-div-main");
var cursor = document.querySelector(".cursor");
var imageTrack = document.querySelector("#image-track");

imageTrack.addEventListener("mouseenter", function () {
  cursor.style.opacity = "100%";
});

imageTrack.addEventListener("mouseleave", function () {
  cursor.style.opacity = "0%";
});

main.addEventListener("mousemove", function (event) {
  cursor.style.left = event.clientX + "px";
  cursor.style.top = event.clientY + "px";
});
