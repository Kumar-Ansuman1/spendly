// Category bar width animation on profile page
document.addEventListener("DOMContentLoaded", function() {
    var bars = document.querySelectorAll(".category-bar");
    bars.forEach(function(bar) {
        var width = bar.getAttribute("data-width");
        if (width) {
            bar.style.width = width + "%";
        }
    });
});
