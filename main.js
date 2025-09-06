// ==UserScript==
// @name         jp kawai
// @namespace    charismafight@hotmail.com
// @version      0.1
// @description  修改网页标题为“Hello, Tampermonkey!”
// @author       lli
// @match        https://www.tokyokawaiilife.jp/*/*
// @grant        none
// @license      MIT
// ==/UserScript==

(function () {
  "use strict";
  const testName = "カートに入れる";
  document.addEventListener("click", (e) => {
    if (e.target.matches(`input[alt="${testName}"]`)) {
      console.log(e.target);
    }
  });
})();
