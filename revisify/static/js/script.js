// Check to see if device is mobile or desktop
function mobileDisplay() {
    if ($('.menuIcon').css('display') == 'none') {
      // If desktop
      return false;
    }
    else {
      // If mobile
      return true;
    }
}

// Account Menu in Navigation Bar

$(function(){
    $("#rightNav").hover( function() {
      $("#dropdownMenu").fadeIn(50);
      $(".dropdownArrow path").css("animation", "menuArrowUp 0.25s forwards");
    }, function(){
      $("#dropdownMenu").fadeOut(50);
      $(".dropdownArrow path").css("animation", "menuArrowDown 0.25s forwards");
    });
});

$(document).mouseup(function (e) {  // Closes menu if open and clicked elsewhere
  var container = $("#dropdownMenu");

  if (!container.is(e.target) && container.has(e.target).length === 0) {
    $("#dropdownMenu").fadeOut(60);
  }
});

var menu = $('#menu');
var menuContent = $('#menuContent');
var mobileSearch = $("#searchMobileDisplay");
var showSearch = $("#showSearch");
var hideSearch = $("#hideSearch");
var menuWidth = document.getElementById('menu');
var menuContentWidth = document.getElementById('menuContent');
var menuShow = false;

function toggleMenu() {
  // Hides search if open
  if ($("#searchMobileDisplay").is(':visible')) {
    toggleSearch();
  }

  if (menuShow === false) {
    if ($('.welcomeIntro') && $('nav').hasClass('welcomeNavigation')) {
      $('nav').removeClass('welcomeNavigation')
      $('nav').addClass('welcomeNavigationDisabled')
    }

    $('#menu').animate({
      left: 0,
    }, 10).show();

    menuShow = true;
  } else {
    if ($('.welcomeIntro') && $('nav').hasClass('welcomeNavigationDisabled')) {
        $('nav').addClass('welcomeNavigation')
        $('nav').removeClass('welcomeNavigationDisabled')
    }

    $('#menu').animate({
      left: '-50em',
    }, 10).fadeOut(120);

    menuShow = false;
  }
}

$(document).mouseup(function (e) {  // Closes menu if open and clicked elsewhere
  var menuContainer = $("#menu");
  var navContainer = $("nav");

  if (!menuContainer.is(e.target) && menuContainer.has(e.target).length === 0 && !navContainer.is(e.target) && navContainer.has(e.target).length === 0) {
    if (menuShow === true) {toggleMenu();}
  }
});

// Toggles display of search bar in smaller screens

function toggleSearch() {
  // Hides hamburger menu if open and search pressed
  if (menuShow === true) {
    toggleMenu();
  }

  if (mobileSearch.is(':hidden')) { // Shows search
    mobileSearch.slideDown(20);
    showSearch.hide();
    hideSearch.fadeIn(50);
    mobileSearch.focus();
  } else {
    mobileSearch.slideUp(20); // Hides search
    hideSearch.hide();
    showSearch.fadeIn(50);
    mobileSearch.val('');
  }
}

$('.notificationBar svg').click(function() {
  $('.notificationBar').slideUp(50, function(){
    $('.notificationBar').remove();
  });
});

// UI Elements

$('.segment span').click(function(){
  $('.segment span').removeClass('active');

  var option = $(this);
  option.addClass('active');

});

$('.overlay').click(function(){
  hidePopup();
});

// Subjects/Topics Page ----------------------------------------------------------------------------------------------------------------

$('.actionBar .shareButton').click(function() {
  var link = $(this).attr('share-link');

  $('#shareFacebook').attr('href', 'https://www.facebook.com/sharer/sharer.php?u=' + link);
  $('#shareTwitter').attr('href', 'https://twitter.com/home?status=Check%20out%20this%20topic%20on%20%23Revisify%20' + link);
  $('#shareGoogle').attr('href', 'https://plus.google.com/share?url=' + link);
  $('#shareClassroom').attr('href', 'https://classroom.google.com/share?url=' + link);
  $('#shareLink').val(link);

  $('.overlay').fadeIn(50);
  $('#sharePopup').fadeIn(50);
});

