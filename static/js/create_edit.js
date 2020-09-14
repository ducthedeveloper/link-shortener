//
var icon = document.getElementById("icon");
function toggleAdvSettings() {
  let openAdvSettings = document.getElementById("advSettings");
  openAdvSettings.addEventListener("click", function () {
    let modal = document.getElementById("advRequirements");
    this.classList.toggle("active");
    if (modal.style.maxHeight) {
      modal.style.maxHeight = null;
      icon.className = "fa fa-angle-right";
    } else {
      modal.style.maxHeight = modal.scrollHeight + "px";
      icon.className = "fa fa-angle-right open";
    }
  });
}
// button disable
function disableBtn() {
  let orgLink = document.getElementById("orgUrl");
  let shortLink = document.getElementById("shortlink");
  let formInput = document.getElementsByClassName("formRequiredField");
  for (i = 0; i < formInput.length; i++) {
    submit.disabled = true;
    formInput[i].addEventListener("keyup", function () {
      if (shortLink.value === "" || orgLink.value === "") {
        submit.disabled = true;
      } else {
        submit.disabled = false;
      }
    });
  }
}
// dynamic text update

function txtUpdateOnChange() {
  let shortLink = document.getElementById("shortlink");
  shortLink.addEventListener("keyup", function () {
    let printout = document.getElementById("shortlinked");
    var x = shortLink.value;
    printout.innerHTML = "www.fueled.by/" + x;
  });
}

//copy inline
function copySingle() {
  let hoverCopy = document.getElementsByClassName("copyHoverSquare");
  var range = document.createRange();
  range.selectNode(document.getElementById("shortlinked"));
  window.getSelection().removeAllRanges(); // clear current selection
  window.getSelection().addRange(range); // to select text
  document.execCommand("copy");
  window.getSelection().removeAllRanges();
  hoverCopy[0].innerHTML = "copied!";
  setTimeout(function () {
    hoverCopy[0].innerHTML = "copy";
  }, 800);
}
// date picker
if ($(".editAndCreate").length) {
  function datePicker() {
    $(function () {
      $('input[name="birthday"]').daterangepicker({
        singleDatePicker: true,
        showDropdowns: true,
        minYear: 1901,
        maxYear: parseInt(moment().format("YYYY"), 10),
      });
    });
  }
}
