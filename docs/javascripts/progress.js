document.addEventListener("DOMContentLoaded", function () {
  var STORAGE_KEY = "el-progress";
  var TOKEN_KEY = "el-github-token";
  var GIST_ID_KEY = "el-gist-id";
  var GIST_FILENAME = "engineering-learning-progress.json";
  var syncTimeout = null;

  function getToken() {
    return localStorage.getItem(TOKEN_KEY);
  }

  function getGistId() {
    return localStorage.getItem(GIST_ID_KEY);
  }

  function getProgress() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_KEY)) || {};
    } catch (e) {
      return {};
    }
  }

  function saveProgressLocal(data) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  }

  function scheduleSyncToGist(data) {
    if (!getToken()) return;
    if (syncTimeout) clearTimeout(syncTimeout);
    syncTimeout = setTimeout(function () {
      syncToGist(data);
    }, 1000);
  }

  function syncToGist(data) {
    var token = getToken();
    if (!token) return;

    var gistId = getGistId();
    var body = JSON.stringify({
      description: "Engineering Learning Progress",
      public: false,
      files: {}
    });
    var payload = JSON.parse(body);
    payload.files[GIST_FILENAME] = { content: JSON.stringify(data, null, 2) };

    if (gistId) {
      fetch("https://api.github.com/gists/" + gistId, {
        method: "PATCH",
        headers: {
          Authorization: "token " + token,
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ files: payload.files })
      }).catch(function () {});
    } else {
      fetch("https://api.github.com/gists", {
        method: "POST",
        headers: {
          Authorization: "token " + token,
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      })
        .then(function (r) { return r.json(); })
        .then(function (gist) {
          if (gist.id) {
            localStorage.setItem(GIST_ID_KEY, gist.id);
          }
        })
        .catch(function () {});
    }
  }

  function pullFromGist(callback) {
    var token = getToken();
    var gistId = getGistId();
    if (!token || !gistId) {
      callback(null);
      return;
    }

    fetch("https://api.github.com/gists/" + gistId, {
      headers: { Authorization: "token " + token }
    })
      .then(function (r) { return r.json(); })
      .then(function (gist) {
        if (gist.files && gist.files[GIST_FILENAME]) {
          var remote = JSON.parse(gist.files[GIST_FILENAME].content);
          callback(remote);
        } else {
          callback(null);
        }
      })
      .catch(function () { callback(null); });
  }

  function mergeProgress(local, remote) {
    if (!remote) return local;
    var merged = Object.assign({}, remote, local);
    return merged;
  }

  function showTokenPrompt() {
    var existing = document.getElementById("token-setup");
    if (existing) return;

    var panel = document.getElementById("progress-panel");
    if (!panel) return;

    var div = document.createElement("div");
    div.id = "token-setup";
    div.innerHTML =
      '<div style="background:#f5f5f5;border:1px solid #e0e0e0;border-radius:8px;padding:1rem;margin-bottom:1rem;">' +
      "<p style=\"margin:0 0 0.5rem\"><strong>跨设备同步</strong>：输入 GitHub Token 可在多设备间同步学习进度</p>" +
      '<p style="margin:0 0 0.5rem;font-size:0.85rem;color:#666;">需要 gist 权限。<a href="https://github.com/settings/tokens/new?scopes=gist&description=engineering-learning" target="_blank">点此创建</a></p>' +
      '<div style="display:flex;gap:0.5rem;">' +
      '<input id="token-input" type="password" placeholder="ghp_xxxx" style="flex:1;padding:0.5rem;border:1px solid #ccc;border-radius:4px;">' +
      '<input id="gist-id-input" type="text" placeholder="Gist ID（可选，已有则填）" style="width:200px;padding:0.5rem;border:1px solid #ccc;border-radius:4px;">' +
      '<button id="token-save" style="padding:0.5rem 1rem;background:#4caf50;color:white;border:none;border-radius:4px;cursor:pointer;">保存</button>' +
      "</div></div>";

    panel.parentNode.insertBefore(div, panel);

    document.getElementById("token-save").addEventListener("click", function () {
      var token = document.getElementById("token-input").value.trim();
      var gistId = document.getElementById("gist-id-input").value.trim();
      if (!token) return;
      localStorage.setItem(TOKEN_KEY, token);
      if (gistId) {
        localStorage.setItem(GIST_ID_KEY, gistId);
      }
      div.remove();
      initProgressPanel();
    });
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
        saveProgressLocal(progress);
        scheduleSyncToGist(progress);
        updateButtons();
      });
    });

    // Pull remote on page load to merge
    pullFromGist(function (remote) {
      if (remote) {
        progress = mergeProgress(progress, remote);
        saveProgressLocal(progress);
        updateButtons();
      }
    });

    updateButtons();
  }

  // Progress panel on index page
  function initProgressPanel() {
    var panel = document.getElementById("progress-panel");
    if (!panel) return;

    var token = getToken();
    if (!token) {
      showTokenPrompt();
    }

    var progress = getProgress();

    function render(progress) {
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

      if (token) {
        html += '<div style="margin-top:1rem;font-size:0.8rem;color:#9e9e9e;">已启用跨设备同步</div>';
      }

      panel.innerHTML = html;
    }

    render(progress);

    // Pull remote and re-render
    if (token) {
      pullFromGist(function (remote) {
        if (remote) {
          progress = mergeProgress(progress, remote);
          saveProgressLocal(progress);
          render(progress);
        }
      });
    }
  }

  initProgressPanel();
});