$('.actionBar .editButton').click(function() {
  editMode = true;

  $('.toolbar:first-child').show();

  $('.topicText').attr('contenteditable', true);

  // Hide action bar, study mode section and progress chart section
  $('.topicOverviewFirstRow .column').eq(0).css('transform', 'translateX(-150vw)');
  $('.topicOverviewFirstRow .column').eq(1).css('transform', 'translateX(150vw)');
  $('.actionBar').css('transform', 'translateX(150vw)');

  setTimeout(function() {
    $('.actionBar').slideUp(100);
    $('.topicOverviewFirstRow').slideUp(200);
  }, 150);

  // Replace page title with edit topic name input and show edit functions
  setTimeout(function() {
    $('h1').html('Edit Topic');
    $('input.topicName').slideDown(100);

    $('.questionToolbar').removeClass('hidden');
    $('.addQuestionButton').removeClass('hidden');

    // Cannot simply remove class for some reason, this is a workaround
    $('.questionSortHandle').attr('class', 'questionSortHandle');
    $('.addQuestion').attr('class', 'addQuestion');
    $('.deleteQuestion').attr('class', 'deleteQuestion');


    if (mobileDisplay()) {
        $('.saveTopic').removeClass('hidden');
    }
  }, 250);
});

$('.actionBar .deleteButton').click(function() {
  $('.overlay').fadeIn(50);
  $('#deletePopup').fadeIn(50);
});

// Weekly Goal

$('.weeklyGoalPopupChoice').click(function() {
  $('.weeklyGoalPopupChoice').removeClass('active');
  $(this).addClass('active');
});

$('.weeklyGoalPopupChoiceCustomChoose svg').eq(0).click(function() {
  var goal = parseInt($('.weeklyGoalPopupChoiceCustom p span').html());

  if (goal != 1) {
    $('.weeklyGoalPopupChoiceCustom').attr('topic-goal', goal - 1);
    $('.weeklyGoalPopupChoiceCustom p span').eq(0).html(goal - 1);
  }

  // If goal is '1' rename 'topics' to 'topic' for correct grammar
  if (goal-1 == 1) {
    $('.weeklyGoalPopupChoiceCustom p span').eq(1).html('');
  }
});

$('.weeklyGoalPopupChoiceCustomChoose svg').eq(1).click(function() {
  var goal = parseInt($('.weeklyGoalPopupChoiceCustom p span').html());

  if (goal != 40) {
    $('.weeklyGoalPopupChoiceCustom p span').html(goal + 1);
    $('.weeklyGoalPopupChoiceCustom').attr('topic-goal', goal + 1);
  }

  if (goal+1 != 1) {
    $('.weeklyGoalPopupChoiceCustom p span').eq(1).html('s');
  }
});

function weeklyGoalSubmit() {
  var goal = $('.weeklyGoalPopupChoice.active').attr('topic-goal');
  Sijax.request('editWeeklyGoal', [goal]);
  $('*').css('cursor','progress');
}

function confirmEmail() {
  Sijax.request('confirmEmail');
  $('*').css('cursor','progress');
}

function studyStreakCount(results) {
  var streak = 0;

  for (i=0; i <= results.length-1; i++) {
    var result = results[i];

    if (i === 0) {
      if (moment.utc(result).local().format('DDMMYY') === moment().format('DDMMYY') ||
          moment.utc(result).local().format('DDMMYY') === moment().subtract(1, 'days').format('DDMMYY')) {
        streak += 1;
      }
    }
    else {
      if (moment.utc(result).local().format('DDMMYY') !== moment.utc(results[i-1]).local().format('DDMMYY')) {
        if (moment.utc(result).local().format('DDMMYY') === moment.utc(results[i-1]).local().subtract(1, 'days').format('DDMMYY')) {
          streak += 1;
        }
        else {
          return streak;
        }
      }
    }
  }

  return streak;
}

function updateStudyStreak(results) {
  // Calculate streak from list of previous result dates
  var streak = studyStreakCount(results);

  // Update page with study streak
  $('.studyStreakCount').html(streak);

  // Calculate time left until the end of the day
  // .append() is used over .html() due to annoying bug in Microsoft Edge
  $('.studyStreakTimeLeft').append(moment().add(1, 'days').startOf('day').fromNow());
  $('.timeScale').append($('.momentTimeScale').html());
}

$('.studyModeInfoButton').click(function() {
  $('.studyModeMain').slideUp(100, function() {
    $('.studyModeInfo').fadeIn(100);
  });
});

$('.studyModeInfo button').click(function() {
  $('.studyModeInfo').fadeOut(100, function() {
    $('.studyModeMain').slideDown(100);
  });
});

// Search Page ---------------------------------------------------------------------------------------------------------------

$('.searchToggle span').click(function(){

  $('.searchResults .column').hide();
  var option = $(this);

  // This is trimmed since the HTML is not layed out in an abnormal way to prevent
  // Spacing between the options since they are displayed as inline-block
  var text = option.html().trim();

  switch (text) {
    case 'Subjects':
      $('.searchResultsSubjects').show();
      break;
    case 'Topics':
      $('.searchResultsTopics').show();
      break;
    case 'People':
      $('.searchResultsPeople').show();
      break;
  }
});

