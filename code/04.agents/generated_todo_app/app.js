document.addEventListener("DOMContentLoaded", function () {
  const form = document.getElementById("todo-form");
  const input = document.getElementById("todo-input");
  const list = document.getElementById("todo-list");
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    const val = input.value.trim();
    if (val) {
      addTodo(val);
      input.value = "";
    }
  });
  function addTodo(text) {
    const li = document.createElement("li");
    li.textContent = text;
    li.addEventListener("click", function () {
      li.classList.toggle("done");
    });
    li.addEventListener("dblclick", function () {
      if (li.classList.contains("done")) return;
      const currentText = li.childNodes[0].nodeValue;
      const editInput = document.createElement("input");
      editInput.type = "text";
      editInput.value = currentText;
      editInput.className = "edit-input";
      li.childNodes[0].nodeValue = "";
      li.insertBefore(editInput, li.firstChild);
      editInput.focus();
      editInput.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          finishEdit();
        }
      });
      editInput.addEventListener("blur", finishEdit);
      function finishEdit() {
        var val = editInput.value.trim();
        li.removeChild(editInput);
        li.childNodes[0].nodeValue = val ? val : currentText;
      }
    });
    const btn = document.createElement("button");
    btn.textContent = "Remove";
    btn.className = "remove-btn";
    btn.onclick = function (e) {
      e.stopPropagation();
      list.removeChild(li);
    };
    li.appendChild(btn);
    list.appendChild(li);
  }
});
