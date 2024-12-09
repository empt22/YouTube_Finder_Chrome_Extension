console.clear
console.log('This is a popup from EL - 20241209!')

console.log("comment outside searchWord function :)") /* does print */

/** search the current website for words */
const searchWord = () => {
  
    console.log("comment inside searchWord function :)") /* doesn't print */

    const text = document.body.textContent ; 
    const flower = text.includes("flower" || "Flower") ;

    /* get all the text data on the page */
    const allInnerText = document.body.innerText ;

    return{
      oneWord: flower,
      otherData: allInnerText,
      otherData2: 4
    }
}

chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.scripting.executeScript({
        target: { tabId: tabs[0].id},
        func: searchWord
    }, (result) => {
                     
        if (result[0].result.oneWord){
          
            console.log("found some flowers!")
            const pageResult = "This webpage has flower info";
            document.getElementById("foundWord").innerText = pageResult; 

        } else {
            console.log("didn't find flowers")
        }
    }
)

}


)