function addPage() {
  var container = $('<div>').addClass('page' + page).hide();
  $('.searchResultsSubjects').append(container);

  var container = $('<div>').addClass('page' + page).hide();
  $('.searchResultsTopics').append(container);

  var container = $('<div>').addClass('page' + page).hide();
  $('.searchResultsPeople').append(container);
}

function addSearchItem(column, title, subtitle, link, icon, textcolor, iconcolor) {
  var link = $('<a>').attr('href', link);

  var item = $('<div>').addClass('searchItem');

  // Search Item Icon
  var itemIcon = $('<div>').addClass('searchItemIcon unselectable');

  if (column == 'people') {
    itemIcon.css('background-image', 'url("'+ icon +'")');
  }
  else {
    itemIcon.css('color', textcolor);
    itemIcon.css('background-color', iconcolor);
    itemIcon.html(title.charAt(0).toUpperCase());
  }

  item.append(itemIcon);

  // Search Item Text
  var itemText = $('<div>').addClass('searchItemText');

  var itemTextTitle = $('<div>').addClass('searchItemTextTitle').html(title);
  itemText.append(itemTextTitle);

  // Search Item Subtitle
  var itemTextSubtitle = $('<div>').addClass('searchItemTextSubtitle');

  // Search Item Subtitle icon
  if (column !== 'people') {
    var itemTextSubtitleIcon = $('<img>').attr('src', icon);
    itemTextSubtitle.append(itemTextSubtitleIcon);
  }

  var itemTextSubtitleText = $('<span>').html(subtitle);
  itemTextSubtitle.append(itemTextSubtitleText);

  itemText.append(itemTextSubtitle);

  item.append(itemText);

  link.html(item);

  switch (column) {
    case 'subjects':
      $('.searchResultsSubjects .page' + page).append(link);
      break;
    case 'topics':
      $('.searchResultsTopics .page' + page).append(link);
      break;
    case 'people':
      $('.searchResultsPeople .page' + page).append(link);
      break;
  }
}

// User Profile Settings -----------------------------------------------------------------------------------------------------

function setupProfileNext(skip) {
  var button = $('.setupProfileButton');

  // If submitting profile picture
  if (button.html() === 'Next') {
    // If profile picture is uploaded by the user
    if (!defaultProfilePicture() || skip) {
      $('.errorText').fadeOut(50);

      // Fade out and in button text
      $('.setupProfileButton').hide();
      $('.setupProfileButton').html('Save');
      $('.setupProfileButton').fadeIn(50);

      // Move profile picture form to left
      $('.image-editor').css('position', 'relative');
      $('form#userDetails').css('position', 'relative');

      $('.image-editor').animate({left: '-=' + $(window).width()}, 125, function() {
        $('.image-editor').slideUp(50);

        // Move user details form from right to center
        $('form#userDetails').removeClass('hidden');
        $('form#userDetails').slideDown(50);
        $('form#userDetails').css('left', $(window).width());
        $('form#userDetails').animate({left: '-=' + $(window).width()}, 200);
      });

      if (!skip) {
        profilePictureSubmit();
      }
    }
    else {
      $('.errorText').html('You forgot to upload a profile picture.');
    }

  }
  // If account details are submitted
  else {
    if (skip) {
      // If skipping form, submitting the data will be invalid on the server
      // side so will not enter blank details
      $('#userDetails').submit();
    }
    else {
      var education = $('#userDetails #education').val().trim();
      var location = $('.selectator_chosen_item_title span').html();

      if (education === '' && location == 'Select your location') {
        $('.errorText').html('Please enter your place of education and your location.');
        $('.errorText').fadeIn(50);
      }
      else if (education !== '' && location == 'Select your location') {
        $('.errorText').html('Please enter your location.');
        $('.errorText').fadeIn(50);
      }
      else if (education === '' && location != 'Select your location') {
        $('.errorText').html('Please enter your place of education.');
        $('.errorText').fadeIn(50);
      }
      else {
        $('.errorText').fadeOut(50);
        $('#userDetails').submit();
      }
    }
  }
}


function editProfile() {
  if (mobileDisplay()) {
    window.location.href = 'https://revisify.com/edit-my-details';
  }
  else {
    $('.overlay').fadeIn(50);
    $('#editUserDetailsPopup').fadeIn(50);
  }
}


// Checks if cropit has the default profile picture or one that is uploaded
function defaultProfilePicture() {
  if (img.cropit('imageSrc') === undefined) {
    return true;
  }
  else {
    return false;
  }
}


