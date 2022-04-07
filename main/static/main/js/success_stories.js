$(document).ready(function() {
    console.info('doc ready');
    $('.slider').slick({
        arrows: true,
        autoplay: true,
        autoplaySpeed: 10000,
        centerMode: false,
        dots: true,
        pauseOnDotsHover: true,
        swipeToSlide: true,
//        prevArrow: '<i class="bi bi-arrow-left-square-fill slick-prev" data-role="none">prev</i>',
   });
});
