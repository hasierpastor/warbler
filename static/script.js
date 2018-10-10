$(document).ready(function() {
  console.log('JS Loaded');
  $('#messages').on('click', 'button', function(event) {
    // event.preventDefault();
    $(event.target).toggleClass('far fas');
    // $(event.target)
    //   .parent()
    //   .toggleClass('favorite');
    // message_id =
    // message_id = event.target.id;
    // $.ajax({
    //   url: '/',
    //   data: { message_id },
    //   method: 'POST',
    //   success: function(response) {
    //     console.log(response);
    //   }
    // });
  });
});