$('.cropit-image-preview, .userProfilePicture p').click( function(e) {
  if (mobileDisplay() && e.target.id === 'EditProfilePicture') {
    window.location.href = 'https://revisify.com/change-profile-picture';
  }
  else if (defaultProfilePicture()) {
    $('#picture').click();
  }
});

// This event handler is seperate from the one above since once a photo has been
// added, defaultProfilePicture() will return false.
$('.cropit-image-change span').click( function() {
  $('#picture').click();
});

// Validates uploaded profile picture for correct size and file type
function profilePictureValidation() {
  var file = document.getElementById('picture');
  var error = false;

  if ('files' in file) {
    file = file.files[0];

    // Check if file is less than 8MB
    if (file.size > 8388608) {
      $('.cropit-image-preview').css('background-image', '');
      $('.errorText').html('Your profile picture must be smaller than 3MB in size.');
      error = true;
    }


    // Check if file is only .PNG, .JPEG or .JPG
    var filename = document.getElementById('picture').value.split('.');
    var fileType = ['png', 'jpeg', 'jpg'];
    var correctFileType = fileType.indexOf(filename[filename.length - 1]) > -1;

    if (correctFileType === false) {
      $('.cropit-image-preview').css('background-image', '');
      $('.errorText').html('Profile pictures can only be .png, .jpg, or .jpeg filetypes.');
      error = true;
    }

    // If no file size or file type error
    if (!error) {
      $('#picturePopup').fadeIn(50);
      $('.overlay').fadeIn(50);

      $('.cropit-image-preview p').fadeOut(50);
      $('.errorText').fadeOut(50);
      $('.cropit-image-change').slideDown(100);
      $('.cropit-zoom-container').slideDown(100);
      $('.cropit-image-preview-overlay').fadeOut(50);

      $('.cropit-image-preview').css('cursor', 'move');
    }
  }
}

function profilePictureSubmit() {
  if (img.cropit('imageSrc')) {
    var offset = img.cropit('offset');
    var imageSize = img.cropit('imageSize');
    var previewSize = img.cropit('previewSize');
    var zoom = img.cropit('zoom');

    var x1 = Math.round(Math.abs(offset.x) / zoom);
    var x2 = Math.round((Math.abs(offset.x) + previewSize.width) / zoom);

    var y1 = Math.round(Math.abs(offset.y) / zoom);
    var y2 = Math.round((Math.abs(offset.y) + previewSize.height) / zoom);

    // Add crop coordinates to form
    $('form#profilePicture #crop').val(x1 + ',' + y1 + ',' + x2 + ',' + y2);

    // Submit form
    $('form#profilePicture').submit();

  } else {
    $('form .errorText').html('You forgot to upload a profile picture!');
  }
}

// New Subject Page ----------------------------------------------------------------------------------------------------------

function outline(x) {
  $('.subjectColor').css('box-shadow', 'none');
  switch (x) {
    case 0:
      $('#Red').css('box-shadow', 'inset 0 0 0 0.3em #FFEBEE');
      break;
    case 1:
      $('#Pink').css('box-shadow' ,'inset 0 0 0 0.3em #FCE4EC');
      break;
    case 2:
      $('#Purple').css('box-shadow' ,'inset 0 0 0 0.3em #EDE7F6');
      break;
    case 3:
      $('#Blue').css('box-shadow' ,'inset 0 0 0 0.3em #E3F2FD');
      break;
    case 4:
      $('#Cyan').css('box-shadow' ,'inset 0 0 0 0.3em #E0F7FA');
      break;
    case 5:
      $('#Teal').css('box-shadow' ,'inset 0 0 0 0.3em #E0F2F1');
      break;
    case 6:
      $('#Green').css('box-shadow' ,'inset 0 0 0 0.3em #F1F8E9');
      break;
    case 7:
      $('#Lime').css('box-shadow' ,'inset 0 0 0 0.3em #F9FBE7');
      break;
    case 8:
      $('#Orange').css('box-shadow' ,'inset 0 0 0 0.3em #FBE9E7');
      break;
    case 9:
      $('#Brown').css('box-shadow' ,'inset 0 0 0 0.3em #EFEBE9');
      break;
  }
}


function charCheck(name) {
  var check = new RegExp('.*[A-Za-z0-9].*');
  return !check.test(name);
}

// Study Page -----------------------------------------------------------------------------------------------------------------

function AddQuestionHistory(correct) {
  // If questionHistory has began being populated, update the previous question
  // as to whether the question was correct or incorrect
  if (questionHistory.length > 0) {
    questionHistory.slice(-1)[0]['correct'] = correct
  }

  // Add the current question to questionHistory
  questionHistory.push({
    'number': number,
    'correct': null
  });
}


