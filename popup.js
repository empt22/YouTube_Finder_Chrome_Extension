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

/**Heroku app python */
/*
document.getElementById('process-button').addEventListener('click', async () => {
    try {
        const response = await fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/hello', {
            method: 'GET',
        });

        const result = await response.json();
        document.getElementById('result').textContent = result.message;
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('result').textContent = 'Error connecting to server';
    }
});
*/

// popup.js

document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('process-button');
    const sendInputButton = document.getElementById('send-input-button');
    const resultElement = document.getElementById('result');

    button.addEventListener('click', function() {
        fetchHelloWorld()
            .then(result => {
                resultElement.textContent = result;
            })
            .catch(error => {
                resultElement.textContent = "Error: " + error;
            });
    });

    // if clicked, send current url and all content
    sendInputButton.addEventListener('click', function() {
        // website URL, text content 
        const currentUrl = window.location.href;
        const pageContent = document.body.textContent;

        // Send the data to the Flask app
        sendDataToFlask(currentUrl, pageContent)
            .then(response => {
                resultElement.textContent = "Data sent successfully!";
            })
            .catch(error => {
                resultElement.textContent = "Error: " + error;
            });
    });

});

function fetchHelloWorld() {
    return fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/hello')  
        .then(response => response.text())
        .then(data => {
            return data;
        });
}

// when button clicked, send to app
function sendDataToFlask(url, content) {
    return fetch('https://evening-wave-25134-21052b612e3a.herokuapp.com/hello', {  
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url, content: content })
    })
    .then(response => response.json())
    .then(data => {
        return data;
    });
}


