chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === "getPageData"){

        const pageData = {
            url: window.location.href,
            content: document.body.textContent || ""
        };
        sendResponse(pageData);
    }

})
;