function getScore(correct) {
  var score = 0;

  for (i=0; i <= questionHistory.length-1; i++) {
    if (questionHistory[i]['correct']) {
      score++;
    };
  }

  // If question just answered was correct
  if (correct) {
    score++;
  }

  return score;
}


function showQuestion() {
  $('h1').hide();
  $('h1').html(questions[number-1]['question']);
  $('h1').fadeIn(150);

  $('.answerContainer .answer').removeClass('answerShow');
  $('.answerContainer').slideUp(50);

  $('.answer').html(questions[number-1]['answer']);
  $('.answer img').attr('data-action', 'zoom');
  $('h1 img').attr('data-action', 'zoom');

  if ($('.answer').html() !== null && $('.answer').html() !== "") {
    $('.answerButton').html('Show Answer');
    $('.answerButton').removeClass('hidden');
  } else {
    $('.answerButton').addClass('hidden');
  }
}


function changeQuestion(random, correct, undo) {
  if (undo) {
    // If there is only one question in the list, do not undo. Although the undo
    // button disappears, undoing can be activated using the keyboard shortcut
    if (questionHistory.length === 1) {
      return;
    }

    // Remove current question from history
    questionHistory.pop();

    // Get last question number before it is removed next
    number = questionHistory.slice(-1)[0]['number']

    // Remove question about to show since it is added at the end of this
    // function
    questionHistory.pop();
  }
  else if (random) {
    var newNumber;

    // Get random question number that is not the same as the last question
    do {
      newNumber = Math.floor((Math.random() * questions.length)) + 1;
    }
    while (number === newNumber);

    number = newNumber;
  }
  else {
    number += 1;

    if (number > questions.length) {
      Sijax.request('result', [getScore(correct)]);
      studyFinished = true;
      return;
    }
  }

  AddQuestionHistory(correct);
  showQuestion();

  // Show undo (and finish button in practice mode) if at least one question has
  // been recorded
  if (questionHistory.length > 1) {
    $('.undoQuestion').removeClass('hidden');
    $('.finishPractice').removeClass('hidden');
  }
  else {
    $('.undoQuestion').addClass('hidden');
    $('.finishPractice').addClass('hidden');
  }

  if (!random) {
    setProgressBar();
  }
}


$('.answerButton').click(function() {
  // If there is an answer for the current question
  if (questions[number-1]['answer'] !== null) {

    // Update answer button text
    if ($('.answerContainer').is(':visible')) {
      $('.answerButton').html('Show Answer');
    } else {
      $('.answerButton').html('Hide Answer');
    }

    // Show/hide answer
    $('.answerContainer').slideToggle(120, 'easeInQuad', function() {
      $('.answerContainer .answer').toggleClass('answerShow');
    });
	}
});

// Test Mode

function setProgressBar() {
  percentage = (number / questions.length) * 100;

  $('.progressBar').css('width', percentage + '%');

  // We find the width below over $('.progressBar').width() because it's width
  // which is updated above is not updated quick enough so we calculate what
  // it's width we be like below
  var progressBarWidth = $(window).width() * percentage / 100;

  // +10 added so that the text will not be squished in if width of bar and
  // text is very close
  var progressBarTextWidth = $('.progressBarText').outerWidth(true) + 10;

  if (progressBarWidth < progressBarTextWidth) {
    $('.progressBarText').addClass('progressBarTextOutside');
  }
  else {
    $('.progressBarText').removeClass('progressBarTextOutside');
  }
}

$('.progressBarContainer').click(function() {
  $('.progressBarContainer').addClass('progressBarContainerShow');
  $('.studyBottomBar').addClass('studyBottomBarProgressBarShow');

  setTimeout(function() {
    $('.progressBarContainer').removeClass('progressBarContainerShow');
    $('.studyBottomBar').removeClass('studyBottomBarProgressBarShow');
  }, 1500);
});

// Practice Mode

