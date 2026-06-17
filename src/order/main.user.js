// ==UserScript==
// @name         jp kawai
// @namespace    charismafight@hotmail.com
// @version      2.0
// @description  automatically submit basic data to order
// @author       lli
// @match        *://www.tokyokawaiilife.jp/*
// @grant        none
// @license      MIT
// ==/UserScript==

(function () {
  "use strict";

  // 存储键名常量
  const STORAGE_KEYS = {
    ENABLED: "script_enabled", // 总开关
    QUANTITY: "persistent_number_input",
    AUTO_ADD_TO_CART: "auto_add_to_cart",
    PRODUCT_KEYWORD: "product_keyword",
    AUTO_FINAL_CONFIRM: "auto_final_confirm",
  };

  // 等待元素加载的辅助函数
  function waitForElement(selector, timeout = 5000) {
    return new Promise((resolve, reject) => {
      const element = document.querySelector(selector);
      if (element) return resolve(element);

      const observer = new MutationObserver(() => {
        const element = document.querySelector(selector);
        if (element) {
          observer.disconnect();
          resolve(element);
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });

      setTimeout(() => {
        observer.disconnect();
        reject(new Error(`Element ${selector} not found within ${timeout}ms`));
      }, timeout);
    });
  }

  // 通过 name 属性查找元素
  function waitForElementByName(name, timeout = 5000) {
    return new Promise((resolve, reject) => {
      const selector = `[name="${name}"]`;
      const element = document.querySelector(selector);
      if (element) return resolve(element);

      const observer = new MutationObserver(() => {
        const element = document.querySelector(selector);
        if (element) {
          observer.disconnect();
          resolve(element);
        }
      });

      observer.observe(document.body, {
        childList: true,
        subtree: true,
      });

      setTimeout(() => {
        observer.disconnect();
        reject(new Error(`Element with name="${name}" not found within ${timeout}ms`));
      }, timeout);
    });
  }

  // 短暂延迟，用于等待DOM更新
  const microDelay = () => new Promise((resolve) => setTimeout(resolve, 50));

  // 创建控制面板
  function createControlPanel() {
    const container = document.createElement("div");
    container.style.cssText = `
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 9999;
            background: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.15);
            font-family: Arial, sans-serif;
            font-size: 14px;
            min-width: 200px;
            border: 1px solid #ddd;
        `;

    // ========== 总开关（放在最顶部，最显眼） ==========
    const enabledContainer = document.createElement("div");
    enabledContainer.style.cssText = `
            margin-bottom: 15px;
            padding-bottom: 10px;
            border-bottom: 2px solid #ddd;
        `;

    const enabledCheckbox = document.createElement("input");
    enabledCheckbox.type = "checkbox";
    enabledCheckbox.id = "script_enabled_checkbox";
    enabledCheckbox.style.transform = "scale(1.2)";
    enabledCheckbox.style.marginRight = "8px";

    const enabledLabel = document.createElement("label");
    enabledLabel.htmlFor = "script_enabled_checkbox";
    enabledLabel.textContent = "脚本总开关";
    enabledLabel.style.fontWeight = "bold";
    enabledLabel.style.fontSize = "15px";
    enabledLabel.style.color = "#333";

    const enabledStatus = document.createElement("span");
    enabledStatus.style.marginLeft = "10px";
    enabledStatus.style.fontSize = "12px";
    enabledStatus.style.padding = "2px 6px";
    enabledStatus.style.borderRadius = "4px";

    const savedEnabled = localStorage.getItem(STORAGE_KEYS.ENABLED);
    const isEnabled = savedEnabled === null ? true : savedEnabled === "true"; // 默认开启
    enabledCheckbox.checked = isEnabled;

    // 更新状态标签
    function updateEnabledStatus() {
      if (enabledCheckbox.checked) {
        enabledStatus.textContent = "● 已启用";
        enabledStatus.style.backgroundColor = "#d4edda";
        enabledStatus.style.color = "#155724";
      } else {
        enabledStatus.textContent = "○ 已禁用";
        enabledStatus.style.backgroundColor = "#f8d7da";
        enabledStatus.style.color = "#721c24";
      }
    }
    updateEnabledStatus();

    enabledCheckbox.addEventListener("change", () => {
      localStorage.setItem(STORAGE_KEYS.ENABLED, enabledCheckbox.checked);
      updateEnabledStatus();
      updateStatus(statusDiv, enabledCheckbox.checked ? "脚本已启用" : "脚本已禁用", !enabledCheckbox.checked);
    });

    enabledContainer.appendChild(enabledCheckbox);
    enabledContainer.appendChild(enabledLabel);
    enabledContainer.appendChild(enabledStatus);
    container.appendChild(enabledContainer);

    // ========== 数量输入框 ==========
    const quantityLabel = document.createElement("div");
    quantityLabel.textContent = "数量:";
    quantityLabel.style.marginBottom = "5px";
    quantityLabel.style.fontWeight = "bold";

    const quantityInput = document.createElement("input");
    quantityInput.type = "number";
    quantityInput.placeholder = "input quantity";
    quantityInput.style.cssText = `
            width: 100%;
            padding: 5px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        `;

    const savedQuantity = localStorage.getItem(STORAGE_KEYS.QUANTITY);
    if (savedQuantity !== null) {
      quantityInput.value = savedQuantity;
    }

    quantityInput.addEventListener("input", () => {
      localStorage.setItem(STORAGE_KEYS.QUANTITY, quantityInput.value);
    });

    // ========== 商品关键词输入框 ==========
    const keywordLabel = document.createElement("div");
    keywordLabel.textContent = "商品关键词:";
    keywordLabel.style.marginBottom = "5px";
    keywordLabel.style.fontWeight = "bold";

    const keywordInput = document.createElement("input");
    keywordInput.type = "text";
    keywordInput.placeholder = "输入商品名称关键词";
    keywordInput.style.cssText = `
            width: 100%;
            padding: 5px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        `;

    const savedKeyword = localStorage.getItem(STORAGE_KEYS.PRODUCT_KEYWORD);
    if (savedKeyword !== null) {
      keywordInput.value = savedKeyword;
    }

    keywordInput.addEventListener("input", () => {
      localStorage.setItem(STORAGE_KEYS.PRODUCT_KEYWORD, keywordInput.value);
    });

    // ========== 自动加入购物车复选框 ==========
    const autoAddCheckbox = document.createElement("input");
    autoAddCheckbox.type = "checkbox";
    autoAddCheckbox.id = "auto_add_checkbox";

    const autoAddLabel = document.createElement("label");
    autoAddLabel.htmlFor = "auto_add_checkbox";
    autoAddLabel.textContent = "自动加入购物车";
    autoAddLabel.style.marginLeft = "5px";

    const autoAddContainer = document.createElement("div");
    autoAddContainer.style.marginBottom = "10px";
    autoAddContainer.appendChild(autoAddCheckbox);
    autoAddContainer.appendChild(autoAddLabel);

    const savedAutoAdd = localStorage.getItem(STORAGE_KEYS.AUTO_ADD_TO_CART);
    if (savedAutoAdd !== null) {
      autoAddCheckbox.checked = savedAutoAdd === "true";
    }

    autoAddCheckbox.addEventListener("change", () => {
      localStorage.setItem(STORAGE_KEYS.AUTO_ADD_TO_CART, autoAddCheckbox.checked);
    });

    // ========== 自动最后确认复选框 ==========
    const autoFinalConfirmCheckbox = document.createElement("input");
    autoFinalConfirmCheckbox.type = "checkbox";
    autoFinalConfirmCheckbox.id = "auto_final_confirm_checkbox";

    const autoFinalConfirmLabel = document.createElement("label");
    autoFinalConfirmLabel.htmlFor = "auto_final_confirm_checkbox";
    autoFinalConfirmLabel.textContent = "自动最后确认";
    autoFinalConfirmLabel.style.marginLeft = "5px";

    const autoFinalConfirmContainer = document.createElement("div");
    autoFinalConfirmContainer.style.marginBottom = "10px";
    autoFinalConfirmContainer.appendChild(autoFinalConfirmCheckbox);
    autoFinalConfirmContainer.appendChild(autoFinalConfirmLabel);

    const savedAutoFinalConfirm = localStorage.getItem(STORAGE_KEYS.AUTO_FINAL_CONFIRM);
    if (savedAutoFinalConfirm !== null) {
      autoFinalConfirmCheckbox.checked = savedAutoFinalConfirm === "true";
    }

    autoFinalConfirmCheckbox.addEventListener("change", () => {
      localStorage.setItem(STORAGE_KEYS.AUTO_FINAL_CONFIRM, autoFinalConfirmCheckbox.checked);
    });

    // ========== 状态显示区域 ==========
    const statusDiv = document.createElement("div");
    statusDiv.style.cssText = `
            margin-top: 10px;
            padding: 5px;
            background: #f0f0f0;
            border-radius: 4px;
            font-size: 12px;
            color: #666;
        `;
    statusDiv.textContent = "就绪";

    // 组装面板
    container.appendChild(quantityLabel);
    container.appendChild(quantityInput);
    container.appendChild(keywordLabel);
    container.appendChild(keywordInput);
    container.appendChild(autoAddContainer);
    container.appendChild(autoFinalConfirmContainer);
    container.appendChild(statusDiv);

    document.body.appendChild(container);

    return {
      enabledCheckbox,
      quantityInput,
      keywordInput,
      autoAddCheckbox,
      autoFinalConfirmCheckbox,
      statusDiv,
    };
  }

  // 更新状态显示
  function updateStatus(statusDiv, message, isError = false) {
    statusDiv.textContent = message;
    statusDiv.style.color = isError ? "red" : "#666";
    console.log(message);
  }

  // 检查脚本是否启用
  function isScriptEnabled(enabledCheckbox) {
    return enabledCheckbox.checked;
  }

  // ========== 需要你实现的函数 ==========
  async function autoAddToCart(keyword, statusDiv) {
    updateStatus(statusDiv, `正在自动加入购物车: ${keyword}`);
    const product = await waitForElementByName(keyword);
    product.click();
    updateStatus(statusDiv, `自动加入购物车完成`);
    return true;
  }

  async function autoFinalConfirm(statusDiv) {
    updateStatus(statusDiv, `正在执行最后确认`);
    const confirmBtn = await waitForElement("#order");
    confirmBtn?.click();
    updateStatus(statusDiv, `最后确认完成`);
    return true;
  }

  // ========== 优化的自动提交流程 ==========

  // 处理购物车页面
  async function handleCartPage(controls) {
    const { enabledCheckbox, quantityInput, statusDiv } = controls;

    // 检查总开关
    if (!isScriptEnabled(enabledCheckbox)) {
      updateStatus(statusDiv, "脚本已禁用，跳过购物车处理");
      return;
    }

    try {
      const countInput = await waitForElement("#count");
      const tempValue = quantityInput.value;

      updateStatus(statusDiv, `当前数量: ${countInput.value}, 目标数量: ${tempValue}`);

      if (countInput.value !== tempValue && tempValue) {
        countInput.value = tempValue;
        countInput.dispatchEvent(new Event("change", { bubbles: true }));
        await microDelay();
        const calcButton = await waitForElement("#submit_1");
        calcButton.click();
        updateStatus(statusDiv, "已更新数量并重新计算价格");
        await microDelay();
      }

      const buyButton = await waitForElement("#buy_here");
      buyButton.click();
      updateStatus(statusDiv, "已点击结算按钮");
    } catch (error) {
      updateStatus(statusDiv, `购物车页面处理失败: ${error.message}`, true);
    }
  }

  // 处理订单支付页面
  async function handleOrderPaymentPage(controls) {
    const { enabledCheckbox, statusDiv } = controls;

    // 检查总开关
    if (!isScriptEnabled(enabledCheckbox)) {
      updateStatus(statusDiv, "脚本已禁用，跳过订单支付处理");
      return;
    }

    try {
      const settleButton = await waitForElement("#settleEdit");
      settleButton.click();
      updateStatus(statusDiv, "已进入确认页面");
    } catch (error) {
      updateStatus(statusDiv, `订单支付页面处理失败: ${error.message}`, true);
    }
  }

  // 处理确认页面
  async function handleConfirmPage(controls) {
    const { enabledCheckbox, autoFinalConfirmCheckbox, statusDiv } = controls;

    // 检查总开关
    if (!isScriptEnabled(enabledCheckbox)) {
      updateStatus(statusDiv, "脚本已禁用，跳过确认页面处理");
      return;
    }

    try {
      await microDelay();

      const codOption = await waitForElement("#fs2_settle-cod");
      codOption.click();
      updateStatus(statusDiv, "已选择货到付款");

      await microDelay();

      const submitButton = await waitForElement("#submit");
      submitButton.click();
      updateStatus(statusDiv, "订单已提交");

      if (autoFinalConfirmCheckbox.checked) {
        await microDelay();
        await autoFinalConfirm(statusDiv);
      } else {
        updateStatus(statusDiv, "自动最后确认已关闭，需要手动确认");
      }
    } catch (error) {
      updateStatus(statusDiv, `确认页面处理失败: ${error.message}`, true);
    }
  }

  // 主逻辑
  async function main() {
    const controls = createControlPanel();
    const url = window.location.href;
    const { enabledCheckbox, autoAddCheckbox, keywordInput } = controls;

    // 商品页面处理
    if (url.includes("/fs/lizlisaadmin/") && !url.includes("ShoppingCart") && !url.includes("DeliveryEdit") && !url.includes("SettleEdit")) {
      // 检查总开关和自动加入购物车开关
      if (isScriptEnabled(enabledCheckbox) && autoAddCheckbox.checked && keywordInput.value) {
        await autoAddToCart(keywordInput.value, controls.statusDiv);
        updateStatus(controls.statusDiv, "自动加入购物车完成，等待手动进入购物车");
      } else if (!isScriptEnabled(enabledCheckbox)) {
        updateStatus(controls.statusDiv, "脚本已禁用");
      } else {
        updateStatus(controls.statusDiv, "商品页面 - 等待操作");
      }
    }

    // 购物车页面处理
    if (url.includes("ShoppingCart.html")) {
      await handleCartPage(controls);
    }

    // 订单支付页面处理
    if (url.includes("DeliveryEdit.html")) {
      await handleOrderPaymentPage(controls);
    }

    // 确认页面处理
    if (url.includes("SettleEdit.html")) {
      await handleConfirmPage(controls);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
