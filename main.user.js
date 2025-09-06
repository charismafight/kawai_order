// ==UserScript==
// @updateURL  https://raw.githubusercontent.com/charismafight/kawai_order/main/main.user.js
// @downloadURL  https://raw.githubusercontent.com/charismafight/kawai_order/main/main.user.js
// @name         jp kawai
// @namespace    charismafight@hotmail.com
// @version      0.1
// @description  修改网页标题为“Hello, Tampermonkey!”
// @author       lli
// @match        https://www.tokyokawaiilife.jp/*/*
// @grant        none
// @license      MIT
// ==/UserScript==

console.log("tamper monkey started");

(function () {
  "use strict";
  const testName = "カートに入れる";
  document.addEventListener("click", (e) => {
    if (e.target.matches(`input[alt="${testName}"]`)) {
      console.log(e.target);
    }
  });
})();