$('.finishPractice').click(function() {
  studyFinished = true;

  percentage = Math.floor((getScore() / (questionHistory.length-1)) * 100);

  reviewQuestionNumbers = [];
  reviewQuestionCorrect = [];
  // Iterate from last question to first question in questionHistory.
  // -2 is used rather than -1 because the last question has no value for
  // correct since it was recorded but never answered so -2 is used over -1
  for (i = questionHistory.length-2; i >= 0; i--) {
    // Add question number of item if it is not already in the list
    if (reviewQuestionNumbers.indexOf(questionHistory[i]['number']) === -1) {
      // Two lists are used rather than one since checking if a question number
      // is already a list containing both numbers and if it was correct would
      // be difficult
      reviewQuestionNumbers.push(questionHistory[i]['number']);
      reviewQuestionCorrect.push(questionHistory[i]['correct']);
    }
  }

  reviewQuestions = [];
  for (i=1; i <= questions.length; i++) {

    // Create new row if the question is an odd number i.e. in the left column
    // of the page.
    if (i % 2 !== 0) { // If i is an odd number
      if (i <= 2) {
        $('<div class="reviewQuestionRow" id="reviewQuestionRow' + i + '"></div>').insertBefore('.reviewQuestionsMore');
      }
      else {
        $('.reviewQuestionsMore').append('<div class="reviewQuestionRow" id="reviewQuestionRow' + i + '"></div>');
        $('.reviewQuestionsMoreShow span').removeClass('hidden');
      }

      var reviewQuestionRow = '#reviewQuestionRow' + i;
    }
    else { // If i is an even number
      var reviewQuestionRow = '#reviewQuestionRow' + (i-1);
    }


    $(reviewQuestionRow).append('<div class="reviewQuestion" id="reviewQuestion' + i + '">' +
      '  <div class="reviewQuestionQuestion" id="reviewQuestionQuestion' + i + '"></div>' +
      '  <div class="reviewQuestionAnswer" id="reviewQuestionAnswer' + i + '"></div>' +
      '</div>');

    // Add question & answer HTML to page
    $('#reviewQuestionQuestion' + i).append(questions[i-1]['question']);
    $('#reviewQuestionAnswer' + i).append(questions[i-1]['answer']);

    // Display tick, cross or null line depending on result
    var reviewQuestionNumber = reviewQuestionNumbers.indexOf(i);
    if (reviewQuestionNumber !== -1) {
      if (reviewQuestionCorrect[reviewQuestionNumber]) {
        // Show tick if question was right
        $('#reviewQuestion' + i).append('<svg viewBox="0 0 100 100"><path d="M99.13,23.62l-11.8-11.8a3,3,0,0,0-4.23,0L47.94,47,36.67,58.22l-4.27-4.27L17,38.52a3,3,0,0,0-4.23,0L.87,50.32a3,3,0,0,0,0,4.23L34.51,88.18a3,3,0,0,0,4.23,0L99.07,27.85A2.94,2.94,0,0,0,99.13,23.62Z"/></svg>');
      }
      else {
        // Show cross if question was wrong
        $('#reviewQuestion' + i).append('<svg viewBox="0 0 100 100"><path d="M75.1,56.85,68.23,50,80.81,37.41,99.06,19.16a3.38,3.38,0,0,0,0-4.79L85.67,1a3.43,3.43,0,0,0-4.83,0L58.31,23.51,50,31.77l-8.16-8.16L19.23,1a3.38,3.38,0,0,0-4.79,0L1,14.37a3.38,3.38,0,0,0,0,4.79L21.81,39.92,31.87,50,21.23,60.62,1,80.77a3.38,3.38,0,0,0,0,4.79L14.4,98.92a3.38,3.38,0,0,0,4.79,0L41,77.1l9-9,8.5,8.5L80.77,98.92a3.38,3.38,0,0,0,4.79,0L98.92,85.57a3.38,3.38,0,0,0,0-4.79Z"/></svg>');
      }
    }
    else {
      // Show null line if question was not answered
      $('#reviewQuestion' + i).append('<svg viewBox="0 0 100 100"><path d="M96.61,62.87A3.39,3.39,0,0,0,100,59.48V40.53a3.43,3.43,0,0,0-3.41-3.41H3.39A3.39,3.39,0,0,0,0,40.51V59.4a3.39,3.39,0,0,0,3.39,3.39Z"/></svg>');
    }
  }

  configureResultsPage();
});

$('.reviewQuestionsMoreShow span').click(function() {
  $('.reviewQuestionsMore').slideDown(200);
  $('.reviewQuestionsMoreShow').addClass('hidden');
});


// Results

function resultsPage(percentage, results, weeklyGoal) {
  // Set question to value lower than 1 so that the prevent leave popup does not
  // show
  question = 0;

  window.percentage = percentage;
  window.results = results;
  window.weeklyGoal = weeklyGoal;

  configureResultsPage();

  // If user is not signed in, server will not provide a value for 'weeklyGoal'.
  // Don't load the previous results chart and the weekly goal chart as a result
  if (!weeklyGoal) {
    return;
  }

  if (weeklyGoal.progress / weeklyGoal.user.weeklyGoal === 1) {
    weeklyGoalCompleted(weeklyGoal);
  }
  else {
    configurePastResultsChart(results);
    configureWeeklyGoalChart(weeklyGoal, percentage);
  }
}


