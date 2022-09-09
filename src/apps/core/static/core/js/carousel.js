jQuery(function($) {
  jQuery(document).ready(function(){  
     $('.home-reviews__slider').slick({
         infinite: false,
         slidesToShow: 3,
         slidesToScroll: 3,
         dots: false,
         prevArrow: $('.home-reviews__arrow-prev'),
         nextArrow: $('.home-reviews__arrow-next'),
         responsive: [{
          breakpoint: 991,
          settings: {
            slidesToShow: 1,
            slidesToScroll: 1,
            centerMode: true,
          }
        }]
     });

     $('.mobile-page-reviews__slider').slick({
        infinite: true,
        slidesToShow: 1,
        slidesToScroll: 1,
        dots: true,
        arrows: false,
        centerMode: true,
    });
  }); 
});