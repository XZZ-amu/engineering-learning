document.addEventListener("DOMContentLoaded", function () {
  var STORAGE_KEY = "el-progress";

  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function saveProgress(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  // Chapter status buttons
  var statusContainer = document.querySelector(".chapter-status");
  if (statusContainer) {
    var chapter = statusContainer.dataset.chapter;
    var progress = getProgress();
    var buttons = statusContainer.querySelectorAll(".status-btn");

    function updateButtons() {
      var state = progress[chapter];
      buttons.forEach(function (btn) {
        btn.classList.remove("active");
      });
      if (state === "done") {
        statusContainer.querySelector(".status-btn.done").classList.add("active");
      } else if (state === "stuck") {
        statusContainer.querySelector(".status-btn.stuck").classList.add("active");
      }
    }

    buttons.forEach(function (btn) {
      btn.addEventListener("click", function () {
        var newState = btn.classList.contains("done") ? "done" : "stuck";
        progress[chapter] = newState;
        saveProgress(progress);
        updateButtons();
      });
    });

    updateButtons();
  }

  // Progress panel on index page
  var panel = document.getElementById("progress-panel");
  if (panel) {
    var progress = getProgress();
    var chapters = {
      "P0 每天都会碰到": [
        { id: "chapter-05", title: "异步任务与队列", url: "chapters/chapter-05/" },
        { id: "chapter-06", title: "API 设计", url: "chapters/chapter-06/" },
        { id: "chapter-07", title: "文件与存储", url: "chapters/chapter-07/" },
        { id: "chapter-08", title: "React 状态", url: "chapters/chapter-08/" }
      ],
      "P1 做好产品必须懂": [
        { id: "chapter-09", title: "AI 工程", url: "chapters/chapter-09/" },
        { id: "chapter-10", title: "数据库", url: "chapters/chapter-10/" },
        { id: "chapter-11", title: "认证付费", url: "chapters/chapter-11/" },
        { id: "chapter-12", title: "WebSocket", url: "chapters/chapter-12/" }
      ],
      "P2 从能做到做得好": [
        { id: "chapter-13", title: "系统设计", url: "chapters/chapter-13/" },
        { id: "chapter-14", title: "性能优化", url: "chapters/chapter-14/" },
        { id: "chapter-15", title: "安全基础", url: "chapters/chapter-15/" }
      ]
    };

    var html = "";
    Object.keys(chapters).forEach(function (group) {
      var items = chapters[group];
      var doneCount = items.filter(function (c) { return progress[c.id] === "done"; }).length;

      html += '<div class="progress-group">';
      html += '<div class="progress-header">';
      html += '<span class="progress-title">' + group + "</span>";
      html += '<span class="progress-count">' + doneCount + "/" + items.length + "</span>";
      html += "</div>";
      html += '<div class="progress-blocks">';

      items.forEach(function (c) {
        var state = progress[c.id] || "unread";
        html += '<a href="' + c.url + '" class="progress-block ' + state + '" title="' + c.title + '">';
        html += c.title;
        html += "</a>";
      });

      html += "</div></div>";
    });

    panel.innerHTML = html;
  }
});