function configureResultsPage() {
  $('section.studyPage').remove();
  $('.studyBottomBar, .progressBar').fadeOut(50);

  $('section.resultsPage').removeClass('hidden');

  var title;
  if (percentage === 100) {
    title = 'Perfection!';
  }
  else if (percentage >= 75) {
    title = 'Brilliant!';
  }
  else if (percentage >= 50) {
    title = 'On Your Way!';
  }
  else if (percentage >= 35) {
    title = 'Not Bad...';
  }
  else {
    title = 'Practice Makes Perfect';
  }

  $('section.resultsPage h1').html(title);
  $('section.resultsPage p.resultPercentage').append(percentage + '%');
}


function configureWeeklyGoalChart(weeklyGoal, percentage) {
  var weeklyGoalText;
  if (weeklyGoal.progress / weeklyGoal.user.weeklyGoal >= 1) {
    weeklyGoalText = 'You\'ve achieved your goal, well done!';
  }
  else if (percentage >= 90) {
    weeklyGoalText = 'You\'re one step closer to your goal!';
  }
  else {
    weeklyGoalText = 'You must score 90% or higher to add to your weekly goal. Keep going!';
  }

  $('.weeklyGoalText').html(weeklyGoalText);
  $('.weeklyGoalFraction').html(weeklyGoal.progress + '/' + weeklyGoal.user.weeklyGoal);

  var circumference = 3.14159265359 * (2 * 80);
  $('.weeklyGoalChartProgress').css('stroke-dashoffset', circumference);

  if (weeklyGoal.progress / weeklyGoal.user.weeklyGoal >= 1) {
    var dashoffset = 0;
  }
  else {
    var dashoffset = circumference - ((weeklyGoal.progress / weeklyGoal.user.weeklyGoal) * circumference);
  }

  setTimeout(function() {
    $('.weeklyGoalChartProgress').css('stroke-dashoffset', dashoffset);
  }, 100);
}


function configurePastResultsChart(results) {
  if (results.length > 1) {
    Chart.defaults.global.defaultFontFamily = "'Texta-Regular'";
    Chart.defaults.global.elements.point = {
      hoverRadius: 6,
      hitRadius: 10,
    };

    if (mobileDisplay()) {
      var tickFontSize = 14
      var stepSize = 25
    }
    else {
      var tickFontSize = 18
      var stepSize = 20
    }

    resultChart = new Chart($('.resultChart canvas'), {
      type: 'line',
      data: {
        labels: results.map(function(result) {
          return result.date;
        }),
        datasets: [{
          fillColor: 'transparent',
          borderColor: textcolor,
          pointBackgroundColor: textcolor,
          pointRadius: 6,
          backgroundColor: 'transparent',
          pointHoverBackgroundColor: textcolor,
          pointHoverBorderColor: textcolor,
          lineTension: 0,
          data: results.map(function(result) {
            return result.percentage;
          }),
        }]
      },

      options: {
        scales: {
          yAxes: [{
            gridLines: {
              lineWidth: 2,
              zeroLineWidth: 2,
              zeroLineColor: navcolor,
              drawBorder: false
            },

            ticks: {
              callback: function(label, index, labels) {
                return label + '%    ';
              },
              max: 100,
              min: 0,
              stepSize: stepSize,
              fontSize: tickFontSize,
              fontColor: textcolor
            },
          }],
          xAxes: [{
            lineColor: 'transparent',
            gridLines: {
              lineColor: 'transparent',
              display: false,
            },
            ticks: {
              fontSize: tickFontSize,
              fontColor: textcolor
            }
          }]
        },
        legend: {
          display: false
        },
        tooltips: {
          mode: 'x-axis',
          titleFontColor: bgcolor,
          bodyFontColor: bgcolor,
          titleFontSize: 18,
          bodyFontSize: 22,
          backgroundColor: textcolor,
          cornerRadius: 5,
          callbacks: {
            label: function(tooltipItem, data) {
              return tooltipItem.yLabel + '%';
            }
          }
        }
      }
    });
  }
  else {
    $('.pastResultsColumn').addClass('hidden');

    $('.weeklyGoalColumn').removeClass('large-6');
  }
}


