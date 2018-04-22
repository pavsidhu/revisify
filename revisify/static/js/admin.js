function warnPopup(userID) {
  $('.overlay').fadeIn(50);
  $('#warnPopup').fadeIn(50);
  $('#accountID').val(userID);
}

function banPopup(userID) {
  $('.overlay').fadeIn(50);
  $('#banPopup').fadeIn(50);
  $('#banAccountID').val(userID);
}

function AdminEditButton(action) {
  $('#editAccount').attr('action', action);
  $('#editAccount').submit();
}

function createSocialImage() {
  var values = Sijax.getFormValues('#createSocialImageForm');
  Sijax.request('createSocialImage', [values]);
}

function showSocialImage(src) {
  $('#showSocialImage img').attr('src', src);

  $('.overlay').fadeIn(50);
  $('#showSocialImage').fadeIn(50);
}
