document.addEventListener("DOMContentLoaded", function () {
  document.querySelectorAll(".admonition.quiz").forEach(function (quiz) {
    var items = quiz.querySelectorAll("li");
    var locked = false;

    items.forEach(function (item) {
      var checkbox = item.querySelector('input[type="checkbox"]');
      if (checkbox) {
        var isCorrect = checkbox.checked;
        checkbox.style.display = "none";
        item.dataset.correct = isCorrect;
        item.classList.add("quiz-option");
      }
    });

    items.forEach(function (item) {
      item.addEventListener("click", function () {
        if (locked) return;
        locked = true;

        if (item.dataset.correct === "true") {
          item.classList.add("quiz-correct");
        } else {
          item.classList.add("quiz-wrong");
          items.forEach(function (i) {
            if (i.dataset.correct === "true") {
              i.classList.add("quiz-correct");
            }
          });
        }

        items.forEach(function (i) {
          i.classList.add("quiz-locked");
        });

        var details = quiz.querySelector("details");
        if (details) {
          details.open = true;
        }
      });
    });
  });
});