function weeklyGoalCompleted(weeklyGoal) {
  $('.overlay').fadeIn(50);

  $('.weeklyGoalOverlay').removeClass('hidden');
  $('.weeklyGoalDescription').attr('class', 'weeklyGoalDescription hidden');

  var circumference = 3.14159265359 * (2 * 80);
  $('.weeklyGoalOverlay .weeklyGoalChartProgress').css('stroke-dashoffset', circumference);

  setTimeout(function() {
    $('.weeklyGoalOverlay .weeklyGoalChartProgress').css('stroke-dashoffset', 0);
  }, 100);

  $('.confettiContainer').removeClass('hidden');
  for (i = 0; i <= 50; i++) {
    $('.confettiContainer').append('<div class="confetti confetti' + i + '"></div>');
    $('.confetti' + i).css('left', (Math.random() * 100) + 'vw');
    var animation = Math.round(Math.random() * 2) + 1;
    switch(animation) {
      case 1:
        $('.confetti' + i).css('animation', 'confetti1 ' + ((Math.random() * 1)+1.5) + 's '+ (Math.random() * 6) +'s linear forwards');
        break
      case 2:
        $('.confetti' + i).css('animation', 'confetti2 ' + ((Math.random() * 1)+1.5) + 's '+ (Math.random() * 6) +'s linear forwards');
        break
      case 3:
        $('.confetti' + i).css('animation', 'confetti3 ' + ((Math.random() * 1)+1.5) + 's '+ (Math.random() * 6) +'s linear forwards');
        break
      default:
        break
    }
  }
}

$('.weeklyGoalOverlay button').click(function() {
  $('.overlay, .weeklyGoalOverlay, .confettiContainer').fadeOut(50);
  $('.weeklyGoalDescription').attr('class', 'weeklyGoalDescription');
  configurePastResultsChart(window.results);
  configureWeeklyGoalChart(window.weeklyGoal, window.percentage);
});

// User Profile Page ---------------------------------------------------------------------------------------------------------

$('.userProfileBarSubjects').click(function() {
  $('.userFollowing, .userFollowers').hide();
  $('.userSubjects').show();

  $('.userProfileBarStats span').removeClass('active');

  var option = $(this);
  option.addClass('active');
});

$('.userProfileBarFollowing').click(function() {
  $('.userSubjects, .userFollowers').hide();
  $('.userFollowing').show();

  $('.userProfileBarStats span').removeClass('active');

  var option = $(this);
  option.addClass('active');
});

$('.userProfileBarFollowers').click(function() {
  $('.userSubjects, .userFollowing').hide();
  $('.userFollowers').show();

  $('.userProfileBarStats span').removeClass('active');

  var option = $(this);
  option.addClass('active');
});


$('.userProfileReport').click(function() {
  if (mobileDisplay()) {
    window.location.href = 'https://revisify.com/user/' + userHash + '/report';
  }
  else {
    $('#reportUserPopup').fadeIn(50);
    $('.overlay').fadeIn(50);
  }
});

$('.userProfileAdminWarn').click(function() {
  if (mobileDisplay()) {
    window.location.href = 'https://revisify.com/user/' + userHash + '/warn';
  }
  else {
    $('#warnUserPopup').fadeIn(50);
    $('.overlay').fadeIn(50);
  }
});

$('.userProfileAdminBan').click(function() {
  if (mobileDisplay()) {
    window.location.href = 'https://revisify.com/user/' + userHash + '/ban';
  }
  else {
    $('#banUserPopup').fadeIn(50);
    $('.overlay').fadeIn(50);
  }
});


function reportUserSend() {
  $('*').css('cursor', 'progress');

  var issue = $('#reportUserForm #issue').val();
  Sijax.request('reportUser', [issue]);

  return false;
}

function warnUserSend() {
  $('*').css('cursor', 'progress');

  var reason = $('#warnUserForm #reason').val();
  Sijax.request('warnUser', [reason]);

  return false;
}

function banUserSend() {
  $('*').css('cursor', 'progress');

  var reason = $('#banUserForm #reason').val();
  Sijax.request('banUser', [reason]);

  return false;
}

// Settings Page -------------------------------------------------------------------------------------------------------------

function deleteAccountPopup() {
  $('#deleteAccountPopup').fadeIn(50);
  $('.overlay').fadeIn(50);
}

function profilePopup() {
  $('#profilePopup').fadeIn(50);
  $('.overlay').fadeIn(50);
}

function hidePopup() {
  $('.popup').fadeOut(50);
  $('.overlay').fadeOut(50);
}

$(document).keyup(function(e) {
  if (e.keyCode == 27) {
    hidePopup();
  }
});

// Foundation ----------------------------------------------------------------------------------------------------------------

$(document).foundation();

// Google Analytics ----------------------------------------------------------------------------------------------------------

(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
(i[r].q=i[r].q||[]).push(arguments);},i[r].l=1*new Date();a=s.createElement(o),
m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m);
})(window,document,'script','//www.google-analytics.com/analytics.js','ga');

ga('create', 'UA-41576939-4', 'auto');
ga('send', 'pageview');

// Google AdSense
[].forEach.call(document.querySelectorAll('.adsbygoogle'), function(){
(adsbygoogle = window.adsbygoogle || []).push({});
});
